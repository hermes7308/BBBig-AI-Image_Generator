import glob
import json
import os
import threading
import time
import uuid
from datetime import datetime
import shutil

import torch
from diffusers import StableDiffusionPipeline
from dotenv import load_dotenv
from flask import request
from torch import autocast

load_dotenv()
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
model_id = "CompVis/stable-diffusion-v1-4"
device = "cuda"

HOME_PATH = os.getenv("HOME_PATH")
TASK_STATES_FILENAME = os.getenv("TASK_STATES_FILENAME")

waiting_queue = []

WAITING = "Waiting"
RUNNING = "Running"
COMPLETED = "Completed"


class Task:
    def __init__(self, task_id, text, guidance_scale, num_of_generation, directory_path):
        self.task_id = task_id
        self.text = text
        self.guidance_scale = guidance_scale
        self.num_of_generation = num_of_generation
        self.directory_path = directory_path
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_date = None
        self.status = None
        self.set_status(WAITING)

    def set_status(self, status):
        self.status = status
        self.updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class StableDiffusion(threading.Thread):
    def __init__(self):
        super().__init__()
        self.pipe = None
        self.running = True

    @staticmethod
    def get_task_directory(task_id):
        return os.path.join(HOME_PATH, task_id)

    @staticmethod
    def save_task_states(task):
        task_states_path = os.path.join(task.directory_path, TASK_STATES_FILENAME)
        with open(task_states_path, "w") as f:
            temp = task.__dict__
            task_states = json.dumps(temp, indent=4)
            f.write(task_states)

    def load_pipe(self):
        print("=" * 50)
        print("Stable Diffusion Settings")
        print("* Model ID:", model_id)
        print("* Device:", device)
        print("* HOME_PATH:", HOME_PATH)
        print("* Status:", WAITING, RUNNING, COMPLETED)
        print("=" * 50)
        pipe = StableDiffusionPipeline.from_pretrained(model_id, revision="fp16",
                                                       torch_dtype=torch.float16,
                                                       use_auth_token=AUTH_TOKEN)
        pipe.to(device)
        self.pipe = pipe

    def create_task_id(self):
        while True:
            task_id = str(uuid.uuid4())
            directory_path = self.get_task_directory(task_id=task_id)
            if os.path.exists(directory_path):
                continue

            os.makedirs(directory_path)
            break

        return task_id, directory_path

    def get_task(self, task_id):
        task_directory = self.get_task_directory(task_id=task_id)
        task_states_path = os.path.join(task_directory, TASK_STATES_FILENAME)
        with open(task_states_path, "r") as f:
            task = json.load(f)
            images = self.get_images(task_id=task_id)
            task["images"] = [f"{request.host_url}{image}" for image in images]
            return task

    def get_images(self, task_id):
        task_directory = self.get_task_directory(task_id=task_id)
        image_file_pattern = os.path.join(task_directory, "*.png")
        image_paths = glob.glob(image_file_pattern)
        images = []
        for image_path in image_paths:
            _, task_id, filename = image_path.replace(HOME_PATH, "").split("\\")
            image = f"image/{task_id}/{filename}"
            images.append(image)

        return images

    def get_generated_tasks(self):
        task_ids = os.listdir(path=HOME_PATH)
        tasks = []
        for task_id in task_ids:
            task = self.get_task(task_id=task_id)
            tasks.append(task)

        tasks.sort(reverse=True, key=lambda t: t["updated_date"])
        return tasks

    def get_image(self, task_id, filename):
        task_directory = self.get_task_directory(task_id=task_id)
        image_path = os.path.join(task_directory, filename)
        return image_path

    def generate_task(self, text, guidance_scale=8.5, num_of_generation=12):
        if self.pipe is None:
            return None

        task_id, directory_path = self.create_task_id()
        task = Task(task_id=task_id, text=text, guidance_scale=guidance_scale, num_of_generation=num_of_generation,
                    directory_path=directory_path)
        self.save_task_states(task=task)
        waiting_queue.append(task)
        return task_id

    def delete_task(self, taskID):
        task_directory = os.path.join(HOME_PATH, taskID)
        if os.path.exists(task_directory):
            shutil.rmtree(task_directory)

    def stop(self):
        self.running = False

    def run(self):
        print("=" * 50)
        print("Start Stable Diffusion waiting queue.")
        print("=" * 50)

        while self.running:
            if len(waiting_queue) == 0:
                time.sleep(1)
                continue

            task = waiting_queue.pop()
            task.set_status(RUNNING)
            self.save_task_states(task=task)

            print("Generating for", task.task_id)
            for index in range(task.num_of_generation):
                print("No. " + str(index + 1), task.task_id)
                with autocast(device):
                    image = self.pipe(task.text, guidance_scale=task.guidance_scale)["sample"][0]

                filename = "{}.png".format(datetime.now().strftime("%Y-%m-%d %H%M%S"))
                image_path = os.path.join(task.directory_path, filename)
                image.save(image_path)

            task.set_status(COMPLETED)
            self.save_task_states(task=task)

        print("=" * 50)
        print("Stable Diffusion queue thread exit.")
        print("=" * 50)

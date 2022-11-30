import os
import signal
import sys
import time

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from googletrans import Translator

from stable_diffusion import StableDiffusion, waiting_queue

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

translator = Translator()
sd = StableDiffusion()
# sd.setDaemon(True)
sd.load_pipe()
sd.start()


def exit_gracefully(*args):
    sd.stop()
    sd.join()
    time.sleep(2)
    sys.exit(0)


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route("/translate", methods=['POST'])
def translate():
    data = request.json
    translated_data = translator.translate(text=data["requestText"])
    result = {
        "originLang": translated_data.src,
        "originText": translated_data.origin,
        "destLang": translated_data.dest,
        "destText": translated_data.text,
    }
    return jsonify(result)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    task_id = sd.generate_task(text=str(data["requestText"]),
                               guidance_scale=float(data["guidanceScale"]),
                               num_of_generation=int(data["numOfGeneration"]))
    error_message = None
    if task_id is None:
        error_message = "Stable Diffusion pip is not loaded."

    return jsonify({
        "errorMessage": error_message,
        "taskID": task_id
    })


@app.route("/queue", methods=["GET"])
def get_queue():
    return jsonify({
        "numOfQueue": len(waiting_queue),
        "queue": [task.__dict__ for task in waiting_queue]
    })


@app.route("/task/<task_id>", methods=["GET"])
def get_task(task_id):
    task = sd.get_task(task_id=task_id)
    return task


@app.route("/generated_tasks", methods=["GET"])
def get_generated_tasks():
    generated_tasks = sd.get_generated_tasks()
    return generated_tasks


@app.route("/task/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    sd.delete_task(taskID=task_id)
    return jsonify({
        "status": "deleted"
    })


@app.route("/image/<task_id>/<filename>", methods=["GET"])
def get_image(task_id, filename):
    image_path = sd.get_image(task_id=task_id, filename=filename)
    return send_file(image_path, mimetype="image/png")


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)

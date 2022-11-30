<script>
export default {
  data() {
    return {}
  },
  computed: {
    tasks() {
      return this.$store.state.tasks;
    }
  },
  mounted() {
    this.getGeneratedTasks()
  },
  methods: {
    getGeneratedTasks() {
      this.$store.dispatch("getGeneratedTasks");
    },
    deleteTask(taskID) {
      this.$store.dispatch("deleteTask", {taskID: taskID});
    },
    downloadFile(url) {
      this.$store.dispatch("downloadFile", {url: url});
    },
    copyText(text) {
      this.$store.dispatch("copyText", {text: text});
    }
  }
}
</script>

<template>
  <div class="container">
    <div v-if="tasks.length === 0" class="d-block text-center">
      <div class="spinner-grow text-success" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <template v-if="tasks.length !== 0">
      <h1>Generated Tasks</h1>
      <div v-for="task in tasks">
        <div class="row">
          <div v-if="task.images.length === 0" class="mt-5 mb-5 text-md-center">
            <div class="spinner-grow text-success" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          <div v-for="imageURL in task.images" class="col-4 mb-4 d-inline" @click="downloadFile(imageURL)">
            <img class="w-100" :src="imageURL" alt="AI image">
          </div>
        </div>
        <div class="row mb-4 mt-1">
          <button class="btn btn-success" type="button" data-bs-toggle="collapse"
                  :data-bs-target="`#collapse_${task.task_id}`"
                  aria-expanded="false" :aria-controls="`#collapse_${task.task_id}`">
            <i class="bi bi-braces"></i>
          </button>
          <div class="collapse mt-4 " :id="`collapse_${task.task_id}`">
            <p class="mb-1">ID:
              <span @click="copyText(task.task_id)" title="Copy task ID">{{ task.task_id }}</span>
              <button class="btn btn-sm link-primary" title="Copy text" @click="copyText(task.text)">
                <i class="bi bi-clipboard2"></i>
              </button>
              <button class="btn btn-sm link-danger" @click="deleteTask(task.task_id)" title="Delete">
                <i class="bi bi-trash"></i>
              </button>
            </p>
            <div class="card card-body">
              {{ task.text }}
            </div>
            <div class="mt-2 mb-2">
              <ul>
                <li>Number of images: {{ task.num_of_generation }}</li>
                <li>Scale: {{ task.guidance_scale }}</li>
              </ul>
            </div>
            <div class="text-sm mb-0 mt-2 d-flex flex-row align-items-md-center">
              <span>
                Created at {{ task.created_date }}
              </span>
            </div>
          </div>
        </div>
        <div class="mb-4 border-bottom"></div>
      </div>
    </template>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>

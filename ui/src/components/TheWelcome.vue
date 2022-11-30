<script setup>
import WelcomeItem from './WelcomeItem.vue';</script>

<script>
export default {
  data() {
    return {
    }
  },
  computed: {
    originText: {
      get() {
        return this.$store.state.originText;
      },
      set(val) {
        this.$store.state.originText = val;
      }
    },
    translatedResult() {
      return this.$store.state.translatedResult;
    },
    settings() {
      return this.$store.state.settings;
    },
    images() {
      return this.$store.state.images;
    },
    taskID() {
      return this.$store.state.taskID;
    },
    taskSyncing() {
      return this.$store.state.syncTaskID != null;
    },
    submittable() {
      return this.$store.state.submittable;
    },
  },
  mounted() {
  },
  methods: {
    translate() {
      this.$store.dispatch("translate");
    },
    generate() {
      this.$store.dispatch("generate");
    },
    downloadFile(url) {
      this.$store.dispatch("downloadFile", {url: url});
    }
  }
}
</script>

<template>
  <WelcomeItem>
    <template #icon>
      <i class="bi bi-braces"></i>
    </template>
    <template #heading>Request Text</template>

    <form>
      <div class="form-group">
        <textarea class="form-control" rows="3"
                  v-model="originText"
                  @change="translate"></textarea>
      </div>
    </form>
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <i class="bi bi-translate"></i>
    </template>
    <template #heading>Translated Text</template>

    <p>
      {{ translatedResult.destText }}
    </p>
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <i class="bi bi-sliders2"></i>
    </template>
    <template #heading>Settings</template>

    <div class="mb-3">
      <label for="guidance-scale" class="form-label">Scale: {{ settings.guidanceScale }}</label>
      <input type="range" class="form-range"
             id="guidance-scale"
             placeholder="8.5"
             aria-label="Guidance Scale"
             aria-describedby="guidance-scale"
             min="1"
             max="20"
             step="0.1"
             v-model="settings.guidanceScale">
    </div>
    <div class="mb-3">
      <label for="num-of-generation" class="form-label">Count: {{ settings.numOfGeneration }}</label>
      <input type="range" class="form-range"
             id="num-of-generation"
             placeholder="The number of generation"
             aria-label="The number of generation"
             aria-describedby="num-of-generation"
             min="1"
             max="12"
             step="1"
             v-model="settings.numOfGeneration">
    </div>
    <div class="mb-3 d-grid">
      <button class="btn btn-success" @click="generate"
              :disabled="taskSyncing || !submittable">
        <i class="bi bi-play-fill"></i> Generate
      </button>
    </div>
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <i class="bi bi-images"></i>
    </template>
    <template #heading>Generated Images</template>

    <div class="row">
      <div v-for="imageURL in images" class="col-4 mb-4" @click="downloadFile(imageURL)">
        <img class="w-100" :src="imageURL" alt="AI image">
      </div>
      <div v-if="!taskSyncing && images.length === 0" class="md-4">
        You can generate your images using what you are thinking.
      </div>
      <div v-if="taskSyncing" class="mt-4 md-4 d-block text-center">
        <div class="spinner-grow text-success" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </WelcomeItem>
</template>

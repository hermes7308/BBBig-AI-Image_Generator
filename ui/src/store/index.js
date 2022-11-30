import {createStore} from 'vuex'
import api from "../api"

const store = createStore({
    // data
    state: {
        originText: "",
        translatedResult: {
            originLang: "en",
            originText: "",
            destLang: "en",
            destText: ""
        },
        settings: {
            guidanceScale: 8.5,
            numOfGeneration: 3
        },
        images: [],
        queueStatus: {
            "numOfQueue": 0,
            "queue": null
        },
        taskID: null,
        tasks: [],
        queue: null,
        submittable: true
    },
    // Computed data
    getters: {},
    // Change data
    mutations: {},
    // Mutation + Async
    actions: {
        translate(store) {
            store.state.submittable = false;
            api.post("/translate",
                {
                    "requestText": store.state.originText,
                })
                .then((response) => {
                    store.state.translatedResult = response.data;
                    store.state.submittable = true;
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        generate(store) {
            if (store.state.translatedResult.destText.length === 0) {
                alert("Please input text to generate images");
                return;
            }
            api.post("/generate",
                {
                    "requestText": store.state.translatedResult.destText,
                    "guidanceScale": store.state.settings.guidanceScale,
                    "numOfGeneration": store.state.settings.numOfGeneration
                })
                .then((response) => {
                    store.state.taskID = response.data.taskID;
                    if (store.state.taskID == null) {
                        alert(`The task ID is null, error message: ${response.data.errorMessage}`)
                        return
                    }

                    store.state.images = [];
                    store.state.syncTaskID = setInterval(() => {
                        store.dispatch("syncTask");
                    }, 5000);
                    window.addEventListener("beforeunload", (e) => {
                        clearInterval(store.state.syncTaskID);
                    });
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        getQueue(store) {
            api.get("/queue")
                .then((response) => {
                    store.state.queue = response.data;
                })
                .catch((error) => {
                    console.log(error);
                })
        },
        syncTask(store) {
            api.get(`/task/${store.state.taskID}`)
                .then((response) => {
                    if (response.data.status === "Completed" && store.state.syncTaskID != null) {
                        clearInterval(store.state.syncTaskID);
                        store.state.images = response.data.images;
                        store.state.syncTaskID = null;
                    }
                })
                .catch((error) => {
                    console.log(error);
                })
        },
        getGeneratedTasks(store) {
            api.get("/generated_tasks")
                .then((response) => {
                    store.state.tasks = response.data;
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        deleteTask(store, {taskID: taskID}) {
            if (!confirm(`Do you want to delete a task (${taskID})`)) {
                return;
            }

            api.delete(`/task/${taskID}`)
                .then((response) => {
                    store.dispatch("getGeneratedTasks");
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        downloadFile(store, {url}) {
            let link = document.createElement("a");
            link.href = url;
            link.target = "_blank";
            link.click();
        },
        copyText(store, {text}) {
            navigator.clipboard.writeText(text);
        }
    },
    modules: {}
});

export default store;
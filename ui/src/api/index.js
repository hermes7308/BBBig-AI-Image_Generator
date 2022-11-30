import axios from "axios";

const protocol = window.location.protocol;
const hostname = window.location.hostname;
const port = "5000";
const baseURL = `${protocol}//${hostname}:${port}`;

const instance = axios.create({
    baseURL: baseURL
})

export default instance;
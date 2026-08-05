import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/v1/",
  headers: {
    "Content-Type": "application/json",
  },
});

export const fetchTasks = async () => {
  const response = await api.get("tasks/");
  const backendTasks = Array.isArray(response.data)
    ? response.data
    : response.data.results || [];
  return backendTasks.map((task) => ({
    id: task.id,
    title: task.title,
    description: task.content || task.description || "",
    completed: Boolean(task.done),
    created_at: task.created_at,
  }));
};

export const createTask = async (payload) => {
  const response = await api.post("tasks/", payload);
  const task = response.data;
  return {
    id: task.id,
    title: task.title,
    description: task.content || task.description || "",
    completed: Boolean(task.done),
    created_at: task.created_at,
  };
};

export const updateTask = async (id, payload) => {
  const response = await api.patch(`tasks/${id}/`, payload);
  const task = response.data;
  return {
    id: task.id,
    title: task.title,
    description: task.content || task.description || "",
    completed: Boolean(task.done),
    created_at: task.created_at,
  };
};

export const deleteTask = async (id) => {
  await api.delete(`tasks/${id}/`);
};

export const generateTaskReport = async () => {
  const response = await api.post("tasks/report/", {
    format: "summary",
    include_completed: true,
    language: "es",
  });
  return response.data;
};

export default api;

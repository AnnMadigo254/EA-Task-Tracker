// import axios from 'axios'

// // Create axios instance
// const api = axios.create({
//   baseURL: 'http://127.0.0.1:8000/api',
//   headers: {
//     'Content-Type': 'application/json',
//   },
// })

// // Request interceptor - add JWT token
// api.interceptors.request.use(
//   (config) => {
//     const token = localStorage.getItem('access_token')
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`
//     }
//     return config
//   },
//   (error) => {
//     return Promise.reject(error)
//   }
// )

// // Response interceptor - handle token refresh
// api.interceptors.response.use(
//   (response) => response,
//   async (error) => {
//     const originalRequest = error.config

//     // If 401 and not already retried
//     if (error.response?.status === 401 && !originalRequest._retry) {
//       originalRequest._retry = true

//       try {
//         const refreshToken = localStorage.getItem('refresh_token')
//         const response = await axios.post('http://127.0.0.1:8000/api/auth/refresh/', {
//           refresh: refreshToken,
//         })

//         const { access } = response.data
//         localStorage.setItem('access_token', access)

//         // Retry original request with new token
//         originalRequest.headers.Authorization = `Bearer ${access}`
//         return axios(originalRequest)
//       } catch (refreshError) {
//         // Refresh failed - logout
//         localStorage.removeItem('access_token')
//         localStorage.removeItem('refresh_token')
//         return Promise.reject(refreshError)
//       }
//     }

//     return Promise.reject(error)
//   }
// )

// // API Methods
// export default {
//   // ========== Authentication ==========
//   async login(username, password) {
//     const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
//       username,
//       password,
//     })
//     const { access, refresh } = response.data
//     localStorage.setItem('access_token', access)
//     localStorage.setItem('refresh_token', refresh)
//     return response.data
//   },

//   logout() {
//     localStorage.removeItem('access_token')
//     localStorage.removeItem('refresh_token')
//   },

//   isAuthenticated() {
//     return !!localStorage.getItem('access_token')
//   },

//   // ========== Users ==========
//   getUsers() {
//     return api.get('/users/')
//   },

//   getCurrentUser() {
//     return api.get('/users/me/')
//   },

//   getArchitects() {
//     return api.get('/users/architects/')
//   },

//   // ========== Boards ==========
//   getBoards() {
//     return api.get('/boards/')
//   },

//   getBoard(id) {
//     return api.get(`/boards/${id}/`)
//   },

//   createBoard(data) {
//     return api.post('/boards/', data)
//   },

//   updateBoard(id, data) {
//     return api.put(`/boards/${id}/`, data)
//   },

//   deleteBoard(id) {
//     return api.delete(`/boards/${id}/`)
//   },

//   getBoardStatistics(id) {
//     return api.get(`/boards/${id}/statistics/`)
//   },

//   // ========== Columns ==========
//   getColumns(boardId) {
//     return api.get('/columns/', { params: { board: boardId } })
//   },

//   // ========== Tasks ==========
//   getTasks(filters = {}) {
//     return api.get('/tasks/', { params: filters })
//   },

//   getTask(id) {
//     return api.get(`/tasks/${id}/`)
//   },

//   createTask(data) {
//     return api.post('/tasks/', data)
//   },

//   updateTask(id, data) {
//     return api.put(`/tasks/${id}/`, data)
//   },

//   patchTask(id, data) {
//     return api.patch(`/tasks/${id}/`, data)
//   },

//   deleteTask(id) {
//     return api.delete(`/tasks/${id}/`)
//   },

//   moveTask(id, columnId) {
//     return api.post(`/tasks/${id}/move/`, { column_id: columnId })
//   },

//   // ========== Comments ==========
//   getComments(taskId) {
//     return api.get('/comments/', { params: { task: taskId } })
//   },

//   createComment(data) {
//     return api.post('/comments/', data)
//   },

//   deleteComment(id) {
//     return api.delete(`/comments/${id}/`)
//   },
// }



// src/services/api.js
import axios from 'axios';

// Create axios instance with credentials (for session cookies)
const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  withCredentials: true, // ← Critical: sends sessionid cookie
  headers: {
    'Content-Type': 'application/json',
  },
});

// Optional: expose a lightweight auth check
api.isAuthenticated = async () => {
  try {
    // Use a simple endpoint that requires auth
    await api.get('/boards/');
    return true;
  } catch {
    return false;
  }
};

// API Methods
export default {
  // ========== Boards ==========
  getBoards() {
    return api.get('/boards/');
  },

  getBoard(id) {
    return api.get(`/boards/${id}/`);
  },

  createBoard(data) {
    return api.post('/boards/', data);
  },

  updateBoard(id, data) {
    return api.put(`/boards/${id}/`, data);
  },

  deleteBoard(id) {
    return api.delete(`/boards/${id}/`);
  },

  // ========== Columns ==========
  getColumns(boardId) {
    return api.get('/columns/', { params: { board: boardId } });
  },

  // ========== Tasks ==========
  getTasks(filters = {}) {
    return api.get('/tasks/', { params: filters });
  },

  getTask(id) {
    return api.get(`/tasks/${id}/`);
  },

  createTask(data) {
    return api.post('/tasks/', data);
  },

  updateTask(id, data) {
    return api.put(`/tasks/${id}/`, data);
  },

  patchTask(id, data) {
    return api.patch(`/tasks/${id}/`, data);
  },

  deleteTask(id) {
    return api.delete(`/tasks/${id}/`);
  },

  // ✅ No moveTask needed — use patchTask({ column: id }) instead
  // But if you keep it for convenience, just use PATCH:
  moveTask(id, columnId) {
    return api.patch(`/tasks/${id}/`, { column: columnId });
  },

  // ========== Comments ==========
  getComments(taskId) {
    return api.get('/comments/', { params: { task: taskId } });
  },

  createComment(data) {
    return api.post('/comments/', data);
  },

  deleteComment(id) {
    return api.delete(`/comments/${id}/`);
  },

  // ========== Optional: Auth Check ==========
  isAuthenticated: api.isAuthenticated,
};
// // src/services/api.js
// import axios from 'axios';

// // Create axios instance - NO AUTH REQUIRED
// const api = axios.create({
//   baseURL: 'http://127.0.0.1:8000/api/',
//   withCredentials: false, // ← No credentials needed
//   headers: {
//     'Content-Type': 'application/json',
//   },
// });

// // API Methods
// export default {
//   // ========== Boards ==========
//   getBoards() {
//     return api.get('/boards/');
//   },

//   getBoard(id) {
//     return api.get(`/boards/${id}/`);
//   },

//   createBoard(data) {
//     return api.post('/boards/', data);
//   },

//   updateBoard(id, data) {
//     return api.put(`/boards/${id}/`, data);
//   },

//   deleteBoard(id) {
//     return api.delete(`/boards/${id}/`);
//   },

//   getBoardStatistics(id) {
//     return api.get(`/boards/${id}/statistics/`);
//   },

//   // ========== Columns ==========
//   getColumns(boardId) {
//     return api.get('/columns/', { params: { board: boardId } });
//   },

//   createColumn(data) {
//     return api.post('/columns/', data);
//   },

//   updateColumn(id, data) {
//     return api.put(`/columns/${id}/`, data);
//   },

//   deleteColumn(id) {
//     return api.delete(`/columns/${id}/`);
//   },

//   // ========== Tasks ==========
//   getTasks(filters = {}) {
//     return api.get('/tasks/', { params: filters });
//   },

//   getTask(id) {
//     return api.get(`/tasks/${id}/`);
//   },

//   createTask(data) {
//     return api.post('/tasks/', data);
//   },

//   updateTask(id, data) {
//     return api.put(`/tasks/${id}/`, data);
//   },

//   patchTask(id, data) {
//     return api.patch(`/tasks/${id}/`, data);
//   },

//   deleteTask(id) {
//     return api.delete(`/tasks/${id}/`);
//   },

//   moveTask(id, columnId) {
//     return api.post(`/tasks/${id}/move/`, { column_id: columnId });
//   },

//   completeTask(id) {
//     return api.post(`/tasks/${id}/complete/`);
//   },

//   searchTasks(query, filters = {}) {
//     return api.post('/tasks/search/', { query, ...filters });
//   },

//   // ========== Comments ==========
//   getComments(taskId) {
//     return api.get('/comments/', { params: { task: taskId } });
//   },

//   createComment(data) {
//     return api.post('/comments/', data);
//   },

//   updateComment(id, data) {
//     return api.put(`/comments/${id}/`, data);
//   },

//   deleteComment(id) {
//     return api.delete(`/comments/${id}/`);
//   },

//   // ========== Attachments ==========
//   getAttachments(taskId) {
//     return api.get('/attachments/', { params: { task: taskId } });
//   },

//   uploadAttachment(taskId, file) {
//     const formData = new FormData();
//     formData.append('task', taskId);
//     formData.append('file', file);

//     return api.post('/attachments/', formData, {
//       headers: {
//         'Content-Type': 'multipart/form-data',
//       },
//     });
//   },

//   deleteAttachment(id) {
//     return api.delete(`/attachments/${id}/`);
//   },

//   // ========== Notifications ==========
//   getNotifications() {
//     return api.get('/notifications/');
//   },

//   markNotificationAsRead(id) {
//     return api.post(`/notifications/${id}/mark_read/`);
//   },

//   markAllNotificationsAsRead() {
//     return api.post('/notifications/mark_all_read/');
//   },

//   getUnreadCount() {
//     return api.get('/notifications/unread_count/');
//   },
// };




import axios from 'axios';

// Use relative URL for Docker (nginx will proxy to backend)
const api = axios.create({
  baseURL: '/api/',  // Changed from http://127.0.0.1:8000/api/
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Keep all your existing methods
export default {
  getBoards() {
    return api.get('/boards/');
  },
  
  getBoard(id) {
    return api.get(`/boards/${id}/`);
  },
  
  getColumns(boardId) {
    return api.get('/columns/', { params: { board: boardId } });
  },
  
  getTasks(filters = {}) {
    return api.get('/tasks/', { params: filters });
  },
  
  createTask(data) {
    return api.post('/tasks/', data);
  },
  
  patchTask(id, data) {
    return api.patch(`/tasks/${id}/`, data);
  },
  
  deleteTask(id) {
    return api.delete(`/tasks/${id}/`);
  },
  
  moveTask(id, columnId) {
    return api.post(`/tasks/${id}/move/`, { column_id: columnId });
  },
};
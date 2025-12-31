// import { defineStore } from "pinia";

// export const useBoardsStore = defineStore({
//   id: "boards",
//   state: () => ({
//     boards: [],
//     selectedBoard: 0,
//     selectedColumn: 0,
//     selectedTask: 0,
//   }),
//   getters: {
//     getColumns: (state) => state.boards[state.selectedBoard]?.columns,
//     getCurrentBoard: (state) => state.boards[state.selectedBoard],
//     getCurrentColumn: (state) =>
//       state.boards[state.selectedBoard]?.columns[state.selectedColumn],
//     getTask: (state) =>
//       state.boards[state.selectedBoard]?.columns[state.selectedColumn]?.tasks[
//         state.selectedTask
//       ],
//     getColumnsNames: (state) =>
//       state.boards[state.selectedBoard]?.columns.map((c) => c.name),
//   },
//   actions: {
//     changeTaskColumn(index) {
//       if (!(index === this.selectedColumn)) {
//         this.getCurrentBoard?.columns[index]?.tasks.push(this.getTask);
//         this.getCurrentColumn?.tasks.splice(this.selectedTask, 1);
//         this.selectedColumn = index;
//         this.selectedTask = this.getCurrentColumn?.tasks.length - 1;
//       }
//     },
//     saveTaskChanges({ task, column }) {
//       this.getCurrentColumn.tasks[this.selectedTask] = task;
//       if (this.selectedColumn !== column) {
//         this.changeTaskColumn(column);
//       }
//     },
//   },
// });

import { defineStore } from "pinia";
import api from '@/services/api';

export const useBoardsStore = defineStore({
  id: "boards",
  state: () => ({
    boards: [],
    selectedBoard: 0,
    selectedColumn: 0,
    selectedTask: 0,
    loading: false,
    error: null,
  }),
  getters: {
    getColumns: (state) => state.boards[state.selectedBoard]?.columns,
    getCurrentBoard: (state) => state.boards[state.selectedBoard],
    getCurrentColumn: (state) =>
      state.boards[state.selectedBoard]?.columns[state.selectedColumn],
    getTask: (state) =>
      state.boards[state.selectedBoard]?.columns[state.selectedColumn]?.tasks[
        state.selectedTask
      ],
    getColumnsNames: (state) =>
      state.boards[state.selectedBoard]?.columns.map((c) => c.name),
  },
  actions: {
    // ========== API Actions ==========

    async fetchBoards() {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.getBoards();
        const boardsData = response.data.results || response.data;

        this.boards = await Promise.all(
          boardsData.map(async (board) => {
            try {
              // Fetch columns for this board
              const columnsResponse = await api.getColumns(board.id);
              const columns = columnsResponse.data.results || columnsResponse.data;

              // Fetch all tasks for this board
              const tasksResponse = await api.getTasks({ board: board.id });
              const tasks = tasksResponse.data.results || tasksResponse.data;

              // Organize tasks under each column
              const columnsWithTasks = columns
                .sort((a, b) => a.position - b.position)
                .map(column => ({
                  id: column.id,
                  name: column.name,
                  color: column.color,
                  tasks: tasks
                    .filter(task => task.column === column.id)
                    .sort((a, b) => a.position - b.position)
                    .map(task => ({
                      // Core fields
                      id: task.id,
                      title: task.title,
                      description: task.description,
                      status: task.status,
                      priority: task.priority,
                      position: task.position,
                      // EA-specific fields (snake_case → camelCase)
                      projectName: task.project_name || '',
                      taskName: task.task_name || '',
                      taskType: task.task_type || 'Solution Design',
                      designStatus: task.design_status || '',
                      devStatus: task.dev_status || '',
                      sitStatus: task.sit_status || '',
                      progressNotes: task.progress_notes || '',
                      dependencies: task.dependencies || '',
                      comments: task.comments || '',
                      // Assignment fields
                      bapm: task.bapm || '',
                      stakeholder: task.stakeholder || '',
                      // Dates
                      startDate: task.start_date,
                      dueDate: task.due_date,
                      completedDate: task.completed_date,
                      // Owner
                      owner: task.owner,
                      ownerName: task.owner_name || '',
                      // Metadata
                      commentsCount: task.comments_count || 0,
                      attachmentsCount: task.attachments_count || 0,
                      historyCount: task.history_count || 0,
                    }))
                }));

              return {
                id: board.id,
                // Extract name from owner instead of board name
                name: board.owner_name || board.name.replace("'s Board", ""), // ← Cleaner name
                owner: board.owner,
                ownerName: board.owner_name || '',
                description: board.description || '',
                columns: columnsWithTasks,
              };
            } catch (err) {
              console.error(`Error loading board ${board.name}:`, err);
              return null;
            }
          })
        );

        // Remove any failed loads
        this.boards = this.boards.filter(board => board !== null);

        // Reset selection if out of bounds
        if (this.selectedBoard >= this.boards.length) {
          this.selectedBoard = Math.max(0, this.boards.length - 1);
        }

      } catch (error) {
        this.error = error.response?.data?.detail || error.message || 'Failed to load boards';
        console.error('Error fetching boards:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async addTask(columnIndex, taskData) {
      try {
        const board = this.getCurrentBoard;
        const column = board?.columns[columnIndex];
        if (!column) throw new Error('Column not found');

        const newTask = {
          column: column.id,
          title: taskData.title,
          description: taskData.description || '',
          project_name: taskData.projectName || '',
          task_name: taskData.taskName || '',
          task_type: taskData.taskType || 'Solution Design',
          priority: taskData.priority || 'Medium',
          status: 'To Do',
          position: column.tasks.length,
          // EA fields
          design_status: taskData.designStatus || '',
          dev_status: taskData.devStatus || '',
          sit_status: taskData.sitStatus || '',
          progress_notes: taskData.progressNotes || '',
          dependencies: taskData.dependencies || '',
          bapm: taskData.bapm || '',
          stakeholder: taskData.stakeholder || '',
        };

        await api.createTask(newTask);
        await this.fetchBoards();

      } catch (error) {
        this.error = error.response?.data?.detail || error.message;
        throw error;
      }
    },

    async updateTaskApi(taskId, updates) {
      try {
        // Map camelCase back to snake_case for API
        const apiUpdates = {};
        for (const [key, value] of Object.entries(updates)) {
          const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
          apiUpdates[snakeKey] = value;
        }
        await api.patchTask(taskId, apiUpdates);
        await this.fetchBoards();
      } catch (error) {
        this.error = error.response?.data?.detail || error.message;
        throw error;
      }
    },

    async deleteTaskApi(taskId) {
      try {
        await api.deleteTask(taskId);
        await this.fetchBoards();
      } catch (error) {
        this.error = error.response?.data?.detail || error.message;
        throw error;
      }
    },

    async moveTaskApi(taskId, newColumnId) {
      try {
        await api.patchTask(taskId, { column: newColumnId });
        await this.fetchBoards();
      } catch (error) {
        this.error = error.response?.data?.detail || error.message;
        throw error;
      }
    },

    // ========== Local UI Actions ==========

    async changeTaskColumn(index) {
      if (index === this.selectedColumn) return;

      const task = this.getTask;
      if (!task?.id) {
        const board = this.getCurrentBoard;
        board?.columns[index]?.tasks.push(task);
        this.getCurrentColumn?.tasks.splice(this.selectedTask, 1);
        this.selectedColumn = index;
        this.selectedTask = this.getCurrentColumn?.tasks.length - 1;
        return;
      }

      try {
        const newColumn = this.getCurrentBoard.columns[index];
        await this.moveTaskApi(task.id, newColumn.id);
      } catch (error) {
        console.error('Move task failed:', error);
      }
    },

    async saveTaskChanges({ task, column }) {
      const currentTask = this.getTask;
      if (!currentTask?.id) return;

      try {
        await this.updateTaskApi(currentTask.id, task);

        if (this.selectedColumn !== column) {
          const newColumn = this.getCurrentBoard.columns[column];
          await this.moveTaskApi(currentTask.id, newColumn.id);
        }
      } catch (error) {
        console.error('Save task failed:', error);
      }
    },

    // ========== Selection Helpers ==========

    setSelectedBoard(index) {
      this.selectedBoard = index;
      this.selectedColumn = 0;
      this.selectedTask = 0;
    },

    setSelectedColumn(index) {
      this.selectedColumn = index;
      this.selectedTask = 0;
    },

    setSelectedTask(index) {
      this.selectedTask = index;
    },
  },
});
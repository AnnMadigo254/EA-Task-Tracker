<template>
  <div class="bg-white dark:bg-dark-grey rounded-lg p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
    <!-- Header -->
    <div class="flex justify-between items-start mb-6">
      <h2 class="text-xl font-bold text-black dark:text-white">
        {{ isEditing ? 'Edit Task' : task.title }}
      </h2>
      <button @click="closeView" class="text-medium-grey hover:text-red text-2xl leading-none">
        ✕
      </button>
    </div>

    <!-- Edit/Save Toggle -->
    <div class="flex justify-end mb-4">
      <button 
        @click="toggleEditMode"
        class="text-sm font-bold px-4 py-2 rounded-full transition-colors"
        :class="isEditing ? 'bg-main-purple text-white hover:bg-main-purple-hover' : 'bg-main-purple/10 text-main-purple hover:bg-main-purple/20'"
      >
        {{ isEditing ? '✓ Save Changes' : '✏️ Edit Task' }}
      </button>
    </div>

    <!-- Title (only in edit mode) -->
    <div class="mb-4" v-if="isEditing">
      <label class="text-xs font-bold text-medium-grey mb-2 block">Title</label>
      <input 
        v-model="editableTask.title"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
      />
    </div>

    <!-- Project Name -->
    <div class="mb-4">
      <label class="text-xs font-bold text-medium-grey mb-2 block">Project Name</label>
      <input 
        v-if="isEditing"
        v-model="editableTask.projectName"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
      />
      <p v-else class="text-sm font-bold text-main-purple">
        {{ task.projectName || 'N/A' }}
      </p>
    </div>

    <!-- Description -->
    <div class="mb-4">
      <label class="text-xs font-bold text-medium-grey mb-2 block">Description</label>
      <textarea 
        v-if="isEditing"
        v-model="editableTask.description"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white resize-none focus:outline-none focus:border-main-purple"
        rows="3"
      ></textarea>
      <p v-else class="text-sm text-medium-grey whitespace-pre-wrap">
        {{ task.description || 'No description' }}
      </p>
    </div>

    <!-- Task Name -->
    <div class="mb-4">
      <label class="text-xs font-bold text-medium-grey mb-2 block">Task Name</label>
      <input 
        v-if="isEditing"
        v-model="editableTask.taskName"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
      />
      <p v-else class="text-sm text-medium-grey">
        {{ task.taskName || 'N/A' }}
      </p>
    </div>

    <!-- Quarter -->
    <div class="mb-4">
      <label class="text-xs font-bold text-medium-grey mb-2 block">Quarter</label>
      <select 
        v-if="isEditing"
        v-model="editableTask.quarter"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
      >
        <option value="Q3_2025">Q3 2025</option>
        <option value="Q4_2025">Q4 2025</option>
        <option value="Q1_2026">Q1 2026</option>
        <option value="Q2_2026">Q2 2026</option>
        <option value="Q3_2026">Q3 2026</option>
        <option value="Q4_2026">Q4 2026</option>
        <option value="Q1_2027">Q1 2027</option>
        <option value="Q2_2027">Q2 2027</option>
      </select>
      <p v-else class="text-sm font-bold text-main-purple">
        {{ formatQuarter(task.quarter) }}
      </p>
    </div>

    <!-- Status Row (Design/Dev/SIT) -->
    <div class="grid grid-cols-3 gap-2 mb-4">
      <div>
        <label class="text-xs font-bold text-medium-grey mb-1 block">Design</label>
        <select 
          v-if="isEditing"
          v-model="editableTask.designStatus"
          class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-2 py-1 text-xs dark:text-white focus:outline-none focus:border-main-purple"
        >
          <option value="">Not Started</option>
          <option value="In Progress">In Progress</option>
          <option value="Completed">Completed</option>
          <option value="On Hold">On Hold</option>
        </select>
        <span v-else class="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800 inline-block">
          {{ task.designStatus || 'Not Started' }}
        </span>
      </div>

      <div>
        <label class="text-xs font-bold text-medium-grey mb-1 block">Dev</label>
        <select 
          v-if="isEditing"
          v-model="editableTask.devStatus"
          class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-2 py-1 text-xs dark:text-white focus:outline-none focus:border-main-purple"
        >
          <option value="">Not Started</option>
          <option value="In Progress">In Progress</option>
          <option value="Completed">Completed</option>
          <option value="Pending">Pending</option>
        </select>
        <span v-else class="px-2 py-1 text-xs rounded bg-green-100 text-green-800 inline-block">
          {{ task.devStatus || 'Not Started' }}
        </span>
      </div>

      <div>
        <label class="text-xs font-bold text-medium-grey mb-1 block">SIT</label>
        <select 
          v-if="isEditing"
          v-model="editableTask.sitStatus"
          class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-2 py-1 text-xs dark:text-white focus:outline-none focus:border-main-purple"
        >
          <option value="">Not Started</option>
          <option value="In Progress">In Progress</option>
          <option value="Completed">Completed</option>
        </select>
        <span v-else class="px-2 py-1 text-xs rounded bg-purple-100 text-purple-800 inline-block">
          {{ task.sitStatus || 'Not Started' }}
        </span>
      </div>
    </div>

    <!-- Priority & Status -->
    <div class="grid grid-cols-2 gap-4 mb-4">
      <div>
        <label class="text-xs font-bold text-medium-grey mb-2 block">Priority</label>
        <select 
          v-if="isEditing"
          v-model="editableTask.priority"
          class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
        >
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
        <span v-else class="px-3 py-1 text-xs font-bold rounded-full inline-block" :class="getPriorityClass(task.priority)">
          {{ task.priority }}
        </span>
      </div>

      <div>
        <label class="text-xs font-bold text-medium-grey mb-2 block">Column Status</label>
        <select 
          v-if="isEditing"
          v-model="editableTask.status"
          class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
        >
          <option v-for="column in boardsStore.getColumnsNames" :key="column" :value="column">
            {{ column }}
          </option>
        </select>
        <p v-else class="text-sm font-bold text-main-purple">
          {{ task.status }}
        </p>
      </div>
    </div>

    <!-- BA/PM -->
    <div class="mb-4">
      <label class="text-xs font-bold text-medium-grey mb-2 block">BA/PM</label>
      <input 
        v-if="isEditing"
        v-model="editableTask.bapm"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
      />
      <p v-else class="text-sm text-medium-grey">
        {{ task.bapm || 'N/A' }}
      </p>
    </div>

    <!-- Progress Notes -->
    <div class="mb-4">
      <label class="text-xs font-bold text-medium-grey mb-2 block">Progress Notes</label>
      <textarea 
        v-if="isEditing"
        v-model="editableTask.progressNotes"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white resize-none focus:outline-none focus:border-main-purple"
        rows="3"
      ></textarea>
      <p v-else class="text-sm text-medium-grey whitespace-pre-wrap">
        {{ task.progressNotes || 'No progress notes' }}
      </p>
    </div>

    <!-- Dependencies -->
    <div class="mb-4">
      <label class="text-xs font-bold text-medium-grey mb-2 block">Dependencies</label>
      <input 
        v-if="isEditing"
        v-model="editableTask.dependencies"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
      />
      <p v-else class="text-sm text-medium-grey">
        {{ task.dependencies || 'None' }}
      </p>
    </div>

    <!-- Comments -->
    <div class="mb-6">
      <label class="text-xs font-bold text-medium-grey mb-2 block">Comments</label>
      <textarea 
        v-if="isEditing"
        v-model="editableTask.comments"
        class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white resize-none focus:outline-none focus:border-main-purple"
        rows="2"
      ></textarea>
      <p v-else class="text-sm text-medium-grey whitespace-pre-wrap">
        {{ task.comments || 'No comments' }}
      </p>
    </div>

    <!-- Delete Button -->
    <button 
      v-if="!isEditing"
      @click="deleteTask"
      class="w-full bg-red hover:bg-red/80 text-white rounded-full py-2 text-sm font-bold transition-colors"
    >
      Delete Task
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useBoardsStore } from '@/stores/boards';
import { useManagerStore } from '@/stores/manager';

const boardsStore = useBoardsStore();
const managerStore = useManagerStore();

const isEditing = ref(false);
const editableTask = ref({});

const task = computed(() => boardsStore.getTask);

// Initialize editable task
const initEditableTask = () => {
  editableTask.value = { ...task.value };
};

initEditableTask();

const formatQuarter = (quarter) => {
  if (!quarter) return 'N/A';
  return quarter.replace('_', ' ');
};

const getPriorityClass = (priority) => {
  const classes = {
    'Critical': 'bg-red-100 text-red-800',
    'High': 'bg-orange-100 text-orange-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'Low': 'bg-gray-100 text-gray-800',
  };
  return classes[priority] || 'bg-gray-100 text-gray-800';
};

const toggleEditMode = async () => {
  if (isEditing.value) {
    // Save changes
    try {
      const columnIndex = boardsStore.getColumnsNames.indexOf(editableTask.value.status);
      await boardsStore.saveTaskChanges({
        task: editableTask.value,
        column: columnIndex
      });
      isEditing.value = false;
      closeView();
    } catch (error) {
      console.error('Failed to save task:', error);
      alert('Failed to save changes. Please try again.');
    }
  } else {
    isEditing.value = true;
  }
};

const deleteTask = () => {
  managerStore.delete = { visible: true, task: true };
};

const closeView = () => {
  managerStore.overlay = false;
  managerStore.taskView = false;
};
</script>
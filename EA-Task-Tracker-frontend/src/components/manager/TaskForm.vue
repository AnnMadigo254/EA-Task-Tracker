<template>
  <form @submit.prevent="onSubmit" class="bg-white dark:bg-dark-grey rounded-lg p-1">
    <div class="p-5 pr-3 flex flex-col gap-6 max-h-[90vh] overflow-y-scroll">
      <div class="flex justify-between items-center">
        <h4 class="text-black dark:text-white font-bold text-lg">
          {{ managerStore.taskForm.edit ? 'Edit Task' : 'Add New Task' }}
        </h4>
      </div>

      <!-- Title -->
      <BaseInput 
        ref="inputTitle" 
        v-model="form.task.title" 
        inputName="Title" 
        placeholder="e.g. CRB API Integration" 
      />

      <!-- Description -->
      <BaseTextarea 
        v-model="form.task.description" 
        inputName="Description"
        placeholder="Brief description of the task..." 
      />

      <!-- Project Name -->
      <BaseInput 
        v-model="form.task.projectName" 
        inputName="Project Name" 
        placeholder="e.g. Credit Bureau Integration" 
      />

      <!-- Task Name -->
      <BaseInput 
        v-model="form.task.taskName" 
        inputName="Task Name" 
        placeholder="e.g. Solution Design" 
      />

      <!-- Status Row (Design/Dev/SIT) -->
      <div class="grid grid-cols-3 gap-3">
        <div class="flex flex-col gap-2">
          <p class="text-medium-grey text-xs font-bold">Design Status</p>
          <select
            v-model="form.task.designStatus"
            class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
          >
            <option value="">Not Started</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="On Hold">On Hold</option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <p class="text-medium-grey text-xs font-bold">Dev Status</p>
          <select
            v-model="form.task.devStatus"
            class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
          >
            <option value="">Not Started</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Pending">Pending</option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <p class="text-medium-grey text-xs font-bold">SIT Status</p>
          <select
            v-model="form.task.sitStatus"
            class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
          >
            <option value="">Not Started</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
      </div>

      <!-- Priority -->
      <div class="flex flex-col gap-2">
        <p class="text-medium-grey text-xs font-bold">Priority</p>
        <select
          v-model="form.task.priority"
          class="w-full border border-lines-light dark:border-lines-dark bg-transparent rounded px-4 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
        >
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
      </div>

      <!-- BA/PM -->
      <BaseInput 
        v-model="form.task.bapm" 
        inputName="BA/PM" 
        placeholder="e.g. Marystella Obutsula" 
      />

      <!-- Progress Notes -->
      <BaseTextarea 
        v-model="form.task.progressNotes" 
        inputName="Progress Notes"
        placeholder="Latest progress updates..." 
      />

      <!-- Dependencies -->
      <BaseInput 
        v-model="form.task.dependencies" 
        inputName="Dependencies" 
        placeholder="e.g. Waiting for vendor approval" 
      />

      <!-- Comments -->
      <BaseTextarea 
        v-model="form.task.comments" 
        inputName="Comments"
        placeholder="Additional comments or notes..." 
      />

      <!-- Subtasks (Optional - Keep if you want) -->
      <div class="flex flex-col gap-3">
        <p class="text-medium-grey text-xs font-bold">Subtasks (Optional)</p>
        <div ref="errorSubtasks" class="flex items-center justify-between gap-4"
          v-for="(subtask, index) in form.task.subtasks" :key="index">
          <BaseInput 
            :ref="el => { inputs[index] = el }" 
            v-model="subtask.title"
            :placeholder="subtaskPlaceholders[index] ? subtaskPlaceholders[index] : 'Your subtask title...'" 
          />
          <IconCross @click="deleteSubtask(index)" class="cursor-pointer" />
        </div>
        <ButtonSecondaryLarge type="button" @click.stop="addSubtask">+ Add New Subtask</ButtonSecondaryLarge>
      </div>

      <!-- Status Column -->
      <div class="flex flex-col gap-2">
        <p class="text-medium-grey text-xs font-bold">Status</p>
        <BaseSelect @onClickOption="updateColumn" :value="columnName" />
      </div>

      <!-- Submit Button -->
      <ButtonPrimaryLarge type="submit">
        {{ managerStore.taskForm.edit ? 'Save Changes' : 'Create Task' }}
      </ButtonPrimaryLarge>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, onBeforeUpdate } from 'vue'
import { useBoardsStore } from '@/stores/boards.js';
import { useManagerStore } from '@/stores/manager.js';
import BaseSelect from '@/components/form/BaseSelect.vue';
import BaseInput from '@/components/form/BaseInput.vue';
import BaseTextarea from '../form/BaseTextarea.vue';
import IconCross from '../icons/IconCross.vue';
import ButtonPrimaryLarge from '../buttons/PrimaryLarge.vue';
import ButtonSecondaryLarge from '../buttons/SecondaryLarge.vue';
import { v4 as uuid } from 'uuid';

const boardsStore = useBoardsStore();
const managerStore = useManagerStore();
const columnName = ref('')

const inputTitle = ref(null)
const inputs = ref([])

const form = reactive({
  task: {
    title: '',
    description: '',
    projectName: '',
    taskName: '',
    designStatus: '',
    devStatus: '',
    sitStatus: '',
    priority: 'Medium',
    bapm: '',
    progressNotes: '',
    dependencies: '',
    comments: '',
    subtasks: [{ title: '', isCompleted: false }, { title: '', isCompleted: false }]
  },
  column: 0
})

const subtaskPlaceholders = {
  0: 'e.g. Review design document',
  1: 'e.g. Get stakeholder approval'
}

const deleteSubtask = (index) => {
  if (form.task.subtasks.length === 2) {
    form.task.subtasks[index].title = ''
    form.task.subtasks[index].isCompleted = false
  } else {
    form.task.subtasks.splice(index, 1)
  }
}

const addSubtask = () => {
  form.task.subtasks.push({ title: '', isCompleted: false })
}

const onSubmit = async () => {
  if (validate()) {
    try {
      if (managerStore.taskForm.edit) {
        await boardsStore.saveTaskChanges({ task: form.task, column: form.column })
      } else {
        // Add task via API
        await boardsStore.addTask(form.column, {
          ...form.task,
          id: uuid()
        })
      }
      managerStore.hideOverlay()
    } catch (error) {
      console.error('Error saving task:', error)
      alert('Failed to save task. Please try again.')
    }
  }
}

const validate = () => {
  let valid = true
  if (form.task.title.trim().length === 0) {
    valid = false
    inputTitle.value.error = true
  }
  inputs.value.forEach((e, index) => {
    if (form.task.subtasks[index]?.title.trim().length === 0) {
      // Subtasks are optional, so we just skip empty ones
      // valid = false
      // e.error = true
    }
  })
  return valid
}

const updateColumn = ({ index, name }) => {
  form.column = index
  columnName.value = name
}

// EDIT MODE
if (managerStore.taskForm.edit) {
  const task = boardsStore.getTask
  form.task = {
    title: task.title || '',
    description: task.description || '',
    projectName: task.projectName || '',
    taskName: task.taskName || '',
    designStatus: task.designStatus || '',
    devStatus: task.devStatus || '',
    sitStatus: task.sitStatus || '',
    priority: task.priority || 'Medium',
    bapm: task.bapm || '',
    progressNotes: task.progressNotes || '',
    dependencies: task.dependencies || '',
    comments: task.comments || '',
    subtasks: task.subtasks || [{ title: '', isCompleted: false }, { title: '', isCompleted: false }]
  }
  form.column = JSON.parse(JSON.stringify(boardsStore.selectedColumn))
  columnName.value = JSON.parse(JSON.stringify(boardsStore.getColumnsNames[boardsStore.selectedColumn]))
} else {
  columnName.value = JSON.parse(JSON.stringify(boardsStore.getColumnsNames[0]))
}

onBeforeUpdate(() => {
  inputs.value = []
})
</script>





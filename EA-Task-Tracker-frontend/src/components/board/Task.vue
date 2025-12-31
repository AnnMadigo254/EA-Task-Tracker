<!-- <template>
  <article class="group flex flex-col bg-white dark:bg-dark-grey p-4 rounded-lg cursor-pointer shadow-task max-w-[280px]">
    <h3 class="text-black dark:text-white font-bold select-none pointer-events-none"
      :class="managerStore.dragging ? '' : 'group-hover:text-main-purple'">
      {{ task.title }}
    </h3>
    <p class="text-xs text-medium-grey font-bold select-none pointer-events-none">{{ subtasksCompleted }} substasks</p>
  </article>
</template>

<script setup>
import { computed } from 'vue';
import { useManagerStore } from '../../stores/manager';
const managerStore = useManagerStore()
const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

const subtasksCompleted = computed(() => {
  const completed = props.task.subtasks.filter((sub) => sub.isCompleted).length;
  const total = props.task.subtasks.length;
  return `${completed} of ${total}`
})
</script> -->


<template>
  <article class="group flex flex-col bg-white dark:bg-dark-grey p-4 rounded-lg cursor-pointer shadow-task max-w-[280px]">
    <!-- Title -->
    <h3 class="text-black dark:text-white font-bold mb-2 line-clamp-2">
      {{ task.title }}
    </h3>

    <!-- Project & Task Type -->
    <div class="text-xs text-medium-grey mb-2">
      <span class="font-semibold">Project:</span> {{ task.projectName || '—' }}
    </div>
    <div class="text-xs text-medium-grey mb-2">
      <span class="font-semibold">Type:</span> {{ task.taskType || 'Solution Design' }}
    </div>

    <!-- Progress Status Badges -->
    <div class="flex flex-wrap gap-1 mb-2">
      <span v-if="task.designStatus" class="px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-800">
        Design: {{ task.designStatus }}
      </span>
      <span v-if="task.devStatus" class="px-2 py-0.5 text-xs rounded bg-green-100 text-green-800">
        Dev: {{ task.devStatus }}
      </span>
      <span v-if="task.sitStatus" class="px-2 py-0.5 text-xs rounded bg-purple-100 text-purple-800">
        SIT: {{ task.sitStatus }}
      </span>
    </div>

    <!-- Stakeholders -->
    <div v-if="task.stakeholder || task.bapm" class="text-xs text-medium-grey mb-2">
      <span v-if="task.stakeholder">
        <span class="font-semibold">Stakeholder:</span> {{ task.stakeholder }}
      </span>
      <span v-if="task.bapm" class="block">
        <span class="font-semibold">BA/PM:</span> {{ task.bapm }}
      </span>
    </div>

    <!-- Priority Badge -->
    <div class="mt-auto">
      <span 
        class="px-2 py-1 text-xs font-bold rounded-full"
        :class="getPriorityClass(task.priority)"
      >
        {{ task.priority }}
      </span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue';
import { useManagerStore } from '../../stores/manager';

const managerStore = useManagerStore();
const props = defineProps({
  task: { type: Object, required: true }
});

// Priority color mapping
const getPriorityClass = (priority) => {
  const classes = {
    'Critical': 'bg-red-100 text-red-800',
    'High': 'bg-orange-100 text-orange-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'Low': 'bg-gray-100 text-gray-800',
  };
  return classes[priority] || 'bg-gray-100 text-gray-800';
};
</script>
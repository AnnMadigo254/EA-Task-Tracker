<template>
  <header class="bg-white dark:bg-dark-grey top-0 left-0 w-full flex items-center sm:pr-4">
    <div class="hidden items-center sm:flex pl-6 h-20 border-r border-r-lines-light dark:border-r-lines-dark md:h-24"
      :class="managerStore.sidebar ? ['min-w-[256px]', 'lg:min-w-[300px]'] : ['min-w-[200px]']">
      <img class="hidden dark:block" src="@/assets/icons/logo-light.png" alt="logo">
      <img class="dark:hidden" src="@/assets/icons/logo-dark.png" alt="logo">
    </div>
    <div class="mx-auto max-w-sm w-11/12 flex items-center h-16 gap-4 sm:h-20">
      <div>
        <img class="sm:hidden" src="@/assets/icons/logo-mobile.svg" height="25" width="24" alt="logo">
      </div>
      <div @click="showMobileBar" class="flex items-center gap-2 group cursor-pointer sm:hidden">
        <h1 class="text-black dark:text-white font-bold text-lg cursor-pointer">
          {{ formatBoardName(boardsStore.getCurrentBoard?.name) }}
        </h1>
        <IconArrowDown v-if="!managerStore.sidebarMobile" />
        <IconArrowUp v-else />
      </div>
      <h1 class="text-black dark:text-white font-bold hidden text-2xl sm:block">
        {{ formatBoardName(boardsStore.getCurrentBoard?.name) }}
      </h1>
      <div v-if="boardsStore.boards.length" class="flex items-center gap-4 ml-auto">
        <AddButtonMobile />
        <PrimarySmall @click="addTask" class="hidden sm:block">+ Add New Task</PrimarySmall>
        <Dropdown target="Board" @onClickEdit="editTask" @onClickDelete="deleteTask" />
      </div>
    </div>
  </header>
</template>

<script setup>
import AddButtonMobile from '@/components/buttons/AddTaskMobile.vue'
import { useBoardsStore } from '@/stores/boards';
import { useManagerStore } from '@/stores/manager';
import Dropdown from '@/components/manager/Dropdown.vue';
import IconArrowDown from './icons/IconArrowDown.vue';
import IconArrowUp from './icons/IconArrowUp.vue';
import PrimarySmall from './buttons/PrimarySmall.vue';

const boardsStore = useBoardsStore()
const managerStore = useManagerStore()

const editTask = () => {
  managerStore.overlay = true
  managerStore.boardForm = { edit: true, visible: true }
}

const deleteTask = () => {
  managerStore.overlay = true
  managerStore.delete = { board: true, visible: true }
}

const addTask = () => {
  managerStore.overlay = true
  managerStore.taskForm = { visible: true, edit: false };
}

const showMobileBar = () => {
  managerStore.sidebarMobile = true;
  managerStore.overlay = true
}

// Format board names with proper capitalization and spacing
const formatBoardName = (name) => {
  if (!name) return '';
  
  // Map of username to proper display name
  const nameMap = {
    'abellwandili': 'Abell Wandili',
    "abell wandili's board": 'Abell Wandili',
    'amonsabul': 'Amon Sabul',
    "amon sabul's board": 'Amon Sabul',
    'annmadigo': 'Ann Madigo',
    "ann madigo's board": 'Ann Madigo',
    'danronoh': 'Dan Ronoh',
    "dan ronoh's board": 'Dan Ronoh',
    'davidbarmasai': 'David Barmasai',
    "david barmasai's board": 'David Barmasai',
    'duncansituma': 'Duncan Situma',
    "duncan situma's board": 'Duncan Situma',
    'everlynemosomi': 'Everlyne Mosomi',
    "everlyne mosomi's board": 'Everlyne Mosomi',
    "faithn.oling'a": "Faith N. Oling'a",
    "faith n. oling'a's board": "Faith N. Oling'a",
    'joramnjagi': 'Joram Njagi',
    "joram njagi's board": 'Joram Njagi',
    'kelvinmaxwellmurithi': 'Kelvin Maxwell Murithi',
    "kelvin maxwell murithi's board": 'Kelvin Maxwell Murithi',
    'michaelmalala': 'Michael Malala',
    "michael malala's board": 'Michael Malala',
    'samuelmburu': 'Samuel Mburu',
    "samuel mburu's board": 'Samuel Mburu',
    'simonthuku': 'Simon Thuku',
    "simon thuku's board": 'Simon Thuku'
  };
  
  // Convert to lowercase for matching
  const lowerName = name.toLowerCase();
  
  // Return mapped name or original if not found
  return nameMap[lowerName] || name;
}
</script>
<template>
  <header class="bg-white dark:bg-dark-grey top-0 left-0 w-full flex items-center">
    <!-- Logo Section -->
    <div class="hidden items-center sm:flex pl-6 h-20 border-r border-r-lines-light dark:border-r-lines-dark md:h-24"
      :class="managerStore.sidebar ? ['min-w-[256px]', 'lg:min-w-[300px]'] : ['min-w-[200px]']">
      <img class="hidden dark:block" src="@/assets/icons/logo-light.png" alt="logo">
      <img class="dark:hidden" src="@/assets/icons/logo-dark.png" alt="logo">
    </div>

    <!-- Main Header Content -->
    <div class="flex-1 flex items-center h-16 sm:h-20 px-4 gap-4">
      <!-- Left: Mobile Logo & Board Name -->
      <div class="flex items-center gap-4">
        <img class="sm:hidden" src="@/assets/icons/logo-mobile.svg" height="25" width="24" alt="logo">
        
        <!-- Mobile Board Selector -->
        <div @click="showMobileBar" class="flex items-center gap-2 cursor-pointer sm:hidden">
          <h1 class="text-black dark:text-white font-bold text-lg">
            {{ formatBoardName(boardsStore.getCurrentBoard?.name) }}
          </h1>
          <IconArrowDown v-if="!managerStore.sidebarMobile" />
          <IconArrowUp v-else />
        </div>
        
        <!-- Desktop Board Name -->
        <h1 class="text-black dark:text-white font-bold hidden text-xl sm:block">
          {{ formatBoardName(boardsStore.getCurrentBoard?.name) }}
        </h1>
      </div>

      <!-- Center: Search & Quarter Filter -->
      <div v-if="boardsStore.boards.length" class="flex items-center gap-3 flex-1 max-w-2xl mx-4">
        <!-- Search Bar -->
        <div class="relative flex-1 max-w-md hidden md:block">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            type="text"
            placeholder="Search tasks, projects, BA/PM..."
            class="w-full border border-lines-light dark:border-lines-dark bg-white dark:bg-dark-grey rounded-lg px-4 py-2 pl-10 text-sm dark:text-white focus:outline-none focus:border-main-purple"
          />
          <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-medium-grey" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>

        <!-- Quarter Selector -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <label class="text-xs font-bold text-medium-grey whitespace-nowrap hidden sm:inline">Quarter:</label>
          <select 
            v-model="selectedQuarter"
            @change="changeQuarter"
            class="border border-lines-light dark:border-lines-dark bg-white dark:bg-dark-grey rounded-lg px-3 py-2 text-sm dark:text-white focus:outline-none focus:border-main-purple"
          >
            <option value="">All</option>
            <option value="Q3_2025">Q3 2025</option>
            <option value="Q4_2025">Q4 2025</option>
            <option value="Q1_2026">Q1 2026</option>
            <option value="Q2_2026">Q2 2026</option>
            <option value="Q3_2026">Q3 2026</option>
            <option value="Q4_2026">Q4 2026</option>
            <option value="Q1_2027">Q1 2027</option>
          </select>
        </div>
      </div>

      <!-- Right: Action Buttons -->
      <div v-if="boardsStore.boards.length" class="flex items-center gap-3 ml-auto">
        <!-- Mobile Search Toggle -->
        <button 
          @click="toggleMobileSearch" 
          class="md:hidden p-2 text-medium-grey hover:text-main-purple"
          title="Search"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </button>

        <AddButtonMobile />
        <PrimarySmall @click="addTask" class="hidden sm:block">+ Add New Task</PrimarySmall>
        <Dropdown target="Board" @onClickEdit="editTask" @onClickDelete="deleteTask" />
      </div>
    </div>

    <!-- Mobile Search Bar (Toggleable) -->
    <div v-if="showMobileSearch" class="absolute top-16 left-0 right-0 bg-white dark:bg-dark-grey border-b border-lines-light dark:border-lines-dark p-4 md:hidden z-50">
      <div class="relative">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="Search tasks..."
          class="w-full border border-lines-light dark:border-lines-dark bg-white dark:bg-dark-grey rounded-lg px-4 py-2 pl-10 text-sm dark:text-white focus:outline-none focus:border-main-purple"
        />
        <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-medium-grey" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, watch } from 'vue';
import AddButtonMobile from '@/components/buttons/AddTaskMobile.vue'
import { useBoardsStore } from '@/stores/boards';
import { useManagerStore } from '@/stores/manager';
import Dropdown from '@/components/manager/Dropdown.vue';
import IconArrowDown from './icons/IconArrowDown.vue';
import IconArrowUp from './icons/IconArrowUp.vue';
import PrimarySmall from './buttons/PrimarySmall.vue';

const boardsStore = useBoardsStore()
const managerStore = useManagerStore()
const selectedQuarter = ref('Q1_2026')
const searchQuery = ref('')
const showMobileSearch = ref(false)
let searchTimeout = null

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

const changeQuarter = () => {
  boardsStore.setQuarter(selectedQuarter.value);
}

const toggleMobileSearch = () => {
  showMobileSearch.value = !showMobileSearch.value
  if (!showMobileSearch.value) {
    searchQuery.value = ''
    handleSearch()
  }
}

const handleSearch = () => {
  // Debounce search
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    filterTasks(searchQuery.value)
  }, 300)
}

const filterTasks = (query) => {
  if (!query || query.trim() === '') {
    // Reset filter - show all tasks
    boardsStore.boards.forEach(board => {
      board.columns.forEach(column => {
        column.tasks.forEach(task => {
          task.hidden = false
        })
      })
    })
    return
  }

  const searchLower = query.toLowerCase().trim()
  
  // Filter tasks in current board
  boardsStore.boards.forEach(board => {
    board.columns.forEach(column => {
      column.tasks.forEach(task => {
        const matchesSearch = 
          task.title?.toLowerCase().includes(searchLower) ||
          task.description?.toLowerCase().includes(searchLower) ||
          task.projectName?.toLowerCase().includes(searchLower) ||
          task.taskName?.toLowerCase().includes(searchLower) ||
          task.bapm?.toLowerCase().includes(searchLower) ||
          task.stakeholder?.toLowerCase().includes(searchLower) ||
          task.priority?.toLowerCase().includes(searchLower) ||
          task.status?.toLowerCase().includes(searchLower)
        
        // Toggle visibility based on search
        task.hidden = !matchesSearch
      })
    })
  })
}

// Clear search when switching boards
watch(() => boardsStore.selectedBoard, () => {
  searchQuery.value = ''
  filterTasks('')
})

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
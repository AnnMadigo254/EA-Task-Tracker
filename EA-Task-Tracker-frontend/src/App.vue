<!-- <template>
  <HeaderVue />
  <main>
    <div class="flex w-full ">
      <SideBar />
      <div v-dragscroll:nochilddrag
        class="relative h-full w-screen max-h-[calc(100vh-64px)] bg-light-grey dark:bg-very-dark-grey"
        :class="managerStore.sidebar ? 'sm:pl-[256px] lg:pl-[300px]' : ''">
        <div data-dragscroll class="p-6 w-full overflow-auto max-h-[calc(100vh-64px)] transition-all">
          <Board data-dragscroll v-if="boardsStore.getColumns" />
          <NoBoards v-else-if="boardsStore.boards.length === 0" />
          <EmptyBoard v-else />
        </div>
      </div>
    </div>
    <ShowSidebar v-if="!managerStore.SideBar" />
  </main>
  <bgOverlay data-no-dragscroll />
  <div class="absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] z-10 max-w-xs w-11/12 sm:max-w-md">
    <TaskView v-if="managerStore.taskView" />
    <TaskForm v-if="managerStore.taskForm.visible" />
    <Delete v-if="managerStore.delete.visible" />
    <BoardForm v-if="managerStore.boardForm.visible" />
    <SidebarMobile v-if="managerStore.sidebarMobile" />
  </div>
</template>

<script setup>
import EmptyBoard from './components/board/Empty.vue';
import Board from './components/board/Board.vue'
import HeaderVue from './components/Header.vue';
import bgOverlay from './components/bgOverlay.vue';
import TaskView from './components/manager/TaskView.vue'
import TaskForm from './components/manager/TaskForm.vue';
import Delete from './components/manager/Delete.vue';
import BoardForm from './components/manager/BoardForm.vue';
import SideBar from './components/manager/Sidebar.vue';
import SidebarMobile from './components/manager/SidebarMobile.vue';
import ShowSidebar from './components/manager/sidebar/ShowSidebar.vue';

import { onMounted } from 'vue';
import { useBoardsStore } from '@/stores/boards.js';
import { useManagerStore } from '@/stores/manager.js';
import NoBoards from './components/board/NoBoards.vue';

const boardsStore = useBoardsStore();
const managerStore = useManagerStore();

onMounted(async () => {
  //INIT STORAGE
  boardsStore.$subscribe((mutations, state) => {

    localStorage.setItem('boards', JSON.stringify(state))

  })
  const storageData = localStorage.getItem("boards")
  if (storageData === null) {
    const jsonData = await import("./assets/json/data.json")
    boardsStore.boards = jsonData.boards;
  } else {
    boardsStore.$state = JSON.parse(storageData)
  }

  //DARK MODE
  if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
    managerStore.darkmode = true;
  } else {
    localStorage.setItem('theme', 'light')
    managerStore.darkmode = false;
  }
  managerStore.$subscribe((mutations, state) => {
    localStorage.setItem('theme', (state.darkmode ? 'dark' : 'light'))
    if (state.darkmode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  })
}) 
</script> -->

<template>
  <HeaderVue />
  <main>
    <div class="flex w-full">
      <SideBar />
      <div
        v-dragscroll:nochilddrag
        class="relative h-full w-screen max-h-[calc(100vh-64px)] bg-light-grey dark:bg-very-dark-grey"
        :class="managerStore.sidebar ? 'sm:pl-[256px] lg:pl-[300px]' : ''"
      >
        <div
          data-dragscroll
          class="p-6 w-full overflow-auto max-h-[calc(100vh-64px)] transition-all"
        >
          <!-- Loading State -->
          <div v-if="boardsStore.loading" class="flex items-center justify-center h-full">
            <div class="text-medium-grey text-lg">Loading EA Tasks...</div>
          </div>

          <!-- Error State -->
          <div
            v-else-if="boardsStore.error"
            class="flex flex-col items-center justify-center h-full gap-4"
          >
            <div class="text-red text-lg">⚠️ {{ boardsStore.error }}</div>
            <button
              @click="loadBoards"
              class="px-4 py-2 bg-main-purple text-white rounded-lg hover:bg-main-purple-hover"
            >
              Retry
            </button>
          </div>

          <!-- Board Display -->
          <Board data-dragscroll v-else-if="boardsStore.getColumns" />
          <NoBoards v-else-if="boardsStore.boards.length === 0" />
          <EmptyBoard v-else />
        </div>
      </div>
    </div>
    <ShowSidebar v-if="!managerStore.SideBar" />
  </main>
  <bgOverlay data-no-dragscroll />
  <div
    class="absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] z-10 max-w-xs w-11/12 sm:max-w-md"
  >
    <TaskView v-if="managerStore.taskView" />
    <TaskForm v-if="managerStore.taskForm.visible" />
    <Delete v-if="managerStore.delete.visible" />
    <BoardForm v-if="managerStore.boardForm.visible" />
    <SidebarMobile v-if="managerStore.sidebarMobile" />
  </div>
</template>

<script setup>
import EmptyBoard from './components/board/Empty.vue';
import Board from './components/board/Board.vue';
import HeaderVue from './components/Header.vue';
import bgOverlay from './components/bgOverlay.vue';
import TaskView from './components/manager/TaskView.vue';
import TaskForm from './components/manager/TaskForm.vue';
import Delete from './components/manager/Delete.vue';
import BoardForm from './components/manager/BoardForm.vue';
import SideBar from './components/manager/Sidebar.vue';
import SidebarMobile from './components/manager/SidebarMobile.vue';
import ShowSidebar from './components/manager/sidebar/ShowSidebar.vue';

import { onMounted } from 'vue';
import { useBoardsStore } from '@/stores/boards.js';
import { useManagerStore } from '@/stores/manager.js';
import NoBoards from './components/board/NoBoards.vue';

const boardsStore = useBoardsStore();
const managerStore = useManagerStore();

// ✅ Load boards from Django API (no login needed — session auth via browser)
const loadBoards = async () => {
  try {
    await boardsStore.fetchBoards();
    localStorage.setItem('boards', JSON.stringify(boardsStore.$state));
  } catch (error) {
    console.error('Failed to load boards from API:', error);

    // Fallback 1: localStorage
    const storageData = localStorage.getItem('boards');
    if (storageData !== null) {
      boardsStore.$state = JSON.parse(storageData);
      return;
    }

    // Fallback 2: local JSON (dev only)
    try {
      const jsonData = await import('./assets/json/data.json');
      boardsStore.boards = jsonData.boards;
    } catch (fallbackError) {
      console.error('All fallbacks failed:', fallbackError);
      boardsStore.error = 'Could not load boards. Please refresh or check your connection.';
    }
  }
};

onMounted(async () => {
  // Load boards from API
  await loadBoards();

  // Persist store to localStorage
  boardsStore.$subscribe((mutations, state) => {
    localStorage.setItem('boards', JSON.stringify(state));
  });

  // Dark mode setup
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const savedTheme = localStorage.getItem('theme');

  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add('dark');
    managerStore.darkmode = true;
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    managerStore.darkmode = false;
    localStorage.setItem('theme', 'light');
  }

  // Sync dark mode changes to localStorage and DOM
  managerStore.$subscribe((mutations, state) => {
    localStorage.setItem('theme', state.darkmode ? 'dark' : 'light');
    if (state.darkmode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  });
});
</script>
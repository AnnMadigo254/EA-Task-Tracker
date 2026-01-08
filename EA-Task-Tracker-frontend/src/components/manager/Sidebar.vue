<template>
  <div class="z-10 transition-all fixed top-16 left-0 h-[calc(100vh-64px)]"
    :class="managerStore.sidebar ? 'translate-x-[0]' : 'translate-x-[-100%]'">
    <div
      class="bg-white dark:bg-dark-grey h-full w-64 lg:w-[300px] hidden sm:flex sm:flex-col border-r border-r-lines-light dark:border-r-lines-dark overflow-hidden">
      
      <!-- Header - Fixed at top -->
      <div class="flex-shrink-0">
        <p class="text-medium-grey text-xs font-bold py-4 px-6">
          ALL BOARDS ({{ boardsStore.boards.length }})
        </p>
      </div>
      
      <!-- Scrollable boards list -->
      <div class="flex-1 overflow-y-auto px-0 py-0">
        <div 
          @click="onClickBoard(index)" 
          v-for="(board, index) in boardsStore.boards" 
          :key="index"
          class="flex items-center gap-4 w-11/12 rounded-r-full px-6 py-3 cursor-pointer text-medium-grey font-bold"
          :class="board?.name === boardsStore?.getCurrentBoard?.name ?
            ['bg-main-purple', 'text-white', 'fill-white', 'hover:bg-main-purple-light']
            :
            ['fill-medium-grey', 'hover:text-main-purple', 'hover:fill-main-purple', 'hover:bg-medium-grey/10']">
          <IconBoard />
          <span>{{ formatBoardName(board.name) }}</span>
        </div>
        
        <div 
          @click="createNewBoard()"
          class="flex items-center gap-4 w-11/12 rounded-r-full px-6 py-3 cursor-pointer font-bold fill-main-purple text-main-purple hover:bg-medium-grey/10">
          <IconBoard />
          <span>+ Create New Board</span>
        </div>
      </div>
      
      <!-- Footer - Fixed at bottom -->
      <div class="flex-shrink-0 flex flex-col gap-2 py-4 border-t border-lines-light dark:border-lines-dark">
        <DarkModeSwitch class="w-10/12 mx-auto" />
        <HideSidebar class="w-11/12" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useManagerStore } from '@/stores/manager';
import { useBoardsStore } from '@/stores/boards';
import IconBoard from '@/components/icons/IconBoard.vue';
import DarkModeSwitch from './sidebar/DarkModeSwitch.vue';
import HideSidebar from './sidebar/HideSidebar.vue';

const managerStore = useManagerStore();
const boardsStore = useBoardsStore();

const onClickBoard = (index) => {
  boardsStore.selectedBoard = index;
};

const createNewBoard = () => {
  managerStore.overlay = true;
  managerStore.boardForm = { visible: true, edit: false };
};

// Format board names with proper capitalization and spacing
const formatBoardName = (name) => {
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
};
</script>
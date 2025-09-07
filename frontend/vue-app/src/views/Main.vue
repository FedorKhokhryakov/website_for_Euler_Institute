<template>
    <div class="bg-white relative">
      <div class="container mx-auto px-4 py-6">
        <div class="max-w-2xl mx-auto">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
            
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Поиск"
              class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent focus:outline-none transition-all"
              @input="handleSearch"
              @focus="isInputFocused = true"
              @blur="onInputBlur"
            />

            <div v-if="isLoading" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-green-600"></div>
            </div>
          </div>
        </div>
      </div>
      <div 
        v-if="showResults && searchResults.length > 0"
        class="absolute top-full left-0 right-0 bg-white border border-gray-200 shadow-lg z-50 max-w-2xl mx-auto mt-1 rounded-lg overflow-hidden"
        >
        <div class="max-h-96 overflow-y-auto">
            <div 
            v-for="result in searchResults"
            :key="result.id"
            class="p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
            @mousedown="selectResult(result)"
            >
            <h3 class="font-medium text-gray-900">{{ result.title }}</h3>
            <div class="flex items-center mt-2">
                <span class="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                {{ result.type }}
                </span>
            </div>
            </div>
        </div>
        </div>

        <div 
        v-else-if="showResults && searchQuery && !isLoading"
        class="absolute top-full left-0 right-0 bg-white border border-gray-200 shadow-lg z-50 max-w-2xl mx-auto mt-1 rounded-lg"
        >
        <div class="p-4 text-center text-gray-500">
            Ничего не найдено
        </div>
        </div>
    </div>
</template>

<script setup>

import { ref, computed, watch } from 'vue'
import { useAuthStore } from "../stores/auth"
import axios from 'axios'

const authStore = useAuthStore()
const searchQuery = ref('')
const searchResults = ref([])
const isLoading = ref(false)
const isInputFocused = ref(false)
const debounceTimeout = ref(null)

const showResults = computed(() => {
  return isInputFocused.value && searchQuery.value.length > 0
})

const handleSearch = () => {
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value)
  }

  isLoading.value = true
  debounceTimeout.value = setTimeout(() => {
    performSearch()
  }, 300)
}

const performSearch = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/search/', {
      params: {
        q: searchQuery.value,
        limit: 10
      },
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    searchResults.value = response.data.results || []
  } catch (error) {
    console.error('Search error:', error)
    searchResults.value = []
  } finally {
    isLoading.value = false
  }
}

const onInputBlur = () => {
  setTimeout(() => {
    isInputFocused.value = false
  }, 200)
}

const selectResult = (result) => {
  console.log('Selected result:', result)
  searchQuery.value = ''
  searchResults.value = []
}

import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value)
  }
})

</script>
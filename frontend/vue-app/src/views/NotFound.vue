<template>
  <div class="flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-800 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-700 mb-4">Страница не найдена</h2>
      <p class="text-gray-600 mb-8">
        Извините, страница которую вы ищете, не существует.
      </p>
      <router-link 
        to="/main" 
        class="bg-green-600 hover:bg-green-800 text-white px-6 py-3 rounded-lg transition-colors"
      >
        Вернуться на главную
      </router-link>
    </div>
  </div>
</template>

<script setup>
</script>
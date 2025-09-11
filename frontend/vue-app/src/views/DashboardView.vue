<template>
  <div class="dashboard">
    <h1>Главная панель</h1>
    <p>Текущее время: {{ new Date().toLocaleTimeString() }}</p>
    <p>Проверка отображения контента</p>
  </div>
</template>


<script setup>
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  background-color: #f8f9fa;
  min-height: 400px;
}

.dashboard h1 {
  color: #2e7d32;
  margin: 0 0 1rem 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.dashboard p {
  color: #333;
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}
</style>
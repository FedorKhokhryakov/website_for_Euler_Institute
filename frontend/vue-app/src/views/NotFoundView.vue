<template>
  <div class="not-found-container">
    <div class="not-found-card">
      <div class="not-found-header">
        <h1>404 - Страница не найдена</h1>
      </div>

      <div class="not-found-content">
        <p>Запрашиваемая страница не существует.</p>
        <button @click="goToDashboard" class="not-found-button">
          На главную
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  padding: 20px;
}

.not-found-card {
  background-color: white;
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  border: 1px solid #e0e0e0;
  text-align: center;
}

.not-found-header {
  margin-bottom: 2rem;
}

.not-found-header h1 {
  color: #2e7d32;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.not-found-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.not-found-content p {
  color: #333;
  margin: 0;
  font-size: 1rem;
}

.not-found-button {
  background-color: #2e7d32;
  color: white;
  padding: 10px;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
}

.not-found-button:hover {
  background-color: #1b5e20;
}
</style>
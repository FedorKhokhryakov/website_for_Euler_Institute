<template>
  <div class="user-profile">
    <div class="profile-header">
      <h1>Профиль сотрудника</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="userData" class="profile-content">
      <div class="profile-main">
        <div class="photo-placeholder">
          <div class="photo-icon">
            <span>📷</span>
          </div>
          <p>Фотография</p>
        </div>
        <div class="info-container">
          <div class="info-row">
            <span class="info-label">ФИО:</span>
            <span class="info-value">{{ userData.last_name }} {{ userData.first_name }} {{ userData.middle_name || '' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Email:</span>
            <span class="info-value">{{ userData.email }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Лаборатория:</span>
            <span class="info-value">{{ userData.laboratory || 'Не указана' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Год рождения:</span>
            <span class="info-value">{{ userData.birth_year || 'Не указан' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Год окончания вуза:</span>
            <span class="info-value">{{ userData.graduation_year || 'Не указан' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Ученая степень:</span>
            <span class="info-value">{{ userData.academic_degree || 'Не указана' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Год получения степени:</span>
            <span class="info-value">{{ userData.degree_year || 'Не указан' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Ученое звание:</span>
            <span class="info-value">{{ userData.academic_title || 'Не указано' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Должность:</span>
            <span class="info-value">{{ userData.position || 'Не указана' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Ставка:</span>
            <span class="info-value">{{ userData.rate || 'Не указана' }}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Статус:</span>
            <span class="info-value">{{ userData.status || 'Не указан' }}</span>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const route = useRoute()
const authStore = useAuthStore()
const { user: currentUser } = storeToRefs(authStore)

const userId = route.params.id
const userData = ref(null)
const loading = ref(true)
const error = ref('')

const loadUserData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    userData.value = {
      id: userId,
      first_name: 'Иван',
      last_name: 'Иванов',
      middle_name: 'Иванович',
      email: 'ivanov@institute.ru',
      laboratory: 'Лаборатория математического моделирования',
      birth_year: 1985,
      graduation_year: 2007,
      academic_degree: 'Кандидат физико-математических наук',
      degree_year: 2011,
      academic_title: 'Доцент',
      position: 'Старший научный сотрудник',
      rate: '1.0',
      status: 'Основной сотрудник'
    }
    
  } catch (err) {
    error.value = 'Не удалось загрузить данные пользователя'
    console.error('Ошибка загрузки:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.user-profile {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 2rem;
}

.profile-header h1 {
  color: #2e7d32;
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error-state {
  color: #d32f2f;
}

.profile-main {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.photo-placeholder {
  width: 150px;
  text-align: center;
  flex-shrink: 0;
}

.photo-icon {
  width: 120px;
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.photo-icon span {
  font-size: 3rem;
}

.photo-placeholder p {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.info-container {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1rem;
}

.info-row {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.info-label {
  font-weight: 600;
  color: #2e7d32;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 500;
}
</style>
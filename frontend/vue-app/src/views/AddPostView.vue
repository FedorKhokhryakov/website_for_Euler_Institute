<template>
  <div class="add-post">
    <form @submit.prevent="submitForm" class="post-form compact-form">
      <div class="form-row">
        <label for="type">* Тип:</label>
        <select id="type" v-model="post.type" required @change="handleTypeChange">
          <option value="">Выберите тип</option>
          <option value="publication">Публикация</option>
          <option value="monograph">Монография</option>
          <option value="presentation">Доклад</option>
          <option value="lecture">Курс лекций/семинар</option>
          <option value="patent">Патент</option>
          <option value="supervision">Научное руководство</option>
          <option value="editing">Редактирование научных изданий</option>
          <option value="editorial_board">Работа в составе ред. коллегии</option>
          <option value="org_work">Научно-орг. работа</option>
          <option value="opposition">Оппонирование</option>
          <option value="grant">Грант</option>
          <option value="award">Награда</option>
        </select>
      </div>

      <!-- Динамический компонент для конкретного типа -->
      <component
        :is="currentComponent"
        v-model="post.details"
        v-if="post.type"
      />

      <div class="form-row" v-if="post.type">
        <label for="comment">Комментарий:</label>
        <textarea id="comment" v-model="post.comment" rows="3" placeholder="Дополнительная информация"></textarea>
      </div>

      <div class="form-actions" v-if="post.type">
        <button 
          type="submit" 
          :disabled="isSubmitting"
          :class="{ 'disabled': isSubmitting }"
          class="submit-btn"
        >
          <span v-if="isSubmitting">Отправка...</span>
          <span v-else>Добавить {{ postTypeLabel }}</span>
        </button>
        <button 
          type="button" 
          @click="resetForm"
          :disabled="isSubmitting"
          class="reset-btn"
        >
          Сбросить
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, shallowRef } from 'vue'
import { publicationsAPI } from '../services/api.js'
import AddPublicationView from '../components/forms/AddPublicationView.vue'

const isSubmitting = ref(false)

const componentMap = {
  publication: AddPublicationView,
  // Здесь будут другие компоненты для остальных типов
}

const post = reactive({
  type: '',
  comment: '',
  details: {}
})

const currentComponent = computed(() => {
  return post.type ? componentMap[post.type] : null
})

const postTypeLabel = computed(() => {
  const labels = {
    publication: 'публикацию',
    monograph: 'монографию',
    presentation: 'доклад',
    lecture: 'курс лекций',
    patent: 'патент',
    supervision: 'научное руководство',
    editing: 'редактирование',
    editorial_board: 'работу в ред. коллегии',
    org_work: 'научно-орг. работу',
    opposition: 'оппонирование',
    grant: 'грант',
    award: 'награду'
  }
  return labels[post.type] || 'публикацию'
})

const handleTypeChange = () => {
  // Сбрасываем детали при смене типа
  post.details = {}
  post.comment = ''
}

const formatPostData = () => {
  return {
    post: {
      post_type: post.type,
      comment: post.comment || ''
    },
    details: { ...post.details }
  }
}

const submitForm = async () => {
  if (isSubmitting.value) return;
  
  isSubmitting.value = true;
  
  try {
    const formattedData = formatPostData()
    
    console.log('Отправляемые данные:', formattedData)
    
    const response = await publicationsAPI.create(formattedData)
    
    if (response.status === 201) {
      alert(`${postTypeLabel.value} успешно добавлена!`);
      resetForm();
    }
  } catch (error) {
    console.error('Ошибка:', error.response?.data || error);
    alert('Произошла ошибка при отправке данных: ' + (error.response?.data?.message || error.message));
  } finally {
    isSubmitting.value = false;
  }
}

const resetForm = () => {
  post.type = ''
  post.comment = ''
  post.details = {}
}
</script>

<style scoped>
.add-post {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.compact-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 15px;
  align-items: center;
  min-height: 40px;
}

.form-row label {
  font-weight: bold;
  text-align: right;
}

input, select, textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #4CAF50;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 20px;
  grid-column: 1 / -1;
}

button {
  padding: 10px 20px;
  border: none;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
}

.reset-btn {
  background-color: #f44336;
  color: white;
}

.submit-btn:not(.disabled):hover,
.submit-btn:not(.disabled):focus {
  background-color: #388E3C;
}

.reset-btn:not(.disabled):hover,
.reset-btn:not(.disabled):focus {
  background-color: #D32F2F;
}

button:disabled,
button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

button.disabled {
  cursor: wait;
}
</style>
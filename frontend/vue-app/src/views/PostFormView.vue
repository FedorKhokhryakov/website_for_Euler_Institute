<template>
  <div class="add-post">
    <form @submit.prevent="submitForm" class="post-form compact-form">
      <div class="form-section">
        <div class="form-row">
          <label for="type">* Тип:</label>
          <select 
            id="type" 
            v-model="post.type" 
            required 
            @change="handleTypeChange"
            :disabled="isEditMode"
          >
            <option value="">Выберите тип</option>
            <option value="publication">Публикация</option>
            <option value="presentation">Доклад</option>
          </select>
        </div>

        <component
          :is="currentComponent"
          :model-value="post.details"
          @update:model-value="handleDetailsUpdate"
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
            <span v-else>{{ submitButtonText }}</span>
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { publicationsAPI } from '../services/api.js'
import AddPublicationComponent from '../components/forms/AddPublicationComponent.vue'
import AddPresentationComponent from '../components/forms/AddPresentationComponent.vue'

const route = useRoute()
const router = useRouter()

const props = defineProps({
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'edit'].includes(value)
  }
})

const isSubmitting = ref(false)
const postId = ref(null)

const isEditMode = computed(() => props.mode === 'edit')
const submitButtonText = computed(() => 
  isEditMode.value ? 'Сохранить изменения' : 'Добавить запись'
)

const componentMap = {
  publication: AddPublicationComponent,
  presentation: AddPresentationComponent,
}

const post = reactive({
  type: '',
  comment: '',
  details: {}
})

const currentComponent = computed(() => {
  return post.type ? componentMap[post.type] : null
})

const handleDetailsUpdate = (newDetails) => {
  post.details = { ...newDetails }
}

const handleTypeChange = () => {
  if (!isEditMode.value) {
    post.details = {}
    post.comment = ''
  }
}

const loadPostData = async () => {
  if (isEditMode.value && route.params.id) {
    try {
      postId.value = route.params.id
      const response = await publicationsAPI.getPostInformation(postId.value)
      console.log("Загруженные данные: ", response.data)
      const postData = response.data
      
      post.type = postData.post.type
      post.comment = postData.post.comment || ''
      
      handleDetailsUpdate(postData.details)
      
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
      alert('Не удалось загрузить данные для редактирования')
      router.back()
    }
  }
}

const formatPostData = () => {
  const details = { ...post.details }
  
  const dateFields = ['preprint_date', 'submission_date', 'acceptance_date', 'publication_date']
  dateFields.forEach(field => {
    if (details[field] === '') {
      details[field] = null
    }
  })

  if (details.internal_authors_list && !Array.isArray(details.internal_authors_list)) {
    details.internal_authors_list = []
  }


  return {
    post: {
      type: post.type,
      comment: post.comment || ''
    },
    details: details
  }
}

const submitForm = async () => {
  if (isSubmitting.value) return;
  
  isSubmitting.value = true;
  
  try {
    const formattedData = formatPostData()

    console.log("Подтверждение формы: ", formattedData)
    
    if (isEditMode.value) {
      const response = await publicationsAPI.updatePost(postId.value, formattedData)
      if (response.status === 200) {
        alert('Запись успешно обновлена!')
        router.back()
      }
    } else {
      const response = await publicationsAPI.createPost(formattedData)
      if (response.status === 201) {
        alert('Запись успешно добавлена!')
        resetForm()
      }
    }
  } catch (error) {
    console.error('Ошибка:', error.response?.data || error)
    alert('Произошла ошибка: ' + (error.response?.data?.message || error.message))
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  if (!isEditMode.value) {
    post.type = ''
    post.comment = ''
    post.details = {}
  }
}

onMounted(() => {
  loadPostData()
})
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
  gap: 1rem;
}

.form-section {
  padding: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.form-row label {
  font-weight: 600;
  text-align: right;
}

input, select, textarea {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
  grid-column: 1 / -1;
}

button {
  padding: 0.75rem 1.5rem;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.submit-btn {
  background-color: var(--color-primary);
  color: white;
}

.reset-btn {
  background-color: var(--color-secondary);
  color: white;
}

.submit-btn:not(.disabled):hover,
.submit-btn:not(.disabled):focus {
  background-color: var(--color-primary-dark);
}

.reset-btn:not(.disabled):hover,
.reset-btn:not(.disabled):focus {
  background-color: var(--color-secondary-dark);
}

button:disabled,
button.disabled {
  background-color: var(--color-text-secondary);
  cursor: not-allowed;
}

button.disabled {
  cursor: wait;
}
</style>
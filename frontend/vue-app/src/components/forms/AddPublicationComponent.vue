<template>
  <div class="publication-form">
    <div class="form-section">
      <h3>Данные о препринте</h3>
      
      <div class="form-row">
        <label for="title">* Название:</label>
        <input type="text" id="title" v-model="formData.title" required>
      </div>

      <div class="form-row">
        <label for="language">* Язык:</label>
        <select id="language" v-model="formData.language" required>
          <option value="">Выберите язык</option>
          <option value="russian">Русский</option>
          <option value="english">Английский</option>
        </select>
      </div>

      <div class="form-row">
        <label for="preprint_date">* Дата препринта:</label>
        <input type="date" id="preprint_date" v-model="formData.preprint_date" required>
      </div>

      <div class="form-row">
        <label for="preprint_number">* Номер препринта:</label>
        <input type="text" id="preprint_number" v-model="formData.preprint_number" required>
      </div>

      <div class="form-row">
        <label>Внешние авторы:</label>
        <div class="authors-container">
          <div v-for="(author, index) in formData.external_authors" :key="index" class="author-input">
            <input 
              type="text" 
              v-model="formData.external_authors[index]" 
              :placeholder="`Автор ${index + 1}`"
            >
            <button type="button" @click="removeExternalAuthor(index)" class="btn-remove">×</button>
          </div>
          <button type="button" @click="addExternalAuthor" class="btn-add-author">+ Добавить автора</button>
        </div>
      </div>
      <div class="checkbox-row">
        <label>Направлено на публикацию: </label>
        <div class="checkbox-section">
          <input type="checkbox" v-model="showSubmissionFields">
        </div>
      </div>
    </div>


    <div v-if="showSubmissionFields" class="form-section">
      <h4>Данные об отправке в журнал</h4>
      
      <div class="form-row">
        <label for="submission_date">Дата отправки:</label>
        <input type="date" id="submission_date" v-model="formData.submission_date">
      </div>

      <div class="form-row">
        <label for="journal_name">Название журнала:</label>
        <input type="text" id="journal_name" v-model="formData.journal_name">
      </div>

      <div class="form-row">
        <label for="journal_issn">ISSN журнала:</label>
        <input type="text" id="journal_issn" v-model="formData.journal_issn">
      </div>

      <div class="checkbox-row">
        <label>Принято к публикации: </label>
        <div class="checkbox-section">
          <input type="checkbox" v-model="showAcceptanceFields">
        </div>
      </div>
    </div>

    <div v-if="showAcceptanceFields" class="form-section">
      <h4>Данные о принятии статьи</h4>
      
      <div class="form-row">
        <label for="acceptance_date">Дата принятия:</label>
        <input type="date" id="acceptance_date" v-model="formData.acceptance_date">
      </div>

      <div class="form-row">
        <label for="doi">DOI:</label>
        <input type="text" id="doi" v-model="formData.doi">
      </div>

      <div class="checkbox-row">
        <label>Опубликовано: </label>
        <div class="checkbox-section">
          <input type="checkbox" v-model="showPublicationFields">
        </div>
      </div>
    </div>

    <div v-if="showPublicationFields" class="form-section">
      <h4>Данные о публикации</h4>
      
      <div class="form-row">
        <label for="publication_date">Дата публикации:</label>
        <input type="date" id="publication_date" v-model="formData.publication_date">
      </div>

      <div class="form-row triple-column">
        <label>Детали публикации:</label>
        <div class="multi-input-container">
          <div class="input-group">
            <input type="text" v-model="formData.journal_volume" placeholder="Том">
          </div>
          <div class="input-group">
            <input type="text" v-model="formData.journal_number" placeholder="Номер">
          </div>
          <div class="input-group">
            <input type="text" v-model="formData.journal_pages_or_article_number" placeholder="Страницы/Номер статьи">
          </div>
        </div>
      </div>

      <div class="checkbox-row">
        <label for="journal_level">Уровень журнала:</label>
        <input type="text" id="journal_level" v-model="formData.journal_level">
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed, nextTick } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const showSubmissionFields = ref(false)
const showAcceptanceFields = ref(false)
const showPublicationFields = ref(false)

const isUpdating = ref(false)

const currentStatus = computed(() => {
  if (showPublicationFields.value) return 'published'
  if (showAcceptanceFields.value) return 'accepted'
  if (showSubmissionFields.value) return 'submitted'
  return 'preprint'
})


const formData = reactive({
  title: '',
  language: '',
  preprint_date: '',
  preprint_number: '',
  external_authors: [''],
  
  submission_date: '',
  journal_name: '',
  journal_issn: '',
  
  acceptance_date: '',
  doi: '',
  
  publication_date: '',
  journal_volume: null,
  journal_number: null,
  journal_pages_or_article_number: '',
  journal_level: '',

  current_status: 'preprint'
})

const prepareFormData = () => {
  const cleanedData = { ...formData }
  
  const dateFields = ['submission_date', 'acceptance_date', 'publication_date']
  dateFields.forEach(field => {
    if (cleanedData[field] === '') {
      cleanedData[field] = null
    }
  })
  
  const numericFields = ['journal_volume', 'journal_number']
  numericFields.forEach(field => {
    if (cleanedData[field] === '' || cleanedData[field] === null) {
      cleanedData[field] = null
    } else {
      cleanedData[field] = Number(cleanedData[field])
    }
  })
  
  cleanedData.external_authors = cleanedData.external_authors.filter(author => author.trim() !== '')
  
  return cleanedData
}

watch(currentStatus, (newStatus) => {
  formData.current_status = newStatus
})

watch(showSubmissionFields, (newValue) => {
  if (!newValue) {
    showAcceptanceFields.value = false

    formData.submission_date = ''
    formData.journal_name = ''
    formData.journal_issn = ''
  }
})

watch(showAcceptanceFields, (newValue) => {
  if (!newValue) {
    showPublicationFields.value = false

    formData.acceptance_date = ''
    formData.doi = ''
  }
})

watch(showPublicationFields, (newValue) => {
  if (!newValue) {
    formData.publication_date = ''
    formData.journal_volume = null
    formData.journal_number = null
    formData.journal_pages_or_article_number = ''
    formData.journal_level = ''
  }
})

const addExternalAuthor = () => {
  formData.external_authors.push('')
}

const removeExternalAuthor = (index) => {
  if (formData.external_authors.length > 1) {
    formData.external_authors.splice(index, 1)
  }
}

watch(formData, () => {
  if (isUpdating.value) return
  
  isUpdating.value = true
  const cleanedData = prepareFormData()
  emit('update:modelValue', cleanedData)
  
  nextTick(() => {
    isUpdating.value = false
  })
}, { deep: true })


watch(() => props.modelValue, (newValue, oldValue) => {
  if (isUpdating.value) return
  if (JSON.stringify(newValue) === JSON.stringify(oldValue)) return
  
  isUpdating.value = true
  
  if (newValue.current_status) {
    const status = newValue.current_status
    showSubmissionFields.value = status === 'submitted' || status === 'accepted' || status === 'published'
    showAcceptanceFields.value = status === 'accepted' || status === 'published'
    showPublicationFields.value = status === 'published'
  }

  Object.keys(formData).forEach(key => {
    if (newValue[key] !== undefined && formData[key] !== newValue[key]) {
      formData[key] = newValue[key]
    }
  })
  
  nextTick(() => {
    isUpdating.value = false
  })
}, { immediate: true })
</script>

<style scoped>
.publication-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-section {
  padding: 1rem;
}

.form-section h3, .form-section h4 {
  color: var(--color-primary);
  margin-bottom: 1rem;
  text-align: center;
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

.checkbox-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
}

.checkbox-row label {
  font-weight: 600;
  text-align: right;
  margin: 0;
}

.checkbox-section input[type="checkbox"] {
  margin: 0;
  width: auto;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--color-primary);
}

.authors-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.author-input {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-remove {
  background: var(--color-secondary);
  color: white;
  border: none;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-add-author {
  background: none;
  border: 1px dashed var(--color-border);
  padding: 0.5rem;
  cursor: pointer;
  color: var(--color-primary);
}

.triple-column .multi-input-container {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
}

input, select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
}

input:focus, select:focus {
  outline: none;
  border-color: var(--color-primary);
}
</style>
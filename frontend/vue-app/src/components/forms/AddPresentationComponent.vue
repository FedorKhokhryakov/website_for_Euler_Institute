<template>
  <div class="publication-form">
    <div class="form-section">
      <h3>Информация о препринте</h3>
      
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
          <option value="german">Немецкий</option>
          <option value="french">Французский</option>
          <option value="other">Другой</option>
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
    </div>

    <div class="checkbox-section">
      <label class="checkbox-label">
        <input type="checkbox" v-model="showSubmissionFields">
        Направлено на публикацию
      </label>
    </div>

    <div v-if="showSubmissionFields" class="form-section">
      <h4>Информация об отправке в журнал</h4>
      
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

      <div class="checkbox-section">
        <label class="checkbox-label">
          <input type="checkbox" v-model="showAcceptanceFields">
          Принято к публикации
        </label>
      </div>
    </div>

    <div v-if="showAcceptanceFields" class="form-section">
      <h4>Информация о принятии статьи</h4>
      
      <div class="form-row">
        <label for="acceptance_date">Дата принятия:</label>
        <input type="date" id="acceptance_date" v-model="formData.acceptance_date">
      </div>

      <div class="form-row">
        <label for="doi">DOI:</label>
        <input type="text" id="doi" v-model="formData.doi">
      </div>

      <div class="checkbox-section">
        <label class="checkbox-label">
          <input type="checkbox" v-model="showPublicationFields">
          Опубликовано
        </label>
      </div>
    </div>

    <div v-if="showPublicationFields" class="form-section">
      <h4>Информация о публикации</h4>
      
      <div class="form-row">
        <label for="publication_date">Дата публикации:</label>
        <input type="date" id="publication_date" v-model="formData.publication_date">
      </div>

      <div class="form-row triple-column">
        <label>Детали публикации:</label>
        <div class="multi-input-container">
          <div class="input-group">
            <input type="number" v-model="formData.journal_volume" placeholder="Том" min="1">
          </div>
          <div class="input-group">
            <input type="number" v-model="formData.journal_number" placeholder="Номер" min="1">
          </div>
          <div class="input-group">
            <input type="text" v-model="formData.journal_pages_or_article_number" placeholder="Страницы/Номер статьи">
          </div>
        </div>
      </div>

      <div class="form-row">
        <label for="journal_level">Уровень журнала:</label>
        <input type="text" id="journal_level" v-model="formData.journal_level" placeholder="WoS, Scopus, RINC и т.д.">
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

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
  journal_level: ''
})

const addExternalAuthor = () => {
  formData.external_authors.push('')
}

const removeExternalAuthor = (index) => {
  if (formData.external_authors.length > 1) {
    formData.external_authors.splice(index, 1)
  }
}

watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

watch(() => props.modelValue, (newValue) => {
  Object.assign(formData, newValue)
}, { immediate: true })
</script>

<style scoped>
.publication-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-section {
  border: 1px solid var(--color-border);
  padding: 1rem;
}

.form-section h3, .form-section h4 {
  color: var(--color-primary);
  margin-bottom: 1rem;
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

.checkbox-section {
  margin: 1rem 0;
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
<template>
  <div class="publication-form">
    <div class="form-row">
      <label for="title">* Название:</label>
      <input type="text" id="title" v-model="localDetails.title" required>
    </div>

    <div class="form-row">
      <label for="authors">* Автор(ы):</label>
      <input type="text" id="authors" v-model="localDetails.authors" placeholder="Авторы через запятую" required>
    </div>

    <div class="form-row">
      <label>Дополнительные даты:</label>
      <div class="dates-container">
        <div class="date-input">
          <input type="date" v-model="localDetails.received_date">
          <span>Получена</span>
        </div>
        <div class="date-input">
          <input type="date" v-model="localDetails.decision_date">
          <span>Принята</span>
        </div>
        <div class="date-input">
          <input type="date" v-model="localDetails.published_date">
          <span>Опубликована</span>
        </div>
      </div>
    </div>

    <div class="form-row triple-column">
      <label>Издание:</label>
      <div class="multi-input-container">
        <div class="input-group">
          <input type="text" v-model="localDetails.journal" placeholder="Название издания">
        </div>
        <div class="input-group">
          <input type="text" v-model="localDetails.journal_tome" placeholder="Том" class="small-input">
        </div>
        <div class="input-group">
          <input type="text" v-model="localDetails.journal_number" placeholder="Номер" class="small-input">
        </div>
      </div>
    </div>

    <div class="form-row">
      <label for="articleId">ID статьи:</label>
      <input type="text" id="articleId" v-model="localDetails.article_id" placeholder="DOI или другой идентификатор">
    </div>

    <div class="form-row">
      <label>Страницы:</label>
      <input type="text" v-model="localDetails.pages" placeholder="123-145">
    </div>

    <div class="form-row">
      <label>* Год:</label>
      <input type="number" v-model="localDetails.year" :min="2000" :max="new Date().getFullYear() + 1" required>
    </div>

    <div class="form-row">
      <label for="language">* Язык:</label>
      <select id="language" v-model="localDetails.language" required>
        <option value="">Выберите язык</option>
        <option value="russian">Русский</option>
        <option value="english">Английский</option>
        <option value="german">Немецкий</option>
        <option value="french">Французский</option>
        <option value="other">Другой</option>
      </select>
    </div>

    <div class="form-row">
      <label for="webpage">Веб-страница:</label>
      <input type="url" id="webpage" v-model="localDetails.web_page" placeholder="https://example.com">
    </div>

    <div class="form-row checkbox-row">
      <label for="facultyCoauthors">Соавторы с факультета:</label>
      <input type="checkbox" id="facultyCoauthors" v-model="localDetails.faculty_coauthors">
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const localDetails = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

<style scoped>
.publication-form {
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

.dates-container {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.date-input {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.date-input span {
  font-size: 0.8em;
  color: #666;
  text-align: center;
}

.triple-column .multi-input-container {
  display: grid;
  grid-template-columns: 1fr 80px 80px;
  gap: 10px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.checkbox-row label {
  text-align: right;
  margin: 0;
}

.checkbox-row input[type="checkbox"] {
  width: auto;
  margin: 0;
}

input, select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}

.small-input {
  min-width: 80px;
}

input:focus, select:focus {
  outline: none;
  border-color: #4CAF50;
}
</style>
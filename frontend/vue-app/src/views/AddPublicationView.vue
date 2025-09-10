<template>
  <div class="add-publication">
    <form @submit.prevent="submitForm" class="publication-form compact-form">
      <!-- Тип публикации -->
      <div class="form-row">
        <label for="type">* Тип:</label>
        <select id="type" v-model="publication.type" required>
          <option value="">Выберите тип</option>
          <option value="publication">Публикация</option>
          <option value="monograph">Монография</option>
          <option value="reports">Доклад</option>
          <option value="lectures">Курс лекций/семинар</option>
          <option value="patents">Патент</option>
          <option value="supervision">Научное руководство</option>
          <option value="editing">Редактирование научных изданий</option>
          <option value="editorial_board">Работа в составе ред. коллегии</option>
          <option value="org_work">Научно-орг. работа</option>
          <option value="opposition">Оппонирование</option>
          <option value="grants">Грант</option>
          <option value="awards">Награда</option>
        </select>
      </div>

      <!-- Название статьи -->
      <div class="form-row">
        <label for="title">* Название:</label>
        <input type="text" id="title" v-model="publication.title" required>
      </div>

      <!-- Автор(ы) -->
      <div class="form-row">
        <label for="authors">* Автор(ы):</label>
        <input type="text" id="authors" v-model="publication.authors" placeholder="Авторы через запятую" required>
      </div>

      <!-- Количество авторов -->
      <div class="form-row">
        <label for="authorCount">* Кол-во авторов:</label>
        <input type="number" id="authorCount" v-model="publication.authorCount" min="1" required class="small-input">
      </div>

      <!-- Дополнительные даты -->
      <div class="form-row">
        <label>Дополнительные даты:</label>
        <div class="dates-container">
          <div class="date-input">
            <input type="date" v-model="publication.receivedDate">
            <span>Получена</span>
          </div>
          <div class="date-input">
            <input type="date" v-model="publication.decisionDate">
            <span>Принята</span>
          </div>
          <div class="date-input">
            <input type="date" v-model="publication.publishedDate">
            <span>Опубликована</span>
          </div>
        </div>
      </div>

      <!-- Издание, том, номер -->
      <div class="form-row triple-column">
        <label>Издание:</label>
        <div class="multi-input-container">
          <div class="input-group">
            <input type="text" v-model="publication.journal" placeholder="Название издания">
          </div>
          <div class="input-group">
            <input type="text" v-model="publication.volume" placeholder="Том" class="small-input">
          </div>
          <div class="input-group">
            <input type="text" v-model="publication.issue" placeholder="Номер" class="small-input">
          </div>
        </div>
      </div>

      <!-- Идентификационный номер статьи -->
      <div class="form-row">
        <label for="articleId">ID статьи:</label>
        <input type="text" id="articleId" v-model="publication.articleId" placeholder="DOI или другой идентификатор">
      </div>

      <div class="form-row">
        <label>Страницы:</label>
        <input type="text" v-model="publication.pages" placeholder="123-145">
      </div>

      <div class="form-row">
        <label>* Год:</label>
        <input type="text" v-model="publication.year" placeholder="2005">
      </div>

      <!-- Язык издания -->
      <div class="form-row">
        <label for="language">* Язык:</label>
        <select id="language" v-model="publication.language" required>
          <option value="">Выберите язык</option>
          <option value="russian">Русский</option>
          <option value="english">Английский</option>
          <option value="german">Немецкий</option>
          <option value="french">Французский</option>
          <option value="other">Другой</option>
        </select>
      </div>

      <!-- Веб-страница -->
      <div class="form-row">
        <label for="webpage">Веб-страница:</label>
        <input type="url" id="webpage" v-model="publication.webpage" placeholder="https://example.com">
      </div>

      <!-- Соавторы среди коллектива факультета -->
      <div class="form-row checkbox-row">
        <label for="facultyCoauthors">Соавторы с факультета:</label>
        <input type="checkbox" id="facultyCoauthors" v-model="publication.facultyCoauthors">
      </div>

      <!-- Комментарий -->
      <div class="form-row">
        <label for="comment">Комментарий:</label>
        <textarea id="comment" v-model="publication.comment" rows="3" placeholder="Дополнительная информация"></textarea>
      </div>

      <!-- Кнопки отправки и сброса -->
      <div class="form-actions">
        <button 
          type="submit" 
          :disabled="isSubmitting"
          :class="{ 'disabled': isSubmitting }"
          class="submit-btn"
        >
          <span v-if="isSubmitting">Отправка...</span>
          <span v-else>Добавить публикацию</span>
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
import { ref, reactive } from 'vue'

const isSubmitting = ref(false)

const publication = reactive({
  type: '',
  title: '',
  authors: '',
  authorCount: 1,
  receivedDate: '',
  decisionDate: '',
  publishedDate: '',
  journal: '',
  volume: '',
  issue: '',
  articleId: '',
  pages: '',
  year: new Date().getFullYear(),
  language: '',
  webpage: '',
  facultyCoauthors: false,
  comment: ''
})

const submitForm = async () => {
  if (isSubmitting.value) return;
  
  isSubmitting.value = true;
  
  try {
    const response = await fetch('http://your-backend-domain.com/api/publications', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(publication)
    });
    
    if (response.ok) {
      const result = await response.json();
      alert('Публикация успешно добавлена!');
      resetForm();
    } else {
      alert('Ошибка при добавлении публикации: ' + response.statusText);
    }
  } catch (error) {
    console.error('Ошибка:', error);
    alert('Произошла ошибка при отправке данных.');
  } finally {
    isSubmitting.value = false;
  }
}

const resetForm = () => {
  Object.assign(publication, {
    type: '',
    title: '',
    authors: '',
    authorCount: 1,
    receivedDate: '',
    decisionDate: '',
    publishedDate: '',
    journal: '',
    volume: '',
    issue: '',
    articleId: '',
    pages: '',
    year: new Date().getFullYear(),
    language: '',
    webpage: '',
    facultyCoauthors: false,
    comment: ''
  })
}
</script>

<style scoped>
.add-publication {
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

.double-column .multi-input-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.triple-column .multi-input-container {
  display: grid;
  grid-template-columns: 1fr 80px 80px;
  gap: 10px;
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

input, select, textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}

.small-input {
  min-width: 80px;
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
  border-radius: 4px;
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
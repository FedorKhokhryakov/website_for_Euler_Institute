<template>
  <div class="publication-detail">
    <div v-if="loading" class="loading">
      <p>Загрузка публикации...</p>
    </div>
    
    <div v-else-if="publication" class="publication-content">
      <button @click="$router.back()" class="back-btn">Назад</button>
      
      <div class="publication-header">
        <span class="publication-type">{{ getTypeLabel(publication.type) }}</span>
        <span class="publication-year">{{ publication.year }}</span>
      </div>
      
      <h1 class="publication-title">{{ publication.title }}</h1>
      
      <div class="publication-meta">
        <div class="meta-item">
          <strong>Авторы:</strong> {{ publication.authors }}
        </div>
        <div class="meta-item">
          <strong>Количество авторов:</strong> {{ publication.authorCount }}
        </div>
        <div v-if="publication.journal" class="meta-item">
          <strong>Издание:</strong> {{ publication.journal }}
          <span v-if="publication.volume">, Том: {{ publication.volume }}</span>
          <span v-if="publication.issue">, Номер: {{ publication.issue }}</span>
        </div>
        <div v-if="publication.pages" class="meta-item">
          <strong>Страницы:</strong> {{ publication.pages }}
        </div>
        <div class="meta-item">
          <strong>Язык:</strong> {{ getLanguageLabel(publication.language) }}
        </div>
        <div v-if="publication.articleId" class="meta-item">
          <strong>ID статьи:</strong> {{ publication.articleId }}
        </div>
        <div v-if="publication.facultyCoauthors" class="meta-item">
          <span class="faculty-coauthors">Соавторы с факультета</span>
        </div>
      </div>

      <div v-if="hasDates" class="publication-dates">
        <h3>Даты:</h3>
        <div class="dates-grid">
          <div v-if="publication.receivedDate" class="date-item">
            <strong>Получена:</strong> {{ formatDate(publication.receivedDate) }}
          </div>
          <div v-if="publication.decisionDate" class="date-item">
            <strong>Принята:</strong> {{ formatDate(publication.decisionDate) }}
          </div>
          <div v-if="publication.publishedDate" class="date-item">
            <strong>Опубликована:</strong> {{ formatDate(publication.publishedDate) }}
          </div>
        </div>
      </div>

      <div v-if="publication.webpage" class="publication-link">
        <h3>Ссылка:</h3>
        <a :href="publication.webpage" target="_blank" rel="noopener noreferrer">
          {{ publication.webpage }}
        </a>
      </div>

      <div v-if="publication.comment" class="publication-comment">
        <h3>Комментарий:</h3>
        <p>{{ publication.comment }}</p>
      </div>
    </div>
    
    <div v-else class="not-found">
      <p>Публикация не найдена</p>
      <button @click="$router.back()" class="back-btn">← Назад</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { publicationsAPI } from '../services/api'

const route = useRoute()
const publication = ref(null)
const loading = ref(true)

const hasDates = computed(() => {
  return publication.value && (
    publication.value.receivedDate || 
    publication.value.decisionDate || 
    publication.value.publishedDate
  )
})
/*
const loadPublication = async (id) => {
  loading.value = true;
  try {
    const response = await publicationsAPI.getById(id)
    publication.value = response.data;
  } catch (error) {
    console.error('Ошибка:', error);
    // Fallback на моковые данные
    publication.value = getMockPublication(id);
  } finally {
    loading.value = false;
  }
}
*/

const loadPublication = async (id) => {
  loading.value = true;
  try {
    // Заглушка для тестирования верстки
    await new Promise(resolve => setTimeout(resolve, 500));
    
    publication.value = {
      id: id,
      type: 'publication',
      title: 'Исследование методов машинного обучения',
      authors: 'Иванов И.И., Петров П.П., Сидоров С.С.',
      authorCount: 3,
      receivedDate: '2024-01-15',
      decisionDate: '2024-02-20',
      publishedDate: '2024-03-10',
      journal: 'Журнал компьютерных наук',
      volume: '15',
      issue: '3',
      articleId: 'DOI:10.1234/abc123',
      pages: '123-145',
      year: '2024',
      language: 'russian',
      webpage: 'https://example.com/article1',
      facultyCoauthors: false,
      comment: 'Важное исследование в области искусственного интеллекта и машинного обучения'
    };
    
  } catch (error) {
    console.error('Ошибка:', error);
  } finally {
    loading.value = false;
  }
}

const getTypeLabel = (type) => {
  const typeLabels = {
    publication: 'Публикация',
    monograph: 'Монография',
    reports: 'Доклад',
    lectures: 'Курс лекций',
    patents: 'Патент',
    supervision: 'Научное руководство',
    editing: 'Редактирование',
    editorial_board: 'Ред. коллегия',
    org_work: 'Научно-орг. работа',
    opposition: 'Оппонирование',
    grants: 'Грант',
    awards: 'Награда'
  }
  return typeLabels[type] || type
}

const getLanguageLabel = (language) => {
  const languageLabels = {
    russian: 'Русский',
    english: 'Английский',
    german: 'Немецкий',
    french: 'Французский',
    other: 'Другой'
  }
  return languageLabels[language] || language
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

onMounted(() => {
  const publicationId = route.params.id
  loadPublication(publicationId)
})
</script>

<style scoped>
.publication-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.back-btn {
  background: none;
  border: none;
  color: #4CAF50;
  cursor: pointer;
  font-size: 16px;
  margin-bottom: 20px;
  padding: 0;
}

.back-btn:hover {
  text-decoration: underline;
}

.publication-content {
  background: white;
  padding: 20px;
  border: 1px solid #ddd;
}

.publication-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.publication-type {
  background-color: #4CAF50;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
}

.publication-year {
  color: #666;
  font-size: 14px;
}

.publication-title {
  color: #333;
  margin: 0 0 15px 0;
  font-size: 20px;
  line-height: 1.3;
}

.publication-meta {
  margin-bottom: 15px;
}

.meta-item {
  margin-bottom: 8px;
  color: #555;
  font-size: 14px;
}

.faculty-coauthors {
  background-color: #ffeb3b;
  color: #333;
  padding: 2px 6px;
  font-size: 11px;
}

.publication-dates,
.publication-link,
.publication-comment {
  margin-bottom: 15px;
}

.publication-dates h3,
.publication-link h3,
.publication-comment h3 {
  color: #333;
  margin-bottom: 8px;
  font-size: 16px;
}

.dates-grid {
  display: grid;
  gap: 8px;
}

.date-item {
  color: #555;
  font-size: 14px;
}

.publication-link a {
  color: #4CAF50;
  text-decoration: none;
  word-break: break-all;
  font-size: 14px;
}

.publication-link a:hover {
  text-decoration: underline;
}

.publication-comment p {
  color: #555;
  line-height: 1.4;
  margin: 0;
  font-size: 14px;
}

.loading, .not-found {
  text-align: center;
  padding: 30px;
  color: #666;
}
</style>
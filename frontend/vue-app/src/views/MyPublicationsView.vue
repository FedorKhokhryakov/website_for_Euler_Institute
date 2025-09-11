<template>
  <div class="all-publications">
    <div class="publications-header">
      <h1>Все публикации</h1>
      <div class="search-controls">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Поиск по названию, авторам..." 
          class="search-input"
        >
        <select v-model="filterType" class="filter-select">
          <option value="">Все типы</option>
          <option value="publication">Публикация</option>
          <option value="monograph">Монография</option>
          <option value="reports">Доклад</option>
          <option value="lectures">Курс лекций</option>
          <option value="patents">Патент</option>
          <option value="supervision">Научное руководство</option>
          <option value="editing">Редактирование</option>
          <option value="editorial_board">Ред. коллегия</option>
          <option value="org_work">Научно-орг. работа</option>
          <option value="opposition">Оппонирование</option>
          <option value="grants">Грант</option>
          <option value="awards">Награда</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <p>Загрузка публикаций...</p>
    </div>

    <div v-else-if="filteredPublications.length === 0" class="no-results">
      <p>Публикации не найдены</p>
    </div>

    <div v-else class="publications-list">
      <div 
        v-for="publication in filteredPublications" 
        :key="publication.id" 
        class="publication-card"
        @click="viewPublication(publication.id)"
      >
        <div class="publication-header">
          <span class="publication-type">{{ getTypeLabel(publication.type) }}</span>
          <span class="publication-year">{{ publication.year }}</span>
        </div>
        
        <h3 class="publication-title">{{ publication.title }}</h3>
        
        <p class="publication-authors">{{ publication.authors }}</p>
        
        <div v-if="publication.journal" class="publication-journal">
          {{ publication.journal }}
          <span v-if="publication.volume || publication.issue">
            ({{ publication.volume }}{{ publication.issue ? '(' + publication.issue + ')' : '' }})
          </span>
        </div>
        
        <div v-if="publication.pages" class="publication-pages">
          Страницы: {{ publication.pages }}
        </div>
        
        <div class="publication-footer">
          <span class="publication-language">Язык: {{ getLanguageLabel(publication.language) }}</span>
        </div>
      </div>
    </div>

    <div v-if="!loading && filteredPublications.length > 0" class="pagination">
      <button 
        @click="prevPage" 
        :disabled="currentPage === 1" 
        class="pagination-btn"
      >
        Назад
      </button>
      <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
      <button 
        @click="nextPage" 
        :disabled="currentPage === totalPages" 
        class="pagination-btn"
      >
        Вперед
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { publicationsAPI } from '../services/api'

const router = useRouter()

const publications = ref([])
const loading = ref(true)
const searchQuery = ref('')
const filterType = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

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

const languageLabels = {
  russian: 'Русский',
  english: 'Английский',
  german: 'Немецкий',
  french: 'Французский',
  other: 'Другой'
}

const filteredPublications = computed(() => {
  let filtered = publications.value;

  if (filterType.value) {
    filtered = filtered.filter(pub => pub.type === filterType.value);
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(pub => 
      pub.title.toLowerCase().includes(query) ||
      pub.authors.toLowerCase().includes(query) ||
      (pub.journal && pub.journal.toLowerCase().includes(query))
    );
  }

  const startIndex = (currentPage.value - 1) * itemsPerPage;
  return filtered.slice(startIndex, startIndex + itemsPerPage);
})

const totalPages = computed(() => {
  const totalItems = publications.value.length;
  return Math.ceil(totalItems / itemsPerPage);
})

onMounted(async () => {
  await loadPublications();
})

watch(searchQuery, () => {
  currentPage.value = 1;
})

watch(filterType, () => {
  currentPage.value = 1;
})

const loadPublications = async () => {
  loading.value = true;
  try {
    const response = await publicationsAPI.getAll()
    console.log("Публикации: ", response.data)
    publications.value = response.data;
  } catch (error) {
    console.error('Ошибка:', error);
  } finally {
    loading.value = false;
  }
}

/*const loadPublications = async () => {
  loading.value = true;
  try {
    // Моковые данные для тестирования
    publications.value = [
      {
        id: 1,
        type: 'publication',
        title: 'Исследование методов машинного обучения',
        authors: 'Иванов И.И., Петров П.П.',
        authorCount: 2,
        journal: 'Журнал компьютерных наук',
        volume: '15',
        issue: '3',
        pages: '123-145',
        year: '2024',
        language: 'russian',
        facultyCoauthors: true,
        receivedDate: '2024-01-15',
        decisionDate: '2024-02-20',
        publishedDate: '2024-03-10',
        articleId: 'DOI:10.1234/abc123',
        webpage: 'https://example.com/article1',
        comment: 'Важное исследование в области ИИ'
      },
      {
        id: 2,
        type: 'monograph',
        title: 'Современные подходы к анализу данных',
        authors: 'Сидоров С.С., Козлов К.К., Новиков Н.Н.',
        authorCount: 3,
        journal: '',
        volume: '',
        issue: '',
        pages: '256',
        year: '2023',
        language: 'english',
        facultyCoauthors: false,
        receivedDate: '',
        decisionDate: '',
        publishedDate: '2023-11-05',
        articleId: '',
        webpage: '',
        comment: 'Монография по Big Data'
      },
      {
        id: 3,
        type: 'reports',
        title: 'Доклад на конференции по веб-разработке',
        authors: 'Алексеев А.А.',
        authorCount: 1,
        journal: 'Труды конференции WebDev 2024',
        volume: '2',
        issue: '1',
        pages: '45-52',
        year: '2024',
        language: 'russian',
        facultyCoauthors: true,
        receivedDate: '2024-02-10',
        decisionDate: '2024-02-28',
        publishedDate: '2024-03-15',
        articleId: 'CONF-2024-001',
        webpage: 'https://conference.org/report123',
        comment: ''
      }
    ];
    
    // Имитация задержки сети
    await new Promise(resolve => setTimeout(resolve, 500));
    
  } catch (error) {
    console.error('Ошибка:', error);
  } finally {
    loading.value = false;
  }
}*/

const viewPublication = (id) => {
  router.push(`/publication/${id}`);
}

const getTypeLabel = (type) => {
  return typeLabels[type] || type;
}

const getLanguageLabel = (language) => {
  return languageLabels[language] || language;
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
}
</script>

<style scoped>
.all-publications {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.publications-header {
  margin-bottom: 30px;
}

.publications-header h1 {
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.search-controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 250px;
  padding: 10px;
  border: 1px solid #ddd;
  font-size: 14px;
}

.filter-select {
  padding: 10px;
  border: 1px solid #ddd;
  font-size: 14px;
  min-width: 150px;
}

.publications-list {
  display: grid;
  gap: 20px;
  margin-bottom: 30px;
}

.publication-card {
  border: 1px solid #e0e0e0;
  padding: 20px;
  cursor: pointer;
  background: white;
}

.publication-card:hover {
  border-color: #4CAF50;
}

.publication-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.publication-type {
  background-color: #4CAF50;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: bold;
}

.publication-year {
  color: #666;
  font-size: 14px;
}

.publication-title {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 18px;
  line-height: 1.4;
}

.publication-authors {
  color: #555;
  margin: 0 0 10px 0;
  font-style: italic;
}

.publication-journal {
  color: #666;
  margin: 0 0 8px 0;
  font-size: 14px;
}

.publication-pages {
  color: #777;
  font-size: 13px;
  margin-bottom: 10px;
}

.publication-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.publication-language {
  color: #888;
  font-size: 12px;
}

.faculty-coauthors {
  background-color: #ffeb3b;
  color: #333;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: bold;
}

.loading, .no-results {
  text-align: center;
  padding: 40px;
  color: #666;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}
</style>
<template>
  <div class="year-report">
    <div v-if="loading" class="loading">
      <p>Загрузка отчета...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="report" class="report-content">
      <div class="all-publications">
        <h1>Публикации</h1>
        <div 
          v-for="publication in publications"
          :key="publication.post.id"
          class="post-card"
        >
          <span class="post-full-title">{{ getFullTitle(publication) }}</span>
          <button class="btn-edit" @click="editPost(publication)" title="Редактировать публикацию">
            ✏️
          </button>
          <button class="btn-delete" @click="deletePost(publication)" title="Удалить публикацию">
            🗑️
          </button>
        </div>
      </div>

      <div class="all-presentations">
        <h1>Доклады</h1>
        <div 
          v-for="presentation in presentations"
          :key="presentation.id"
          class="post-card"
        >
          <span class="post-full-title">{{ getFullTitle(presentation) }}</span>
          <button class="btn-edit" @click="editPost(presentation)" title="Редактировать доклад">
            ✏️
          </button>
          <button class="btn-delete" @click="deletePost(presentation)" title="Удалить доклад">
            🗑️
          </button>
        </div>
      </div>

      <button class="btn-add-post" @click="addPost">
        Добавить новую запись
      </button>

      <div class="science-report">
        <div class="report-text">
          <label for="report_text">Развернутый отчет о полученных результатах:</label>
          <textarea id="report_text" rows="3"></textarea>
        </div>

        <button class="btn-submit" @click="submitReport" title="Отослать отчет на проверку">
            Отослать
        </button>

        <div class="report-status">
          <div class="status-item">
            <strong>Статус отчета:</strong> {{ report_status }}
          </div>
          <div class="admin-comment" v-if="admin_comment">
            <strong>Комментарий админа:</strong> {{ admin_comment }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter} from 'vue-router'
import { publicationsAPI } from '../services/api'

const route = useRoute()
const router = useRouter()

const year = computed(() => route.params.year)
const report = ref(null)
const loading = ref(true)
const error = ref('')
const report_status = ref('')
const admin_comment = ref('')

const publications = computed(() => {
  return report.value?.posts?.filter(post => post.post.type === 'publication') || []
})

const presentations = computed(() => {
  return report.value?.posts?.filter(post => post.post.type === 'presentation') || []
})

onMounted(async () => {
  await loadYearReport();
})

watch(year, async (newYear) => {
  if (newYear) {
    await loadYearReport();
  }
})

const loadYearReport = async () => {
  loading.value = true;
  try {
    const response = await publicationsAPI.getYearReport(year.value)
    report.value = response.data;
    console.log(report.value);
    if (report.value.year_report) {
      report_status.value = report.value.year_report.status
      admin_comment.value = report.value.year_report.admin_comment
    }
  } catch (err) {
    console.error('Ошибка:', err);
    error.value = 'Не удалось загрузить отчет'
  } finally {
    loading.value = false;
  }
}

const getFullTitle = (post) => {
  const title = post.details?.title || post.post?.id || 'Без названия'
  
  if (post.post.type !== 'publication') {
    return title
  }
  
  const status = getPublicationStatusForYear(post.details, parseInt(year.value))
  
  const statusText = getStatusText(status)
  return `${title} (${statusText})`
}

const getPublicationStatusForYear = (publication, reportYear) => {
  const dates = {
    preprint: publication.preprint_date ? new Date(publication.preprint_date).getFullYear() : null,
    submitted: publication.submission_date ? new Date(publication.submission_date).getFullYear() : null,
    accepted: publication.acceptance_date ? new Date(publication.acceptance_date).getFullYear() : null,
    published: publication.publication_date ? new Date(publication.publication_date).getFullYear() : null
  }
  
  if (dates.published && dates.published <= reportYear) {
    return 'published'
  }
  if (dates.accepted && dates.accepted <= reportYear) {
    return 'accepted'
  }
  if (dates.submitted && dates.submitted <= reportYear) {
    return 'submitted'
  }
  if (dates.preprint && dates.preprint <= reportYear) {
    return 'preprint'
  }
  
  return publication.current_status || 'preprint'
}

const getStatusText = (status) => {
  const statusMap = {
    'preprint': 'Препринт',
    'submitted': 'Направлена на публикацию', 
    'accepted': 'Принята к публикации',
    'published': 'Опубликована'
  }
  return statusMap[status] || status
}

const editPost = (post) => {
  router.push(`/posts/edit/${post.post.id}`)
}

const deletePost = async (post) => {
  if (confirm(`Вы уверены, что хотите удалить "${getFullTitle(post)}"?`)) {
    try {
      await publicationsAPI.deletePost(post.post.id)
      await loadYearReport()
    } catch (err) {
      console.error('Ошибка удаления:', err)
      alert('Не удалось удалить запись')
    }
  }
}

const addPost = () => {
  router.push('/posts/create/')
}

const submitReport = () => {
}
</script>

<style scoped>
.year-report {
  padding: 1rem;
  max-width: 1000px;
  margin: 0 auto;
}

.loading, .error-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.error-state {
  color: var(--color-secondary);
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.all-publications, .all-presentations {
  padding: 1rem;
  margin-bottom: -1rem
}

.all-publications h1, .all-presentations h1 {
  color: var(--color-text-primary);
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.post-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  margin-bottom: 0.5rem;
}

.post-full-title {
  flex: 1;
  font-size: 1rem;
  color: var(--color-text-primary);
}

.btn-edit, .btn-delete {
  background: none;
  border: 1px solid var(--color-border);
  cursor: pointer;
  padding: 0.5rem;
  margin-left: 0.5rem;
  font-size: 1rem;
}

.btn-edit:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-delete:hover {
  color: var(--color-secondary);
  border-color: var(--color-secondary);
}

.btn-add-post {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 0.5rem;
}

.btn-add-post:hover {
  background-color: var(--color-primary-dark);
}

.science-report {
  padding: 1rem;
}

.report-text {
  margin-bottom: 1rem;
}

.report-text label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.report-text textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.btn-submit {
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.btn-submit:hover {
  background-color: var(--color-primary-dark);
}

.report-status {
  padding: 0.75rem;
  background-color: var(--color-surface);
}

.status-item {
  margin-bottom: 0.5rem;
}

.admin-comment {
  border-top: 1px solid var(--color-border);
  padding-top: 0.5rem;
}
</style>
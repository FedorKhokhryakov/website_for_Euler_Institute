<template>
  <div class="year-report">
    <div v-if="loading" class="loading">
      <p>Загрузка отчета...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="report" class="report-content">
      <div class="content-section">
        <div class="all-publications">
          <h1 class="section-title">Публикации</h1>
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
          <div v-if="publications.length === 0" class="empty-state">
            Нет публикаций
          </div>
          <button class="btn-add-post" @click="addPublication">
            Добавить публикацию
          </button>
        </div>

        <div class="all-presentations">
          <h1 class="section-title">Доклады</h1>
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
          <div v-if="presentations.length === 0" class="empty-state">
            Нет докладов
          </div>
          <button class="btn-add-post" @click="addPresentation">
            Добавить доклад
          </button>
        </div>
      </div>

      <div class="science-report">
        <div class="report-field">
          <label for="external_publications">Внешние публикации:</label>
          <textarea 
            id="external_publications" 
            v-model="external_publications"
            rows="2"
          ></textarea>
        </div>
        <div class="report-fields">
          <div class="report-field">
            <label for="short_report_text">Краткий отчет:</label>
            <textarea 
              id="short_report_text" 
              v-model="short_report_text"
              rows="2"
              :disabled="isTextareaDisabled"
            ></textarea>
          </div>

          <div class="report-field">
            <label for="report_text">Развернутый отчет о полученных результатах:</label>
            <textarea 
              id="report_text" 
              v-model="report_text"
              rows="3"
              :disabled="isTextareaDisabled"
            ></textarea>
          </div>
        </div>

        <button 
          class="btn-submit" 
          @click="saveReport" 
          title="Сохранить научный отчет"
        >
          Сохранить
        </button>

        <button 
          v-if="showUserSubmitButton"
          class="btn-submit" 
          @click="signReport" 
          title="Отослать отчет на проверку"
        >
          Подписать
        </button>

        <div v-if="showAdminControls" class="admin-controls">
          <div class="admin-comment-input">
            <label for="admin_comment_input">Комментарий администратора:</label>
            <textarea 
              id="admin_comment_input" 
              v-model="admin_comment_input"
              rows="2"
              placeholder="Введите комментарий для пользователя..."
            ></textarea>
          </div>
          <div class="admin-buttons">
            <button 
              class="btn-reject" 
              @click="rejectReport"
              title="Вернуть отчет на доработку"
            >
              Отклонить
            </button>
          </div>
        </div>

        <div class="report-status">
          <div class="status-item">
            <strong>Статус отчета:</strong> {{ getReportStatus(report_status) }}
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
import { publicationsAPI, adminAPI, reportAPI} from '../services/api'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const year = computed(() => route.params.year)
const report = ref(null)
const loading = ref(true)
const error = ref('')
const report_text = ref('')
const short_report_text = ref('')
const external_publications = ref('')
const report_status = ref('')
const admin_comment = ref('')
const admin_comment_input = ref('')

const isAdminReviewing = computed(() => {
  return (authStore.isImpersonating || authStore.isAdmin) && report_status.value === 'signed'
})

const isTextareaDisabled = computed(() => {
  return report_status.value === 'signed' ||
         isAdminReviewing.value
})

const showUserSubmitButton = computed(() => {
  return report_status.value === 'wip'
})

const showAdminControls = computed(() => {
  return isAdminReviewing.value
})

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
    if (report.value.year_report) {
      report_text.value = report.value.year_report.report_text
      short_report_text.value = report.value.year_report.short_report_text
      external_publications.value = report.value.year_report.external_publications
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
    online_first: publication.online_first_publication_date ? new Date(publication.online_first_publication_date).getFullYear() : null,
    published: publication.publication_date ? new Date(publication.publication_date).getFullYear() : null
  }
  
  if (dates.published && dates.published <= reportYear) {
    return 'published'
  }
  if (dates.online_first && dates.online_first <= reportYear) {
    return 'online_first'
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
    'submitted': 'Направлена в журнал', 
    'accepted': 'Принята к публикации',
    'online_first': 'Опубликована online-first',
    'published': 'Опубликована'
  }
  return statusMap[status] || status
}

const getReportStatus = (status) => {
  return status === "wip" ? "В работе" : "Подписан"
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

const addPublication = () => {
  router.push('/posts/create?type=publication')
}

const addPresentation = () => {
}

const saveReport = async () => {
  try {
    const requestData = {
      report_text: report_text.value,
      short_report_text: short_report_text.value,
      external_publications: external_publications.value
    }

    await reportAPI.saveReport(year.value, requestData)
    alert('Отчет успешно сохранен')
  } catch (err) {
    console.error('Ошибка сохранения:', err)
    alert('Не удалось сохранить отчет')
  }
}

const signReport = async () => {
  if (confirm(`Вы уверены, что хотите подписать отчет?`)) {
    try {
      const requestData = {
        report_text: report_text.value,
        short_report_text: short_report_text.value,
        external_publications: external_publications.value
      }

      await reportAPI.signReport(year.value, requestData)
      await loadYearReport()
      alert('Отчет успешно подписан')
    } catch (err) {
      console.error('Ошибка подписания:', err)
      alert('Не удалось подписать отчет')
    }
  }
}

const rejectReport = async () => {
  if (confirm(`Вы уверены, что хотите отклонить отчет?`)) {
    try {
      const requestData = {
        new_status: 'wip',
        admin_comment: admin_comment_input.value
      }

      const targetUserId = authStore.user?.id
      await adminAPI.sendReportToRework(targetUserId, year.value, requestData)
      await loadYearReport()
    } catch (err) {
      console.error('Ошибка отклонения отчета:', err)
      alert('Не удалось отклонить отчет')
    }
  }
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
  gap: 1.5rem;
}

.content-section {
  background-color: var(--color-surface);
  padding: 1.5rem;
}

.all-publications, .all-presentations {
  margin-bottom: 2rem;
}

.all-publications:last-child, .all-presentations:last-child {
  margin-bottom: 0;
}

.section-title {
  color: var(--color-text-primary);
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
  text-align: center;
}

.post-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  margin-bottom: 0.5rem;
  background-color: var(--color-surface);
}

.post-full-title {
  flex: 1;
  font-size: 1rem;
  color: var(--color-text-primary);
}

.btn-edit, .btn-delete {
  background: none;
  border: 2px solid var(--color-border);
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

.empty-state {
  text-align: center;
  padding: 1rem;
  color: var(--color-text-secondary);
  font-style: italic;
  border: 2px dashed var(--color-border);
  margin-bottom: 0.5rem;
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
  background-color: var(--color-surface);
  padding: 1.5rem;
}

.report-fields {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.report-field {
  margin-bottom: 1rem;
}

.report-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.report-field textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
  background-color: var(--color-background);
}

.report-field textarea:disabled {
  background-color: var(--color-surface-dark);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.btn-submit {
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 1rem;
  margin-right: 0.75rem;
}

.btn-submit:hover {
  background-color: var(--color-primary-dark);
}

.admin-controls {
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-surface-dark);
}

.admin-comment-input {
  margin-bottom: 1rem;
}

.admin-comment-input label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.admin-comment-input textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
  background-color: var(--color-background);
}

.admin-buttons {
  display: flex;
  gap: 1rem;
}

.btn-reject {
  background-color: var(--color-secondary);
  color: var(--color-text-light);
  border: none;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  font-size: 1rem;
  flex: 1;
}

.btn-reject:hover {
  background-color: var(--color-secondary-dark);
}

.btn-approve {
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  font-size: 1rem;
  flex: 1;
}

.btn-approve:hover {
  background-color: var(--color-primary-dark);
}

.report-status {
  padding: 0.75rem;
  background-color: var(--color-surface-dark);
  border: 1px solid var(--color-border);
}

.status-item {
  margin-bottom: 0.5rem;
}

.admin-comment {
  border-top: 1px solid var(--color-border);
  padding-top: 0.5rem;
}
</style>
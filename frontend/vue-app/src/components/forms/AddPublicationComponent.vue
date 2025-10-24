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
        <label>Соавторы с инст. Эйлера:</label>
        <div class="authors-container">
          <div v-for="(authorId, index) in formData.internal_authors_list" :key="index" class="author-input">
            <div class="searchable-select">
              <input
                type="text"
                v-model="searchQueries[index]"
                :placeholder="`Начните вводить...`"
                class="form-select search-input"
                @focus="openDropdown(index)"
                @input="handleSearchInput(index)"
              />
              <div v-if="activeDropdownIndex === index && filteredUsers(index).length > 0" class="dropdown">
                <div
                  v-for="user in filteredUsers(index)"
                  :key="user.id"
                  class="dropdown-item"
                  @click="selectInternalAuthor(index, user)"
                >
                  {{ getUserDisplayName(user) }}
                </div>
              </div>
              <div v-if="activeDropdownIndex === index && filteredUsers(index).length === 0" class="dropdown">
                <div class="dropdown-item no-results">
                  Сотрудники не найдены
                </div>
              </div>
            </div>
            <button type="button" @click="removeInternalAuthor(index)" class="btn-remove">×</button>
          </div>
          <button type="button" @click="addInternalAuthor" class="btn-add-author">
            + Добавить соавтора
          </button>
          <label class="text-hint"> Не нужно пытаться добавить себя! Вы будете автоматически добавлены в публикацию как автор.</label>
        </div>
      </div>

      <div class="form-row">
        <label>Иные соавторы:</label>
        <div class="authors-container">
          <div v-for="(author, index) in formData.external_authors_list" :key="index" class="author-input">
            <input 
              type="text" 
              v-model="formData.external_authors_list[index]" 
              :placeholder="`И.О. Фамилия`"
            >
            <button type="button" @click="removeExternalAuthor(index)" class="btn-remove">×</button>
          </div>
          <button type="button" @click="addExternalAuthor" class="btn-add-author">+ Добавить соавтора</button>
        </div>
      </div>
    
      <div class="checkbox-row">
        <label>Направлено в журнал: </label>
        <div class="checkbox-section">
          <input type="checkbox" v-model="showSubmissionFields">
        </div>
      </div>
    </div>

    <div v-if="showSubmissionFields" class="form-section">
      <h3>Данные об отправке в журнал</h3>
      
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
      <h3>Данные о принятии статьи</h3>
      
      <div class="form-row">
        <label for="acceptance_date">Дата принятия:</label>
        <input type="date" id="acceptance_date" v-model="formData.acceptance_date">
      </div>

      <div class="checkbox-row">
        <label>Опубликовано (online-first): </label>
        <div class="checkbox-section">
          <input type="checkbox" v-model="showOnlineFirstFields">
        </div>
      </div>
    </div>

    <div v-if="showOnlineFirstFields" class="form-section">
      <h3>Данные о публикации (online-first)</h3>
      
      <div class="form-row">
        <label for="online_first_date">Дата онлайн-публикации:</label>
        <input type="date" id="online_first_date" v-model="formData.online_first_date">
      </div>

      <div class="form-row">
        <label for="doi">DOI:</label>
        <input type="text" id="doi" v-model="formData.doi">
      </div>

      <div class="checkbox-row">
        <label>Опубликовано в печатной версии: </label>
        <div class="checkbox-section">
          <input type="checkbox" v-model="showPublicationFields">
        </div>
      </div>
    </div>

    <div v-if="showPublicationFields" class="form-section">
      <h3>Данные о публикации в печатной версии</h3>
      
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
            <input type="text" v-model="formData.journal_pages_or_article_number" placeholder="Страницы">
          </div>
        </div>
      </div>

      <div class="form-row">
        <label for="journal_level">Уровень журнала:</label>
        <input type="text" id="journal_level" v-model="formData.journal_level" placeholder="Ссылка на уровень журнала в Белом списке">
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed, nextTick, onMounted, onUnmounted} from 'vue'
import { usersAPI } from '../../services/api.js'
import { useAuthStore } from '../../stores/auth'

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
const showOnlineFirstFields = ref(false)
const showPublicationFields = ref(false)
const isUpdating = ref(false)
const availableUsers = ref([])
const isLoadingUsers = ref(false)
const authStore = useAuthStore()
const activeDropdownIndex = ref(-1)
const searchQueries = ref([''])

const currentStatus = computed(() => {
  if (showPublicationFields.value) return 'published'
  if (showOnlineFirstFields.value) return 'online_first'
  if (showAcceptanceFields.value) return 'accepted'
  if (showSubmissionFields.value) return 'submitted'
  return 'preprint'
})

const filteredUsers = (index) => {
  const query = searchQueries.value[index] || ''
  if (!query.trim()) {
    return availableUsers.value.filter(user => 
      !isUserSelected(user.id) || formData.internal_authors_list[index] === user.id
    )
  }
  
  const searchTerm = query.toLowerCase()
  return availableUsers.value.filter(user => {
    const userName = getUserDisplayName(user).toLowerCase()
    const isAvailable = !isUserSelected(user.id) || formData.internal_authors_list[index] === user.id
    return isAvailable && userName.includes(searchTerm)
  })
}

const openDropdown = (index) => {
  activeDropdownIndex.value = index
  while (searchQueries.value.length <= index) {
    searchQueries.value.push('')
  }
  
  const currentUserId = formData.internal_authors_list[index]
  if (currentUserId) {
    const currentUser = availableUsers.value.find(user => user.id === currentUserId)
    if (currentUser) {
      searchQueries.value[index] = getUserDisplayName(currentUser)
    }
  }
}

const handleSearchInput = (index) => {
  activeDropdownIndex.value = index
}

const selectInternalAuthor = (index, user) => {
  formData.internal_authors_list[index] = user.id
  searchQueries.value[index] = getUserDisplayName(user)
  activeDropdownIndex.value = -1
}

const addInternalAuthor = () => {
  formData.internal_authors_list.push('')
  searchQueries.value.push('')
}

const removeInternalAuthor = (index) => {
  if (formData.internal_authors_list.length > 0) {
    formData.internal_authors_list.splice(index, 1)
    searchQueries.value.splice(index, 1)
  }
}

const isUserSelected = (userId) => {
  return formData.internal_authors_list.includes(userId) && userId !== ''
}

const getUserDisplayName = (user) => {
  const parts = []
  if (user.second_name_rus) parts.push(user.second_name_rus)
  if (user.first_name_rus) parts.push(user.first_name_rus)
  if (user.middle_name_rus) parts.push(user.middle_name_rus)
  return parts.join(' ') || user.username
}

const formData = reactive({
  title: '',
  language: '',
  preprint_date: '',
  preprint_number: '',
  external_authors_list: [],
  internal_authors_list: [], 
  
  submission_date: '',
  journal_name: '',
  journal_issn: '',
  
  acceptance_date: '',
  
  online_first_date: '',
  doi: '',
  
  publication_date: '',
  journal_volume: null,
  journal_number: null,
  journal_pages_or_article_number: '',
  journal_level: '',

  current_status: 'preprint'
})

const initializeSearchQueries = () => {
  searchQueries.value = formData.internal_authors_list.map(userId => {
    const user = availableUsers.value.find(u => u.id === userId)
    return user ? getUserDisplayName(user) : ''
  })
  
  if (searchQueries.value.length === 0) {
    searchQueries.value = ['']
  }
}

const loadAvailableUsers = async () => {
  try {
    isLoadingUsers.value = true

    const response = await usersAPI.getAllUsers()

    const filteredUsers = response.data.users.filter(user =>
      user.id !== authStore.user?.id
    )
  

    availableUsers.value = filteredUsers || []

    initializeSearchQueries()

  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
    availableUsers.value = []
  } finally {
    isLoadingUsers.value = false
  }
}

const prepareFormData = () => {
  const cleanedData = { ...formData }
  
  const dateFields = ['submission_date', 'acceptance_date', 'online_first_date', 'publication_date']
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
  
  cleanedData.external_authors_list = cleanedData.external_authors_list.filter(author => author.trim() !== '')
  
  cleanedData.internal_authors_list = cleanedData.internal_authors_list.filter(id => id !== '')
  
  return cleanedData
}

const addExternalAuthor = () => {
  formData.external_authors_list.push('')
}

const removeExternalAuthor = (index) => {
  if (formData.external_authors_list.length > 0) {
    formData.external_authors_list.splice(index, 1)
  }
}

const handleClickOutside = (event) => {
  const searchContainers = document.querySelectorAll('.searchable-select')
  let isInside = false
  searchContainers.forEach(container => {
    if (container.contains(event.target)) {
      isInside = true
    }
  })
  if (!isInside) {
    activeDropdownIndex.value = -1
  }
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
    showOnlineFirstFields.value = false
    formData.acceptance_date = ''
  }
})

watch(showOnlineFirstFields, (newValue) => {
  if (!newValue) {
    showPublicationFields.value = false
    formData.online_first_date = ''
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
    showSubmissionFields.value = status === 'submitted' || status === 'accepted' || status === 'online_first' || status === 'published'
    showAcceptanceFields.value = status === 'accepted' || status === 'online_first' || status === 'published'
    showOnlineFirstFields.value = status === 'online_first' || status === 'published'
    showPublicationFields.value = status === 'published'
  }

  Object.keys(formData).forEach(key => {
    if (newValue[key] !== undefined && formData[key] !== newValue[key]) {
      if (key === 'internal_authors_list' && Array.isArray(newValue[key])) {
        formData[key] = newValue[key].filter(id => id !== authStore.user?.id)
        nextTick(() => {
          initializeSearchQueries()
        })
      } else {
        formData[key] = newValue[key]
      }
    }
  })
  
  if (!Array.isArray(formData.internal_authors_list)) {
    formData.internal_authors_list = []
    searchQueries.value = ['']
  }

  nextTick(() => {
    isUpdating.value = false
  })
}, { immediate: true })

onMounted(() => {
  loadAvailableUsers()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
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

.form-section h3 {
  color: var(--color-primary);
  margin-bottom: 1rem;
  text-align: center;
}

.form-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  align-items: start;
  margin-bottom: 1rem;
}

.form-row label {
  font-weight: 600;
  text-align: right;
  margin-top: 0.5rem;
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

.author-input select {
  flex: 1;
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

.btn-remove:hover {
  background: var(--color-secondary-dark);
}

.btn-add-author {
  background: none;
  border: 1px dashed var(--color-border);
  padding: 0.5rem;
  cursor: pointer;
  color: var(--color-primary);
}

.btn-add-author:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

select option:disabled {
  color: #999;
  background-color: #f5f5f5;
}

.searchable-select {
  position: relative;
  flex: 1;
  width: 100%;
}

.search-input {
  width: 100%;
  box-sizing: border-box;
}

.text-hint {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
  font-style: italic;
}

.no-results {
  color: var(--color-text-secondary);
  font-style: italic;
  cursor: default;
}

.no-results:hover {
  background-color: transparent;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-top: none;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-item {
  padding: 0.5rem;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
}

.dropdown-item:hover {
  background-color: var(--color-hover);
}

.dropdown-item:last-child {
  border-bottom: none;
}
</style>
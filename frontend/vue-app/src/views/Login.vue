<template>
  <div class="flex items-center justify-center">
    <div class="bg-grey-100 p-6 rounded-2xl shadow-md w-96">
      <h2 class="text-2xl font-bold mb-4 text-center">Вход</h2>

      <form @submit.prevent="loginUser">
        <div class="mb-4">
          <label class="block text-sm mb-1">Email</label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full p-2 border rounded-lg"
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm mb-1">Пароль</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full p-2 border rounded-lg"
          />
        </div>

        <button
          type="submit"
          class="w-full bg-green-500 text-white p-2 rounded-lg hover:bg-green-800 transition"
        >
          Войти
        </button>
      </form>

      <p v-if="error" class="text-red-500 mt-3 text-center">
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"
import { useAuthStore } from "../stores/auth"

const email = ref("")
const password = ref("")
const error = ref("")
const router = useRouter()
const authStore = useAuthStore()

const loginUser = async () => {
  try {

    if (!email.value || !password.value) {
      error.value = "Заполните все поля"
      return
    }
    
    if (!email.value.includes('@')) {
      error.value = "Введите корректный email"
      return
    }

    const response = await axios.post("http://localhost:8000/api/login/", {
      email: email.value,
      password: password.value
    })

    authStore.setToken(response.data.token)

    router.push("/main")

  } catch (err) {
    if (err.response?.status === 400) {
      error.value = "Неверный email или пароль"
    } else if (err.response?.status === 500) {
      error.value = "Ошибка сервера"
    } else {
      error.value = "Ошибка соединения"
    }
  }
}
</script>


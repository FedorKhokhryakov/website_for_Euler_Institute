<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const showAuthButton = computed(() => {
  return route.path !== '/login'
})

const authButtonConfig = computed(() => {
  if (authStore.isAuthenticated) {
    return {
      text: 'Личный кабинет',
      link: '/account',
    }
  } else {
    return {
      text: 'Войти',
      link: '/login', 
    }
  }
})
</script>

<template>
	<div>
		<header class="bg-green-700 text-white shadow-lg sticky top-0 z-50">
		  <div class="container mx-auto px-4 py-3">
			<div class="flex justify-between items-center">
			  <div class="flex items-center space-x-3">
				<div class="bg-white p-2 rounded-full flex items-center justify-center shadow-md">
				  <img 
					src="./assets/logo.png" 
					alt="Logo" 
					class="h-8 w-8 object-contain"
				  />
				</div>
				<span class="text-xl font-bold">Институт им. Эйлера</span>
			  </div>


			  <router-link v-if="showAuthButton" :to=authButtonConfig.link>
				<button class="bg-white text-green-900 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition-all">
				   {{ authButtonConfig.text }}
				</button>
			  </router-link>
			</div>
		  </div>
		</header>	
		<main class="container mx-auto px-4 py-6">
			<router-view />
		</main>
	</div>
</template>


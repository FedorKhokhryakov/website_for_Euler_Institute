<template>
  <div id="app" :class="{ 'with-impersonation': isImpersonating }">
    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { isImpersonating } = storeToRefs(authStore)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  font-size: 14px;
  line-height: 1.4;
  color: #333;
  background-color: #fff;
}

#app {
  min-height: 100vh;
}

#app.with-impersonation {
  padding-top: 30px;
}
</style>
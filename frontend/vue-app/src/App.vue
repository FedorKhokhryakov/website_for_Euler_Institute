<template>
  <router-view />
</template>

<script setup>
// App.vue не содержит логики, только отображает текущий роут
// Вся логика маршрутизации и аутентификации находится в router/index.js
</script>

<style>
/* Глобальные стили */
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

</style>
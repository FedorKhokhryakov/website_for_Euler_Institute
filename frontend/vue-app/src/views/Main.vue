<template>
    {{ authStore.isAuthenticated() }}
</template>

<script setup>
import { useAuthStore } from "../stores/auth"

const authStore = useAuthStore()
</script>
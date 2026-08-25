<script setup lang="ts">
import { Activity } from "lucide-vue-next";
import { computed } from "vue";
import { RouterView } from "vue-router";

import { publicConfig } from "./config";

const heading = computed(() => publicConfig.title || "Super AI 骨架");
</script>

<template>
  <main class="shell">
    <header>
      <Activity :size="20" aria-hidden="true" />
      <h1>{{ heading }}</h1>
    </header>
    <RouterView />
  </main>
</template>

<style scoped>
.shell {
  font-family: sans-serif;
  max-width: 720px;
  margin: 2rem auto;
  padding: 0 1rem;
}

header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>

<script setup lang="ts">
import DOMPurify from "dompurify";
import { marked } from "marked";
import { computed } from "vue";

import { publicConfig } from "../config";

const html = computed(() => {
  const markdown = [
    "这是桌面 Web 骨架页面。",
    "",
    `- API 基址：\`${publicConfig.apiBaseUrl || "未配置"}\``,
    "",
    "认证、聊天、知识库、AIOps、MCP 尚未实现。",
  ].join("\n");
  return DOMPurify.sanitize(String(marked.parse(markdown)));
});
</script>

<template>
  <section v-html="html"></section>
</template>

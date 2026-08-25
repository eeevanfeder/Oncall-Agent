import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [vue()],
  define: {
    __SUPER_AI_PUBLIC_CONFIG__: JSON.stringify({
      title: "test-title",
      apiBaseUrl: "http://127.0.0.1:8000",
      analyticsPublicKey: "",
    }),
  },
  test: {
    environment: "node",
    include: ["tests/**/*.spec.ts"],
  },
});

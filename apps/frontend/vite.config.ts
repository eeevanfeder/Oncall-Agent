import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

import { extractPublicFrontendConfig, loadMergedConfig } from "./config-loader";

const publicConfig = extractPublicFrontendConfig(loadMergedConfig());

export default defineConfig({
  plugins: [vue()],
  define: {
    __SUPER_AI_PUBLIC_CONFIG__: JSON.stringify(publicConfig),
  },
});

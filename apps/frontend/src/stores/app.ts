import { defineStore } from "pinia";

import { publicConfig } from "../config";

export const useAppStore = defineStore("app", {
  state: () => ({
    title: publicConfig.title,
    apiBaseUrl: publicConfig.apiBaseUrl,
  }),
});

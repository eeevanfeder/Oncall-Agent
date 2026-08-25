/// <reference types="vite/client" />

declare const __SUPER_AI_PUBLIC_CONFIG__: {
  title: string;
  apiBaseUrl: string;
  analyticsPublicKey: string;
};

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<object, object, unknown>;
  export default component;
}

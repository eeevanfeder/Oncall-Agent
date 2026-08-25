export type PublicFrontendConfig = {
  title: string;
  apiBaseUrl: string;
  analyticsPublicKey: string;
};

export const publicConfig: PublicFrontendConfig = __SUPER_AI_PUBLIC_CONFIG__;

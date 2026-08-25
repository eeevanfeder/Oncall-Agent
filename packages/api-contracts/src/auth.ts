export type AuthUser = {
  id: string;
  email: string;
  createdAt: string;
};

export type AuthRegisterRequest = {
  email: string;
  password: string;
};

export type AuthLoginRequest = {
  email: string;
  password: string;
};

export type AuthLoginResponse = {
  accessToken: string;
  user: AuthUser;
};

export type AuthLogoutResponse = Record<string, never>;

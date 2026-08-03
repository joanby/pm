export const AUTH_STORAGE_KEY = "pm-mvp-auth";
export const AUTH_USERNAME_KEY = "pm-mvp-username";
export const MVP_USER = "user";
export const MVP_PASSWORD = "password";

export function validateCredentials(username: string, password: string): boolean {
  return username === MVP_USER && password === MVP_PASSWORD;
}

export function isSessionActive(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  return window.localStorage.getItem(AUTH_STORAGE_KEY) === "1";
}

export function getSessionUsername(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(AUTH_USERNAME_KEY);
}

export function setSessionActive(active: boolean, username?: string): void {
  if (typeof window === "undefined") {
    return;
  }
  if (active && username) {
    window.localStorage.setItem(AUTH_STORAGE_KEY, "1");
    window.localStorage.setItem(AUTH_USERNAME_KEY, username);
    return;
  }
  window.localStorage.removeItem(AUTH_STORAGE_KEY);
  window.localStorage.removeItem(AUTH_USERNAME_KEY);
}

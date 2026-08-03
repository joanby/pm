export const AUTH_STORAGE_KEY = "pm-mvp-auth";
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

export function setSessionActive(active: boolean): void {
  if (typeof window === "undefined") {
    return;
  }
  if (active) {
    window.localStorage.setItem(AUTH_STORAGE_KEY, "1");
  } else {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
  }
}

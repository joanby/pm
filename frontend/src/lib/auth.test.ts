import { beforeEach, describe, expect, it } from "vitest";
import {
  AUTH_STORAGE_KEY,
  isSessionActive,
  setSessionActive,
  validateCredentials,
} from "@/lib/auth";

describe("auth", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("accepts the official MVP credentials", () => {
    expect(validateCredentials("user", "password")).toBe(true);
  });

  it("rejects invalid credentials", () => {
    expect(validateCredentials("wrong", "password")).toBe(false);
    expect(validateCredentials("user", "wrong")).toBe(false);
  });

  it("tracks session state in localStorage", () => {
    expect(isSessionActive()).toBe(false);
    setSessionActive(true);
    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBe("1");
    expect(isSessionActive()).toBe(true);
    setSessionActive(false);
    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBeNull();
    expect(isSessionActive()).toBe(false);
  });
});

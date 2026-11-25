import { test, expect } from "@playwright/test";

test("login and logout flow", async ({ page }) => {
  await page.goto("http://localhost:8000/");

  // Verify login form is shown
  const usernameInput = page.locator("input#username");
  const passwordInput = page.locator("input#password");
  const submitButton = page.locator("button[type='submit']");

  await expect(usernameInput).toBeVisible();
  await expect(passwordInput).toBeVisible();
  await expect(submitButton).toContainText("Iniciar sesión");

  // The login screen must not leak the seeded admin credentials.
  await expect(page.getByText(/usuario \/ contraseña/i)).toHaveCount(0);

  // Fill in credentials
  await usernameInput.fill("usuario");
  await passwordInput.fill("contraseña");

  // Submit login
  await submitButton.click();

  // Wait for Kanban board to appear
  await expect(page.locator("text=Kanban Studio")).toBeVisible({ timeout: 5000 });

  // Verify logout button is present
  const logoutButton = page.locator("button:has-text('Cerrar sesión')");
  await expect(logoutButton).toBeVisible();

  // Click logout
  await logoutButton.click();

  // Verify we're back to login form
  await expect(usernameInput).toBeVisible({ timeout: 5000 });
});

test("a new user can register from the login screen and reach the board", async ({ page }) => {
  const username = `e2e_register_${Date.now()}`;

  await page.goto("http://localhost:8000/");
  await page.getByRole("button", { name: "Regístrate" }).click();

  await page.locator("input#username").fill(username);
  await page.locator("input#displayName").fill("Usuario Registrado");
  await page.locator("input#password").fill("clave-e2e-segura");
  await page.getByRole("button", { name: "Crear cuenta" }).click();

  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible({ timeout: 5000 });
  // A newly registered member should not see the admin-only user management entry point.
  await expect(page.getByRole("button", { name: "Gestionar usuarios" })).toHaveCount(0);
});

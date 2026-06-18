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

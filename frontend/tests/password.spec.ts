import { expect, test } from "@playwright/test";

test("a user can change their own password and log in with the new one", async ({ page }) => {
  const username = `e2e_password_${Date.now()}`;
  const oldPassword = "clave-original-segura";
  const newPassword = "clave-nueva-segura";

  // Register a throwaway user so we never touch the seeded admin's credentials.
  await page.goto("http://localhost:8000/");
  await page.getByRole("button", { name: "Regístrate" }).click();
  await page.locator("input#username").fill(username);
  await page.locator("input#displayName").fill("Usuario Cambia Clave");
  await page.locator("input#password").fill(oldPassword);
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible({ timeout: 5000 });

  await page.getByRole("button", { name: "Cambiar contraseña" }).click();
  await page.getByLabel("Contraseña actual").fill(oldPassword);
  await page.getByLabel("Nueva contraseña", { exact: true }).fill(newPassword);
  await page.getByLabel("Confirmar nueva contraseña").fill(newPassword);
  await page.getByRole("button", { name: "Guardar nueva contraseña" }).click();
  await expect(page.getByText(/actualizada correctamente/i)).toBeVisible();
  await page.getByRole("button", { name: "Cerrar", exact: true }).click();

  await page.getByRole("button", { name: "Cerrar sesión" }).click();
  await expect(page.locator("input#username")).toBeVisible();

  await page.locator("input#username").fill(username);
  await page.locator("input#password").fill(newPassword);
  await page.locator("button[type='submit']").click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible({ timeout: 5000 });
});

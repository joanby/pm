import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.locator("input#username").fill("usuario");
  await page.locator("input#password").fill("contraseña");
  await page.locator("button[type='submit']").click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
});

test("admin can open user management and create a user", async ({ page }) => {
  const username = `e2e_${Date.now()}`;

  await page.getByRole("button", { name: "Gestionar usuarios" }).click();
  await expect(page.getByRole("heading", { name: "Gestión de usuarios" })).toBeVisible();

  await page.getByLabel("Nombre de usuario").fill(username);
  await page.getByLabel("Nombre visible").fill("Usuario E2E");
  await page.getByLabel("Contraseña").fill("clave-e2e-segura");
  await page.getByTestId("add-user-button").click();

  const userRow = page.getByTestId("user-list").locator("li").filter({ hasText: `@${username}` });
  await expect(userRow).toBeVisible();

  await userRow.getByRole("button", { name: "Eliminar" }).click();
  await expect(page.getByTestId("user-list").locator("li").filter({ hasText: `@${username}` })).toHaveCount(0);
});

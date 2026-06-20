import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.locator("input#username").fill("usuario");
  await page.locator("input#password").fill("contraseña");
  await page.locator("button[type='submit']").click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
});

test("creates, switches between, and deletes boards", async ({ page }) => {
  const boardName = `Tablero E2E ${Date.now()}`;

  await page.getByRole("button", { name: "+ Nuevo tablero" }).click();
  await page.getByLabel("Nombre del nuevo tablero").fill(boardName);
  await page.getByLabel("Nombre del nuevo tablero").press("Enter");

  const newTab = page.getByTestId("board-tab").filter({ hasText: boardName });
  await expect(newTab).toBeVisible();
  await expect(newTab).toHaveAttribute("data-active", "true");

  // The new board starts empty, no cards yet.
  await expect(page.locator('[data-testid^="card-"]')).toHaveCount(0);

  await page.getByLabel(`Eliminar ${boardName}`).click();
  await expect(page.getByTestId("board-tab").filter({ hasText: boardName })).toHaveCount(0);
});

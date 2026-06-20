import { expect, test } from "@playwright/test";
import { initialData } from "../src/lib/kanban";

test.beforeEach(async ({ page }) => {
  const loginResponse = await page.request.post("/api/auth/login", {
    data: { username: "usuario", password: "contraseña" },
  });
  const { token } = await loginResponse.json();
  await page.request.post("/api/board", {
    data: initialData,
    headers: { Authorization: `Bearer ${token}` },
  });

  await page.goto("/");
  await page.locator("input#username").fill("usuario");
  await page.locator("input#password").fill("contraseña");
  await page.locator("button[type='submit']").click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
});

test("ai chat applies a board update", async ({ page }) => {
  const columnName = `Chat Backlog ${Date.now()}`;

  await page
    .getByLabel("Mensaje para la IA")
    .fill(`Rename the first column to ${columnName}. Return a complete boardUpdate.`);
  await page.getByRole("button", { name: "Enviar" }).click();

  await expect(page.locator(`input[aria-label="Título de la columna"][value="${columnName}"]`)).toBeVisible({
    timeout: 90_000,
  });
  await expect(page.getByTestId("ai-chat-messages")).toContainText(/renamed|actualizado|updated/i);
});

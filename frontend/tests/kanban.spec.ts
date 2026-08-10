import { expect, test, type Page } from "@playwright/test";

import { resetDemoBoard } from "./e2e-helpers";

test.beforeEach(async ({ request }) => {
  if (process.env.PM_E2E_DOCKER !== "1") {
    return;
  }

  await resetDemoBoard(request);
});

const login = async (page: Page) => {
  await page.getByPlaceholder("user").fill("user");
  await page.getByPlaceholder("password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
};

test("loads the kanban board", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /sign in to kanban studio/i })).toBeVisible();
  await login(page);
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await page.goto("/");
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await page.goto("/");
  await login(page);
  const card = page.getByTestId("card-card-1");
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});

test("moves a card into Discovery column", async ({ page }) => {
  await page.goto("/");
  await login(page);
  const card = page.getByTestId("card-card-6");
  const targetColumn = page.getByTestId("column-col-discovery");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 160,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-6")).toBeVisible();
});

test("logs out and hides the board", async ({ page }) => {
  await page.goto("/");
  await login(page);
  await page.getByRole("button", { name: /log out/i }).click();
  await expect(page.getByRole("heading", { name: /sign in to kanban studio/i })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(0);
});

test("persists a card after reload", async ({ page }) => {
  await page.goto("/");
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Persisted card");
  await firstColumn.getByPlaceholder("Details").fill("Survives reload.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Persisted card")).toBeVisible();

  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
  await expect(page.getByText("Persisted card")).toBeVisible();
});

// --- AI chat sidebar (Parte 10) -------------------------------------------
//
// Exercises `AiChatSidebar.tsx` / `src/lib/ai-api.ts` against the real
// backend contract (`docs/api-ai.md`). Testids used below:
//   - data-testid="ai-chat-sidebar"   sidebar container
//   - data-testid="ai-chat-input"     message textarea/input
//   - data-testid="ai-chat-send"      send button
//   - data-testid="ai-chat-message"   one element per chat bubble, with
//                                     data-role="user" | "assistant"
//   - data-testid="ai-chat-loading"   visible while waiting for a reply
//
// They call the real OpenRouter API (like
// backend/tests/integration/test_ai_chat.py) and need OPENROUTER_API_KEY
// configured in the running container's .env.

const assistantMessages = (page: Page) =>
  page
    .getByTestId("ai-chat-sidebar")
    .locator('[data-testid="ai-chat-message"][data-role="assistant"]');

// Chat history persists across test runs (it isn't reset like the board),
// so a matching assistant bubble can already be on screen from a previous
// run before this call's own reply arrives. Waiting on the *count* growing
// past its pre-send value (rather than "a reply is visible") is what
// guarantees we waited for this send's own response.
//
// OpenRouter's free-tier model also occasionally 502s on a cold first
// call (observed in practice, not a code defect — docs/api-ai.md documents
// 502 as an expected upstream failure mode). If that happens, retry once
// through the sidebar's own Retry action, exactly like a real user would.
const sendChatMessageAndWaitForReply = async (page: Page, message: string) => {
  const sidebar = page.getByTestId("ai-chat-sidebar");
  const countBefore = await assistantMessages(page).count();

  await sidebar.getByTestId("ai-chat-input").fill(message);
  await sidebar.getByTestId("ai-chat-send").click();

  try {
    await expect(assistantMessages(page)).toHaveCount(countBefore + 1, { timeout: 45_000 });
    return;
  } catch (error) {
    const errorBanner = sidebar.getByRole("alert");
    if (!(await errorBanner.isVisible())) {
      throw error;
    }
  }

  await sidebar.getByRole("button", { name: /retry/i }).click();
  await expect(assistantMessages(page)).toHaveCount(countBefore + 1, { timeout: 45_000 });
};

test("sends a chat message and displays the AI response", async ({ page }) => {
  test.setTimeout(90_000);
  await page.goto("/");
  await login(page);

  const sidebar = page.getByTestId("ai-chat-sidebar");
  await expect(sidebar).toBeVisible();

  await sendChatMessageAndWaitForReply(
    page,
    "How many columns are on my board? Reply briefly."
  );

  await expect(sidebar.getByTestId("ai-chat-loading")).toBeHidden();

  // Text-only response: the board stays untouched.
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("applies a Kanban board update returned by the AI", async ({ page }) => {
  test.setTimeout(90_000);
  await page.goto("/");
  await login(page);

  const cardTitle = "AI E2E Test Card";
  await sendChatMessageAndWaitForReply(
    page,
    `Add a new card titled '${cardTitle}' to the Backlog column with details ` +
      "'Created by Parte 10 E2E test'. Return the full updated board in the board field."
  );

  // The board updates automatically in the UI, without a manual reload.
  const backlogColumn = page.getByTestId("column-col-backlog");
  await expect(backlogColumn.getByText(cardTitle)).toBeVisible({ timeout: 10_000 });
});

test("persists chat history after reload", async ({ page }) => {
  test.setTimeout(90_000);
  await page.goto("/");
  await login(page);

  const question = `Say hello in one short sentence. (e2e-${Date.now()})`;
  await sendChatMessageAndWaitForReply(page, question);

  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();

  const sidebar = page.getByTestId("ai-chat-sidebar");
  await expect(sidebar.getByText(question)).toBeVisible();
  await expect(assistantMessages(page).last()).toBeVisible();
});

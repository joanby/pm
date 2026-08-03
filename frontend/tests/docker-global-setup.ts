import { request as playwrightRequest } from "@playwright/test";

import { resetDemoBoard, waitForDockerApi } from "./e2e-helpers";

const BASE_URL = "http://127.0.0.1:8000";

export default async function globalSetup(): Promise<void> {
  await waitForDockerApi(BASE_URL);

  const request = await playwrightRequest.newContext({ baseURL: BASE_URL });
  try {
    await resetDemoBoard(request);
  } finally {
    await request.dispose();
  }
}

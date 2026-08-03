import type { APIRequestContext } from "@playwright/test";

import { initialData } from "@/lib/kanban";

const MVP_HEADERS = {
  "X-MVP-Username": "user",
};

export async function resetDemoBoard(request: APIRequestContext): Promise<void> {
  const response = await request.put("/api/board", {
    headers: MVP_HEADERS,
    data: initialData,
  });

  if (!response.ok()) {
    throw new Error(`Unable to reset demo board (${response.status()}).`);
  }
}

export async function waitForDockerApi(baseURL: string): Promise<void> {
  const healthUrl = new URL("/api/health", baseURL).toString();

  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const response = await fetch(healthUrl);
      if (response.ok) {
        return;
      }
    } catch {
      // Retry until the container is ready.
    }

    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  throw new Error(`Docker API not ready at ${healthUrl}`);
}

import { vi } from "vitest";
import { initialData } from "@/lib/kanban";

const boardResponse = () =>
  new Response(JSON.stringify(initialData), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });

const jsonResponse = (payload: unknown, status = 200) =>
  new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });

export const mockKanbanApi = () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? "GET";

      if (url === "/api/board" && method === "GET") {
        return boardResponse();
      }

      if (url.startsWith("/api/columns/") && url.endsWith("/cards") && method === "POST") {
        const body = JSON.parse(String(init?.body));
        return jsonResponse(
          {
            id: body.id ?? "card-test",
            title: body.title,
            details: body.details,
          },
          201
        );
      }

      if (url.startsWith("/api/columns/") && method === "PATCH") {
        return new Response(null, { status: 200 });
      }

      if (url.startsWith("/api/cards/") && url.endsWith("/move") && method === "PUT") {
        return boardResponse();
      }

      if (url.startsWith("/api/cards/") && method === "DELETE") {
        return new Response(null, { status: 204 });
      }

      return jsonResponse({ detail: "Not found" }, 404);
    })
  );
};

export const restoreFetch = () => {
  vi.unstubAllGlobals();
};

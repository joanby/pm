import { afterEach, describe, expect, it, vi } from "vitest";
import { initialData } from "@/lib/kanban";
import { AiApiError, fetchChatHistory, sendChatMessage } from "@/lib/ai-api";

const jsonResponse = (payload: unknown, status = 200) =>
  new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });

describe("ai-api", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe("sendChatMessage", () => {
    it("posts the message with the auth header and returns the parsed response", async () => {
      const fetchMock = vi.fn(async (input: RequestInfo, init?: RequestInit) => {
        expect(input).toBe("/api/ai/chat");
        expect(init?.method).toBe("POST");
        expect(init?.headers).toMatchObject({ "X-MVP-Username": "user" });
        expect(JSON.parse(String(init?.body))).toEqual({ message: "Hello" });

        return jsonResponse({
          message: "Hi there!",
          boardUpdated: false,
          board: initialData,
        });
      });
      vi.stubGlobal("fetch", fetchMock);

      const result = await sendChatMessage("user", "Hello");

      expect(result.message).toBe("Hi there!");
      expect(result.boardUpdated).toBe(false);
      expect(result.board).toEqual(initialData);
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    it("throws AiApiError with the response status when the request fails", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn(async () => new Response("Missing OPENROUTER_API_KEY", { status: 503 }))
      );

      await expect(sendChatMessage("user", "Hello")).rejects.toMatchObject({
        name: "AiApiError",
        status: 503,
      });
    });
  });

  describe("fetchChatHistory", () => {
    it("returns the persisted messages", async () => {
      const messages = [
        { id: "msg-1", role: "user", content: "Hi", created_at: "2026-08-10T00:00:00Z" },
        { id: "msg-2", role: "assistant", content: "Hello!", created_at: "2026-08-10T00:00:01Z" },
      ];
      vi.stubGlobal(
        "fetch",
        vi.fn(async (input: RequestInfo) => {
          expect(input).toBe("/api/ai/history");
          return jsonResponse({ messages });
        })
      );

      const result = await fetchChatHistory("user");

      expect(result).toEqual(messages);
    });

    it("throws AiApiError on a non-ok response", async () => {
      vi.stubGlobal("fetch", vi.fn(async () => new Response("Not found", { status: 404 })));

      await expect(fetchChatHistory("user")).rejects.toBeInstanceOf(AiApiError);
    });
  });
});

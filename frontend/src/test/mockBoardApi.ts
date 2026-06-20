import { vi } from "vitest";
import type { BoardData } from "@/lib/kanban";

type AiChatResult = { message: string; boardUpdate: BoardData | null };

type MockBoardApiOptions = {
  boardId?: string;
  boardName?: string;
  aiResponse?: AiChatResult;
};

export const mockBoardApi = (board: BoardData, options: MockBoardApiOptions = {}) => {
  const boardId = options.boardId ?? "board-1";
  const boardName = options.boardName ?? "Tablero principal";
  let currentBoard = board;

  global.fetch = vi.fn(async (url, init) => {
    const method = init?.method ?? "GET";

    if (url === "/api/boards" && method === "GET") {
      return { ok: true, json: async () => [{ id: boardId, name: boardName, updated_at: "now" }] };
    }
    if (url === `/api/boards/${boardId}` && method === "GET") {
      return {
        ok: true,
        json: async () => ({ id: boardId, name: boardName, updated_at: "now", ...currentBoard }),
      };
    }
    if (url === `/api/boards/${boardId}` && method === "PUT") {
      currentBoard = JSON.parse(init!.body as string) as BoardData;
      return { ok: true, json: async () => ({ status: "ok" }) };
    }
    if (url === "/api/ai/chat" && method === "POST") {
      return { ok: true, json: async () => options.aiResponse ?? { message: "ok", boardUpdate: null } };
    }
    return { ok: false, json: async () => ({}) };
  }) as unknown as typeof fetch;

  return { boardId };
};

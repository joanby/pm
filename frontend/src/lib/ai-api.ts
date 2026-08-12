import type { BoardData } from "@/lib/kanban";

export class AiApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "AiApiError";
    this.status = status;
  }
}

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  created_at: string;
};

export type ChatResponse = {
  message: string;
  boardUpdated: boolean;
  board: BoardData;
};

async function request<T>(
  username: string,
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-MVP-Username": username,
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new AiApiError(response.status, detail || response.statusText);
  }

  return (await response.json()) as T;
}

export async function sendChatMessage(
  username: string,
  message: string
): Promise<ChatResponse> {
  return request<ChatResponse>(username, "/api/ai/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export async function fetchChatHistory(username: string): Promise<ChatMessage[]> {
  const data = await request<{ messages: ChatMessage[] }>(username, "/api/ai/history");
  return data.messages;
}

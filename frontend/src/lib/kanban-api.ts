import type { BoardData } from "@/lib/kanban";

export class KanbanApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "KanbanApiError";
    this.status = status;
  }
}

type CardPayload = {
  id: string;
  title: string;
  details: string;
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
    throw new KanbanApiError(response.status, detail || response.statusText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function fetchBoard(username: string): Promise<BoardData> {
  return request<BoardData>(username, "/api/board");
}

export async function renameColumn(
  username: string,
  columnId: string,
  title: string
): Promise<void> {
  await request(username, `/api/columns/${columnId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}

export async function createCard(
  username: string,
  columnId: string,
  payload: { title: string; details: string; id?: string }
): Promise<CardPayload> {
  return request<CardPayload>(username, `/api/columns/${columnId}/cards`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function deleteCard(username: string, cardId: string): Promise<void> {
  await request<void>(username, `/api/cards/${cardId}`, {
    method: "DELETE",
  });
}

export async function moveCardOnBoard(
  username: string,
  cardId: string,
  columnId: string,
  position: number
): Promise<BoardData> {
  return request<BoardData>(username, `/api/cards/${cardId}/move`, {
    method: "PUT",
    body: JSON.stringify({ column_id: columnId, position }),
  });
}

export async function replaceBoard(
  username: string,
  board: BoardData
): Promise<BoardData> {
  return request<BoardData>(username, "/api/board", {
    method: "PUT",
    body: JSON.stringify(board),
  });
}

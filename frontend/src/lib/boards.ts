import { authedFetch } from "@/lib/api";
import { type BoardData } from "@/lib/kanban";

export type BoardSummary = {
  id: string;
  name: string;
  updated_at: string;
};

export type BoardDetail = BoardData & {
  id: string;
  name: string;
  updated_at: string;
};

export const listBoards = async (token: string): Promise<BoardSummary[]> => {
  const response = await authedFetch(token, "/api/boards");
  if (!response.ok) {
    throw new Error("No se pudieron cargar los tableros");
  }
  return response.json();
};

export const createBoard = async (token: string, name: string): Promise<BoardDetail> => {
  const response = await authedFetch(token, "/api/boards", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
  if (!response.ok) {
    throw new Error("No se pudo crear el tablero");
  }
  return response.json();
};

export const getBoard = async (token: string, boardId: string): Promise<BoardDetail> => {
  const response = await authedFetch(token, `/api/boards/${boardId}`);
  if (!response.ok) {
    throw new Error("No se pudo cargar el tablero");
  }
  return response.json();
};

export const updateBoard = async (
  token: string,
  boardId: string,
  board: BoardData
): Promise<void> => {
  const response = await authedFetch(token, `/api/boards/${boardId}`, {
    method: "PUT",
    body: JSON.stringify(board),
  });
  if (!response.ok) {
    throw new Error("No se pudo guardar el tablero");
  }
};

export const renameBoard = async (
  token: string,
  boardId: string,
  name: string
): Promise<void> => {
  const response = await authedFetch(token, `/api/boards/${boardId}`, {
    method: "PATCH",
    body: JSON.stringify({ name }),
  });
  if (!response.ok) {
    throw new Error("No se pudo renombrar el tablero");
  }
};

export const deleteBoard = async (token: string, boardId: string): Promise<void> => {
  const response = await authedFetch(token, `/api/boards/${boardId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("No se pudo eliminar el tablero");
  }
};

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { KanbanBoard } from "@/components/KanbanBoard";

const mockBoard = {
  columns: [
    { id: "col-backlog", title: "Backlog", cardIds: ["card-1"] },
  ],
  cards: {
    "card-1": { id: "card-1", title: "Test card", details: "Details" },
  },
};

describe("KanbanBoard API integration", () => {
  beforeEach(() => {
    global.fetch = vi.fn(async (url, options) => {
      if (url === "/api/board" && (!options || options.method === "GET")) {
        return {
          ok: true,
          json: async () => mockBoard,
        };
      }
      if (url === "/api/board" && options?.method === "POST") {
        return { ok: true, json: async () => ({ status: "ok" }) };
      }
      if (url === "/api/ai/chat" && options?.method === "POST") {
        return {
          ok: true,
          json: async () => ({
            message: "He actualizado el tablero.",
            boardUpdate: {
              columns: [
                { id: "col-backlog", title: "AI Backlog", cardIds: ["card-1"] },
              ],
              cards: mockBoard.cards,
            },
          }),
        };
      }
      return { ok: false };
    }) as unknown as typeof fetch;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads board data from the backend", async () => {
    render(<KanbanBoard token="test-token" />);
    await waitFor(() => expect(screen.getByText("Kanban Studio")).toBeInTheDocument());
    expect(screen.getByText("Test card")).toBeInTheDocument();
  });

  it("saves changes after renaming a column", async () => {
    render(<KanbanBoard token="test-token" />);
    await waitFor(() => expect(screen.getByText("Kanban Studio")).toBeInTheDocument());
    const input = screen.getByLabelText("Título de la columna");
    await userEvent.clear(input);
    await userEvent.type(input, "Updated backlog");
    expect((input as HTMLInputElement).value).toBe("Updated backlog");
    await waitFor(
      () => expect(global.fetch).toHaveBeenCalledWith("/api/board", expect.any(Object)),
      { timeout: 1000 }
    );
  });

  it("applies board updates returned by ai chat", async () => {
    render(<KanbanBoard token="test-token" />);
    await waitFor(() => expect(screen.getByText("Kanban Studio")).toBeInTheDocument());

    await userEvent.type(screen.getByLabelText("Mensaje para la IA"), "Renombra la primera columna");
    await userEvent.click(screen.getByRole("button", { name: /enviar/i }));

    await waitFor(() => expect(screen.getByDisplayValue("AI Backlog")).toBeInTheDocument());
    expect(screen.getByText("He actualizado el tablero.")).toBeInTheDocument();
  });
});

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
      return { ok: false };
    }) as any;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads board data from the backend", async () => {
    render(<KanbanBoard />);
    await waitFor(() => expect(screen.getByText("Kanban Studio")).toBeInTheDocument());
    expect(screen.getByText("Test card")).toBeInTheDocument();
  });

  it("saves changes after renaming a column", async () => {
    render(<KanbanBoard />);
    await waitFor(() => expect(screen.getByText("Kanban Studio")).toBeInTheDocument());
    const input = screen.getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "Updated backlog");
    expect((input as HTMLInputElement).value).toBe("Updated backlog");
    expect(global.fetch).toHaveBeenCalledWith("/api/board", expect.any(Object));
  });
});

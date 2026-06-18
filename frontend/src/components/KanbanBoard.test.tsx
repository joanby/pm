import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData } from "@/lib/kanban";

const mockBoard = initialData;
const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
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

  it("renders five columns", async () => {
    render(<KanbanBoard />);
    await waitFor(() => expect(screen.getAllByTestId(/column-/i)).toHaveLength(5));
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    const column = await waitFor(() => getFirstColumn());
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
    expect(global.fetch).toHaveBeenCalledWith("/api/board", expect.any(Object));
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    const column = await waitFor(() => getFirstColumn());
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
    expect(global.fetch).toHaveBeenCalledWith("/api/board", expect.any(Object));
  });
});

import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData } from "@/lib/kanban";
import { mockBoardApi } from "@/test/mockBoardApi";

const mockBoard = initialData;
const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    mockBoardApi(mockBoard, { aiResponse: { message: "ok", boardUpdate: null } });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders five columns", async () => {
    render(<KanbanBoard userId="user-1" token="test-token" role="member" />);
    await waitFor(() => expect(screen.getAllByTestId(/column-/i)).toHaveLength(5));
  });

  it("renames a column", async () => {
    render(<KanbanBoard userId="user-1" token="test-token" role="member" />);
    const column = await waitFor(() => getFirstColumn());
    const input = within(column).getByLabelText("Título de la columna");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
    await waitFor(
      () => expect(global.fetch).toHaveBeenCalledWith("/api/boards/board-1", expect.any(Object)),
      { timeout: 1000 }
    );
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard userId="user-1" token="test-token" role="member" />);
    const column = await waitFor(() => getFirstColumn());
    const addButton = within(column).getByRole("button", {
      name: /nueva tarjeta/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/título de la tarjeta/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/detalles/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /añadir tarjeta/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /eliminar new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
    expect(global.fetch).toHaveBeenCalledWith("/api/boards/board-1", expect.any(Object));
  });

  it("shows ai chat responses", async () => {
    render(<KanbanBoard userId="user-1" token="test-token" role="member" />);
    await waitFor(() => expect(screen.getByText("Kanban Studio")).toBeInTheDocument());

    await userEvent.type(screen.getByLabelText("Mensaje para la IA"), "Di ok");
    await userEvent.click(screen.getByRole("button", { name: /enviar/i }));

    await waitFor(() => expect(screen.getByText("ok")).toBeInTheDocument());
    expect(global.fetch).toHaveBeenCalledWith("/api/ai/chat", expect.any(Object));
  });

  it("hides user management for non-admin users", async () => {
    render(<KanbanBoard userId="user-1" token="test-token" role="member" />);
    await waitFor(() => expect(screen.getByText("Kanban Studio")).toBeInTheDocument());
    expect(screen.queryByText("Gestionar usuarios")).not.toBeInTheDocument();
  });

  it("shows user management entry point for admins", async () => {
    render(<KanbanBoard userId="user-1" token="test-token" role="admin" />);
    await waitFor(() => expect(screen.getByText("Gestionar usuarios")).toBeInTheDocument());
  });
});

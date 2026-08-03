import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { KanbanBoard } from "@/components/KanbanBoard";

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  const login = async () => {
    await userEvent.type(screen.getByPlaceholderText("user"), "user");
    await userEvent.type(screen.getByPlaceholderText("password"), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
  };

  it("requires login before showing the board", () => {
    render(<KanbanBoard />);
    expect(screen.getByRole("heading", { name: /sign in to kanban studio/i })).toBeInTheDocument();
    expect(screen.queryAllByTestId(/column-/i)).toHaveLength(0);
  });

  it("shows an error for invalid credentials", async () => {
    render(<KanbanBoard />);
    await userEvent.type(screen.getByPlaceholderText("user"), "wrong");
    await userEvent.type(screen.getByPlaceholderText("password"), "wrong");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    expect(screen.getByRole("alert")).toHaveTextContent(/invalid credentials/i);
  });

  it("renders five columns after login", async () => {
    render(<KanbanBoard />);
    await login();
    expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    await login();
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    await login();
    const column = getFirstColumn();
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
  });
});

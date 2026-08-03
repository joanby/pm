import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { AUTH_USERNAME_KEY } from "@/lib/auth";
import { mockKanbanApi } from "@/test/kanban-api-mock";

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    window.localStorage.clear();
    mockKanbanApi();
  });

  const login = async () => {
    await userEvent.type(screen.getByPlaceholderText("user"), "user");
    await userEvent.type(screen.getByPlaceholderText("password"), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });
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

  it("restores an existing session from localStorage", async () => {
    window.localStorage.setItem("pm-mvp-auth", "1");
    window.localStorage.setItem(AUTH_USERNAME_KEY, "user");
    render(<KanbanBoard />);
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /kanban studio/i })).toBeInTheDocument();
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });
  });

  it("returns to the login screen after logout", async () => {
    render(<KanbanBoard />);
    await login();
    await userEvent.click(screen.getByRole("button", { name: /log out/i }));
    expect(screen.getByRole("heading", { name: /sign in to kanban studio/i })).toBeInTheDocument();
    expect(screen.queryAllByTestId(/column-/i)).toHaveLength(0);
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

    await waitFor(() => {
      expect(within(column).getByText("New card")).toBeInTheDocument();
    });

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    await waitFor(() => {
      expect(within(column).queryByText("New card")).not.toBeInTheDocument();
    });
  });
});

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AiChatSidebar } from "@/components/AiChatSidebar";
import { fetchChatHistory, sendChatMessage } from "@/lib/ai-api";
import { initialData } from "@/lib/kanban";

vi.mock("@/lib/ai-api", () => ({
  fetchChatHistory: vi.fn(),
  sendChatMessage: vi.fn(),
}));

const mockedFetchChatHistory = vi.mocked(fetchChatHistory);
const mockedSendChatMessage = vi.mocked(sendChatMessage);

describe("AiChatSidebar", () => {
  beforeEach(() => {
    mockedFetchChatHistory.mockReset();
    mockedSendChatMessage.mockReset();
    mockedFetchChatHistory.mockResolvedValue([]);
  });

  it("loads and displays persisted chat history on mount", async () => {
    mockedFetchChatHistory.mockResolvedValue([
      { id: "msg-1", role: "user", content: "Hi there", created_at: "2026-08-10T00:00:00Z" },
      { id: "msg-2", role: "assistant", content: "Hello! How can I help?", created_at: "2026-08-10T00:00:01Z" },
    ]);

    render(<AiChatSidebar username="user" onBoardUpdated={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText("Hi there")).toBeInTheDocument();
      expect(screen.getByText("Hello! How can I help?")).toBeInTheDocument();
    });
    expect(mockedFetchChatHistory).toHaveBeenCalledWith("user");
  });

  it("sends a message and displays the assistant reply", async () => {
    mockedSendChatMessage.mockResolvedValue({
      message: "There are 5 columns.",
      boardUpdated: false,
      board: initialData,
    });

    render(<AiChatSidebar username="user" onBoardUpdated={vi.fn()} />);
    await waitFor(() => expect(mockedFetchChatHistory).toHaveBeenCalled());

    await userEvent.type(
      screen.getByTestId("ai-chat-input"),
      "How many columns are on my board?"
    );
    await userEvent.click(screen.getByTestId("ai-chat-send"));

    expect(screen.getByText("How many columns are on my board?")).toBeInTheDocument();
    expect(screen.getByTestId("ai-chat-input")).toHaveValue("");

    await waitFor(() => {
      expect(screen.getByText("There are 5 columns.")).toBeInTheDocument();
    });
    expect(mockedSendChatMessage).toHaveBeenCalledWith(
      "user",
      "How many columns are on my board?"
    );
    expect(screen.queryByTestId("ai-chat-loading")).not.toBeInTheDocument();
  });

  it("applies a Kanban board update returned by the AI", async () => {
    const updatedBoard = {
      ...initialData,
      cards: {
        ...initialData.cards,
        "card-new": { id: "card-new", title: "AI created card", details: "" },
      },
    };
    mockedSendChatMessage.mockResolvedValue({
      message: "Added the card.",
      boardUpdated: true,
      board: updatedBoard,
    });
    const onBoardUpdated = vi.fn();

    render(<AiChatSidebar username="user" onBoardUpdated={onBoardUpdated} />);
    await waitFor(() => expect(mockedFetchChatHistory).toHaveBeenCalled());

    await userEvent.type(screen.getByTestId("ai-chat-input"), "Add a card");
    await userEvent.click(screen.getByTestId("ai-chat-send"));

    await waitFor(() => {
      expect(onBoardUpdated).toHaveBeenCalledWith(updatedBoard);
    });
  });

  it("shows an error with a retry action when sending fails, and recovers on retry", async () => {
    mockedSendChatMessage
      .mockRejectedValueOnce(new Error("network error"))
      .mockResolvedValueOnce({
        message: "Now it worked.",
        boardUpdated: false,
        board: initialData,
      });

    render(<AiChatSidebar username="user" onBoardUpdated={vi.fn()} />);
    await waitFor(() => expect(mockedFetchChatHistory).toHaveBeenCalled());

    await userEvent.type(screen.getByTestId("ai-chat-input"), "Hello");
    await userEvent.click(screen.getByTestId("ai-chat-send"));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(/unable to reach the ai assistant/i);
    });

    await userEvent.click(screen.getByRole("button", { name: /retry/i }));

    await waitFor(() => {
      expect(screen.getByText("Now it worked.")).toBeInTheDocument();
    });
    expect(mockedSendChatMessage).toHaveBeenCalledTimes(2);
  });
});

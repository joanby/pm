"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  fetchChatHistory,
  sendChatMessage,
  type ChatRole,
} from "@/lib/ai-api";
import { createId, type BoardData } from "@/lib/kanban";

type DisplayMessage = {
  id: string;
  role: ChatRole;
  content: string;
};

type AiChatSidebarProps = {
  username: string;
  onBoardUpdated: (board: BoardData) => void;
};

export const AiChatSidebar = ({ username, onBoardUpdated }: AiChatSidebarProps) => {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      setIsLoadingHistory(true);
      try {
        const history = await fetchChatHistory(username);
        if (!cancelled) {
          setMessages(
            history.map((entry) => ({
              id: entry.id,
              role: entry.role,
              content: entry.content,
            }))
          );
        }
      } catch {
        if (!cancelled) {
          setError("Unable to load the chat history.");
        }
      } finally {
        if (!cancelled) {
          setIsLoadingHistory(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [username]);

  useEffect(() => {
    const node = scrollRef.current;
    if (node) {
      node.scrollTop = node.scrollHeight;
    }
  }, [messages, isSending]);

  const submitMessage = async (content: string) => {
    setMessages((prev) => [...prev, { id: createId("msg-user"), role: "user", content }]);
    setIsSending(true);
    setError(null);
    setLastFailedMessage(null);

    try {
      const response = await sendChatMessage(username, content);
      setMessages((prev) => [
        ...prev,
        { id: createId("msg-assistant"), role: "assistant", content: response.message },
      ]);
      if (response.boardUpdated) {
        onBoardUpdated(response.board);
      }
    } catch {
      setError("Unable to reach the AI assistant. Please try again.");
      setLastFailedMessage(content);
    } finally {
      setIsSending(false);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isSending) {
      return;
    }
    setInput("");
    void submitMessage(trimmed);
  };

  const handleRetry = () => {
    if (!lastFailedMessage || isSending) {
      return;
    }
    void submitMessage(lastFailedMessage);
  };

  return (
    <aside
      data-testid="ai-chat-sidebar"
      className="flex h-fit max-h-[80vh] w-full flex-col rounded-[32px] border border-[var(--stroke)] bg-white/80 shadow-[var(--shadow)] backdrop-blur lg:w-[360px]"
    >
      <div className="border-b border-[var(--stroke)] px-6 py-5">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          AI Assistant
        </p>
        <h2 className="mt-2 font-display text-xl font-semibold text-[var(--navy-dark)]">
          Ask about your board
        </h2>
      </div>

      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-6 py-4">
        {isLoadingHistory ? (
          <p className="text-sm text-[var(--gray-text)]">Loading conversation...</p>
        ) : null}

        {!isLoadingHistory && messages.length === 0 ? (
          <p className="text-sm text-[var(--gray-text)]">
            Ask the assistant to summarize, create, or move cards for you.
          </p>
        ) : null}

        {messages.map((entry) => (
          <div
            key={entry.id}
            data-testid="ai-chat-message"
            data-role={entry.role}
            className={
              entry.role === "user"
                ? "ml-auto max-w-[85%] rounded-2xl rounded-tr-sm bg-[var(--secondary-purple)] px-4 py-2 text-sm text-white"
                : "mr-auto max-w-[85%] rounded-2xl rounded-tl-sm bg-[var(--surface)] px-4 py-2 text-sm text-[var(--navy-dark)]"
            }
          >
            {entry.content}
          </div>
        ))}

        {isSending ? (
          <div
            data-testid="ai-chat-loading"
            className="mr-auto max-w-[85%] rounded-2xl rounded-tl-sm bg-[var(--surface)] px-4 py-2 text-sm text-[var(--gray-text)]"
          >
            Thinking...
          </div>
        ) : null}
      </div>

      {error ? (
        <div className="border-t border-[var(--stroke)] px-6 py-3">
          <p role="alert" className="text-sm font-medium text-red-600">
            {error}
          </p>
          {lastFailedMessage ? (
            <button
              type="button"
              onClick={handleRetry}
              className="mt-2 rounded-xl border border-[var(--stroke)] px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
            >
              Retry
            </button>
          ) : null}
        </div>
      ) : null}

      <form
        onSubmit={handleSubmit}
        className="flex items-end gap-2 border-t border-[var(--stroke)] px-6 py-4"
      >
        <textarea
          data-testid="ai-chat-input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="Ask the AI assistant..."
          rows={2}
          className="w-full flex-1 resize-none rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
        />
        <button
          type="submit"
          data-testid="ai-chat-send"
          disabled={isSending || !input.trim()}
          className="rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </aside>
  );
};

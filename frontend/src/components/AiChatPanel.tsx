"use client";

import { type FormEvent, useState } from "react";
import { type BoardData } from "@/lib/kanban";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type AiChatResponse = {
  message: string;
  boardUpdate: BoardData | null;
};

type AiChatPanelProps = {
  board: BoardData;
  boardId: string;
  onBoardUpdate: (board: BoardData) => void;
  token: string;
};

const sendAiChat = async (
  message: string,
  boardId: string,
  board: BoardData,
  history: ChatMessage[],
  token: string
) => {
  const response = await fetch("/api/ai/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      board_id: boardId,
      board,
      history,
    }),
  });

  if (!response.ok) {
    throw new Error("No se pudo contactar con la IA");
  }

  return (await response.json()) as AiChatResponse;
};

export const AiChatPanel = ({ board, boardId, onBoardUpdate, token }: AiChatPanelProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const message = draft.trim();
    if (!message || isSending) {
      return;
    }

    const nextMessages: ChatMessage[] = [...messages, { role: "user", content: message }];
    setMessages(nextMessages);
    setDraft("");
    setError(null);
    setIsSending(true);

    try {
      const data = await sendAiChat(message, boardId, board, messages, token);
      setMessages([...nextMessages, { role: "assistant", content: data.message }]);
      if (data.boardUpdate) {
        onBoardUpdate(data.boardUpdate);
      }
    } catch (err) {
      setMessages(messages);
      setError(err instanceof Error ? err.message : "Error en el chat IA");
      setDraft(message);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <aside className="flex min-h-[520px] flex-col rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-4 shadow-[var(--shadow)] backdrop-blur-xl">
      <div className="flex items-center gap-2 border-b border-[var(--stroke)] pb-4">
        <span className="h-2 w-2 rounded-full bg-[var(--secondary-purple)] shadow-[var(--glow-purple)]" />
        <div>
          <h2 className="font-mono text-sm font-semibold uppercase tracking-[0.2em] text-[var(--text)]">
            Chat IA
          </h2>
          <p className="mt-1 text-xs leading-5 text-[var(--gray-text)]">
            Crea, edita o mueve tarjetas desde aquí.
          </p>
        </div>
      </div>

      <div
        data-testid="ai-chat-messages"
        className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto py-4"
      >
        {messages.length === 0 ? (
          <p className="rounded-lg border border-dashed border-[var(--stroke)] p-3 text-sm leading-6 text-[var(--gray-text)]">
            Pide un cambio del tablero o una recomendación breve.
          </p>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={
                message.role === "user"
                  ? "ml-6 rounded-lg bg-[var(--primary-blue)] px-3 py-2 text-sm leading-6 text-white"
                  : "mr-6 rounded-lg border border-[var(--stroke)] bg-[var(--bg-deep)] px-3 py-2 text-sm leading-6 text-[var(--text)]"
              }
            >
              {message.content}
            </div>
          ))
        )}
      </div>

      {error ? (
        <p className="mb-3 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-300">
          {error}
        </p>
      ) : null}

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Escribe a la IA"
          aria-label="Mensaje para la IA"
          className="min-h-24 resize-none rounded-lg border border-[var(--stroke)] bg-[var(--bg-deep)] px-3 py-3 text-sm leading-6 text-[var(--text)] outline-none transition focus:border-[var(--primary-blue)] focus:shadow-[var(--glow-blue)]"
        />
        <button
          type="submit"
          disabled={isSending || !draft.trim()}
          className="rounded-lg bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold text-white transition hover:shadow-[var(--glow-purple)] disabled:cursor-not-allowed disabled:bg-[var(--gray-text)] disabled:opacity-50"
        >
          {isSending ? "Enviando..." : "Enviar"}
        </button>
      </form>
    </aside>
  );
};

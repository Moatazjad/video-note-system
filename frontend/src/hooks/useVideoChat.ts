'use client';

import { useCallback, useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { ChatMessage } from '@/types/video';

export function useVideoChat(videoId: number) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.getChatHistory(videoId).then((history) => {
      if (!cancelled) setMessages(history);
    }).catch(() => {
      // No history yet is fine -- start with an empty conversation.
    });
    return () => {
      cancelled = true;
    };
  }, [videoId]);

  const sendMessage = useCallback(async (message: string) => {
    const trimmed = message.trim();
    if (!trimmed || isSending) return;

    setError(null);
    setIsSending(true);

    const optimisticUser: ChatMessage = {
      id: -Date.now(),
      role: 'user',
      content: trimmed,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUser]);

    try {
      const reply = await api.sendChatMessage(videoId, trimmed);
      setMessages((prev) => [...prev, reply]);
    } catch {
      setError('Failed to get a response. Please try again.');
    } finally {
      setIsSending(false);
    }
  }, [videoId, isSending]);

  return { messages, sendMessage, isSending, error };
}

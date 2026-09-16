'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Loader2, Send, MessageCircle } from 'lucide-react';
import { useVideoChat } from '@/hooks/useVideoChat';
import { cn } from '@/lib/utils';

interface VideoChatProps {
  videoId: number;
  isRtl?: boolean;
}

export function VideoChat({ videoId, isRtl }: VideoChatProps) {
  const { messages, sendMessage, isSending, error } = useVideoChat(videoId);
  const [draft, setDraft] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!draft.trim()) return;
    sendMessage(draft);
    setDraft('');
  };

  return (
    <Card className="border-border/60 bg-card/90 backdrop-blur-md shadow-xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 font-display">
          <MessageCircle className="w-5 h-5 text-primary" />
          Ask about this video
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          dir={isRtl ? 'rtl' : 'ltr'}
          className="flex flex-col gap-3 max-h-96 overflow-y-auto"
        >
          {messages.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Ask a question about this video&apos;s content.
            </p>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                'flex',
                msg.role === 'user' ? 'justify-end' : 'justify-start',
                isRtl && (msg.role === 'user' ? 'justify-start' : 'justify-end')
              )}
            >
              <div
                className={cn(
                  'max-w-[85%] rounded-lg px-4 py-2 text-sm',
                  msg.role === 'user'
                    ? 'grad-accent-bg text-[oklch(0.14_0.02_265)] whitespace-pre-wrap'
                    : 'bg-secondary text-secondary-foreground prose prose-invert prose-sm max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0'
                )}
              >
                {msg.role === 'assistant' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}
          {isSending && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              Thinking...
            </div>
          )}
        </div>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Ask a question about this video..."
            disabled={isSending}
            dir={isRtl ? 'rtl' : 'ltr'}
          />
          <Button type="submit" size="icon" disabled={isSending || !draft.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

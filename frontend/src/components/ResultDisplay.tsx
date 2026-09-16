'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSlug from 'rehype-slug';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { CheckCircle2, Download, FileText, RefreshCw, Clock, Languages, Loader2 } from 'lucide-react';
import type { VideoResult } from '@/types/video';
import { NotesTableOfContents } from '@/components/NotesTableOfContents';
import { VideoChat } from '@/components/VideoChat';

interface ResultDisplayProps {
  result: VideoResult;
  onReset: () => void;
}

export function ResultDisplay({ result, onReset }: ResultDisplayProps) {
  const originalLanguage: 'en' | 'ar' = result.detected_language?.toLowerCase().startsWith('ar')
    ? 'ar'
    : 'en';
  const otherLanguage: 'en' | 'ar' = originalLanguage === 'ar' ? 'en' : 'ar';

  const [viewLanguage, setViewLanguage] = useState<'en' | 'ar'>(originalLanguage);
  const [displayedNotes, setDisplayedNotes] = useState(result.notes || '');
  const [isTranslating, setIsTranslating] = useState(false);
  const [translateError, setTranslateError] = useState<string | null>(null);

  const isRtl = viewLanguage === 'ar';

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDownload = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const exportUrl = (path: string) => `${path}?lang=${viewLanguage}`;

  const handleToggleLanguage = async () => {
    setTranslateError(null);

    if (viewLanguage !== originalLanguage) {
      setDisplayedNotes(result.notes || '');
      setViewLanguage(originalLanguage);
      return;
    }

    setIsTranslating(true);
    try {
      const translated = await api.translateNotes(result.id, otherLanguage);
      setDisplayedNotes(translated.content);
      setViewLanguage(otherLanguage);
    } catch {
      setTranslateError('Translation failed. Please try again.');
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="border-border/60 bg-card/90 backdrop-blur-md shadow-xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[oklch(0.75_0.15_155)]">
            <CheckCircle2 className="w-6 h-6" />
            Processing Complete!
          </CardTitle>
          <CardDescription>
            Your notes are ready to download
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm border-b border-border/60 pb-4">
            <div>
              <span className="text-muted-foreground text-xs uppercase tracking-wide">Language</span>
              <p className="font-medium capitalize mt-1">{result.detected_language || 'N/A'}</p>
            </div>
            {result.duration != null && (
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <p className="font-medium">{formatDuration(result.duration)}</p>
              </div>
            )}
          </div>

          <Button
            onClick={handleToggleLanguage}
            variant="outline"
            className="w-full"
            disabled={isTranslating}
          >
            {isTranslating ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Languages className="mr-2 h-4 w-4" />
            )}
            {viewLanguage === originalLanguage
              ? `View in ${otherLanguage === 'ar' ? 'Arabic' : 'English'}`
              : `View in ${originalLanguage === 'ar' ? 'Arabic' : 'English'} (original)`}
          </Button>
          {translateError && <p className="text-sm text-destructive">{translateError}</p>}

          <div className="flex flex-col sm:flex-row gap-3">
            {result.markdown_url && (
              <Button
                onClick={() => handleDownload(api.getDownloadUrl(exportUrl(result.markdown_url!)))}
                className="grad-accent-bg glow-accent flex-1 border-0 text-[oklch(0.14_0.02_265)] hover:opacity-90"
              >
                <FileText className="mr-2 h-4 w-4" />
                Download Markdown
              </Button>
            )}
            {result.pdf_url && (
              <Button
                onClick={() => handleDownload(api.getDownloadUrl(exportUrl(result.pdf_url!)))}
                variant="outline"
                className="flex-1"
              >
                <Download className="mr-2 h-4 w-4" />
                Download PDF
              </Button>
            )}
          </div>

          <Button onClick={onReset} variant="ghost" className="w-full text-muted-foreground">
            <RefreshCw className="mr-2 h-4 w-4" />
            Process Another Video
          </Button>
        </CardContent>
      </Card>

      {displayedNotes && (
        <div className="grid grid-cols-1 md:grid-cols-[200px_1fr] gap-4">
          <NotesTableOfContents markdown={displayedNotes} isRtl={isRtl} />

          <Card className="border-border/60 bg-card/90 backdrop-blur-md shadow-xl">
            <CardHeader>
              <CardTitle className="grad-accent-text font-display">Generated Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                className="prose prose-invert max-w-none"
                dir={isRtl ? 'rtl' : 'ltr'}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSlug]}>
                  {displayedNotes}
                </ReactMarkdown>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {result.status === 'completed' && (
        <VideoChat videoId={result.id} isRtl={isRtl} />
      )}
    </div>
  );
}

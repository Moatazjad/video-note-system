'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { CheckCircle2, Download, FileText, RefreshCw, Clock } from 'lucide-react';
import type { VideoResult } from '@/types/video';

interface ResultDisplayProps {
  result: VideoResult;
  onReset: () => void;
}

export function ResultDisplay({ result, onReset }: ResultDisplayProps) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDownload = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="space-y-6">
      <Card className="shadow-lg border-green-200 dark:border-green-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-600 dark:text-green-400">
            <CheckCircle2 className="w-6 h-6" />
            Processing Complete!
          </CardTitle>
          <CardDescription>
            Your notes are ready to download
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Language:</span>
              <p className="font-medium capitalize">{result.detected_language || 'N/A'}</p>
            </div>
            {result.duration && (
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <p className="font-medium">{formatDuration(result.duration)}</p>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            {result.markdown_url && (
              <Button
                onClick={() => handleDownload(api.getDownloadUrl(result.markdown_url!))}
                className="flex-1"
              >
                <FileText className="mr-2 h-4 w-4" />
                Download Markdown
              </Button>
            )}
            {result.pdf_url && (
              <Button
                onClick={() => handleDownload(api.getDownloadUrl(result.pdf_url!))}
                variant="outline"
                className="flex-1"
              >
                <Download className="mr-2 h-4 w-4" />
                Download PDF
              </Button>
            )}
          </div>

          <Button onClick={onReset} variant="ghost" className="w-full">
            <RefreshCw className="mr-2 h-4 w-4" />
            Process Another Video
          </Button>
        </CardContent>
      </Card>

      {result.notes && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Generated Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose dark:prose-invert max-w-none">
              <pre className="whitespace-pre-wrap text-sm bg-slate-50 dark:bg-slate-900 p-4 rounded-md overflow-x-auto">
                {result.notes}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
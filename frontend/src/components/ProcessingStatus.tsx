'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, XCircle, RefreshCw, StopCircle, Clock } from 'lucide-react';
import type { VideoJobState } from '@/types/video';

interface ProcessingStatusProps {
  state: VideoJobState;
  onCancel: () => Promise<void>;
  onReset: () => void;
}

export function ProcessingStatus({ state, onCancel, onReset }: ProcessingStatusProps) {
  const [isCancelling, setIsCancelling] = useState(false);

  const handleCancel = async () => {
    setIsCancelling(true);
    try {
      await onCancel();
    } finally {
      setIsCancelling(false);
    }
  };

  const isCancelDisabled = (): boolean => {
    return (
      isCancelling ||
      state.status === 'cancelling' ||
      state.status === 'cancelled' ||
      state.status === null
    );
  };

  const isCurrentlyCancelling = (): boolean => {
    return isCancelling || state.status === 'cancelling';
  };

  if (state.error || state.status === 'failed' || state.status === 'cancelled') {
    return (
      <Card className="border-destructive/40 bg-card/90 backdrop-blur-md shadow-xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <XCircle className="w-6 h-6" />
            {state.status === 'cancelled' ? 'Processing Cancelled' : 'Processing Failed'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-foreground mb-4">
            {state.error || `Processing ${state.status}`}
          </p>
          <Button onClick={onReset} variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/60 bg-card/90 backdrop-blur-md shadow-xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 font-display">
          <Loader2 className="w-6 h-6 animate-spin text-primary" />
          {state.status === 'cancelling' ? 'Cancelling...' : 'Processing Video'}
        </CardTitle>
        <CardDescription>
          Video ID: {state.jobId}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-muted-foreground">Status</span>
          <Badge className="grad-accent-bg border-0 text-[oklch(0.14_0.02_265)] uppercase tracking-wide">
            {state.status}
          </Badge>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Progress</span>
            <span className="text-muted-foreground">{state.progress}%</span>
          </div>
          <Progress
            value={state.progress}
            className="h-2 bg-secondary"
            indicatorClassName="grad-accent-bg glow-accent"
          />
        </div>

        {state.currentStep && (
          <div className="rounded-lg border border-primary/30 bg-primary/10 p-4">
            <p className="text-sm text-foreground font-medium">
              {state.currentStep}
            </p>
          </div>
        )}

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="w-4 h-4 shrink-0" />
          <span>Cancellation may take a few moments.</span>
        </div>

        {state.language && state.templateType && (
          <div className="grid grid-cols-2 gap-4 text-sm border-t border-border/60 pt-4">
            <div>
              <span className="text-muted-foreground text-xs uppercase tracking-wide">Language</span>
              <p className="font-medium mt-1">{state.language === 'en' ? 'English' : 'Arabic'}</p>
            </div>
            <div>
              <span className="text-muted-foreground text-xs uppercase tracking-wide">Template</span>
              <p className="font-medium capitalize mt-1">{state.templateType}</p>
            </div>
          </div>
        )}

        <Button
          onClick={handleCancel}
          variant="outline"
          className="w-full border-destructive/40 text-destructive hover:bg-destructive/10"
          disabled={isCancelDisabled()}
        >
          {isCurrentlyCancelling() ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Cancelling...
            </>
          ) : (
            <>
              <StopCircle className="mr-2 h-4 w-4" />
              Cancel Processing
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

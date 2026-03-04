'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, XCircle, RefreshCw, StopCircle, Clock } from 'lucide-react';
import type { VideoJobState, ExtendedStatus } from '@/types/video';

interface ProcessingStatusProps {
  state: VideoJobState;
  onCancel: () => Promise<void>;
  onReset: () => void;
}

function getBadgeVariant(status: ExtendedStatus | null): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'processing':
      return 'default';
    case 'failed':
      return 'destructive';
    case 'completed':
      return 'outline';
    default:
      return 'secondary';
  }
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
      <Card className="shadow-lg border-red-200 dark:border-red-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
            <XCircle className="w-6 h-6" />
            {state.status === 'cancelled' ? 'Processing Cancelled' : 'Processing Failed'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-800 dark:text-red-200 mb-4">
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
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
          {state.status === 'cancelling' ? 'Cancelling...' : 'Processing Video'}
        </CardTitle>
        <CardDescription>
          Video ID: {state.jobId}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Status:</span>
          <Badge variant={getBadgeVariant(state.status)}>
            {state.status}
          </Badge>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Progress</span>
            <span className="text-muted-foreground">{state.progress}%</span>
          </div>
          <Progress value={state.progress} className="h-2" />
        </div>

        {state.currentStep && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
            <p className="text-sm text-blue-800 dark:text-blue-200 font-medium">
              {state.currentStep}
            </p>
          </div>
        )}

        <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-md">
          <p className="text-sm text-amber-800 dark:text-amber-200">
            <Clock className="inline w-4 h-4 mr-1" />
            Cancellation may take a few moments.
          </p>
        </div>

        {state.language && state.templateType && (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Language:</span>
              <p className="font-medium">{state.language === 'en' ? 'English' : 'Arabic'}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Template:</span>
              <p className="font-medium capitalize">{state.templateType}</p>
            </div>
          </div>
        )}

        <Button
          onClick={handleCancel}
          variant="destructive"
          className="w-full"
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

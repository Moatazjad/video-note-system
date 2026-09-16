'use client';

import { VideoForm } from '@/components/VideoForm';
import { ProcessingStatus } from '@/components/ProcessingStatus';
import { ResultDisplay } from '@/components/ResultDisplay';
import { useVideoJob } from '@/hooks/useVideoJob';

export default function Home() {
  const { 
    state, 
    startProcessing, 
    cancelProcessing, 
    reset, 
    isProcessing, 
    isComplete 
  } = useVideoJob();

  return (
    <main className="relative min-h-screen overflow-hidden bg-background">
      <div
        className="bg-glow -top-40 -right-32 h-[420px] w-[420px] opacity-35"
        style={{ backgroundImage: "radial-gradient(circle at 30% 30%, var(--accent-grad-1), transparent 70%)" }}
      />
      <div
        className="bg-glow -bottom-48 -left-32 h-[380px] w-[380px] opacity-25"
        style={{ backgroundImage: "radial-gradient(circle at 60% 60%, var(--accent-grad-2), transparent 70%)" }}
      />
      <div className="relative container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="mb-10">
            <div className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
              Video Note System
            </div>
            <h1 className="mt-2 font-display text-3xl font-bold text-foreground">
              Process a video
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Paste a YouTube link — get structured notes back.
            </p>
          </div>

          {/* Main Content - State-based rendering */}
          {!state.jobId ? (
            // No job: Show form
            <VideoForm 
              onSubmit={startProcessing}
              isSubmitting={isProcessing}
            />
          ) : isComplete && state.result ? (
            // Job complete with result: Show result
            <ResultDisplay 
              result={state.result}
              onReset={reset} 
            />
          ) : (
            // Job in progress: Show status
            <ProcessingStatus
              state={state}
              onCancel={cancelProcessing}
              onReset={reset}
            />
          )}
        </div>
      </div>
    </main>
  );
}
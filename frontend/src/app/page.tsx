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
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Video Note System
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-300">
              Transform educational videos into structured notes
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
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, TriangleAlert } from 'lucide-react';
import { cn } from '@/lib/utils';
import { validateVideoRequest } from '@/lib/validation';
import type { VideoProcessRequest, Language, TemplateType } from '@/types/video';

interface VideoFormProps {
  onSubmit: (request: VideoProcessRequest) => Promise<void>;
  isSubmitting: boolean;
}

function Segmented<T extends string>({
  options,
  value,
  onChange,
  disabled,
}: {
  options: { value: T; label: string }[];
  value: T;
  onChange: (value: T) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex w-fit rounded-lg border border-border overflow-hidden">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          disabled={disabled}
          onClick={() => onChange(opt.value)}
          className={cn(
            'px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50',
            value === opt.value
              ? 'grad-accent-bg text-[oklch(0.14_0.02_265)]'
              : 'bg-transparent text-muted-foreground hover:text-foreground'
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export function VideoForm({ onSubmit, isSubmitting }: VideoFormProps) {
  const [formData, setFormData] = useState<VideoProcessRequest>({
    url: '',
    language: 'en',
    template_type: 'educational',
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const validationError = validateVideoRequest(
      formData.url,
      formData.start_time,
      formData.end_time
    );

    if (validationError) {
      setError(validationError.message);
      return;
    }

    try {
      await onSubmit(formData);
    } catch (err) {
      setError('Failed to start processing');
    }
  };

  return (
    <Card className="border-border/60 bg-card/90 backdrop-blur-md shadow-xl">
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Video URL</label>
            <Input
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              required
              disabled={isSubmitting}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Start time (sec)</label>
              <Input
                type="number"
                placeholder="0"
                min="0"
                value={formData.start_time || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  start_time: e.target.value ? Number(e.target.value) : undefined
                })}
                disabled={isSubmitting}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">End time (sec)</label>
              <Input
                type="number"
                placeholder="Max 7200"
                min="0"
                max="7200"
                value={formData.end_time || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  end_time: e.target.value ? Number(e.target.value) : undefined
                })}
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="flex items-start gap-2.5 rounded-lg border border-primary/30 bg-primary/10 p-3">
            <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <p className="text-sm text-foreground">2 hour limit per video.</p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Language</label>
            <Segmented
              options={[
                { value: 'en', label: 'English' },
                { value: 'ar', label: 'العربية' },
              ]}
              value={formData.language as Language}
              onChange={(value) => setFormData({ ...formData, language: value })}
              disabled={isSubmitting}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Note template</label>
            <Segmented
              options={[
                { value: 'educational', label: 'Educational' },
                { value: 'business', label: 'Business' },
                { value: 'research', label: 'Research' },
              ]}
              value={formData.template_type as TemplateType}
              onChange={(value) => setFormData({ ...formData, template_type: value })}
              disabled={isSubmitting}
            />
          </div>

          {error && (
            <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-4">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            className="grad-accent-bg glow-accent w-full border-0 text-[oklch(0.14_0.02_265)] hover:opacity-90"
            disabled={isSubmitting}
            size="lg"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting Processing...
              </>
            ) : (
              'Generate Notes'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

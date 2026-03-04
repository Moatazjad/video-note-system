'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Video } from 'lucide-react';
import { validateVideoRequest } from '@/lib/validation';
import type { VideoProcessRequest, Language, TemplateType } from '@/types/video';

interface VideoFormProps {
  onSubmit: (request: VideoProcessRequest) => Promise<void>;
  isSubmitting: boolean;
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
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Video className="w-6 h-6" />
          Process Video
        </CardTitle>
        <CardDescription>
          Enter a YouTube URL to generate structured notes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Video URL</label>
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
              <label className="text-sm font-medium">Start Time (seconds)</label>
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
              <label className="text-sm font-medium">End Time (seconds)</label>
              <Input
                type="number"
                placeholder="Max 1200 (20 min)"
                min="0"
                max="1200"
                value={formData.end_time || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  end_time: e.target.value ? Number(e.target.value) : undefined
                })}
                disabled={isSubmitting}
              />
            </div>
          </div>

          <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-md">
            <p className="text-sm text-amber-800 dark:text-amber-200">
              ⚠️ <strong>Limit:</strong> Videos are limited to 20 minutes max.
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Language</label>
            <Select
              value={formData.language}
              onValueChange={(value: Language) => setFormData({ ...formData, language: value })}
              disabled={isSubmitting}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="ar">Arabic</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Note Template</label>
            <Select
              value={formData.template_type}
              onValueChange={(value: TemplateType) =>
                setFormData({ ...formData, template_type: value })
              }
              disabled={isSubmitting}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="educational">Educational</SelectItem>
                <SelectItem value="business">Business</SelectItem>
                <SelectItem value="research">Research</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
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

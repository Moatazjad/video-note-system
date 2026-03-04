/**
 * Strict type definitions for video processing.
 */

// Frontend JobStatus (backend 'queued' normalized to 'pending')
export type JobStatus = 
  | 'pending'
  | 'processing' 
  | 'completed'
  | 'failed'
  | 'cancelled';

// Extended status for UI-only states
export type ExtendedStatus = JobStatus | 'cancelling';

export type Language = 'en' | 'ar';

export type TemplateType = 'educational' | 'business' | 'research';

export interface VideoProcessRequest {
  url: string;
  start_time?: number;
  end_time?: number;
  language: Language;
  template_type: TemplateType;
}

export interface VideoStatus {
  id: number;
  url: string;
  status: JobStatus;
  progress: number;
  current_step: string | null;
  language: Language;
  template_type: TemplateType;
  created_at: string;
  updated_at: string;
  error_message: string | null;
}

export interface VideoResult {
  id: number;
  url: string;
  status: JobStatus;
  notes: string | null;
  detected_language: string | null;
  duration: number | null;
  created_at: string;
  markdown_url: string | null;
  pdf_url: string | null;
}

export interface VideoJobState {
  jobId: number | null;
  status: ExtendedStatus | null;
  progress: number;
  currentStep: string | null;
  error: string | null;
  language: Language | null;
  templateType: TemplateType | null;
  result: VideoResult | null;
}
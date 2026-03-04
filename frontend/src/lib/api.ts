import axios, { AxiosError } from 'axios';
import type { VideoProcessRequest, VideoStatus, VideoResult, JobStatus } from '@/types/video';

// Fail fast - no silent fallbacks in production
const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

if (!BASE_URL) {
  throw new Error('NEXT_PUBLIC_API_URL environment variable is not defined');
}

const client = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

/**
 * Normalize backend status to frontend JobStatus.
 * Handles backend inconsistencies (e.g., 'queued' → 'pending').
 */
function normalizeStatus(status: string): JobStatus {
  // Map backend variations
  if (status === 'queued') return 'pending';
  
  // Validate it's a known status
  const validStatuses: JobStatus[] = [
    'pending', 'processing', 'completed', 'failed', 'cancelled'
  ];
  
  if (validStatuses.includes(status as JobStatus)) {
    return status as JobStatus;
  }
  
  // Fallback for unknown statuses
  console.warn(`Unknown status from backend: ${status}, defaulting to 'processing'`);
  return 'processing';
}

export const api = {
  async processVideo(data: VideoProcessRequest): Promise<VideoStatus> {
    const response = await client.post<VideoStatus>('/process', data);
    return {
      ...response.data,
      status: normalizeStatus(response.data.status),
    };
  },

  async getStatus(videoId: number, signal?: AbortSignal): Promise<VideoStatus> {
    const response = await client.get<VideoStatus>(`/status/${videoId}`, { signal });
    return {
      ...response.data,
      status: normalizeStatus(response.data.status),
    };
  },

  async getResult(videoId: number, signal?: AbortSignal): Promise<VideoResult> {
    const response = await client.get<VideoResult>(`/result/${videoId}`, { signal });
    return response.data;
  },

  async cancelProcessing(videoId: number): Promise<void> {
    await client.delete(`/process/${videoId}`);
  },

  getDownloadUrl(path: string): string {
    return `${BASE_URL}${path}`;
  },
};

// Add response interceptor for future enhancements
client.interceptors.response.use(
  response => response,
  error => {
    // Future: add auth, logging, tracing here
    return Promise.reject(error);
  }
);

export { AxiosError };
export { axios };
/**
 * Client-side validation that mirrors backend rules.
 */

const YOUTUBE_DOMAINS = [
  'youtube.com',
  'www.youtube.com',
  'm.youtube.com',
  'youtu.be',
];

const MAX_DURATION = 1200; // 20 minutes in seconds

export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Extract video ID from YouTube URL.
 */
function extractVideoId(url: URL): string | null {
  const domain = url.hostname.toLowerCase();
  
  if (domain.includes('youtube.com') && url.pathname === '/watch') {
    return url.searchParams.get('v');
  }
  
  if (domain === 'youtu.be') {
    const id = url.pathname.slice(1).split('/')[0];
    return id || null;
  }
  
  if (domain.includes('youtube.com') && url.pathname.startsWith('/shorts/')) {
    return url.pathname.split('/shorts/')[1]?.split('/')[0] || null;
  }
  
  if (domain.includes('youtube.com') && url.pathname.startsWith('/embed/')) {
    return url.pathname.split('/embed/')[1]?.split('/')[0] || null;
  }
  
  return null;
}

export function validateYouTubeUrl(url: string): ValidationError | null {
  try {
    const parsed = new URL(url);
    const domain = parsed.hostname.toLowerCase();
    
    if (!YOUTUBE_DOMAINS.includes(domain)) {
      return {
        field: 'url',
        message: 'Only YouTube URLs are supported',
      };
    }
    
    const videoId = extractVideoId(parsed);
    if (!videoId || videoId.length < 6) {
      return {
        field: 'url',
        message: 'Invalid YouTube URL - no video ID found',
      };
    }
    
    return null;
  } catch {
    return {
      field: 'url',
      message: 'Invalid URL format',
    };
  }
}

export function validateTimeSegment(
  startTime?: number,
  endTime?: number
): ValidationError | null {
  if (startTime !== undefined && endTime !== undefined) {
    if (endTime <= startTime) {
      return {
        field: 'end_time',
        message: 'End time must be greater than start time',
      };
    }
    
    const duration = endTime - startTime;
    if (duration > MAX_DURATION) {
      return {
        field: 'end_time',
        message: `Video segment cannot exceed ${MAX_DURATION / 60} minutes`,
      };
    }
  }
  
  return null;
}

export function validateVideoRequest(
  url: string,
  startTime?: number,
  endTime?: number
): ValidationError | null {
  const urlError = validateYouTubeUrl(url);
  if (urlError) return urlError;
  
  const timeError = validateTimeSegment(startTime, endTime);
  if (timeError) return timeError;
  
  return null;
}
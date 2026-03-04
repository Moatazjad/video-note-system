'use client';

import { useEffect, useReducer, useCallback } from 'react';
import { api, axios } from '@/lib/api';
import { extractApiError } from '@/lib/api-error';
import type {
  VideoProcessRequest,
  VideoJobState,
  ExtendedStatus,
  Language,
  TemplateType,
  JobStatus,
  VideoResult,
} from '@/types/video';

type Action =
  | {
      type: 'JOB_CREATED';
      payload: {
        jobId: number;
        language: Language;
        templateType: TemplateType;
      };
    }
  | {
      type: 'STATUS_UPDATED';
      payload: {
        status: JobStatus;
        progress: number;
        currentStep: string | null;
      };
    }
  | { type: 'CANCEL_REQUESTED' }
  | { type: 'RESULT_LOADED'; payload: VideoResult }
  | { type: 'ERROR'; payload: string }
  | { type: 'RESET' };

const initialState: VideoJobState = {
  jobId: null,
  status: null,
  progress: 0,
  currentStep: null,
  error: null,
  language: null,
  templateType: null,
  result: null,
};

function reducer(state: VideoJobState, action: Action): VideoJobState {
  switch (action.type) {
    case 'JOB_CREATED':
      return {
        ...state,
        jobId: action.payload.jobId,
        status: 'pending',
        progress: 0,
        language: action.payload.language,
        templateType: action.payload.templateType,
        error: null,
        result: null,
      };

    case 'STATUS_UPDATED':
      return {
        ...state,
        status: action.payload.status,
        progress: action.payload.progress,
        currentStep: action.payload.currentStep,
      };

    case 'CANCEL_REQUESTED':
      return {
        ...state,
        status: 'cancelling',
        currentStep: 'Cancelling...',
      };

    case 'RESULT_LOADED':
      return {
        ...state,
        result: action.payload,
      };

    case 'ERROR':
      return {
        ...state,
        error: action.payload,
        status: 'failed',
      };

    case 'RESET':
      return initialState;

    default:
      return state;
  }
}

export function useVideoJob() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const startProcessing = useCallback(async (request: VideoProcessRequest) => {
    try {
      const result = await api.processVideo(request);
      dispatch({
        type: 'JOB_CREATED',
        payload: {
          jobId: result.id,
          language: result.language,
          templateType: result.template_type,
        },
      });
    } catch (error) {
      dispatch({ type: 'ERROR', payload: extractApiError(error) });
    }
  }, []);

  const cancelProcessing = useCallback(async () => {
    if (!state.jobId) return;

    try {
      dispatch({ type: 'CANCEL_REQUESTED' });
      await api.cancelProcessing(state.jobId);
    } catch (error) {
      dispatch({ type: 'ERROR', payload: extractApiError(error) });
    }
  }, [state.jobId]);

  const reset = useCallback(() => {
    dispatch({ type: 'RESET' });
  }, []);

  useEffect(() => {
    if (!state.jobId) return;

    let active = true;
    const controller = new AbortController();

    const fetchStatus = async () => {
      if (!active) return;

      try {
        const status = await api.getStatus(state.jobId!, controller.signal);

        if (!active) return;

        dispatch({
          type: 'STATUS_UPDATED',
          payload: {
            status: status.status,
            progress: status.progress,
            currentStep: status.current_step,
          },
        });

        const isTerminal =
          status.status === 'completed' ||
          status.status === 'failed' ||
          status.status === 'cancelled';

        if (status.status === 'completed' && active) {
          try {
            const result = await api.getResult(state.jobId!, controller.signal);
            if (active) {
              dispatch({ type: 'RESULT_LOADED', payload: result });
            }
          } catch (resultError) {
            if (!axios.isCancel(resultError)) {
              console.error('Failed to fetch result:', resultError);
            }
          }
        }

        if (isTerminal) {
          stop();
        }
      } catch (error) {
        if (!active) return;

        if (axios.isCancel(error)) return;

        dispatch({ type: 'ERROR', payload: extractApiError(error) });
        stop();
      }
    };

    const stop = () => {
      active = false;
      controller.abort();
      clearInterval(interval);
    };

    fetchStatus();

    const interval: ReturnType<typeof setInterval> = setInterval(fetchStatus, 2000);

    return () => {
      stop();
    };
  }, [state.jobId]);

  const isTerminal = (status: ExtendedStatus | null): boolean => {
    return status === 'completed' || status === 'failed' || status === 'cancelled';
  };

  return {
    state,
    startProcessing,
    cancelProcessing,
    reset,
    isProcessing: state.status === 'processing' || state.status === 'pending' || state.status === 'cancelling',
    isComplete: state.status === 'completed',
    isFailed: state.status === 'failed' || state.status === 'cancelled',
    isTerminal: isTerminal(state.status),
  };
}

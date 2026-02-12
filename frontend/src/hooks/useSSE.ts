import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { getCurrentUserToken } from '../firebase/auth';
import { API_BASE_URL } from '../config';

export type SSEConnectionState =
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'disconnected'
  | 'failed';

const SSE_URL = `${API_BASE_URL}/api/v1/events`;
const INITIAL_RETRY_DELAY = 1000;
const MAX_RETRY_DELAY = 30000;
const MAX_RETRIES = 5;

export function useSSE(currentUserEmail?: string) {
  const queryClient = useQueryClient();
  const [connectionState, setConnectionState] =
    useState<SSEConnectionState>('disconnected');
  const eventSourceRef = useRef<EventSource | null>(null);
  const retryCountRef = useRef(0);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Refs avoid stale closures for mutable state in event handlers
  const queryClientRef = useRef(queryClient);
  queryClientRef.current = queryClient;
  const currentUserEmailRef = useRef(currentUserEmail);
  currentUserEmailRef.current = currentUserEmail;

  useEffect(() => {
    const cleanup = () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
        retryTimeoutRef.current = null;
      }
    };

    // Security note: Token is passed via query param because the EventSource API
    // cannot set custom headers. Accepted trade-off for this internal tool (5 users).
    const connect = async () => {
      cleanup();

      const token = await getCurrentUserToken();
      if (!token) {
        setConnectionState('disconnected');
        return;
      }

      setConnectionState(
        retryCountRef.current > 0 ? 'reconnecting' : 'connecting',
      );

      const url = `${SSE_URL}?token=${encodeURIComponent(token)}`;
      const es = new EventSource(url);
      eventSourceRef.current = es;

      es.onopen = () => {
        retryCountRef.current = 0;
        setConnectionState('connected');
      };

      // SSE is a notification signal — invalidate queries to trigger refetch
      es.addEventListener('sync_status', () => {
        queryClientRef.current.invalidateQueries({ queryKey: ['syncStatus'] });
        queryClientRef.current.invalidateQueries({ queryKey: ['brands'] });
      });

      es.addEventListener('new_evaluation', (event: MessageEvent) => {
        // Always invalidate — history list should refresh for any new evaluation
        queryClientRef.current.invalidateQueries({ queryKey: ['evaluations'] });

        // Show toast only for OTHER users' evaluations
        try {
          const data = JSON.parse(event.data);
          if (data.evaluator && data.evaluator !== currentUserEmailRef.current) {
            const name = data.evaluator.split('@')[0];
            toast.info(
              `New evaluation: ${data.brand_name} (${data.score}) by ${name}`,
              { duration: 5000 },
            );
          }
        } catch {
          // Malformed event data — ignore, query invalidation already fired
        }
      });

      es.onerror = () => {
        es.close();
        eventSourceRef.current = null;

        if (retryCountRef.current >= MAX_RETRIES) {
          setConnectionState('failed');
          return;
        }

        setConnectionState('reconnecting');

        // Exponential backoff with jitter
        const delay = Math.min(
          INITIAL_RETRY_DELAY * Math.pow(2, retryCountRef.current),
          MAX_RETRY_DELAY,
        );
        const jitter = delay * (0.5 + Math.random() * 0.5);

        retryCountRef.current += 1;
        retryTimeoutRef.current = setTimeout(() => {
          connect();
        }, jitter);
      };
    };

    connect();
    return cleanup;
  }, []); // eslint-disable-line react-hooks/exhaustive-deps -- refs handle mutable state

  return { connectionState };
}

import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getCurrentUserToken } from '../firebase/auth';

export type SSEConnectionState =
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'disconnected'
  | 'failed';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const SSE_URL = `${BASE_URL}/api/v1/events`;
const INITIAL_RETRY_DELAY = 1000;
const MAX_RETRY_DELAY = 30000;
const MAX_RETRIES = 5;

export function useSSE() {
  const queryClient = useQueryClient();
  const [connectionState, setConnectionState] =
    useState<SSEConnectionState>('disconnected');
  const eventSourceRef = useRef<EventSource | null>(null);
  const retryCountRef = useRef(0);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Ref avoids stale closure for queryClient in event handlers
  const queryClientRef = useRef(queryClient);
  queryClientRef.current = queryClient;

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

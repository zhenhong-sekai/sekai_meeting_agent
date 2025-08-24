'use client';

import { useState, useEffect } from 'react';
import QueryForm from '@/components/QueryForm';
import EventLog from '@/components/EventLog';
import TestSSE from '@/components/TestSSE';
import { SSEEvent } from '@/types/sse';

export default function Home() {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);

  const parseSSEMessage = (event: MessageEvent): SSEEvent | null => {
    console.log('[Client] Received SSE event:', event);
    console.log('[Client] Event type:', event.type);
    console.log('[Client] Event data:', event.data);
    
    if (event.data) {
      try {
        const parsedData = JSON.parse(event.data);
        const result = {
          event: event.type,
          data: parsedData
        };
        console.log('[Client] Parsed SSE event:', result);
        return result;
      } catch (e) {
        console.error('Failed to parse SSE data:', e);
        return null;
      }
    }

    return null;
  };

  const handleSendQuery = async (query: string) => {
    setIsLoading(true);
    setEvents([]);

    // Close any existing EventSource
    if (eventSource) {
      eventSource.close();
    }

    try {
      // Use EventSource for SSE (more reliable than fetch with reader)
      const source = new EventSource(`/api/query?query=${encodeURIComponent(query)}`);
      setEventSource(source);

      source.onopen = () => {
        console.log('[Client] SSE connection opened');
      };

      source.onmessage = (event) => {
        console.log('[Client] SSE message received:', event);
        const parsedEvent = parseSSEMessage(event);
        if (parsedEvent) {
          setEvents(prev => [...prev, parsedEvent]);
        }
      };

      source.addEventListener('start', (event) => {
        console.log('[Client] Start event received:', event);
        const parsedEvent = parseSSEMessage(event);
        if (parsedEvent) {
          setEvents(prev => [...prev, parsedEvent]);
        }
      });

      source.addEventListener('node_update', (event) => {
        console.log('[Client] Node update event received:', event);
        const parsedEvent = parseSSEMessage(event);
        if (parsedEvent) {
          setEvents(prev => [...prev, parsedEvent]);
        }
      });

      source.addEventListener('completion', (event) => {
        console.log('[Client] Completion event received:', event);
        const parsedEvent = parseSSEMessage(event);
        if (parsedEvent) {
          setEvents(prev => [...prev, parsedEvent]);
        }
        source.close();
        setEventSource(null);
        setIsLoading(false);
      });

      source.addEventListener('error', (event) => {
        console.error('[Client] SSE error:', event);
        setEvents(prev => [...prev, {
          event: 'error',
          data: {
            error: 'SSE connection error',
            timestamp: Date.now() / 1000
          }
        }]);
        source.close();
        setEventSource(null);
        setIsLoading(false);
      });

    } catch (error) {
      console.error('Error:', error);
      setEvents(prev => [...prev, {
        event: 'error',
        data: {
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: Date.now() / 1000
        }
      }]);
      setIsLoading(false);
    }
  };

  const handleTestSSE = async () => {
    setIsTesting(true);
    setEvents([]);

    // Close any existing EventSource
    if (eventSource) {
      eventSource.close();
    }

    try {
      const source = new EventSource('/api/test-sse');
      setEventSource(source);

      source.onopen = () => {
        console.log('[Client] Test SSE connection opened');
      };

      source.onmessage = (event) => {
        console.log('[Client] Test SSE message received:', event);
        const parsedEvent = parseSSEMessage(event);
        if (parsedEvent) {
          setEvents(prev => [...prev, parsedEvent]);
        }
      };

      source.addEventListener('error', (event) => {
        console.error('[Client] Test SSE error:', event);
        setEvents(prev => [...prev, {
          event: 'error',
          data: {
            error: 'Test SSE connection error',
            timestamp: Date.now() / 1000
          }
        }]);
        source.close();
        setEventSource(null);
        setIsTesting(false);
      });

    } catch (error) {
      console.error('Error:', error);
      setEvents(prev => [...prev, {
        event: 'error',
        data: {
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: Date.now() / 1000
        }
      }]);
      setIsTesting(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [eventSource]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Meeting Agent UI
          </h1>
          <p className="text-lg text-gray-600">
            Real-time meeting agent workflow interface
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <TestSSE onTestSSE={handleTestSSE} isTesting={isTesting} />
            <QueryForm onSendQuery={handleSendQuery} isLoading={isLoading} />
          </div>
          <div className="lg:col-span-2">
            <EventLog events={events} />
          </div>
        </div>
      </div>
    </div>
  );
}

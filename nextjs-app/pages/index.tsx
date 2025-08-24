import { useState, useEffect } from 'react';
import { SSEEvent } from '../types/sse';

export default function Home() {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
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
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Test SSE</h2>
              <button
                onClick={handleTestSSE}
                className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Test SSE Connection
              </button>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Send Query</h2>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Enter your query..."
                  defaultValue="Help me get transcript of meeting AI Sharing and summarize it"
                  className="w-full p-2 border border-gray-300 rounded"
                  id="queryInput"
                />
                <button
                  onClick={() => {
                    const input = document.getElementById('queryInput') as HTMLInputElement;
                    handleSendQuery(input.value);
                  }}
                  disabled={isLoading}
                  className="w-full bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:bg-gray-400"
                >
                  {isLoading ? 'Processing...' : 'Send Query'}
                </button>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-2">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Event Log</h2>
              <div className="bg-gray-100 p-4 rounded max-h-96 overflow-y-auto">
                {events.length === 0 ? (
                  <p className="text-gray-500">No events yet. Try sending a query or testing SSE.</p>
                ) : (
                  <div className="space-y-2">
                    {events.map((event, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4 py-2 bg-white">
                        <div className="font-semibold text-sm text-gray-600">
                          {event.event} - {new Date(event.data.timestamp * 1000).toLocaleTimeString()}
                        </div>
                        <pre className="text-sm mt-1 whitespace-pre-wrap">
                          {JSON.stringify(event.data, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState, useEffect, useCallback } from 'react';

export default function Home() {
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [abortController, setAbortController] = useState(null);

  const parseSSEMessage = (message) => {
    console.log('[Client] Parsing SSE message:', message);
    const lines = message.split('\n');
    let eventType = 'message';
    let data = '';

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        eventType = line.substring(7);
      } else if (line.startsWith('data: ')) {
        data = line.substring(6);
      }
    }

    if (data) {
      try {
        const parsedData = JSON.parse(data);
        const result = {
          event: eventType,
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

  // Force immediate re-render by using a separate state for each event
  const addEvent = useCallback((event) => {
    console.log('[Client] Adding event to state:', event);
    setEvents(prev => {
      const newEvents = [...prev, event];
      console.log('[Client] New events array length:', newEvents.length);
      return newEvents;
    });
  }, []);

  const handleSendQuery = async (query) => {
    setIsLoading(true);
    setEvents([]);

    // Abort any existing request
    if (abortController) {
      abortController.abort();
    }

    const controller = new AbortController();
    setAbortController(controller);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/query?query=${encodeURIComponent(query)}`, {
        method: 'GET',
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        console.log('[Client] Received chunk:', chunk);
        const messages = chunk.split('\n\n').filter(msg => msg.trim());
        console.log('[Client] Parsed messages:', messages);

        for (const message of messages) {
          const event = parseSSEMessage(message);
          if (event) {
            addEvent(event);
            // Force a small delay to ensure React processes the update
            await new Promise(resolve => setTimeout(resolve, 10));
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was aborted');
      } else {
        console.error('Error:', error);
        addEvent({
          event: 'error',
          data: {
            error: error instanceof Error ? error.message : 'Unknown error',
            timestamp: Date.now() / 1000
          }
        });
      }
    } finally {
      setIsLoading(false);
      setAbortController(null);
    }
  };

  const handleTestSSE = async () => {
    setEvents([]);

    // Abort any existing request
    if (abortController) {
      abortController.abort();
    }

    const controller = new AbortController();
    setAbortController(controller);

    try {
      const response = await fetch('http://localhost:8000/api/v1/test-sse', {
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        console.log('[Client] Received chunk:', chunk);
        const messages = chunk.split('\n\n').filter(msg => msg.trim());
        console.log('[Client] Parsed messages:', messages);

        for (const message of messages) {
          const event = parseSSEMessage(message);
          if (event) {
            addEvent(event);
            // Force a small delay to ensure React processes the update
            await new Promise(resolve => setTimeout(resolve, 10));
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was aborted');
      } else {
        console.error('Error:', error);
        addEvent({
          event: 'error',
          data: {
            error: error instanceof Error ? error.message : 'Unknown error',
            timestamp: Date.now() / 1000
          }
        });
      }
    } finally {
      setAbortController(null);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortController) {
        abortController.abort();
      }
    };
  }, [abortController]);

  const renderEventContent = (event) => {
    const { event: eventType, data } = event;
    
    switch (eventType) {
      case 'start':
        return (
          <div style={{ padding: '1rem', backgroundColor: '#f0f9ff', borderRadius: '0.5rem', border: '1px solid #0ea5e9' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <div style={{ width: '8px', height: '8px', backgroundColor: '#0ea5e9', borderRadius: '50%' }}></div>
              <h3 style={{ margin: 0, color: '#0c4a6e', fontWeight: '600' }}>🚀 Workflow Started</h3>
            </div>
            <p style={{ margin: 0, color: '#0369a1' }}>{data.message}</p>
            <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem', color: '#64748b' }}>
              Query: "{data.query}"
            </p>
          </div>
        );

      case 'node_update':
        const { node, payload } = data;
        const nodeColors = {
          supervisor: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
          zoom: { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' },
          debrief: { bg: '#dcfce7', border: '#22c55e', text: '#166534' },
          notion: { bg: '#f3e8ff', border: '#a855f7', text: '#7c3aed' },
          log_summary: { bg: '#fef2f2', border: '#ef4444', text: '#991b1b' }
        };
        
        const nodeConfig = nodeColors[node] || { bg: '#f1f5f9', border: '#64748b', text: '#475569' };
        
        return (
          <div style={{ 
            padding: '1rem', 
            backgroundColor: nodeConfig.bg, 
            borderRadius: '0.5rem', 
            border: `1px solid ${nodeConfig.border}`,
            marginBottom: '1rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <div style={{ width: '8px', height: '8px', backgroundColor: nodeConfig.border, borderRadius: '50%' }}></div>
              <h3 style={{ margin: 0, color: nodeConfig.text, fontWeight: '600', textTransform: 'capitalize' }}>
                {node === 'log_summary' ? '📋 Final Summary' : `🤖 ${node} Agent`}
              </h3>
            </div>
            
            {payload.step_summary && payload.step_summary.length > 0 && (
              <div style={{ marginBottom: '0.75rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: nodeConfig.text, fontWeight: '500' }}>
                  Step Summary:
                </h4>
                <p style={{ margin: 0, color: nodeConfig.text, fontSize: '0.875rem' }}>
                  {payload.step_summary[payload.step_summary.length - 1]}
                </p>
              </div>
            )}

            {payload.next_step && (
              <div style={{ marginBottom: '0.75rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: nodeConfig.text, fontWeight: '500' }}>
                  Next Step:
                </h4>
                <p style={{ margin: 0, color: nodeConfig.text, fontSize: '0.875rem' }}>
                  {payload.next_step}
                </p>
              </div>
            )}

            {payload.summary && (
              <div style={{ marginBottom: '0.75rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: nodeConfig.text, fontWeight: '500' }}>
                  Summary:
                </h4>
                <p style={{ margin: 0, color: nodeConfig.text, fontSize: '0.875rem' }}>
                  {payload.summary}
                </p>
              </div>
            )}

            {payload.todo && (
              <div style={{ marginBottom: '0.75rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: nodeConfig.text, fontWeight: '500' }}>
                  Action Items:
                </h4>
                <p style={{ margin: 0, color: nodeConfig.text, fontSize: '0.875rem' }}>
                  {payload.todo}
                </p>
              </div>
            )}

            {payload.feedback && (
              <div>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: nodeConfig.text, fontWeight: '500' }}>
                  Feedback:
                </h4>
                <p style={{ margin: 0, color: nodeConfig.text, fontSize: '0.875rem' }}>
                  {payload.feedback}
                </p>
              </div>
            )}

            {payload.transcript_path && payload.transcript_path !== 'Not available' && (
              <div style={{ marginTop: '0.75rem', padding: '0.5rem', backgroundColor: 'rgba(255,255,255,0.5)', borderRadius: '0.25rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: nodeConfig.text, fontWeight: '500' }}>
                  📄 Transcript Path:
                </h4>
                <p style={{ margin: 0, color: nodeConfig.text, fontSize: '0.875rem', fontFamily: 'monospace' }}>
                  {payload.transcript_path}
                </p>
              </div>
            )}

            {payload.notion_parent_id && (
              <div style={{ marginTop: '0.75rem', padding: '0.5rem', backgroundColor: 'rgba(255,255,255,0.5)', borderRadius: '0.25rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: nodeConfig.text, fontWeight: '500' }}>
                  📝 Notion Page Created:
                </h4>
                <p style={{ margin: 0, color: nodeConfig.text, fontSize: '0.875rem', fontFamily: 'monospace' }}>
                  ID: {payload.notion_parent_id}
                </p>
              </div>
            )}
          </div>
        );

      case 'completion':
        return (
          <div style={{ padding: '1rem', backgroundColor: '#f0fdf4', borderRadius: '0.5rem', border: '1px solid #22c55e' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <div style={{ width: '8px', height: '8px', backgroundColor: '#22c55e', borderRadius: '50%' }}></div>
              <h3 style={{ margin: 0, color: '#166534', fontWeight: '600' }}>✅ Workflow Completed</h3>
            </div>
            <p style={{ margin: 0, color: '#15803d' }}>{data.message}</p>
            <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem', color: '#64748b' }}>
              Total Steps: {data.total_steps}
            </p>
          </div>
        );

      case 'test':
        return (
          <div style={{ padding: '1rem', backgroundColor: '#fef3c7', borderRadius: '0.5rem', border: '1px solid #f59e0b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <div style={{ width: '8px', height: '8px', backgroundColor: '#f59e0b', borderRadius: '50%' }}></div>
              <h3 style={{ margin: 0, color: '#92400e', fontWeight: '600' }}>🧪 Test Event</h3>
            </div>
            <p style={{ margin: 0, color: '#a16207' }}>{data.message}</p>
          </div>
        );

      case 'error':
        return (
          <div style={{ padding: '1rem', backgroundColor: '#fef2f2', borderRadius: '0.5rem', border: '1px solid #ef4444' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <div style={{ width: '8px', height: '8px', backgroundColor: '#ef4444', borderRadius: '50%' }}></div>
              <h3 style={{ margin: 0, color: '#991b1b', fontWeight: '600' }}>❌ Error</h3>
            </div>
            <p style={{ margin: 0, color: '#dc2626' }}>{data.error}</p>
          </div>
        );

      default:
        return (
          <div style={{ padding: '1rem', backgroundColor: '#f1f5f9', borderRadius: '0.5rem', border: '1px solid #64748b' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <div style={{ width: '8px', height: '8px', backgroundColor: '#64748b', borderRadius: '50%' }}></div>
              <h3 style={{ margin: 0, color: '#475569', fontWeight: '600', textTransform: 'capitalize' }}>{eventType}</h3>
            </div>
            <pre style={{ margin: 0, fontSize: '0.875rem', color: '#64748b', whiteSpace: 'pre-wrap' }}>
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        );
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '2rem' }}>
      <div style={{ maxWidth: '80rem', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
            Meeting Agent UI
          </h1>
          <p style={{ fontSize: '1.125rem', color: '#6b7280' }}>
            Real-time meeting agent workflow interface
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Test SSE</h2>
              <button
                onClick={handleTestSSE}
                style={{ width: '100%', backgroundColor: '#3b82f6', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer' }}
              >
                Test SSE Connection
              </button>
            </div>

            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Send Query</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <input
                  type="text"
                  placeholder="Enter your query..."
                  defaultValue="Help me get transcript of meeting AI Sharing and summarize it"
                  style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.25rem' }}
                  id="queryInput"
                />
                <button
                  onClick={() => {
                    const input = document.getElementById('queryInput');
                    handleSendQuery(input.value);
                  }}
                  disabled={isLoading}
                  style={{ 
                    width: '100%', 
                    backgroundColor: isLoading ? '#9ca3af' : '#10b981', 
                    color: 'white', 
                    padding: '0.5rem 1rem', 
                    borderRadius: '0.25rem', 
                    border: 'none', 
                    cursor: isLoading ? 'not-allowed' : 'pointer' 
                  }}
                >
                  {isLoading ? 'Processing...' : 'Send Query'}
                </button>
              </div>
            </div>
          </div>
          
          <div>
            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
                Workflow Progress ({events.length} events)
              </h2>
              <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '0.25rem', maxHeight: '32rem', overflowY: 'auto' }}>
                {events.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤖</div>
                    <p style={{ margin: 0, fontSize: '1.125rem' }}>No events yet</p>
                    <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem' }}>Try sending a query or testing SSE to see the workflow in action</p>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {events.map((event, index) => (
                      <div key={index}>
                        {renderEventContent(event)}
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

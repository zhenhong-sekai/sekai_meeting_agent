'use client';

import { useEffect, useRef } from 'react';
import { SSEEvent } from '@/types/sse';

interface EventLogProps {
  events: SSEEvent[];
}

export default function EventLog({ events }: EventLogProps) {
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [events]);

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'start':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'node_update':
        return 'bg-purple-50 border-purple-200 text-purple-800';
      case 'completion':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'test':
        return 'bg-orange-50 border-orange-200 text-orange-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  const renderEventContent = (event: SSEEvent) => {
    switch (event.event) {
      case 'start':
        return (
          <div>
            <div className="font-semibold">🚀 {event.data.message}</div>
            <div className="text-sm mt-1">Query: {event.data.query}</div>
          </div>
        );
      case 'node_update':
        return (
          <div>
            <div className="font-semibold">🤖 {event.data.node}</div>
            {event.data.payload && (
              <div className="text-sm mt-1">
                <pre className="whitespace-pre-wrap text-xs">
                  {JSON.stringify(event.data.payload, null, 2)}
                </pre>
              </div>
            )}
          </div>
        );
      case 'completion':
        return (
          <div>
            <div className="font-semibold">✅ {event.data.message}</div>
            <div className="text-sm mt-1">Total Steps: {event.data.total_steps}</div>
            {event.data.final_summary && (
              <div className="text-sm mt-2 p-2 bg-white rounded border">
                <div className="font-medium">Final Summary:</div>
                <div className="whitespace-pre-wrap">{event.data.final_summary}</div>
              </div>
            )}
          </div>
        );
      case 'error':
        return (
          <div>
            <div className="font-semibold">❌ Error</div>
            <div className="text-sm mt-1">{event.data.error}</div>
          </div>
        );
      case 'test':
        return (
          <div>
            <div className="font-semibold">🧪 {event.data.message}</div>
          </div>
        );
      default:
        return (
          <div>
            <div className="font-semibold">{event.event}</div>
            <div className="text-sm mt-1">
              <pre className="whitespace-pre-wrap text-xs">
                {JSON.stringify(event.data, null, 2)}
              </pre>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Event Log</h3>
        <p className="text-sm text-gray-500">
          {events.length} events received
        </p>
      </div>
      <div
        ref={logRef}
        className="h-96 overflow-y-auto p-4 space-y-3"
      >
        {events.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No events yet. Send a query to see the workflow in action!
          </div>
        ) : (
          events.map((event, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border ${getEventColor(event.event)}`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-medium uppercase tracking-wide">
                  {event.event}
                </span>
                <span className="text-xs text-gray-500">
                  {formatTimestamp(event.data.timestamp)}
                </span>
              </div>
              {renderEventContent(event)}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface QueryFormProps {
  onSendQuery: (query: string) => void;
  isLoading: boolean;
}

export default function QueryForm({ onSendQuery, isLoading }: QueryFormProps) {
  const [query, setQuery] = useState('Help me get transcript of meeting AI Sharing and summarize it');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSendQuery(query.trim());
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Send Query</h3>
        <p className="text-sm text-gray-500">
          Ask the meeting agent to help with your meeting tasks
        </p>
      </div>
      <form onSubmit={handleSubmit} className="p-4">
        <div className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Query
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query (e.g., 'Help me get transcript of meeting AI Sharing and summarize it')"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={3}
              disabled={isLoading}
            />
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Send Query
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { Play, Square } from 'lucide-react';

interface TestSSEProps {
  onTestSSE: () => void;
  isTesting: boolean;
}

export default function TestSSE({ onTestSSE, isTesting }: TestSSEProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Test SSE Connection</h3>
        <p className="text-sm text-gray-500">
          Test the Server-Sent Events connection
        </p>
      </div>
      <div className="p-4">
        <button
          onClick={onTestSSE}
          disabled={isTesting}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isTesting ? (
            <>
              <Square className="w-4 h-4 mr-2" />
              Testing...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Test SSE
            </>
          )}
        </button>
      </div>
    </div>
  );
}

/**
 * Example React Component using CallSage API
 *
 * To use:
 * 1. Generate TypeScript client: npx openapi-typescript-codegen --input ../openapi.yaml --output ./api
 * 2. Import this component in your React app
 * 3. Install axios: npm install axios
 */

import React, { useState } from 'react';
import axios from 'axios';

// TypeScript types (can be auto-generated from OpenAPI spec)
interface QueryResponse {
  success: boolean;
  request_id: string;
  response: string;
  confidence: number;
  sources?: Array<{
    document: string;
    chunk_id: string;
    relevance: number;
  }>;
  fallback_used: boolean;
  processing_time_ms: number;
}

interface ProcessResponse {
  success: boolean;
  request_id: string;
  transcript?: string;
  response: string;
  confidence: number;
  sources?: Array<{
    document: string;
    chunk_id: string;
    relevance: number;
  }>;
  guardrails?: Record<string, any>;
  processing_time_ms: number;
}

const API_BASE_URL = 'http://localhost:8000';

export function InsuranceChatComponent() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTextQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const { data } = await axios.post<QueryResponse>(`${API_BASE_URL}/query`, {
        text: query
      });

      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleAudioQuery = async (file: File) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audio', file);

      const { data } = await axios.post<ProcessResponse>(`${API_BASE_URL}/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Convert ProcessResponse to QueryResponse format for display
      setResponse({
        success: data.success,
        request_id: data.request_id,
        response: data.response,
        confidence: data.confidence,
        sources: data.sources,
        fallback_used: false,
        processing_time_ms: data.processing_time_ms
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>🛡️ Insurance Assistant</h1>

      {/* Text Input */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleTextQuery()}
            placeholder="Ask a question about your insurance policy..."
            style={{
              flex: 1,
              padding: '12px',
              fontSize: '16px',
              border: '1px solid #ddd',
              borderRadius: '8px'
            }}
            disabled={loading}
          />
          <button
            onClick={handleTextQuery}
            disabled={loading || !query.trim()}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              backgroundColor: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading || !query.trim() ? 0.6 : 1
            }}
          >
            {loading ? 'Asking...' : 'Ask'}
          </button>
        </div>
      </div>

      {/* Audio Input */}
      <div style={{ marginBottom: '20px' }}>
        <label
          htmlFor="audio-upload"
          style={{
            display: 'inline-block',
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: '#764ba2',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          🎤 Upload Audio Question
        </label>
        <input
          id="audio-upload"
          type="file"
          accept="audio/*"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleAudioQuery(file);
          }}
          style={{ display: 'none' }}
          disabled={loading}
        />
      </div>

      {/* Loading State */}
      {loading && (
        <div style={{
          padding: '20px',
          backgroundColor: '#f0f0f0',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <p>⏳ Processing your question...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div style={{
          padding: '20px',
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <p style={{ color: '#c00', margin: 0 }}>❌ Error: {error}</p>
        </div>
      )}

      {/* Response */}
      {response && !loading && (
        <div style={{
          padding: '20px',
          backgroundColor: '#f9f9f9',
          borderRadius: '8px',
          border: '1px solid #e0e0e0'
        }}>
          {/* Confidence Badge */}
          <div style={{ marginBottom: '16px' }}>
            <span style={{
              display: 'inline-block',
              padding: '4px 12px',
              backgroundColor: response.confidence > 0.85 ? '#4caf50' : response.confidence > 0.7 ? '#ff9800' : '#f44336',
              color: 'white',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              {(response.confidence * 100).toFixed(0)}% Confidence
            </span>
            <span style={{
              marginLeft: '12px',
              color: '#666',
              fontSize: '14px'
            }}>
              {response.processing_time_ms}ms
            </span>
          </div>

          {/* Response Text */}
          <div style={{
            padding: '16px',
            backgroundColor: 'white',
            borderRadius: '8px',
            marginBottom: '16px',
            lineHeight: '1.6'
          }}>
            {response.response}
          </div>

          {/* Sources */}
          {response.sources && response.sources.length > 0 && (
            <div>
              <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>📚 Sources:</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {response.sources.map((source, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '8px 12px',
                      backgroundColor: 'white',
                      borderRadius: '4px',
                      border: '1px solid #e0e0e0',
                      fontSize: '14px'
                    }}
                  >
                    <strong>{source.document}</strong>
                    <span style={{ color: '#666', marginLeft: '8px' }}>
                      ({(source.relevance * 100).toFixed(0)}% relevant)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Example Queries */}
      <div style={{ marginTop: '40px' }}>
        <h3>💡 Example Questions:</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {[
            'What does this insurance policy cover?',
            'How do I make a claim?',
            'What are the exclusions?',
            'What is the excess amount?'
          ].map((example, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(example);
                setResponse(null);
              }}
              style={{
                padding: '8px 16px',
                backgroundColor: 'white',
                border: '1px solid #667eea',
                color: '#667eea',
                borderRadius: '16px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default InsuranceChatComponent;

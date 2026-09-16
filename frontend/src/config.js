/**
 * API configuration for Anya frontend.
 * In development, defaults to backend running on port 5000.
 * In production (when served by Flask or reverse-proxied), defaults to relative path ('').
 * Can be explicitly overridden with the VITE_API_BASE environment variable.
 */
export const API_BASE = import.meta.env.VITE_API_BASE ?? (import.meta.env.DEV ? 'http://127.0.0.1:5000' : '');


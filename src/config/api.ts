const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    console.log('[API] Using custom API URL:', envUrl);
    return envUrl;
  }

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    console.log('[API] Development environment detected');
    return 'http://localhost:8000';
  }

  console.log('[API] Remote environment detected:', hostname);
  return `${protocol}//${hostname}:8000`;
};

export const API_BASE_URL = getApiBaseUrl();

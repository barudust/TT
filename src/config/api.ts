/**
 * Configuración de API
 * Detecta automáticamente la URL base según el ambiente
 *
 * Precedencia:
 * 1. Variable de entorno VITE_API_URL (desde .env.local)
 * 2. Detección automática según hostname
 */

export const getApiBaseUrl = (): string => {
  // 1. Usar variable de entorno si está definida
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    console.log('[API] Usando URL del .env.local:', envUrl);
    return envUrl;
  }

  // 2. Detección automática
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;

  // En desarrollo local (localhost)
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    console.log('[API] Ambiente local detectado');
    return 'http://localhost:8000';
  }

  // En ngrok o producción
  // Asume que la API está en el mismo dominio pero puerto 8000
  console.log('[API] Ambiente remoto detectado:', hostname);
  return `${protocol}//${hostname}:8000`;
};

export const API_BASE_URL = getApiBaseUrl();


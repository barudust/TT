/**
 * Configuración de API
 * Detecta automáticamente la URL base según el ambiente
 */

export const getApiBaseUrl = (): string => {
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;

  // En desarrollo local (localhost)
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }

  // En ngrok o producción
  // Asume que la API está en el mismo dominio pero puerto 8000
  // Ejemplo: https://abc123.ngrok-free.app:8000
  return `${protocol}//${hostname}:8000`;
};

export const API_BASE_URL = getApiBaseUrl();

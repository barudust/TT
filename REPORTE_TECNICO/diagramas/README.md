# Diagramas nuevos

Cada diagrama está en SVG (editable, Word 365 lo inserta directo) y PNG (al
doble de resolución). Todos comparten estilo: azul = plataforma, gris pizarra =
investigación, naranja = resultado principal / prueba, ámbar = validación.

| Archivo | Reemplaza | Va en |
|---|---|---|
| `D01_arquitectura` | Figura 1 (PostgreSQL, 6 capas) | 5.2 |
| `D02_investigacion_a_produccion` | Figura 2 (scripts 01–03 con selección por modelo) | 5.3 |
| `D03_actualizacion_diaria` | Figura 3 (ETL incremental, "46 features") | 5.4 |
| `D04_entidad_relacion` | Figura 4 (9 tablas) | 5.5 |
| `D05_pantallas` | Figura 5 (3 niveles) | 5.7 |
| `D06_secuencia` | Figura 6 (rutas `/api/...`, PostgreSQL) | 5.8 |
| `D07_despliegue` | — (nuevo) | 5.9 |
| `D08_etapas` | — (nuevo) | 4.1 |
| `D09_particiones` | Apoyo a la tabla de particiones (Tablas 3 y 8) | 4.7 |
| `D10_etiqueta` | — (nuevo) | 2.2 |
| `D11_protocolo` | — (nuevo) | 4.10 |
| `D12_mismas_filas` | — (nuevo) | 4.8 |

**Capturas de la plataforma:** tomarlas de https://tt-frontend-womf.onrender.com
(«Hoy», «Detalle», «Modelos», «Aprende») para acompañar `D05`.

**Para editar:** cambiar el texto en `fuente/diagramas_sistema.py` o
`fuente/diagramas_metodologia.py` y correr
`python REPORTE_TECNICO/diagramas/fuente/generar_diagramas.py` (usa Chrome o
Edge para el PNG). El script avisa si algún texto no cabe en su caja.

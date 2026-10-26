# 01 — Estructura propuesta del documento

> **Idea central:** contar el TT en el orden en que se defiende. El método
> que se describe en el capítulo 4 es el **protocolo final**; los
> resultados del capítulo 6 se presentan **por etapa**, con la Etapa 4 como
> resultado principal; TT1 aparece como punto de partida (Etapa 1) y sus
> decisiones abandonadas se explican en una o dos páginas, no en veinte.
>
> Si el equipo prefiere no mover secciones, la alternativa mínima está al
> final ("Plan B").

---

## 1. Índice propuesto

Columna "Viene de": sección del documento actual (21/10/2026) de donde sale
el contenido. **Nuevo** = no existe hoy.

| Nueva sección | Contenido | Viene de | Acción |
|---|---|---|---|
| Resumen / Abstract | Problema, método, **resultado**, plataforma, paper | Resumen | Reescribir (`textos/T01`) |
| **1. Introducción** | | 1 | |
| 1.1 Motivación | | 1.1 | Matizar (ver 1-02) |
| 1.2 Planteamiento del problema | Señal diaria de 3 clases; por qué clasificación | 1 (párrafos 3–4) | Mover y ampliar un poco |
| 1.3 Objetivos | General y 4 específicos | 1.2 | Conservar (están registrados) |
| 1.4 Alcance y limitaciones | | 1.3 | Actualizar periodo y modelos explorados |
| 1.5 Productos del trabajo | Plataforma desplegada, artículo MICAI, repositorio | **Nuevo** | `textos/T01` |
| 1.6 Organización del documento | | 1 (último párrafo) | Actualizar |
| **2. Marco teórico** | | 2 | |
| 2.1 Conceptos financieros | | 2.1 | Correcciones puntuales |
| 2.2 Generación de etiquetas | | 2.2 | Conservar |
| 2.3 Series de tiempo | | 2.3 | Correcciones puntuales |
| 2.4 Modelos de aprendizaje automático | LR multinomial con L2 y pesos de clase; XGBoost | 2.4 | Corregir fórmulas y el rol de la LR |
| 2.5 Modelos de aprendizaje profundo | | 2.5 | Corregir CNN (pooling) y quitar "la más viable" |
| 2.6 Métricas de evaluación | F1, matriz de confusión, **kappa, AUC, exactitud balanceada, log-loss** | 2.6 | Ampliar |
| 2.7 Simulación económica | Regla +1/−1/0, Sharpe, **costos y rotación** | 2.6.3 | Corregir |
| 2.8 Validación estadística | Bootstrap por bloques, permutación, Wilcoxon/signo | **Nuevo** | `textos/T02` |
| 2.9 Multicolinealidad y regularización | VIF, por qué L2 la maneja | **Nuevo** (sale de 4.4.2) | `textos/T02` |
| **3. Estado del arte** | | 3 | Correcciones puntuales (Tabla 1) |
| **4. Metodología** | | 4 | |
| 4.1 Marco de trabajo y etapas del proyecto | CRISP-DM + SCRUM + **las 6 etapas** (figura) | 4 (intro) | Ampliar (`textos/T04`, `diagramas/D08`) |
| 4.2 Pregunta de investigación e hipótesis | Con las tres redes; con prueba estadística | 4 (intro) | Corregir |
| 4.3 Datos | Fuente, periodo (2013–2025 + 2026 de validación), activos | 4.1 | Actualizar |
| 4.4 Preprocesamiento y etiqueta | | 4.2 | Corregir conteo y partición |
| 4.5 Características | 61 en 9 familias + 15 interacciones (producción) | 4.3 | Corregir conteo, agregar interacciones |
| 4.6 Mismo conjunto de características para todos los modelos | Justificación + multicolinealidad + evidencia (11 de 15) | 4.4 (reemplazo completo) | `textos/T03` |
| 4.7 Partición temporal y validaciones adicionales | A/B/C finales, prueba año por año, origen rodante, prueba ciega 2026 | 4.5 | Reescribir (`diagramas/D09`) |
| 4.8 Escalado y construcción de secuencias | RobustScaler; ventanas alineadas; mismas filas | 4.6, 4.7 | Reescribir |
| 4.9 Modelos | Configuración final (Etapa 4) de los cinco + líneas base | 4.8 | Reescribir (`tablas/T-05`) |
| 4.10 Protocolo de entrenamiento y búsqueda de hiperparámetros | Protocolo anidado dev/final, Optuna, semillas | 4.10 | Reescribir (`diagramas/D11`, `tablas/T-06`) |
| 4.11 Métricas y evaluación | Las ocho métricas para todos; costos | 4.9, 4.11 | Reescribir |
| 4.12 Criterio de selección del modelo | Declarado antes de mirar la prueba | **Nuevo** | `textos/T03` |
| **5. Diseño e implementación del sistema** | | 5 | Reescribir casi completo (`textos/T05`) |
| 5.1 Requerimientos y casos de uso | RF, RNF, CU-01 a CU-03 (los de TT1, actualizados) | TT1 §4.4 (no está en esta versión) | Recuperar y actualizar |
| 5.2 Arquitectura | Investigación fuera de línea / plataforma en línea | 5.1 | `diagramas/D01` |
| 5.3 Del modelo de investigación al de producción | `entrenar_produccion.py`, `.pkl`, versión | 5.2.1 | `diagramas/D02` |
| 5.4 Actualización diaria | Dentro de la API, 16:30 NY, recálculo completo | 5.2.2 | `diagramas/D03` |
| 5.5 Base de datos | SQLite, 4 tablas, normalización | 5.3.1 | `diagramas/D04` |
| 5.6 API REST | 9 GET + 1 POST; formato de respuesta | 5.3.2 | `tablas/T-14` |
| 5.7 Interfaz de usuario | 7 pantallas; seguridad en palabras; guía y glosario | 5.4 | `diagramas/D05` |
| 5.8 Integración cliente-servidor | Secuencia real; CORS; fechas | 5.5 | `diagramas/D06` |
| 5.9 Despliegue | Render (Docker + sitio estático), GitHub | **Nuevo** | `diagramas/D07` |
| 5.10 Pruebas | 24 pruebas automáticas + pruebas funcionales + estabilidad | 5.3.3, 5.5.5 | Homologar tono |
| 5.11 Cambios respecto al diseño de TT1 | Una tabla | **Nuevo** | `tablas/T-15` |
| **6. Experimentación y resultados** | | 6 | Reestructurar por etapas (`textos/T06`) |
| 6.1 Entorno de implementación | Hardware y versiones correctas | 6.1 | Corregir versiones |
| 6.2 Etapa 1: línea base (TT1) | Resumen de Tablas 15–18 en una tabla + por qué no es comparable | 6.2, 6.3, 6.4, 6.5 | Condensar a 1–2 páginas |
| 6.3 Etapa 2: primeras mejoras | Preselección de variables (11 de 15), más variables, ensambles | 6.6.1, 6.6.2, 6.6.4 | Resumir |
| 6.4 Etapa 3: comparación en igualdad de condiciones | 120 corridas; LR 0.399 promedio (paper §7) | **Nuevo** en el reporte | `tablas/T-07` |
| 6.5 Etapa 4: protocolo final — **resultado principal** | A/B/C con IC, ocho métricas, costos | 6.6.3 | `tablas/T-08` a `T-10`, `graficas/G01`–`G03` |
| 6.6 Robustez en el tiempo | Prueba año por año, permutación, prueba ciega 2026 | 6.6.7 | `tablas/T-12`, `T-13`, `graficas/G04`, `G05` |
| 6.7 Etapa 5: búsqueda de mejoras | Calibración, mezclas, SWA, interacciones; etiqueta fuera del planteamiento | 6.6.4–6.6.6 | Conservar con nombres de etapa |
| 6.8 Etapa 6: modelo de la plataforma | Global contra por acción, exceso de MANTENER, peso ×0.90, 2026, niveles de seguridad | 6.3.4, 6.6.7 | Ampliar |
| 6.9 Selección del modelo desplegado | Aplicación del criterio de 4.12 | **Nuevo** | `textos/T03` |
| **7. Conclusiones** | | 7 | Reescribir (`textos/T07`) |
| 7.1 Conclusiones generales | | 7.1 | |
| 7.2 Cumplimiento de objetivos | | 7.2 | |
| 7.3 Discusión | Por qué gana la LR; relación con la literatura | 7.3 | |
| 7.4 Limitaciones | Actualizadas | 7.4 | |
| 7.5 Trabajo futuro | El de TT1 ya se hizo; nuevo trabajo futuro | 7.5 | |
| Referencias | | Referencias | Completar (`correcciones/C08`) |
| **Anexo A.** Artículo publicado en MICAI 2026 | | **Nuevo** | `../PAPER_MICAI/05_INCLUSION_EN_EL_REPORTE.md` |
| **Anexo B.** Tabla completa de características (61 + 15) | Si la Tabla 4 se saca del cuerpo | Tabla 4 | Opcional |
| **Anexo C.** Reproducibilidad | Scripts por etapa, comandos, versiones, etiqueta de git | **Nuevo** | `tablas/T-16` |
| **Anexo D.** Manual de usuario | La guía rápida de la plataforma | §5.5.5 | Opcional; la guía vive en la pestaña «Ayuda» |

---

## 2. Qué se elimina o se reduce

| Sección actual | Páginas | Destino |
|---|---|---|
| §4.4 Selección de características por modelo (4.4.1–4.4.6, Tablas 5–7) | 46–51 | Se reduce a un párrafo en 6.2 (Etapa 1) + la evidencia de 6.3; la teoría de VIF pasa a 2.9 |
| Tabla 8 (repite la Tabla 3) | 52 | Eliminar; una sola tabla de particiones |
| §4.6.4 Normalización local de OHLCV | 54–55 | Un párrafo en 6.2 (Etapa 1): desde la Etapa 3 ninguna red los recibe |
| Tabla 9 (dimensiones con F_Exp) | 56 | Reemplazar por tensores (n, lookback, 61) |
| §5.5.2 y Tabla 14 (puertos locales) | 79 | Reducir a un párrafo de "ejecución local" dentro de 5.9 |
| §6.2–6.5 (resultados TT1 por activo) | 83–95 | Una sola tabla resumen (`tablas/T-01`) y dos párrafos en 6.2 |
| Tablas 25 y 27 (mejores Sharpe individuales; rangos por activo) | 92–93 | Eliminar o mandar a anexo; son resultados de TT1 elegidos entre 105 combinaciones |
| §6.6 (como sección "adicional") | 95–98 | Su contenido pasa a 6.3–6.8 como resultado central |

---

## 3. Figuras y tablas: inventario nuevo

### Figuras

| Nueva | Contenido | Reemplaza | Archivo |
|---|---|---|---|
| Fig. 1 | Etapas del proyecto | — | `diagramas/D08_etapas.svg` |
| Fig. 2 | Construcción de la etiqueta | — | `diagramas/D10_etiqueta.svg` |
| Fig. 3 | Particiones temporales y validaciones | Tablas 3 y 8 (como apoyo) | `diagramas/D09_particiones.svg` |
| Fig. 4 | Protocolo anidado dev/final | — | `diagramas/D11_protocolo.svg` |
| Fig. 5 | Mismas filas para los cinco modelos | — | `diagramas/D12_mismas_filas.svg` |
| Fig. 6 | Arquitectura del sistema | Fig. 1 actual | `diagramas/D01_arquitectura.svg` |
| Fig. 7 | Del entrenamiento a producción | Fig. 2 actual | `diagramas/D02_investigacion_a_produccion.svg` |
| Fig. 8 | Actualización diaria | Fig. 3 actual | `diagramas/D03_actualizacion_diaria.svg` |
| Fig. 9 | Modelo entidad-relación | Fig. 4 actual | `diagramas/D04_entidad_relacion.svg` |
| Fig. 10 | Mapa de pantallas | Fig. 5 actual | `diagramas/D05_pantallas.svg` |
| Fig. 11 | Diagrama de secuencia | Fig. 6 actual | `diagramas/D06_secuencia.svg` |
| Fig. 12 | Despliegue en Render | — | `diagramas/D07_despliegue.svg` |
| Fig. 13–18 | Gráficas de resultados | — (el documento no tiene) | `graficas/G01`–`G06` |
| — | Capturas de la plataforma | — | Tomarlas de https://tt-frontend-womf.onrender.com (ver `diagramas/README.md`) |

### Tablas

Todas las tablas nuevas están en `tablas/TABLAS_NUEVAS.md` (T-01 a T-16).
La numeración final dependerá del orden en el documento.

---

## 4. Plan B (si no se quiere mover la estructura)

Mínimo indispensable sin reordenar capítulos:

1. Corregir todos los puntos **CRÍTICO** de `correcciones/`.
2. En el capítulo 4, agregar al inicio de 4.4, 4.5, 4.8 y 4.10 un recuadro
   "Protocolo final (Etapas 3–4)" con lo que cambió, y marcar el resto como
   "diseño de TT1 (Etapa 1)".
3. En el capítulo 6, renombrar 6.2–6.5 como "Etapa 1 (TT1)" y convertir
   §6.6 en "Resultados finales" con las tablas T-08 a T-13.
4. Reescribir completo el capítulo 7 y el capítulo 5.

El Plan B deja un documento largo y que pide al lector descartar 40 páginas;
por eso se recomienda la estructura de la sección 1.

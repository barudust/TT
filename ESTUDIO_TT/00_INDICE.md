# Estudio del Trabajo Terminal — índice y orden de lectura

> **Para qué es esta carpeta.** Para estudiar el TT de principio a fin sin
> tener que saltar entre 30 archivos. Va de lo general a lo particular:
> primero la historia completa, después cada parte por separado (el modelo,
> el sistema, el paper) y al final las preguntas de la defensa.
>
> Cada documento explica los términos donde aparecen por primera vez. Si
> algo no queda claro, está en el [glosario](02_GLOSARIO.md).
>
> Las cifras se verificaron contra el código y los CSV del repositorio el
> 2026-10-12. Cuando un documento viejo dice otra cosa, manda este (ver
> "Correcciones" al final).
>
> **Punto de partida: el reporte de TT1** (`TT-Fin/TT1 (1.pdf`, 18 de mayo
> de 2026, 102 páginas). Todo lo que se hizo después se compara contra él en
> [D1](D_defensa/D1_TT1_VS_TT2.md). (El archivo `TT-Fin/TT1.pdf`, de abril,
> es un borrador anterior y no se usa.)

> **Carpetas hermanas:** la revisión del reporte técnico está en
> [`../REPORTE_TECNICO/`](../REPORTE_TECNICO/README.md) y todo lo del artículo de MICAI
> (incluida la presentación en el congreso) en [`../PAPER_MICAI/`](../PAPER_MICAI/README.md).

---

## Orden de lectura

### Parte 0 — Lo general (leer primero, en orden)

| # | Documento | Qué te da | Tiempo |
|---|---|---|---|
| 00 | [Resumen de todo](00_RESUMEN.md) | Una mirada rápida a todos los módulos (modelo, sistema, paper, defensa) con las cifras clave, antes de profundizar | 15 min |
| 01 | [Panorama general](01_PANORAMA_GENERAL.md) | Toda la historia del TT en un documento: qué problema, qué se hizo, qué salió, qué se decidió y por qué | 30 min |
| 02 | [Glosario](02_GLOSARIO.md) | Cada término (finanzas, ML, estadística, software) explicado en palabras simples. Úsalo como diccionario | consulta |
| 03 | [**Mapa de experimentos**](03_MAPA_DE_EXPERIMENTOS.md) | **La referencia única**: las 6 etapas, los experimentos A/B/C, qué usa el paper, qué se descartó, qué queda fuera del planteamiento y los puntos a cuidar. Usar estos nombres en el documento final | 20 min |

### Parte A — El modelo (camino de la investigación)

| # | Documento | Qué te da |
|---|---|---|
| A0 | [**Resumen de la sección**](A_modelo/A0_RESUMEN_MODELO.md) | A1–A7 en 10 minutos |
| A1 | [Datos y etiqueta](A_modelo/A1_DATOS_Y_ETIQUETA.md) | De dónde salen los datos, por qué esas 7 acciones y esos años, cómo se define COMPRAR/MANTENER/VENDER |
| A2 | [Las 76 variables](A_modelo/A2_VARIABLES.md) | Cada una de las 61 variables técnicas y las 15 interacciones, una por una: qué mide y por qué está |
| A3 | [Protocolo de entrenamiento y métricas](A_modelo/A3_PROTOCOLO_Y_METRICAS.md) | Cómo se separan los datos en el tiempo, cómo se eligen hiperparámetros, cómo se mide (F1, kappa, Sharpe…) y cómo se prueba que no es suerte |
| A4 | [Modelos clásicos: Regresión Logística y XGBoost](A_modelo/A4_MODELOS_CLASICOS.md) | Cómo funcionan, qué hiperparámetros ganaron y por qué |
| A5 | [Redes neuronales: LSTM, CNN 1D y CNN-LSTM](A_modelo/A5_REDES_NEURONALES.md) | Cómo se diseñó cada red, cuántas capas y parámetros, qué se probó y por qué no ganaron |
| A6 | [Las seis etapas del proyecto](A_modelo/A6_ETAPAS_DEL_PROYECTO.md) | Cada etapa: qué pregunta respondió, qué cambió, qué se descartó |
| A7 | [Resultados y límites](A_modelo/A7_RESULTADOS_Y_LIMITES.md) | Todas las cifras en un solo lugar y cómo leerlas con honestidad |

### Parte B — El sistema (camino de la ingeniería)

| # | Documento | Qué te da |
|---|---|---|
| B0 | [**Resumen de la sección**](B_sistema/B0_RESUMEN_SISTEMA.md) | B1–B5 en 7 minutos |
| B1 | [Arquitectura](B_sistema/B1_ARQUITECTURA.md) | El sistema completo de punta a punta y por qué está dividido así |
| B2 | [API](B_sistema/B2_API.md) | El backend en Flask: endpoints, flujo de datos, inferencia, programación de tareas |
| B3 | [Base de datos](B_sistema/B3_BASE_DE_DATOS.md) | Esquema, normalización (1FN–3FN), por qué SQLite, qué guarda y qué no |
| B4 | [Frontend](B_sistema/B4_FRONTEND.md) | La aplicación web: páginas, tecnologías, qué muestra y cómo |
| B5 | [Despliegue](B_sistema/B5_DESPLIEGUE.md) | Docker, gunicorn, Render, pruebas automáticas y problemas reales que se resolvieron |

### Parte C — El paper (producto extra)

| # | Documento | Qué te da |
|---|---|---|
| C0 | [**Resumen de la sección**](C_paper/C0_RESUMEN_PAPER.md) | El paper en 3 minutos |
| C1 | [El paper de MICAI 2026](C_paper/C1_PAPER_MICAI.md) | Qué es, qué dice, qué versión de los resultados usa, qué se cambió después y qué se mantuvo |

### Parte D — La defensa

| # | Documento | Qué te da |
|---|---|---|
| D0 | [**Resumen de la sección**](D_defensa/D0_RESUMEN_DEFENSA.md) | Las respuestas más probables en 10 minutos |
| D1 | [Del reporte de TT1 a TT2](D_defensa/D1_TT1_VS_TT2.md) | Qué entregaron en TT1 (mayo) y qué cambió después, con la sección del TT1 y la justificación de cada cambio. **Léelo antes de la defensa: los sinodales ya conocen el TT1** |
| D2 | [Preguntas generales y de planteamiento](D_defensa/D2_PREGUNTAS_GENERALES.md) | Contribución, alcance, objetivos, por qué este problema |
| D3 | [Preguntas de datos, etiqueta y variables](D_defensa/D3_PREGUNTAS_DATOS.md) | |
| D4 | [Preguntas de modelos clásicos y redes neuronales](D_defensa/D4_PREGUNTAS_MODELOS.md) | Diseño de las redes, capas, por qué ganó la LR |
| D5 | [Preguntas de estadística y validación](D_defensa/D5_PREGUNTAS_ESTADISTICA.md) | Significancia, sobreajuste, fuga de información |
| D6 | [Preguntas del sistema](D_defensa/D6_PREGUNTAS_SISTEMA.md) | API, base de datos, frontend, despliegue |
| D7 | [Preguntas del paper](D_defensa/D7_PREGUNTAS_PAPER.md) | |
| D8 | [Preguntas trampa y cómo responderlas](D_defensa/D8_PREGUNTAS_TRAMPA.md) | |
| D9 | [**Observaciones de la sinodal (26 oct) y respuestas**](D_defensa/D9_OBSERVACIONES_SINODAL.md) | Métricas iguales, cómo se elige el modelo, multicolinealidad, prueba ciega 2026 y párrafos para el reporte técnico |

---

## Cómo estudiar con esto

**Si tienes poco tiempo:** [00 Resumen](00_RESUMEN.md) y luego el resumen
de cada sección (A0, B0, C0, D0): unos 30 minutos en total.


1. **Primera vuelta (un día):** 01 completo y el resumen inicial de cada
   documento A y B. Con eso ya puedes contar el TT entero.
2. **Segunda vuelta:** los documentos A y B completos, con el glosario abierto.
3. **Semana de la defensa:** la parte D. Las respuestas repiten información
   de A y B a propósito: cada pregunta se entiende sola.
4. **Antes de cada respuesta difícil:** ten a mano el
   [resumen de cifras](A_modelo/A7_RESULTADOS_Y_LIMITES.md#1-la-tabla-que-hay-que-saberse).

## Qué es "el TT" y qué es "el paper"

- **El TT** es el trabajo completo: la comparación de los 5 modelos, todas
  las iteraciones etapas 1 a 6, los análisis posteriores (prueba año por año, exceso de
  MANTENER, evaluación en 2026) y la plataforma web.
- **El paper** (MICAI 2026) es un producto extra que publica una parte del TT:
  la comparación de los 5 modelos con la corrida de la Etapa 3 y la verificación con el
  protocolo de la Etapa 4. Suma valor y se puede usar en la defensa, pero el TT no
  depende de él. Detalle en [C1](C_paper/C1_PAPER_MICAI.md).

## Relación con los documentos que ya existían

Esta carpeta **no reemplaza** a los documentos técnicos; los ordena y los
explica. Si necesitas el detalle original:

| Tema | Documento original |
|---|---|
| Estado y pendientes | `STATUS.md`, `CONTEXTO.md` |
| Guía de defensa extensa (17 capítulos) | `RESULTADOS_OPTIMIZADOS/GUIA_DEFENSA_TT.md` |
| Todo lo probado (expediente) | `RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md` |
| Por qué el modelo llegó a su límite | `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md` |
| Análisis de MANTENER, global vs por acción, 2026 | `RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md` |
| Por qué las redes no aprendían | `RESULTADOS_OPTIMIZADOS/docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md` |
| Etapa 5 (búsqueda de mejoras) | `RESULTADOS_OPTIMIZADOS/docs/VIA7_REFINAMIENTO.md`, `VIA8_DATASET.md` (nombres viejos: Vía 7 y Vía 8) |
| API, métricas, frontend, BD, despliegue | `docs/API.md`, `docs/API_FRONTEND_METRICS.md`, `docs/FRONTEND.md`, `docs/DATABASE.md`, `docs/DEPLOY_RENDER.md` |
| Paper | `paper_review/README.md` |

## Correcciones respecto a documentos anteriores

Al verificar contra el código aparecieron estas diferencias. En esta carpeta
ya están corregidas; si citas un documento viejo, cuida estos puntos:

| Documento viejo dice | Lo correcto (verificado) | Fuente |
|---|---|---|
| La LSTM ganadora es bidireccional | La LSTM **del paper (Etapa 3)** sí era bidireccional; la **ganadora de Optuna (Etapa 4)** es **unidireccional** (`bidir=False`) | `RESULTADOS_OPTIMIZADOS/v5/ganadores_dl.json` |
| La LSTM de la Etapa 4 usa `criterio=val_f1` | Usa `val_loss`; el criterio `val_f1_ma3` lo eligió la CNN | ídem |
| LSTM ≈ 180 000–590 000 parámetros, CNN ≈ 50 000, CNN-LSTM ≈ 120 000 | Ganadoras de la Etapa 4: LSTM **198 480**, CNN **67 007**, CNN-LSTM **276 109**. Las de la Etapa 3: 592 131 / 160 835 / 301 699 | Contado con `crear_modelo()` de `scripts_opt/common_v5.py` |
| Las redes combinan semillas por voto mayoritario | Por **voto suave** (promedio de probabilidades), 5 semillas en la evaluación final | `common_v5.correr()`, `run_v5.cmd_final()` |
| XGBoost usa *early stopping* | No: el número de árboles lo elige Optuna; no hay paro temprano | `run_v5._fit_xgb()` |
| Bootstrap con 1 000 remuestreos | **2 000** remuestreos, bloques de **20 días** | `run_v5._bootstrap_bloques()` |
| Etapa 3: LR F1 = 0.404 | En la Etapa 3, Exp B global: LR **0.385**, XGBoost **0.386** (empate). El 0.404 es de la **Etapa 4** | `v4/resultados_v4.csv`, `v5/resultados_finales.csv` |
| La CNN-LSTM usa `pool_cnn=gap_gmp` | Ese parámetro no lo usa la CNN-LSTM (pasa la secuencia completa a la LSTM) | `CNNLSTMNet` en `common_v5.py` |
| La LR de investigación de la Etapa 4 usa SAGA | Con penalización L2 la investigación de la Etapa 4 usó **lbfgs**; SAGA se usa en producción y cuando hay L1/elasticnet | `run_v5._fit_lr()`, `entrenar_produccion.py` |
| API: 20 pruebas | **23** pruebas (`test_features` 6, `test_main` 12, `test_model` 5) | `api/tests/` |

### Hallazgo nuevo (2026-10-12): la ventana de las redes no incluye el último día

Ningún documento anterior lo menciona. En etapas 3 y 4, la ventana de entrada de
LSTM, CNN y CNN-LSTM son los días `[t − lookback, t − 1]`, y la etiqueta es
el movimiento de `t` a `t + 1`. Es decir, **las redes predicen sin ver las
variables del día t**, que la LR y XGBoost sí ven. No es fuga de información
(les falta un día, no les sobra), pero es una asimetría entre modelos.

**Cuánto pesa:** a la misma LR, quitarle el día *t* le baja el F1 de 0.393 a
0.386 en 2025 (−0.007). La brecha entre la LR y las redes en la Etapa 4 es de 0.03 a
0.045, y en la prueba año por año las redes quedan atrás por 0.02–0.06; además, su
pérdida de validación no baja del azar con ninguna configuración. La
asimetría no explica la diferencia, pero hay que conocerla. Ver
[A5 §7](A_modelo/A5_REDES_NEURONALES.md#7-una-asimetría-que-hay-que-conocer-la-ventana-termina-un-día-antes)
y `scripts_opt/verificar_ventana_redes.py`.

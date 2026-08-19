# Resultados v5 — protocolo corregido y búsqueda de hiperparámetros real

> **En ejecución (2026-08-14).** Este documento se va llenando conforme terminan
> las fases del plan (`PLAN_MAESTRO_BUSQUEDA.md`). Todo lo que aparece aquí sale
> de `RESULTADOS_OPTIMIZADOS/v5/` y es reproducible con `scripts_opt/run_v5.py`.

## Protocolo

El problema de v4 era que la selección (época del checkpoint, lookback) se hacía
mirando el mismo conjunto con el que después se reportaba. v5 separa tres roles:

| Modo | Entrena | Elige época | Decide configuración | Se reporta |
|---|---|---|---|---|
| `dev` | 2018–2022 | 2023 | **2024** | nada |
| `final` | 2018–2023 | 2024 | — | **2025 (una sola vez)** |

Toda la búsqueda —ablaciones y Optuna— ocurre en `dev`. El año 2025 no participa
en ninguna decisión: se evalúa una vez por configuración ya congelada, y cada
evaluación queda marcada en `v5/registro_runs.csv` (`es_evaluacion_en_test`).
(Los rangos son los de Exp B; A y C desplazan el inicio del train.)

Además, las ventanas se construyen sobre la serie continua y se asignan al split
por la fecha de la etiqueta. Verificado: con eso **los cinco modelos se evalúan
sobre exactamente las mismas 1 736 filas**, con cualquier lookback — antes los
profundos veían 1 596 (lb=20) o 1 316 (lb=60) frente a las 1 736 de LR/XGBoost.

---

## G0 — el pipeline nuevo reproduce v4 exactamente

Antes de cambiar nada hay que demostrar que el código nuevo no introduce
diferencias por su cuenta. Corriendo v5 con la configuración de v4
(`criterio=val_loss`, ventanas por split, sin refit, 3 semillas):

**18 de 18 celdas con delta = 0.0000** (3 arquitecturas × 3 experimentos × 2
lookbacks). No "dentro de tolerancia": idénticas.

```bash
python scripts_opt/run_v5.py replicar     # 8 min → v5/g0_replicacion.csv
```

### Hallazgo lateral: el resultado es más frágil que su propia tercera cifra

Al construir el pipeline, una diferencia puramente de implementación —evaluar
validación troceando el array con `torch.from_numpy(...).cuda()` en cada época,
en vez de recorrer un `DataLoader` preconstruido— movía el F1 de test del LSTM
de **0.3617 a 0.3843 (+0.023)**, con los mismos datos, la misma semilla y los
mismos pesos iniciales. La causa es que ese patrón cambia el estado del
asignador de memoria de CUDA, lo que cambia el orden de reducción del backward
no determinista de cuDNN en el LSTM; el entrenamiento amplifica ese ruido de
coma flotante hasta cambiar la época seleccionada.

Con semilla fija y el mismo camino de código, todo reproduce exactamente (tres
corridas idénticas). Pero **una diferencia de implementación que no cambia las
matemáticas mueve el F1 más que la distancia entre dos modelos de la tabla del
paper.** Es la razón por la que a partir de aquí todo se reporta como media ±
desviación sobre 5 semillas, y no como un número suelto.

---

## V1 — torneo de decisiones de protocolo

Seis decisiones, una a la vez, congelando la ganadora antes de pasar a la
siguiente. Exp B GLOBAL, 5 semillas por variante, decidido con 2024. Se adopta
una variante solo si mejora ≥ 0.005 **y** la mejora supera la desviación entre
semillas; si no, se queda la de v4.

F1-macro medio entre semillas sobre 2024 (`v5/v1_ablaciones.csv`):

| Decisión | Variante | CNN | CNN-LSTM | LSTM |
|---|---|---:|---:|---:|
| **D1 criterio de época** | `val_loss` (v4) | 0.3006 | 0.3350 | 0.2859 |
| | **`val_f1`** | **0.3279** | 0.3348 | **0.3444** |
| | `val_f1_ma3` | 0.3226 | 0.3100 | 0.3336 |
| **D2 ventanas alineadas** | no (v4) | 0.3006 | 0.3350 | 0.3444 |
| | **sí** | **0.3139** | 0.3085 | 0.3417 |
| **D3 escalador** | `minmax` (v4) | 0.3139 | 0.3350 | 0.3417 |
| | `standard` | 0.3263 | 0.3153 | 0.3372 |
| | `robust`+clip 5 | 0.3198 | 0.3059 | 0.3093 |
| **D4 pesos de clase** | `balanced` (v4) | 0.3139 | 0.3350 | 0.3417 |
| | `none` | 0.3039 | 0.3118 | 0.3450 |
| | `sqrt` | 0.2932 | 0.3154 | 0.3471 |
| **D5 pooling temporal** | v4 (`last` / `gap+gmp`) | 0.3139 | 0.3350 | 0.3417 |
| | alternativas | 0.3075–0.3306 | 0.3051–0.3055 | 0.3356–0.3463 |
| **D6 refit con train+val** | no (v4) | 0.3139 | 0.3350 | 0.3417 |
| | sí | 0.2897 | 0.2931 | 0.2943 |

### Lo que dice la tabla

1. **El criterio de época es la única palanca grande, y solo para el LSTM:**
   +0.0585 (0.2859 → 0.3444) al seleccionar el checkpoint por F1 de validación
   en vez de por pérdida de validación. Además la desviación entre semillas cae
   a la mitad (0.0305 → 0.0146). Para CNN sube +0.027 pero dentro del ruido, y
   para CNN-LSTM no cambia nada. Es decir: **buena parte de lo que el paper
   reportaba como "el LSTM rinde peor" era el criterio de parada, no el modelo.**
2. **El escalador no era el problema**, como ya anticipaba el diagnóstico: ningún
   cambio significativo. Descartado como explicación.
3. **Los pesos de clase y el pooling temporal no hacen nada.** Ni atención, ni
   media+máx, ni focal-adyacentes: todo dentro del ruido.
4. **Reentrenar con train+val empeora a las tres arquitecturas** (−0.024 a
   −0.047). Esto es importante para el paper: la asimetría (b) del diagnóstico
   —LR/XGBoost reentrenan con validación y los profundos no— **no explica la
   brecha**; darles ese año extra los perjudica, porque sin validación no hay
   forma de parar en el punto correcto.
5. **Alinear las ventanas cuesta −0.027 al CNN-LSTM** y beneficia al CNN
   (+0.013). Aun así se adopta en las tres: sin ella los modelos no se evalúan
   sobre las mismas filas y la tabla del paper no sería comparable. El costo
   queda documentado aquí.

Base congelada para la búsqueda: `v5/base_v5.json`.

---

## V2 — búsqueda de hiperparámetros con Optuna (respuesta al Revisor #2)

*(en ejecución — se completa al terminar)*

## V3 — la misma búsqueda para LR y XGBoost

*(en ejecución)*

## Resultados finales en test 2025

*(pendiente)*

## V6 — intervalos de confianza

*(pendiente)*

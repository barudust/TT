# Plan maestro: exprimir al máximo los resultados con datos de Yahoo Finance

> **Fecha: 2026-08-14.** Este documento reemplaza a `PLAN_OPTUNA_DEEP_MODELS.md`
> (que queda como historial). Se apoya en las mediciones de
> **[`DIAGNOSTICO_MODELOS_PROFUNDOS.md`](DIAGNOSTICO_MODELOS_PROFUNDOS.md)** —
> léelo primero, porque el plan cambia de forma según lo que ahí se midió.
>
> **Restricción del proyecto:** solo datos gratuitos de Yahoo Finance. Todo lo
> que hay aquí la respeta. (Yahoo publica mucho más de lo que el pipeline usa
> hoy: ver Vía 4.)

---

## Resumen ejecutivo

1. **El cómputo dejó de ser el problema.** Un entrenamiento profundo cuesta 10 s.
   El plan completo de este documento cabe en **6–11 h de GPU**; lo caro es el
   tiempo de programación (6–8 días), no el de cálculo.
2. **El problema real es el protocolo, no los hiperparámetros.** Los modelos
   profundos del paper están entrenados 1–2 épocas efectivas, se evalúan sobre
   menos filas de test que LR/XGBoost, no reentrenan con validación, y su
   lookback se eligió mirando test.
3. **Las diferencias del paper pueden ser ruido.** En validación los cinco
   modelos empatan dentro de 0.02. Nadie ha medido un intervalo de confianza.
4. Por eso el plan tiene **siete vías** y no una: arreglar el protocolo (V0–V1)
   viene *antes* que la búsqueda de hiperparámetros (V2), y medir la
   incertidumbre (V6) vale más para el paper que cualquier décima de F1.
5. **Camino recomendado si tienes poco tiempo:** V0 → V1 → V2 → V6. Eso cierra
   el comentario del revisor con evidencia y blinda las conclusiones. V3–V5 son
   mejora incremental.

### Qué resuelve cada vía

| Vía | Qué hace | Para el paper sirve para… | GPU | Programación |
|---|---|---|---|---|
| **V0** | Pipeline v5 con protocolo correcto + replicar v4 | Base para todo lo demás | ~1 h | 1–2 días |
| **V1** | Torneo de 6 decisiones de protocolo (ablaciones) | Tabla de ablación honesta | ~1 h | 0.5 día |
| **V2** | Optuna real en las 3 arquitecturas profundas | **Responde al Revisor #2** | 3–6 h | 0.5 día |
| **V3** | Misma búsqueda automática para LR y XGBoost | Que nadie diga "ahora la asimetría es al revés" | ~0.5 h | 0.3 día |
| **V4** | Más datos y más features, todo desde Yahoo | Subir el techo de verdad | ~2 h | 2–3 días |
| **V5** | Umbrales, calibración, costos de transacción | Mejorar Sharpe y distribución de señales | ~0.2 h | 0.5 día |
| **V6** | Walk-forward + pruebas estadísticas | Convertir números en conclusiones defendibles | ~1 h | 1 día |

---

## Parte 1 — Reglas del juego (no negociables)

Estas reglas existen porque el riesgo #1 de "probar muchas cosas" es acabar
reportando el mejor de 300 intentos sobre el mismo año de test, que es
exactamente lo que un revisor busca.

| # | Regla | Por qué |
|---|---|---|
| **R1** | **La selección SIEMPRE se hace en validación.** Test solo se toca cuando una configuración ya está congelada. | Es el error que ya existe en v4 (H5a) |
| **R2** | **Cada evaluación en test se registra y se numera.** El paper debe poder decir cuántas hubo. | Honestidad estadística |
| **R3** | **Todo número que vaya al paper se reporta como media ± desviación sobre ≥5 semillas.** | El `val_f1` oscila ±0.05 entre épocas |
| **R4** | **Dos modelos solo se comparan si se evaluaron sobre exactamente las mismas filas** (mismas fechas y tickers). | H5c |
| **R5** | **Una decisión se adopta solo si mejora ≥ 0.005 de F1 *y* la mejora supera 1 desviación estándar entre semillas.** Si empata, gana la opción más simple. | Evita perseguir ruido |
| **R6** | **El escalador, los percentiles del target y cualquier estadístico se ajustan solo con train.** Nunca con val ni test. | Ya se cumple; no romperlo |
| **R7** | **Todo run se escribe en el registro maestro** (`v5/registro_runs.csv`), aunque salga mal. | Sin registro no hay bitácora |
| **R8** | **Cualquier cambio que altere una cifra ya citada en `paper/paper.tex` se documenta en una tabla "antes / después"** antes de tocar el `.tex`. | El paper ya está enviado a MICAI |

### Convención de carpetas y nombres

```
RESULTADOS_OPTIMIZADOS/v5/
├── registro_runs.csv          ← registro maestro (una fila por run)
├── optuna_v5.db               ← storage de Optuna (permite reanudar)
├── estudios/                  ← trials_dataframe() exportado por estudio
├── modelos/{arch}/{run_id}/   ← checkpoints de las configs finalistas
└── reportes/                  ← tablas y figuras nuevas
```

**Esquema del registro** (`registro_runs.csv`) — una fila por (modelo, tipo,
ticker, experimento, configuración):

```
run_id, fecha_hora, via, experimento, modelo, tipo, ticker, lookback,
config_json, semillas, criterio_seleccion, escalador, ventanas_alineadas,
refit_trainval, n_train, n_val, n_test,
val_f1_mean, val_f1_std, test_f1_mean, test_f1_std,
test_f1_buy, test_f1_hold, test_f1_sell,
sharpe, win_rate, profit_factor, max_dd,
segundos, git_commit, evaluado_en_test, notas
```

`val_f1_mean` es obligatorio siempre. `test_f1_mean` se deja vacío hasta que la
configuración esté congelada (R1).

---

## Parte 2 — Las tres formas de buscar (y cuándo usar cada una)

Esto responde a la pregunta de "¿planes individuales y me quedo con el mejor, o
tipo búsqueda binaria?". Se usan las tres, cada una donde corresponde:

### E1 — Torneo secuencial con bloqueo (*coordinate descent*)

Para decisiones **excluyentes y pocas** (¿MinMax o Standard?). Se prueba una
decisión a la vez, manteniendo todo lo demás fijo; la ganadora **se congela** y
se pasa a la siguiente decisión sobre esa nueva base.

```
base = config_v4
para cada decisión D en [D1, D2, ... D6]:
    correr todas las variantes de D sobre `base`   (5 semillas c/u)
    si la mejor variante cumple R5:  base = base + variante_ganadora
    si no:                           base se queda igual  (y se anota "sin efecto")
```

- **Ventaja:** barato, interpretable, produce la tabla de ablación del paper.
- **Riesgo:** ignora interacciones (que A y B por separado no sirvan pero juntas sí).
- **Mitigación:** al terminar, correr una vez la combinación de las 2–3 decisiones
  rechazadas por poco, juntas. Si tampoco, se cierra el tema.
- **Se usa en:** V1, y en V4 para elegir familias de features.

### E2 — Eliminatoria (*bracket*)

Para comparar **familias completas** que no se pueden mezclar (universo de 7 vs
50 tickers; target de 1d vs 5d). Se corren todas las ramas hasta el mismo punto,
se conservan las dos mejores, y solo esas avanzan a la fase cara.

- **Se usa en:** V4 (cada familia de features es una rama).
- **Regla de eficiencia:** una rama de features se prueba **primero con LR y
  XGBoost** (2–6 s por fit). Si no ayuda ni a LR ni a XGBoost, no se gasta GPU en
  los modelos profundos. Ahorra el 80 % del trabajo.

### E3 — Optuna (TPE + pruning)

Para espacios **grandes y continuos** (lr, weight_decay, hidden, dropout…). Es la
versión automática de E1+E2 y sí modela interacciones.

- **Se usa en:** V2 y V3.
- **Cuidado:** con 150 trials y una validación de 1 624 filas, el mejor trial está
  sobreajustado a validación por ~+0.02–0.04. Por eso el objetivo de Optuna es la
  **media de 2 semillas** (y en V6, la media de 2 ventanas de validación), y por eso
  el ganador se reentrena y se vuelve a comparar antes de tocar test.

### Regla de desempate (aplica a las tres)

Si dos opciones quedan dentro de 1 desviación estándar entre semillas:
**gana la más simple**, y si empatan en simplicidad, **la más rápida**. Se anota
"empate dentro del ruido" en el registro — eso también es un resultado
publicable.

---

## Parte 3 — Mapa general con compuertas

```
                          ┌─────────────────────────────┐
                          │ V0  pipeline v5 + replicar  │
                          │     v4 (control)            │
                          └──────────────┬──────────────┘
                                         │
                              G0: ¿replica v4 ±0.01?
                          NO ─────────────┴───────────── SÍ
                    (parar: hay un bug,                   │
                     no seguir)                           ▼
                                          ┌───────────────────────────┐
                                          │ V1  torneo de protocolo   │
                                          │     (6 decisiones)        │
                                          └─────────────┬─────────────┘
                                                        │
                                    G1: ¿el mejor val_f1 profundo subió ≥0.01?
                             ┌──────────────────────────┴──────────────────────┐
                            SÍ                                                 NO
                             │                                                  │
                             ▼                                                  ▼
              ┌──────────────────────────┐                   ┌──────────────────────────────┐
              │ V2 Optuna sobre la base  │                   │ V2 Optuna igual (hay que     │
              │    ya mejorada           │                   │    responder al revisor),     │
              └────────────┬─────────────┘                   │    pero la hipótesis pasa a   │
                           │                                 │    ser "no hay señal"         │
                           │                                 └──────────────┬───────────────┘
                           └────────────────┬──────────────────────────────┘
                                            │
                    G2: ¿el mejor profundo supera a LR/XGB en VALIDACIÓN?
             ┌──────────────────────────────┴───────────────────────────┐
            SÍ                                                          NO
             │                                                           │
             ▼                                                           ▼
  ┌────────────────────────────┐                        ┌────────────────────────────────┐
  │ V3 (obligatoria):          │                        │ V3 (recomendada) + V6          │
  │ dar la misma búsqueda a    │                        │ La conclusión del paper se      │
  │ LR/XGB antes de cambiar    │                        │ REFUERZA: "se buscó a fondo y   │
  │ la narrativa del paper     │                        │ aun así pierde"                 │
  └─────────────┬──────────────┘                        └────────────────┬───────────────┘
                └───────────────────┬─────────────────────────────────---┘
                                    ▼
                     ┌──────────────────────────────┐
                     │ V6 walk-forward + estadística│  ← la que más valor añade al paper
                     └──────────────┬───────────────┘
                                    │
                  G6: ¿las diferencias entre modelos son significativas?
             ┌──────────────────────┴───────────────────────┐
            SÍ                                              NO
             │                                               │
             ▼                                               ▼
   se mantiene el ranking                      se reescribe la conclusión como
   con IC reportados                          "empate estadístico" (es un hallazgo
                                               válido y más honesto)
                                    │
                                    ▼
                   ┌────────────────────────────────┐
                   │ V4 (más datos Yahoo) y V5      │
                   │ (capa de decisión) — opcionales│
                   │ si queda tiempo                │
                   └────────────────────────────────┘
```

---

# VÍA 0 — Pipeline v5 con el protocolo correcto

**Objetivo:** un solo módulo que entrene cualquiera de los 5 modelos con
opciones explícitas, que registre siempre validación *y* test, y que reproduzca
v4 cuando se le pide la configuración de v4.

**Precondición:** ninguna. Empieza por aquí.

### Paso 0.1 — `scripts_opt/common_v5.py`

Copiar `common_v4.py` y añadir. Interfaz mínima que debe quedar:

```python
SPLITS_V5 = SPLITS_V4          # mismos splits: A/B/C con test = 2025

@dataclass
class CfgEntrenamiento:
    lookback: int = 20
    escalador: str = "minmax"        # minmax | standard | robust
    clip: float | None = None        # p.ej. 5.0 → recortar a ±5 tras escalar
    ventanas_alineadas: bool = False # False = como v4 (ver 0.2)
    criterio: str = "val_loss"       # val_loss | val_f1 | val_f1_suave3
    epochs: int = 80
    patience: int = 15
    batch: int = 128
    lr: float = 1e-3
    weight_decay: float = 1e-4
    class_weight: str = "balanced"   # balanced | none | sqrt
    scheduler: str = "plateau"       # plateau | cosine | none
    grad_clip: float = 1.0
    refit_trainval: bool = False     # ver 0.3
    seeds: tuple = (42, 1, 7)

def preparar_secuencias(exp_id, cfg, tickers=TICKERS) -> dict
def entrenar(modelo, datos, cfg, trial=None) -> (modelo, historial)
def evaluar(modelo, datos, split) -> dict          # métricas de common.metricas_full
def registrar_run(fila: dict) -> None              # append a v5/registro_runs.csv
```

Detalles obligatorios:

- `entrenar()` calcula **`val_loss` y `val_f1` en cada época** y guarda el
  checkpoint según `cfg.criterio`. `val_f1_suave3` = media móvil de 3 épocas del
  `val_f1` (más estable que el máximo puntual, que es ruido).
- Si `trial` no es `None`, llamar `trial.report(val_f1, epoch)` y
  `if trial.should_prune(): raise optuna.TrialPruned()` — así V2 reusa esto tal cual.
- `evaluar()` devuelve siempre val **y** test, pero **quien llama decide si
  registra el test** (R1).

### Paso 0.2 — Ventanas alineadas (la corrección de H5c)

Hoy `prep_seq_ticker()` construye las ventanas dentro de cada split y pierde las
primeras `lookback` filas de val y de test. El algoritmo correcto:

```python
# 1. serie continua ordenada por fecha, con features + target
# 2. ajustar el escalador SOLO con las filas de train
scaler.fit(df.loc[mask_train, feats])
Z = scaler.transform(df[feats])            # transformar TODA la serie
# 3. una ventana por cada fila i con i >= lookback
#    ventana = Z[i-lookback : i]   etiqueta = target[i]   fecha = index[i]
# 4. el split se decide por la FECHA DE LA ETIQUETA, no por dónde empieza la ventana
```

Con esto val y test conservan sus 252 y 248 filas por ticker, y **los 5 modelos
se evalúan sobre exactamente las mismas fechas** (R4). No hay leakage: una
ventana de test mira hacia atrás a días de validación, que son pasado. Lo único
ajustado con train es el escalador.

> Documentar en el paper: "las ventanas se construyen sobre la serie continua y
> se asignan al split por la fecha de la etiqueta; el escalador se ajusta solo con
> train".

### Paso 0.3 — Paridad de reentrenamiento (la corrección de H5b)

`cfg.refit_trainval=True` debe: (1) entrenar con train, encontrando la mejor
época `E*` en validación; (2) reentrenar desde cero con train+val durante
exactamente `E*` épocas (sin early stopping, porque ya no hay validación); (3)
predecir test con ese modelo. Es lo que LR y XGBoost ya hacen implícitamente.

### Paso 0.4 — `scripts_opt/replicar_v4.py` (control)

Corre el pipeline nuevo con `CfgEntrenamiento()` por defecto (= v4 exacto:
`criterio="val_loss"`, `ventanas_alineadas=False`, `refit_trainval=False`) sobre
las 3 arquitecturas × 3 exps × 2 lookbacks × global.

**Compuerta G0 — criterio de aceptación:** cada `test_f1_macro` debe caer dentro
de **±0.01** del valor correspondiente en `RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv`.
Con semilla fija la reproducción medida es exacta, así que ±0.01 es holgado.

> ⚠️ Si no replica, **para**. Hay un bug en el código nuevo y todo lo que venga
> después estará contaminado. No sigas con V1.

**Presupuesto:** ~20 min de GPU. **Entregable:** `v5/registro_runs.csv` con las
filas de replicación y una nota en el registro con el resultado de G0.

---

# VÍA 1 — Torneo de decisiones de protocolo

**Objetivo:** cobrar las mejoras gratuitas antes de gastar en búsqueda.
**Estrategia:** E1 (torneo secuencial con bloqueo).
**Alcance:** Exp B, GLOBAL, las 3 arquitecturas profundas, **5 semillas** por
variante. Cada variante = 3 arquitecturas × 5 semillas ≈ 15 entrenamientos ≈ 2.5 min.

| # | Decisión | Variantes | Base (v4) | Expectativa |
|---|---|---|---|---|
| **D1** | Criterio de época | `val_loss` / `val_f1` / `val_f1_suave3` | `val_loss` | **Alta** — medido +0.033 en CNN |
| **D2** | Ventanas alineadas | no / sí | no | Media — corrige H5c, cambia las filas de test |
| **D3** | Escalador | `minmax` / `standard` / `robust`+clip 5 | `minmax` | Baja — descartado como causa raíz, pero es barato |
| **D4** | Pesos de clase | `balanced` / `none` / `sqrt` | `balanced` | Media — afecta la distribución de señales |
| **D5** | Pooling temporal | último estado / media+máx / atención | último | Media |
| **D6** | Reentrenar con train+val | no / sí | no | **Alta** — hoy los profundos compiten con 1 año menos |

**Criterio de aceptación:** R5 (≥0.005 y > 1 std entre semillas) en al menos
**2 de las 3 arquitecturas**. Si solo mejora en una, se anota pero no se congela.

**Orden importante:** correr D1 primero, porque cambia el punto de comparación de
todo lo demás. D2 y D6 se dejan al final porque **cambian los números del paper**
(D2 cambia las filas de test; D6 cambia el modelo evaluado).

> **Decisión pendiente para ti (D2/D6):** si estas dos mejoran, hay dos caminos:
> - **Conservador:** dejar las tablas del paper como están y añadir una sección de
>   ablación que muestre el efecto de corregir el protocolo.
> - **Corregido:** regenerar **todas** las cifras del paper con el protocolo nuevo
>   (los 5 modelos, no solo los profundos) y publicar una tabla "antes / después".
>
> Recomendación: hacer la medición, y decidir con el resultado en la mano. Si el
> orden del ranking no cambia, adoptar el corregido (es más defendible). Si cambia,
> es una decisión de autoría, no técnica — **avisar antes de tocar el `.tex`** (R8).

**Presupuesto:** 6 decisiones × ~2.5 variantes × 2.5 min ≈ **40 min de GPU**.
**Entregable:** tabla de ablación (una fila por decisión, Δ val_f1 media ± std por
arquitectura) → candidata directa a tabla del paper. Y una `CfgEntrenamiento`
congelada, la "base v5", que hereda V2.

---

# VÍA 2 — Optuna real en los modelos profundos

**Objetivo:** responder literalmente al Revisor #2 con evidencia.
**Estrategia:** E3.
**Precondición:** G0 aprobado y V1 terminada (la base congelada entra aquí).

### Paso 2.1 — Espacios de búsqueda

**LSTM y CNN-LSTM** (comparten casi todo):

| Hiperparámetro | Rango | Llamada Optuna |
|---|---|---|
| `lookback` | {10, 20, 40, 60} | `suggest_categorical` |
| `hidden` | 16–256 | `suggest_int(..., log=True)` |
| `layers` | 1–3 | `suggest_int` |
| `dropout` | 0.0–0.6 | `suggest_float` |
| `bidir` | {True, False} | `suggest_categorical` |
| `lr` | 1e-5–3e-3 | `suggest_float(..., log=True)` |
| `weight_decay` | 1e-6–1e-1 | `suggest_float(..., log=True)` |
| `batch` | {64, 128, 256, 512} | `suggest_categorical` |
| `pooling` | {último, media+máx, atención} | `suggest_categorical` |
| `loss` | {ce, ce+label_smooth, focal} | `suggest_categorical` |
| `label_smooth` | 0.0–0.2 (solo si aplica) | `suggest_float` |
| `focal_gamma` | 0.5–3.0 (solo si aplica) | `suggest_float` |
| `class_weight` | {balanced, none, sqrt} | `suggest_categorical` |
| `scheduler` | {plateau, cosine, none} | `suggest_categorical` |
| `grad_clip` | {0.5, 1.0, 5.0} | `suggest_categorical` |
| `escalador` | {minmax, standard, robust} | `suggest_categorical` |

**CNN 1D puro:** los comunes (lr, wd, dropout, batch, class_weight, scheduler,
escalador, lookback) más: `n_bloques` 1–4, `filtros_base` 16–256 (log),
`kernel` {3, 5, 7}, `dilatacion` {1, 2}, `usar_batchnorm` {sí, no},
`pooling_final` {gap+gmp, gap, flatten}.

**Cambio obligatorio respecto a v4:** subir `epochs` a 100 y `patience` a 25
sobre el **criterio de selección elegido en D1**. Con la config de v4 los trials
mueren en la época 16 y la búsqueda no puede explorar nada (H2).

### Paso 2.2 — Configuración del estudio

```python
study = optuna.create_study(
    study_name=f"v5_{arch}_expB_global",
    storage="sqlite:///RESULTADOS_OPTIMIZADOS/v5/optuna_v5.db",
    load_if_exists=True,                     # permite reanudar si se corta
    direction="maximize",
    sampler=optuna.samplers.TPESampler(seed=42, n_startup_trials=25,
                                       multivariate=True, group=True),
    pruner=optuna.pruners.MedianPruner(n_startup_trials=15, n_warmup_steps=10),
)
study.optimize(objective, n_trials=150)
study.trials_dataframe().to_csv(f"RESULTADOS_OPTIMIZADOS/v5/estudios/{arch}.csv")
```

El `objective` devuelve la **media del `val_f1` sobre 2 semillas** (42 y 1). Usar
una sola semilla hace que TPE persiga ruido; con 2 el costo se duplica (20 s por
trial) y sigue siendo trivial.

### Paso 2.3 — De la búsqueda al resultado final

1. Tomar los **5 mejores trials** por `val_f1` medio.
2. Reentrenar cada uno con **5 semillas** (42, 1, 7, 2024, 100) → media ± std en
   validación.
3. Elegir el ganador **en validación** (R1); si dos empatan dentro de 1 std, gana
   el más simple (menos parámetros).
4. **Una** evaluación en test del ganador. Registrarla (R2).
5. Transferir la configuración ganadora a Exp A, Exp C y a per-ticker
   **sin volver a buscar** (reentrenar y evaluar). Si sobra tiempo, hacer un
   estudio propio por experimento — con este costo, se puede.

### Paso 2.4 — Salidas para el paper

Además del F1: exportar `optuna.importance.get_param_importances(study)` y la
curva de historia de optimización. Una figura con "150 trials, importancia de
hiperparámetros" es **la respuesta visual directa al comentario del revisor** y
vale más que un párrafo.

**Compuerta G2:** ¿el mejor profundo supera a LR/XGBoost **en validación**?

| Resultado | Qué escribir en el paper |
|---|---|
| **No supera** (lo más probable) | Reforzar la conclusión: "con 150 trials de TPE por arquitectura sobre 16 hiperparámetros, el mejor modelo profundo alcanza X ± s en validación frente a Y ± s de LR; la ventaja del modelo lineal no se debe a una búsqueda desigual". Reescribir el párrafo de *Limitations* (`paper.tex:355`), que hoy admite la asimetría. |
| **Supera en validación pero no en test** | Es el caso más delicado: hay que decirlo tal cual y es un argumento fuerte a favor de V6 (un año de test no alcanza). |
| **Supera en ambos** | Cambia la conclusión del paper (Abstract, Tabla 3, Discusión). **Avisar antes de tocar esas secciones** (R8). |

**Presupuesto:** 3 arquitecturas × 150 trials × 2 semillas. El costo por trial
depende de cuántas épocas corra con el criterio nuevo: hoy los trials mueren en la
época 16 (10 s), pero con `patience=25` sobre `val_f1` pueden llegar a 50–60 épocas
(~30 s por semilla). Rango realista: **3–6 h de GPU**, desatendidas; el pruner
recorta la parte alta. Los finalistas añaden ~10 min.

> Consejo práctico: correr primero **20 trials** y mirar la duración media real
> (`study.trials_dataframe()["duration"]`) antes de lanzar los 150. Con el
> `storage` de sqlite, los 20 primeros no se pierden: el estudio continúa.

---

# VÍA 3 — Simetría de búsqueda para LR y XGBoost

**Objetivo:** que la comparación siga siendo justa después de V2. Si los modelos
profundos reciben 150 trials y LR sigue con un grid de 3 puntos
(`C ∈ {0.01, 0.1, 1}`, `l1_ratio` fijo en 0.5), la asimetría simplemente cambió
de bando y el paper queda igual de atacable.

**Espacio para LR:** `penalty` {l1, l2, elasticnet}, `C` 1e-4–1e3 (log),
`l1_ratio` 0–1 (si elasticnet), `class_weight` {balanced, none},
`escalador` {standard, robust}, `max_iter` fijo 3000.
100 trials × 4 s ≈ **7 min**.

**Espacio para XGBoost:** el que ya existe en `train_all_v4.py:291`, ampliado
igual que en `opt_xgb.py`, con **el mismo número de trials que los profundos**
(150). 150 × 2.2 s ≈ **6 min**.

**Frase objetivo para el paper:** *"every model received an automated TPE search
with the same trial budget (150 trials) under the same selection protocol"*. Con
eso el comentario (b) del revisor queda cerrado sin abrir uno nuevo.

**Compuerta G3:** si LR también mejora, la conclusión se mantiene pero **todas
las cifras cambian** → aplica R8.

---

# VÍA 4 — Más información, sin salir de Yahoo Finance

**Objetivo:** subir el techo real (~0.40 de F1), no exprimir décimas.
**Estrategia:** E2 (eliminatoria), con la regla de eficiencia: **cada familia se
prueba primero con LR y XGBoost** (segundos) y solo las que ayuden pasan a los
modelos profundos.

Dónde se toca: `scripts_v1/01_build_raw_dataset.py` es la fuente de verdad de la
ingeniería de features (`TICKERS` en la línea 30, `MARKET_TICKERS` en la 33,
`descargar_mercado()` en la 69, `DOWNLOAD_START` en la 40). **No editarlo en
sitio**: copiarlo a `scripts_opt/build_dataset_v5.py` y escribir en
`tesis_ml_stocks/01_raw_datasets_v5/`, para no romper lo que ya está publicado.

### 4A — Universo de entrenamiento ampliado (la palanca más prometedora)

El argumento del propio paper es que los modelos profundos pierden por falta de
datos (~10 500 muestras globales). Yahoo entrega gratis cientos de tickers con la
misma profundidad histórica.

- **Diseño:** entrenar con 40–60 tickers líquidos, **evaluar sobre los mismos 7**
  de siempre (las tablas siguen siendo comparables).
- **Variantes a comparar:** (i) entrenar directamente en el universo grande;
  (ii) preentrenar en el universo grande y hacer *fine-tuning* en los 7.
- **Efecto esperado:** train pasa de ~10 k a ~70 k secuencias. Es el único cambio
  que ataca la causa que el propio paper señala.
- **Candidatos** (líquidos, historia larga, sin salir de Yahoo): AAPL, MSFT,
  GOOGL, AMZN, META, NVDA, TSLA, AVGO, AMD, INTC, QCOM, TXN, MU, ADI, AMAT, LRCX,
  KLAC, CSCO, ORCL, CRM, ADBE, NOW, INTU, IBM, ACN, JPM, BAC, WFC, GS, MS, V, MA,
  JNJ, PFE, MRK, ABBV, UNH, XOM, CVX, WMT, COST, HD, PG, KO, PEP, DIS, NFLX, T,
  VZ, CAT.
- ⚠️ **Sesgo de supervivencia:** es una lista de ganadores de hoy. Como universo
  de *entrenamiento* el efecto es menor (no se evalúa sobre ellos), pero hay que
  **declararlo explícitamente** en el paper.
- ⚠️ El target se recalcula por ticker con su propio percentil rodante — el script
  ya lo hace así, solo hay que correrlo con la lista nueva.

**Presupuesto:** descarga ~10 min; entrenamiento ~7× más lento por época (70 s por
entrenamiento global, sigue siendo barato).

### 4B — Features macro y de mercado que Yahoo sí publica

El documento `ALTERNATIVAS_FUTURAS.md` da por hecho que el contexto macro requiere
FRED. **No es cierto:** buena parte se puede aproximar con símbolos de Yahoo.
Familias a probar por separado (E2). **La disponibilidad ya está verificada**
(`% cobertura` = días con dato respecto al calendario de AAPL, 2013–2025,
comprobado el 2026-08-14):

| Familia | Símbolos verificados | Features derivadas |
|---|---|---|
| **F1 Curva de tasas** (proxy con ETFs de bonos) | `SHY` 100 %, `IEI` 100 %, `IEF` 100 %, `TLT` 100 % | retorno 5d/20d de cada uno; `TLT/SHY` (proxy de pendiente de la curva); volatilidad 20d de TLT |
| **F2 Volatilidad** | `^VIX` 100 % (ya se usa), `^VVIX` 99.8 %, `VIXY` 100 % | `^VVIX` normalizado; `VIXY/^VIX` (proxy de contango de futuros); `^VIX` − volatilidad realizada 20d de SPY (prima de riesgo de varianza) |
| **F3 Riesgo y crédito** | `HYG` 100 %, `LQD` 100 % | `HYG/LQD` (proxy de spread de crédito), retornos 5d |
| **F4 Divisas y materias primas** | `DX-Y.NYB` 99.9 % (o `UUP` 100 %), `GC=F` 99.9 % (o `GLD` 100 %), `CL=F` 99.9 % (o `USO` 100 %) | retorno 1d/5d, volatilidad 20d |
| **F5 Sector y amplitud** | `XLK`, `SMH`, `QQQ`, `SPY`, `RSP`, `^RUT`, `XLF`, `XLY`, `XLP` — todos 100 % | fuerza relativa ticker/sector y sector/mercado, `RSP/SPY` (amplitud), `^RUT/SPY` (pequeñas vs grandes) |
| **F6 Transversales (sin descargas nuevas)** | los 7 tickers entre sí | rango percentil del momentum del ticker dentro del universo, beta rodante 60d vs SPY, correlación rodante con el sector |

> ⚠️ **Verificado el 2026-08-14: `^TNX`, `^FVX`, `^IRX`, `^TYX` (índices de tasas
> del Tesoro) y `^VIX9D`, `^VIX3M` ya NO devuelven historial** por yfinance —
> solo los últimos ~16 días, aunque `^VIX`, `^VVIX` y `^RUT` sí funcionan. Por eso
> F1 y F2 usan proxies con ETFs en vez de los índices directos. Yahoo cambia estos
> símbolos sin aviso: **volver a verificar antes de correr nada**.

**Paso obligatorio:** dejar en el repo un script de verificación que descargue
cada símbolo e imprima primera fecha, última fecha y % de cobertura contra el
calendario de AAPL. Es la comprobación de arriba, automatizada, para poder
repetirla.

**Honestidad en el paper:** F1 y F3 son *proxies* (precios de ETFs), no la curva
de tasas ni el spread de crédito reales. Describirlos como tales.

**Cuidados:**
- Alinear al calendario del ticker (`reindex` sobre el índice de la acción) y
  rellenar hacia adelante con límite de 3 días. Nunca hacia atrás (sería futuro).
- Los futuros (`GC=F`, `CL=F`) cotizan días que la bolsa no; el `reindex` lo
  resuelve.
- Usar el cierre del **mismo día** t para predecir el retorno t→t+1 es correcto y
  es lo que ya hace el pipeline con SPY/VIX.

**Orden sugerido:** F6 (gratis, no requiere descargas) → F2 → F1 → F5 → F3 → F4.

### 4C — Historia más larga

`DOWNLOAD_START` está en 2013-01-01. Yahoo tiene AAPL/MSFT desde los 80. Límite
real: META cotiza desde 2012 y TSLA desde 2010, así que **con los 7 tickers no se
puede ir más atrás de 2012** sin perder tickers. Combinado con 4A sí: el universo
ampliado puede entrenarse desde 2000 y evaluarse en los 7 de siempre.
Contrapartida: incluir 2000–2008 mete regímenes muy distintos. Probar como rama
propia, no darlo por bueno.

### 4D — Horizonte del target (experimento aparte, no sustituto)

Predecir el percentil del retorno a 3 o 5 días tiene mucho mejor relación
señal/ruido que a 1 día, y `ALTERNATIVAS_FUTURAS.md` ya estima F1 ≈ 0.45–0.50.
Cambia la naturaleza del estudio ("señal diaria"), así que:
**va como sección de robustez o como trabajo futuro con números, nunca sustituyendo
la tabla principal.** Es barato: se cambia el `shift` en `calcular_target()` y se
recorre todo.

### 4E — Descartado con motivo (dejarlo escrito en el paper)

Intradía: Yahoo solo da 1 minuto de los últimos 30 días y 1 hora de los últimos
730. Para 12 años de historial no alcanza. Ya está en `ALTERNATIVAS_FUTURAS.md`;
mantenerlo como limitación declarada.

**Compuerta G4:** una familia de features se adopta si mejora el `val_f1` de
**LR o XGBoost** según R5. Solo entonces se prueba en los modelos profundos.

---

# VÍA 5 — Capa de decisión (barata, mejora la parte económica)

El paper ya señala que LR predice solo 18 % de BUY frente a un 30 % real
(`paper.tex:301`). Eso es dinero sobre la mesa y no requiere reentrenar nada:
se trabaja sobre las probabilidades ya calculadas.

1. **Umbrales por clase**: buscar en validación tres desplazamientos
   (`b_sell`, `b_hold`, `b_buy`) que se suman a las probabilidades antes del
   `argmax`, maximizando F1-macro. Grid grueso de 11×11 es suficiente.
2. **Escalado por temperatura**: ajustar una `T` en validación (minimizando log-loss)
   antes de aplicar umbrales. Mejora la calibración sin cambiar el ranking.
3. **Abstención por confianza**: si `max(prob) < τ`, forzar HOLD. Menos operaciones,
   mejor Sharpe. Ya se probó en v1 (`lr_confidence_filter.py`, F1 0.412 vs 0.417
   con Sharpe similar); repetirlo sobre el modelo v5 y sobre umbrales calibrados.
4. **Tamaño de posición por probabilidad** en vez de ±1 fijo: `posición ∝ p(BUY) − p(SELL)`.
   Cambia solo el backtest, no el modelo.
5. **Costos de transacción**: repetir el backtest con 5 y 10 puntos base por
   cambio de posición. El paper hoy los omite explícitamente (`paper.tex:162`);
   añadir una tabla de robustez cierra esa limitación con dos horas de trabajo.

**Todo se ajusta en validación** (R1) y se evalúa una vez en test.

---

# VÍA 6 — Walk-forward y estadística (la de mayor valor por hora invertida)

**Por qué:** el propio paper dice que es la extensión más importante
(`paper.tex:355`) y H4 muestra que sin ella el ranking podría ser ruido. Con 10 s
por entrenamiento, ya no hay excusa de costo.

### 6.1 — Walk-forward

Siete pliegues, ventana de entrenamiento móvil de 6 años (como Exp B):

| Pliegue | Train | Val | Test |
|---|---|---|---|
| WF-2019 | 2013–2017 | 2018 | 2019 |
| WF-2020 | 2014–2018 | 2019 | 2020 |
| WF-2021 | 2015–2019 | 2020 | 2021 |
| WF-2022 | 2016–2020 | 2021 | 2022 |
| WF-2023 | 2017–2021 | 2022 | 2023 |
| WF-2024 | 2018–2022 | 2023 | 2024 |
| WF-2025 | 2019–2023 | 2024 | 2025 |

Se reporta media ± std de F1 y Sharpe sobre los 7 pliegues, por modelo. Eso
multiplica por 7 el tamaño efectivo de la evaluación y **separa el efecto del
modelo del efecto del año**, que es exactamente lo que hoy no se puede hacer.

**Presupuesto:** 3 arquitecturas × 7 pliegues × 2 lookbacks × 5 semillas × 10 s ≈
**35 min**. LR y XGBoost, minutos.

**Uso adicional:** los pliegues WF también sirven como **validación robusta para
Optuna** (V2): un objetivo que promedie el `val_f1` de 2–3 pliegues sobreajusta
mucho menos que uno solo. Si sobra tiempo, rehacer V2 así.

### 6.2 — Pruebas estadísticas

- **Bootstrap por bloques** (bloques de 20 días para respetar la autocorrelación,
  1 000 remuestreos) → intervalo de confianza del 95 % para el F1 de cada modelo y
  **para la diferencia entre dos modelos**. Si el IC de la diferencia contiene el
  0, la diferencia no es significativa. **Esta es la prueba que decide si el
  ranking del paper se sostiene.**
- **McNemar** para comparar dos clasificadores sobre las mismas filas (requiere R4).
- **Diebold-Mariano** sobre las series de retorno de estrategia para las métricas
  económicas.
- **Prueba de permutación** contra el azar: barajar las etiquetas 1 000 veces y ver
  dónde cae el F1 observado. Contesta "¿hay señal, siquiera?" — dado H3, es una
  pregunta abierta y de respuesta valiosa.

**Compuerta G6:** si las diferencias entre modelos no son significativas, la
conclusión del paper se reescribe como empate estadístico con LR preferido por
costo e interpretabilidad. **Eso no es un fracaso: es un resultado más fuerte y
más difícil de refutar** que el ranking actual.

---

## Parte 4 — Presupuesto total y escenarios

Con las mediciones de H1 (10 s por entrenamiento global, 1.5 s per-ticker, 2.2 s
XGBoost, 4 s LR):

| Vía | GPU | Programación |
|---|---|---|
| V0 pipeline + replicación | 20 min | 1–2 días |
| V1 torneo de protocolo | 40 min | 0.5 día |
| V2 Optuna (3 arquitecturas × 150 trials × 2 semillas) | 3–6 h | 0.5 día |
| V3 simetría LR/XGB | 15 min | 0.3 día |
| V4 datos Yahoo (según ramas) | 1–2 h | 2–3 días |
| V5 capa de decisión | 10 min | 0.5 día |
| V6 walk-forward + estadística | 1 h | 1 día |
| **Total** | **~6–11 h** | **6–8 días** |

### Escenarios

- **Mínimo (2 días de trabajo, 4–7 h de GPU) — cierra el comentario del revisor:**
  V0 → V1 → V2 → escribir. Entrega: búsqueda Optuna real documentada, tabla de
  ablación de protocolo, párrafo de *Limitations* reescrito.
- **Recomendado (4–5 días, 5–8 h de GPU) — además blinda las conclusiones:**
  añade V3 y V6. Entrega: todos los modelos con el mismo presupuesto de búsqueda +
  intervalos de confianza + walk-forward de 7 años. Con esto el paper pasa de
  "benchmark con un año de test" a "benchmark con evaluación robusta".
- **Completo (2 semanas, ~11 h de GPU) — busca subir el techo:**
  añade V4 y V5. Es el único escenario con posibilidad real de mover el F1 por
  encima de 0.42, y el único que justifica reescribir la narrativa.

---

## Parte 5 — Errores típicos y cómo detectarlos

| Síntoma | Causa probable | Cómo verificar |
|---|---|---|
| El modelo predice una sola clase | Colapso; `class_weight` mal o lr muy alto | Revisar `signal_distribution` en el registro: si una clase >80 %, descartar el run |
| `val_f1` altísimo (>0.5) | Leakage | ¿El escalador se ajustó con val/test? ¿El target usa datos futuros? |
| Los resultados no reproducen | Semilla no fijada en todos lados | Fijar `torch.manual_seed`, `np.random.seed` **y** `random.seed`; con eso ya se verificó reproducción exacta en esta máquina |
| Optuna repite los mismos parámetros | `n_startup_trials` muy bajo o espacio mal definido | Revisar `study.trials_dataframe()` |
| El estudio se corta a mitad | Normal en corridas largas | Ya está previsto: `storage=sqlite` + `load_if_exists=True` reanudan solo |
| Test mejora pero validación no | Estás seleccionando con test sin darte cuenta | Volver a R1; es exactamente lo que pasó en v4 (H5a) |
| Sube el F1 pero baja el Sharpe | Normal: son objetivos distintos | Reportar ambos; no elegir con uno y presumir el otro |

---

## Parte 6 — Checklist maestro

**Vía 0**
- [ ] `common_v5.py` con `CfgEntrenamiento`, `preparar_secuencias`, `entrenar`, `evaluar`, `registrar_run`
- [ ] `entrenar()` calcula y guarda `val_loss` **y** `val_f1` por época
- [ ] Soporte de `trial.report()` / `should_prune()` para reusar en V2
- [ ] Ventanas alineadas implementadas (bandera, por defecto apagada)
- [ ] `refit_trainval` implementado
- [ ] `registro_runs.csv` creado con el esquema completo
- [ ] `replicar_v4.py` corre y **G0 pasa (±0.01)** ← no seguir sin esto

**Vía 1**
- [ ] D1 criterio de época (3 variantes × 3 arq. × 5 semillas)
- [ ] D2 ventanas alineadas
- [ ] D3 escalador
- [ ] D4 pesos de clase
- [ ] D5 pooling
- [ ] D6 reentrenar con train+val
- [ ] Prueba conjunta de las decisiones rechazadas por poco
- [ ] Tabla de ablación escrita + `CfgEntrenamiento` base congelada

**Vía 2**
- [ ] `opt_lstm_v5.py`, `opt_cnn_v5.py`, `opt_cnn_lstm_v5.py` con el espacio de 2.1
- [ ] `epochs=100`, `patience=25` sobre el criterio de D1
- [ ] Objetivo = media de 2 semillas; storage sqlite; TPE seed 42; MedianPruner
- [ ] 150 trials por arquitectura
- [ ] Top-5 reentrenados con 5 semillas y elegidos **en validación**
- [ ] **Una** evaluación en test del ganador, registrada
- [ ] Config ganadora transferida a Exp A/C y per-ticker
- [ ] Exportadas importancia de hiperparámetros e historia de optimización

**Vía 3**
- [ ] LR con Optuna (100 trials)
- [ ] XGBoost con 150 trials (mismo presupuesto que los profundos)
- [ ] Frase de simetría redactada para el paper

**Vía 4**
- [ ] Script de verificación de símbolos de Yahoo (primera fecha, huecos)
- [ ] `build_dataset_v5.py` (copia, no edición in situ) → `01_raw_datasets_v5/`
- [ ] F6 transversales → probar con LR/XGB
- [ ] F2 VIX, F1 tasas, F5 sectores, F3 crédito, F4 divisas → probar con LR/XGB
- [ ] Solo las familias que pasen G4 → modelos profundos
- [ ] 4A universo ampliado (directo y con fine-tuning)
- [ ] Sesgo de supervivencia declarado en el paper

**Vía 5**
- [ ] Umbrales por clase calibrados en validación
- [ ] Temperatura + abstención
- [ ] Tamaño de posición por probabilidad
- [ ] Backtest con costos de 5 y 10 pb

**Vía 6**
- [ ] 7 pliegues walk-forward corriendo para los 5 modelos
- [ ] Bootstrap por bloques con IC de la **diferencia** entre modelos
- [ ] McNemar entre los dos mejores
- [ ] Prueba de permutación contra el azar
- [ ] Decisión de G6 documentada

**Cierre**
- [ ] Tabla "antes / después" de toda cifra del paper que cambie (R8)
- [ ] Recuento de evaluaciones en test reportado (R2)
- [ ] `STATUS.md` y `GUIA_PROGRESO.md` actualizados
- [ ] Párrafo de *Limitations* de `paper.tex` reescrito según G2 y G6

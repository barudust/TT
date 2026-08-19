# Plan: búsqueda de hiperparámetros con Optuna para los modelos profundos

> ## ⛔ SUPERADO (2026-08-14) — ver [`PLAN_MAESTRO_BUSQUEDA.md`](PLAN_MAESTRO_BUSQUEDA.md)
>
> Se conserva como historial. El diagnóstico posterior
> ([`DIAGNOSTICO_MODELOS_PROFUNDOS.md`](DIAGNOSTICO_MODELOS_PROFUNDOS.md))
> encontró tres errores de premisa en este documento:
>
> 1. **Apunta al código equivocado.** Propone construir sobre `opt_lstm.py` /
>    `opt_cnn_*.py`, que son de la iteración **v1** (splits con test distinto por
>    experimento). Los números que el revisor leyó salen de **v4**
>    (`train_all_v4.py` + `common_v4.py`). Optimizar sobre v1 produce cifras que
>    no son comparables con la tabla del paper.
> 2. **La estimación de costo era el problema equivocado.** Medido: un
>    entrenamiento profundo completo tarda **10 segundos**, no minutos. El
>    presupuesto de "15–20 trials" era ~10× más conservador de lo necesario;
>    caben 150 trials por arquitectura en un par de horas.
> 3. **El cuello de botella no son los hiperparámetros.** Con el early stopping
>    actual los modelos profundos del paper están entrenados **1–2 épocas
>    efectivas**, y su `val_loss` nunca mejora al azar. Mover `hidden`/`dropout`
>    dentro de los rangos propuestos no puede arreglar eso.
>
> Lo que sigue siendo válido de este documento: el diagnóstico de la tabla de
> abajo (qué buscó cada script y qué no), y la idea de no tocar los scripts
> originales sino crear scripts nuevos.

> **Estado original: documentado, no ejecutado.** Este plan responde al punto (b)
> del Revisor #2 de MICAI. No se relanzó ningún entrenamiento — solo se dejó
> constancia de la asimetría como limitación honesta en `paper/paper.tex`
> (sección Limitations).

## El comentario del revisor

> "The hyperparameter search appears somewhat constrained, particularly for
> deep models (LSTM hidden=128). A more extensive search, perhaps using the
> Optuna framework that is already employed for XGBoost, could potentially
> improve deep model performance." — Reviewer #2

## Diagnóstico: qué se buscó realmente y qué no

Confirmado leyendo el código (`scripts_opt/opt_*.py`):

| Modelo | Método | Espacio explorado | Import de `optuna` |
|---|---|---|---|
| `opt_xgb.py` | Optuna TPE — 25 trials/ticker, 40 trials/global | 9 hiperparámetros continuos/enteros (`n_estimators`, `max_depth`, `learning_rate`, `subsample`, `colsample_bytree`, `min_child_weight`, `gamma`, `reg_alpha`, `reg_lambda`) | Sí |
| `opt_lr.py` | Grid manual, 3 puntos | `C ∈ {0.01, 0.1, 1}`, `l1_ratio` fijo en 0.5 | No (grid tan chico que no hace falta) |
| `opt_lstm.py` | **Grid manual de 6 configs fijas** (dict `CONFIGS`) × 2 lookbacks | `bidir`, `attn`, `hidden∈{128,192}`, `layers∈{2,3}`, `dropout∈{0.3,0.4}`, `loss∈{ce,focal}`, `label_smooth` — combinaciones elegidas a mano, `lr`/`weight_decay` **fijos** a nivel de módulo (`LR=1e-3`, `WD=1e-4`) | No |
| `opt_cnn_puro.py` | Mismo patrón que `opt_lstm.py` | Filtros/kernel fijos por config, mismo esquema | No |
| `opt_cnn_lstm.py` | Mismo patrón que `opt_lstm.py` | Igual | No |

Es decir: el diagnóstico del revisor es correcto y verificable — XGBoost tiene
búsqueda automática de verdad, los 3 modelos profundos no tienen ninguna
(solo un grid pequeño hecho a mano, y el learning rate ni siquiera está en
ese grid).

## Entorno disponible (verificado 2026-08-14)

- PyTorch 2.12 + CUDA 12.8, GPU NVIDIA RTX 5060 Ti (17 GB VRAM) — detectada y
  funcional en la máquina donde se escribió este plan.
- Optuna 4.8 ya instalado.
- No hay bloqueo de infraestructura, solo de tiempo de cómputo (ver
  estimación al final).

## Diseño propuesto

### Espacio de búsqueda por arquitectura

**LSTM / CNN-LSTM** (via `optuna.trial.Trial`, reemplazando el dict `CONFIGS`):

| Hiperparámetro | Rango sugerido | Tipo | Nota |
|---|---|---|---|
| `hidden` | 64–256 | int (log) | hoy fijo en 128/192 |
| `layers` | 1–3 | int | hoy fijo en 2/3 |
| `dropout` | 0.1–0.5 | float | hoy fijo en 0.3/0.4 |
| `lr` | 1e-4–3e-3 | float (log) | **hoy fijo, ni siquiera está en el grid** |
| `weight_decay` | 1e-5–1e-2 | float (log) | **hoy fijo, ni siquiera está en el grid** |
| `bidir` | {True, False} | categórico | ya en el grid |
| `label_smooth` | 0.0–0.15 | float | ya en el grid |
| `lookback` | {20, 60} | categórico | hoy es un loop externo, se puede meter dentro de Optuna |

**CNN puro**: `n_filters_1/2/3` (rangos ~32–256), `kernel_size ∈ {3,5,7}`,
`dropout`, `lr`, `weight_decay` — mismo criterio.

### Por qué no copiar literalmente el presupuesto de XGBoost (25–40 trials)

Un trial de XGBoost tarda segundos/minutos. Un trial de un modelo profundo
implica entrenar hasta 100 épocas con early stopping (paciencia 20) — mucho
más caro. Copiar "40 trials" tal cual sería excesivo. Recomendado:

- **Pruner de Optuna** (`MedianPruner` o `HyperbandPruner`): reportar
  `f1_va` por época con `trial.report()` + cortar con `trial.should_prune()`
  los trials que van mal desde el principio.
- **1 seed durante la búsqueda**, no 3 — el multi-seed ensembling se aplica
  solo al reentrenar la configuración ganadora final (igual que ya hace
  `opt_xgb.py`: busca con 1 seed, reentrena con `SEEDS=[42,1,7]`).
- Presupuesto realista: **15–20 trials** por combinación (arquitectura ×
  experimento × alcance).

### Alcance recomendado (no repetir las 120 corridas completas)

No tiene sentido repetir per-ticker × 3 experimentos × 3 arquitecturas —
sería carísimo y no es donde está la pregunta del revisor. Acotar a:

- Solo **GLOBAL** (no per-ticker) — es donde el paper reporta el resultado
  principal.
- Solo **Exp B** (el "experimento recomendado" del paper) para el primer
  corte; extender a A/C solo si sobra tiempo.
- Las 3 arquitecturas (LSTM, CNN puro, CNN-LSTM).

Esto da **3 corridas de Optuna** (una por arquitectura) en el primer corte,
cada una de 15–20 trials — mucho más manejable que las 120 originales.

### Dónde implementarlo

No tocar `opt_lstm.py` / `opt_cnn_puro.py` / `opt_cnn_lstm.py` directamente
— romperían la reproducibilidad de los resultados que ya cita el paper.
Crear scripts nuevos que reusen las piezas existentes por import
(`LSTMClasificador`, `preparar_datos_*`, `entrenar()`, etc.) y reemplacen
solo el loop de `CONFIGS` fijo por un `objective()` de Optuna:

- `scripts_opt/opt_lstm_optuna.py`
- `scripts_opt/opt_cnn_puro_optuna.py`
- `scripts_opt/opt_cnn_lstm_optuna.py`

Guardar resultados en `RESULTADOS_OPTIMIZADOS/modelos_optimizados/{lstm,cnn_puro,cnn_lstm}_optuna/`
(carpeta nueva, sin pisar la existente — los resultados actuales siguen
siendo válidos y citados en el paper mientras esto no termine).

### Qué hacer con el resultado

- **Si el F1-macro del mejor modelo profundo sigue por debajo de LR/XGBoost**:
  la conclusión del paper se refuerza — ya no es "no se buscó lo
  suficiente", sino "se buscó a fondo y aun así pierde". Actualizar el
  párrafo de Limitations en `paper/paper.tex` para decirlo así de fuerte
  (con la cifra concreta).
- **Si mejora y supera a LR**: hay que revisar la narrativa del paper
  (Abstract, Tabla de F1 global, sección de Discusión) — sería un cambio
  real de conclusión, no cosmético. Avisar antes de tocar esas secciones.

### Estimación de tiempo (a confirmar con una corrida piloto)

No hay datos de tiempo por época para estos modelos en este hardware
específico. Antes de comprometerse al plan completo: correr **una sola
configuración piloto** (p. ej. LSTM, Exp B, GLOBAL, 3 trials, sin pruner)
y medir el tiempo real por trial. Con eso se puede extrapolar el total y
decidir si el presupuesto de 15–20 trials × 3 corridas es viable en el
tiempo disponible antes de la fecha límite de camera-ready.

## Siguiente paso

Este plan queda documentado y sin ejecutar. Si se decide seguir adelante,
empezar por la corrida piloto de la sección anterior para calibrar el
presupuesto real antes de comprometer horas de GPU.

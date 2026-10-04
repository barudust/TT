# CONTEXTO DEL PROYECTO — TT 2026-B164

> **Para qué sirve este archivo:** retomar el proyecto sin el historial del
> chat. Resume qué es, en qué estado está, qué se decidió y por qué, las
> cifras que hay que citar, los errores conocidos que no hay que repetir y
> dónde está cada cosa. Última actualización: **2026-10-02**.
>
> Si algo aquí contradice a otro documento, este y `STATUS.md` son los más
> recientes; los demás se corrigieron el mismo día (ver §9).

---

## 1. Qué es

Trabajo Terminal **TT 2026-B164** (ESCOM-IPN). Desarrolladores: Reyes Ramos
David y Polvo Cuatianquiz Jesús Baruc. Directores: Abdiel Reyes Vera y
Emmanuel Juárez Carbajal (grafía confirmada el 2026-10-02; documentos viejos
decían "Reyes Vega" y "Juarez Carvajal", y el paper enviado el 8 sep decía
"Cuatiaquiz").

- **Problema:** clasificar cada día COMPRAR / MANTENER / VENDER (BUY / HOLD /
  SELL) para el día siguiente en 7 acciones tecnológicas de EE. UU. (AAPL,
  NVDA, TSLA, AMZN, MSFT, GOOGL, META).
- **Restricciones del TT:** solo datos gratuitos de Yahoo Finance (OHLCV
  diario + SPY + VIX); exactamente 5 modelos (Regresión Logística, XGBoost,
  LSTM, CNN 1D, CNN-LSTM); horizonte de 1 día.
- **Etiqueta:** `r = ln(C_{t+1}/C_t)`; BUY si `r` ≥ percentil 70 de los 252
  días previos del mismo activo, SELL si ≤ percentil 30, HOLD en otro caso
  (percentiles con `shift(1)`, sin fuga de información).
- **Productos:** (1) la comparación de los 5 modelos, (2) un paper aceptado en
  MICAI 2026, (3) una plataforma web que sirve las señales del modelo ganador
  con datos reales.

## 2. Estado actual

| Parte | Estado |
|---|---|
| Modelado | **Cerrado.** Ganador: Regresión Logística global. Justificación de que no se puede mejorar más: `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md` |
| Modelo en producción | LR L2 (C = 0.000165), RobustScaler, 61 indicadores + 15 interacciones, pesos de clase "balanced" con HOLD × 0.90. `MODEL_VERSION = LR-v8-interactions-holdw090`. Entrenado con 2018–2025 |
| Paper MICAI | Capítulo 171490174 (LNAI). Camera-ready enviado el 8 sep 2026 en `paper_review/camera_ready/` (12 páginas). Sus resultados del §7 son la corrida **v4**; el §8 (Robustness) es la **v5**. Springer pidió el 2 oct el material suplementario que el paper cita y faltaba: `paper_review/supplementary/MICAI2026_ch171490174_supplementary.pdf` |
| Plataforma | Terminada: todo lo que muestra sale de Yahoo Finance o del modelo; métricas con la metodología de la tesis. Desplegada en Render desde `main` |
| Documentación | Revisada y corregida el 2026-09-30 |
| Pendiente | Documento escrito de la tesis (no está en el repo), diapositivas y ensayo de la defensa (§10) |

## 3. Cifras que hay que citar

| Qué | Valor | Fuente |
|---|---|---|
| Test 2025, protocolo v5 (Exp B, global) | LR **0.404** F1-macro (IC 95 % [0.379, 0.428]), Sharpe +0.89; XGBoost 0.359; LSTM 0.369; CNN 0.359; CNN-LSTM 0.372. LR significativamente arriba de los otros cuatro | `RESULTADOS_OPTIMIZADOS/v5/resultados_finales.csv`, paper §6 |
| Validación 2024 (v5) | Los cinco entre 0.324 y 0.366 (empate; LR el más bajo) | ídem |
| Walk-forward 2020–2025 (v5) | F1 medio: XGBoost 0.356, LR 0.350, CNN-LSTM 0.328, LSTM 0.314, CNN 0.292. Ningún modelo pasa de 0.394 en ningún año. Sharpe medio LR y XGBoost +0.22 | `RESULTADOS_OPTIMIZADOS/analisis_hold/5_walk_forward_v5_resumen.csv` |
| Costos de transacción (v5, 10 pb) | LR Sharpe +0.62; XGBoost +0.01 (LR rota menos: 0.38 vs 0.65) | `v5/resultados_finales.csv` |
| Global vs por ticker (v5, 21 casos por modelo) | Global gana en LR (18/21, p = 0.002), LSTM y CNN; empata en XGBoost; ningún modelo es mejor por ticker | `analisis_hold/4a_global_vs_porticker_por_modelo.csv` |
| Interacciones (Vía 8) | +0.023 F1 en test 2025, **pero elegidas viendo 2025**: en validación 2024 y en origen rodante 2019–2024 empatan con el LR sin ellas (0.357 vs 0.354) | `analisis_hold/7_interactions_vs_base_rolling.csv` |
| Etiqueta 40/60 ("60/40") | Peor: κ 0.077 vs 0.140 en 2025; sigue prediciendo HOLD 53 % con 20 % real | `analisis_hold/3a_percentiles_target.csv` |
| Ajuste de HOLD (origen rodante 2019–2024) | Peso HOLD × 0.90: F1 0.365 vs 0.357, κ 0.068 vs 0.063, Sharpe +0.54 vs +0.52, HOLD predicho 36 % (real 40 %) | `analisis_hold/7_reglas_alternativas_resumen.csv` |
| **Producción, 2026 fuera de muestra** | Antes (balanced): F1 0.313, κ 0.010, HOLD 60 % (real 35 %), Sharpe +0.38. **Ahora (HOLD × 0.90): F1 0.354, κ 0.035, HOLD 40 %, Sharpe +0.29** (portafolio +0.60 vs buy & hold +0.49) | `analisis_hold/8_confirmacion_2026.csv` |
| Confianza del modelo | 0.33–0.45 (azar 0.33); la tasa de acierto sube de 39 % a 56 % con más confianza | `analisis_hold/2d_accuracy_por_confianza.csv` |

## 4. Decisiones tomadas y por qué

1. **Regresión Logística global en producción.** Gana en el protocolo del paper
   (con IC bootstrap), empata con XGBoost en walk-forward pero opera menos (con
   costos gana claramente), es determinista e interpretable.
2. **Modelo global, no uno por acción.** 7× más datos; gana o empata en los 5
   modelos (§3).
3. **Se mantiene la etiqueta 30/70 a 1 día.** 40/60 empeora y no reduce el
   HOLD; horizonte de 5 días sí mejora (F1 ≈ 0.43) pero cambia el problema y
   contradice el paper → trabajo futuro.
4. **Exceso de HOLD: reentrenar con peso de clase HOLD × 0.90** (no cambiar
   la etiqueta). Un factor fijo sobre P(HOLD) empeora en 6 años de validación
   (el sesgo cambia de signo entre años: 2022 13 % vs 32 % real; 2023 74 % vs
   48 %); una regla adaptativa bajaba el Sharpe. El 0.90 se eligió solo con
   2019–2024 y es el mejor en F1, κ y Sharpe a la vez. No es una mejora
   estadísticamente significativa (Wilcoxon p = 0.31): es un modelo
   equivalente con proporción de HOLD realista.
5. **Se mantienen las 15 interacciones**, pero se presentan como equivalentes,
   no como mejora.
6. **Plataforma sin datos simulados:** overrides manuales `POST /stocks*`
   desactivados (403 salvo `ENABLE_MANUAL_OVERRIDES=1`).
7. **Render despliega desde `main`.** `dev` es rama de trabajo.

## 5. Por qué el modelo dice tanto MANTENER (para explicarlo)

- **Voto dividido:** en el 100 % de los días HOLD, P(BUY) + P(SELL) > P(HOLD)
  (≈ 0.62 contra 0.38). El modelo espera movimiento pero no sabe la dirección;
  con argmax gana HOLD. La magnitud es predecible (volatilidad), el signo casi
  no (eficiencia de mercado).
- **Régimen:** pesan sobre todo variables del mercado (VIX contra su media
  anual), iguales para las 7 acciones → HOLD "en bloque" cuando el VIX está
  bajo (agosto–septiembre de 2026).
- Explicación completa y preguntas de sinodal: `GUIA_DEFENSA_TT.md` P17.1–P17.8.

## 6. Cosas que NO hay que decir (errores ya detectados)

- **CatBoost, GRU, TabNet, Extra-Trees y Transformer NO se corrieron.** Antes
  aparecían como "probados" en tres documentos sin código ni resultados; ya
  se corrigió. Solo LightGBM se probó además de los 5 modelos.
- El walk-forward y los costos de transacción **no** son trabajo futuro: se
  hicieron en v5.
- Las cifras de la Vía 8 son de **test 2025**, no de validación 2024 (el
  `.metrics.json` decía "val 2024"; corregido).
- El F1 0.417 / Sharpe 1.25 (evaluación v1 de mayo) no es comparable con
  v4/v5; no citarlo como resultado final.
- 2025 fue el mejor año del modelo; decirlo y mostrar el walk-forward y 2026.
- Un Sharpe de un año tiene error estándar ≈ 1: no es significativo solo.

## 7. La plataforma

**Flujo:** `initialize_data()` (al arrancar, cada día hábil 16:30 NY, y cada
2 min si falta alguna acción) → descarga ~3 años de Yahoo (descarta la vela
del día si NYSE sigue abierto) → `api/ml/features.py` (76 variables) →
`api/ml/model.py` (probabilidades y señal) → `api/ml/target.py` (resultado
real del día siguiente, misma etiqueta del entrenamiento) → métricas 30/60/90
→ caché en memoria + SQLite.

**Endpoints:** `/health` (incluye `stocksLoaded`), `/stocks`,
`/stocks/:s`, `/stocks/:s/history?days=`, `/stocks/:s/metrics?days=`,
`/metrics?days=`, `/model`, `/market-status`, `POST /admin/refresh`.
Definición de cada métrica: `docs/API_FRONTEND_METRICS.md`.

**Errores que se corrigieron el 2026-09-30** (por si preguntan por versiones
anteriores): "Correcta" comparaba con el día anterior; los "F1" eran
precisiones; Sharpe y drawdown se calculaban sobre el precio de la acción; las
ventanas 60/90 no existían; "mercado cerrado" estaba fijo; la vela intradía se
trataba como cierre; el service worker dejaba a los usuarios con la interfaz
vieja; Sharpe de 1 operación daba siempre 3.00; "Acerca de" decía que las
señales las generaba una LSTM. Antes de julio la API usaba `random`.

**Trampas técnicas conocidas:**
- Si se reentrena el `.pkl`, actualizar `MODEL_VERSION` en `api/ml/model.py`
  (un test falla si no coinciden).
- Si se cambia la estrategia del service worker, cambiar `CACHE_NAME`.
- Render free: la API se duerme; el primer request tarda; si Yahoo falla al
  arrancar, el reintento cada 2 min lo repara solo.
- `ajuste_hold_rolling.py` tarda ~45 min (cada reentrenamiento del pipeline de
  producción con SAGA tarda ~60 s).

## 8. Cómo correr cada cosa (desde la raíz del repo)

```bash
# API (http://localhost:8000) y frontend (http://localhost:5173)
pip install -r api/requirements.txt
python api/main.py
npm --prefix Frontend install
npm --prefix Frontend run dev

# Tests de la API (23)
pip install -r api/requirements-dev.txt
cd api && pytest

# Análisis (dependencias: scripts_opt/requirements.txt)
python scripts_opt/analisis_hold_global.py      # ~1 min, sin red: HOLD, 40/60, global vs por-ticker
python scripts_opt/ajuste_hold_rolling.py       # ~45 min, sin red: elección del ajuste de HOLD
python scripts_opt/ajuste_hold_2026.py          # ~4 min, con red: confirmación en 2026
python scripts_opt/evaluar_produccion_2026.py   # ~1 min, con red: modelo desplegado en 2026
python scripts_opt/entrenar_produccion.py       # regenera el .pkl de producción
```

**Despliegue:** Render, Blueprint `render.yaml`, rama `main`, auto-deploy por
push. API: `https://tt-api-jc7n.onrender.com` (Docker, 1 instancia).
Frontend: `https://tt-frontend-womf.onrender.com` (static site con
`VITE_API_URL`). Tras un deploy, comprobar `/health` (`stocksLoaded: 7`) y
`/model` (`LR-v8-interactions-holdw090`). Detalle: `docs/DEPLOY_RENDER.md`.

**Repositorio:** `barudust/TT` en GitHub (remoto por SSH,
`git@github-barudust:barudust/TT.git`). Ramas: `main` (la que se despliega) y
`dev` (trabajo). `Baru` y `David` se borraron el 2026-09-30 (estaban
contenidas en `main`); un commit local viejo de `Baru` (borrador del 8 de
agosto, superado) quedó en la etiqueta **local** `respaldo/baru-local-2026-08-08`.

## 9. Mapa de documentos

| Para | Leer |
|---|---|
| Defensa: estudiar | `RESULTADOS_OPTIMIZADOS/GUIA_DEFENSA_TT.md` (Cap. 15 banco de preguntas; **Cap. 17 sinodal experta**) |
| Defensa: argumento central | `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md` |
| Redactar la tesis | `docs/THESIS_DOCUMENTATION.md` (qué documento usar por capítulo + cifras) |
| Análisis más reciente (HOLD, 40/60, global, 2026, auditoría web) | `RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md` |
| Todo lo probado (v0–v8) | `RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md` |
| Índice de documentos de investigación | `RESULTADOS_OPTIMIZADOS/docs/README.md` |
| Paper | `paper_review/README.md` |
| Modelo desplegado | `docs/MODEL_INTEGRATION.md` |
| API / métricas / frontend / BD / despliegue | `docs/API.md`, `docs/API_FRONTEND_METRICS.md`, `docs/FRONTEND.md`, `docs/DATABASE.md`, `docs/DEPLOY_RENDER.md` |
| Diagrama de arquitectura | `docs/system_architecture_diagram.svg` (el `_propuesta_inicial.svg` es el original) |
| Scripts vigentes vs historial | `scripts_opt/README.md`, `scripts_v1/README.md` |
| Estado y pendientes | `STATUS.md` |

## 10. Pendientes

0. **Responder el correo de Springer (Atchaya)** con el texto de
   `paper_review/correo_springer.txt` y dos adjuntos: el suplementario
   `paper_review/supplementary/MICAI2026_ch171490174_supplementary.pdf` y
   `078_corrected.zip` (el mismo paquete del 8 sep con el apellido corregido a
   "Cuatianquiz"). El zip no está en el repo (lleva el PDF sin el aviso de la
   licencia): está en el release **borrador** `envio-springer` de GitHub (solo
   colaboradores; no publicarlo) y se regenera con `compilar_paper.py`. Al
   enviarlo, borrar ese release. Preguntar si hace falta un formulario de
   licencia nuevo (el firmado también dice "Cuatiaquiz").
   Después, cuando salga el DOI: `python paper_review/compilar_paper.py --doi
   <DOI>` y subir `paper_review/paper.pdf` (aviso de la licencia, ver
   `paper_review/README.md`). La etiqueta `micai2026` que cita el
   suplementario ya no se debe mover una vez enviado.

1. ~~Verificar el deploy en Render~~ — hecho el 2026-09-30: `/model` sirve
   `LR-v8-interactions-holdw090`. El arranque volvió a quedar sin datos (Yahoo
   falla en el arranque en frío) y el reintento automático cargó las 7 acciones
   en ~2 minutos sin intervención.
2. Documento escrito de la tesis: incorporar walk-forward 2020–2025, exceso de
   HOLD y su ajuste, global vs por-ticker sobre las mismas filas y la
   evaluación 2026 (guía: `docs/THESIS_DOCUMENTATION.md`).
3. Diapositivas de la defensa y ensayo con el Cap. 17.
4. Opcional: verificar `docker compose up` local.

## 11. Historial de la sesión del 2026-09-30 (con Claude)

1. **Análisis del modelo y de la plataforma.** Se midió por qué el modelo
   predice tanto HOLD (voto dividido + régimen de VIX), se evaluó 40/60
   (peor), se comparó global vs por-ticker (gana global), se encontró el
   walk-forward de v5 sin citar y se evaluó 2026 fuera de muestra. Se auditó
   la página y se corrigieron todas las métricas mal calculadas (§7). Se
   escribió `JUSTIFICACION_LIMITE_DEL_MODELO.md`.
2. **Render no cargaba.** El código sí se había desplegado; Yahoo falló en el
   arranque en frío y `/stocks` quedó vacío. Se agregó el reintento cada 2 min
   y `stocksLoaded` en `/health`.
3. **Ajuste de HOLD sin tocar la etiqueta.** Validación por origen rodante
   2019–2024 de factor fijo, reglas adaptativas y pesos de clase; se adoptó
   peso HOLD × 0.90 y se reentrenó producción. Capítulo 17 de la guía de
   defensa. Corrección de modelos "probados" sin evidencia, de "trabajo
   futuro" ya hecho y de errores del Cap. 14.
4. **Cierre.** Revisión de toda la documentación (rutas del paper, rama de
   Render, base de datos, frontend, guía de tesis, diagrama de arquitectura
   nuevo), este archivo, push a `main`, `dev` recreada desde `main` y borrado
   de las ramas `Baru` y `David`.

### Sesión del 2026-10-02 (paper MICAI)

1. El `078.zip` (8 sep) es la versión más reciente del paper; el repo se
   igualó a él. El §7 usa la corrida v4 y el §8 la v5.
2. Springer pidió el suplementario citado en §3.3, §5.1, §7.1, §7.3 y §11. Se
   generó en LaTeX (7 páginas, una sección por cita, verificado contra las
   Tablas 4–6) con `paper_review/supplementary/build_supplementary.py`.
3. Se instaló MiKTeX (+ `cm-super`) y se verificó que el paper compila igual
   al PDF enviado. Se corrigió el apellido "Cuatiaquiz" → "Cuatianquiz" y los
   nombres de los directores en la página "Acerca de".
4. Versiones de bibliotecas: además de la réplica G0 (18/18 corridas
   secuenciales exactas), `scripts_opt/replicar_lr_v4.py` reproduce las 24
   corridas de LR del §7 sin diferencias (Python 3.13.5, scikit-learn 1.7.2).
5. Licencia: `paper_review/paper.pdf` (público) lleva el aviso de la cláusula
   4(c); el formulario firmado y el zip quedan fuera del repo.

# scripts_opt — scripts de la investigación (etapas 2 a 6)

Segunda parte del pipeline (la primera, la Etapa 1 = TT1, está en
`../scripts_v1/`). Se corren desde la raíz del repo: leen de
`tesis_ml_stocks/` y escriben en `../RESULTADOS_OPTIMIZADOS/`.

Los scripts conservan los nombres de trabajo (`_v2`, `_v4`, `_v5`, `via7`,
`via8`). La tabla de abajo los ordena por **etapa**, que es como se cuenta la
investigación en el documento final. Vista general, equivalencias y qué usa
el paper: [`../ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md`](../ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md).

## Por etapa

### Etapa 2 — Primeras mejoras (mayo–junio) · historial, no re-ejecutar

Optimización por modelo con los datos y particiones de TT1. Sus cifras no se
reportan (la mejor configuración se eligió con la prueba).

| Script | Qué hace |
|---|---|
| `common.py` | Carga de los datasets de TT1 (61 variables) con las particiones de TT1 |
| `opt_lr.py`, `opt_xgb.py`, `opt_lstm.py`, `opt_cnn_lstm.py`, `opt_cnn_puro.py`, `opt_cnn_puro_filtradas.py` | Optimización de cada modelo. `opt_lr.py` produjo la LR elasticnet que corrió en la plataforma hasta agosto |
| `analisis_feature_selection.py` | Preselección de variables contra las 61 → **paper §6** |
| `common_v2.py`, `feature_engineering_v2.py`, `opt_lr_v2.py`, `opt_xgb_v2.py` | 181 variables + calibración de umbrales (no mejoró) |
| `common_v3.py`, `expand_market_data.py`, `train_all_v3.py`, `comparar_v1_v3.py` | 94 variables con contexto de mercado (no mejoró) |
| `opt_lgbm.py`, `stacking.py`, `soft_voting.py`, `ensemble_lr_xgb.py`, `lr_confidence_filter.py` | LightGBM, ensambles y filtro por confianza (ninguno supera a la LR sola) |
| `consolidar.py`, `consolidar_120.py`, `reporte_final.py`, `comparar_baseline.py` | Tablas de esa etapa (`consolidar_120.py` reemplaza a `consolidar.py`; `reporte_final.py` a `comparar_baseline.py`) |
| `common_velas.py` | Sin uso (no lo importa ningún script) |

### Etapa 3 — Comparación en igualdad (junio) · paper §3–§7

| Script | Qué hace |
|---|---|
| `common_v4.py`, `train_all_v4.py` | Las 61 variables para los cinco modelos y prueba 2025 en A, B y C (120 corridas) → `RESULTADOS_OPTIMIZADOS/v4/` |
| `consolidar_v4.py`, `plots_extra.py` | Tablas y figuras de la etapa |
| `replicar_lr_v4.py` | Reproduce exactas las 24 corridas de LR del paper (scikit-learn 1.7.2) |
| `plots_paper.py` | Figuras del paper al tamaño impreso (respuesta al revisor #3) |

### Etapa 4 — Protocolo final (agosto) · paper §8 · resultado principal

| Script | Qué hace |
|---|---|
| `diag_deep.py` | Diagnóstico de las redes de la Etapa 3 (época restaurada, curvas sin paro temprano). No toca la prueba |
| `common_v5.py`, `run_v5.py` | Protocolo final y sus pasos 4.1–4.7 (replicación, decisiones, Optuna, costos, intervalos, prueba año por año) → `RESULTADOS_OPTIMIZADOS/v5/` |
| `build_dataset_v5.py` | Dataset ampliado a 93 variables (paso 4.5, no ayudó) |
| `calibrar_v5.py` | Capa de decisión y umbral económico (paso 4.6) |
| `reporte_v5.py` | Tablas y figuras para el §8 del paper |

### Etapa 5 — Búsqueda de mejoras (fin de agosto)

| Script | Qué hace |
|---|---|
| `via7_refinamiento.py` | Ajustes al modelo: calibración, mezclas, SWA, recencia → `RESULTADOS_OPTIMIZADOS/v7/` |
| `via8_dataset.py` | Variables nuevas: rezagos, entre acciones, multi-escala, **interacciones** → `RESULTADOS_OPTIMIZADOS/v8/` |
| `via8_target_extendido.py`, `via8_combinado.py` | Otros horizontes y percentiles de la etiqueta. **Fuera del planteamiento** (trabajo futuro) |

### Etapa 6 — Modelo de la plataforma y validación (septiembre–octubre) · vigente

| Script | Qué hace |
|---|---|
| `entrenar_produccion.py` | **Regenera el `.pkl` de la plataforma** (LR + 15 interacciones, pesos "balanced" con mantener × `PESO_HOLD`). Si se cambia algo, actualizar `MODEL_VERSION` en `api/ml/model.py` (hay una prueba que lo exige) |
| `analisis_hold_global.py` | Por qué el modelo predice tanto mantener, etiqueta 40/60, global contra por acción. ~20 s, sin red |
| `ajuste_hold_rolling.py` | Elige el ajuste de mantener por origen rodante 2019–2024 (peso × 0.90). ~45 min, sin red |
| `ajuste_hold_2026.py`, `evaluar_produccion_2026.py` | Confirman el modelo en 2026 con el mismo código que la API. Requieren red |
| `calibrar_niveles_confianza.py` | Niveles de seguridad que muestra la plataforma |
| `verificar_ventana_redes.py` | Mide el efecto de que la ventana de las redes termine un día antes |
| `calibrar_hold.py` | Antecedente de julio: factor fijo sobre la probabilidad de mantener (sustituido por el peso × 0.90) |
| `observaciones_sinodal.py` | Respuesta a la sinodal (26 oct): ocho métricas para los cinco, cómo se elige el modelo, multicolinealidad (61 contra filtro VIF ≤ 10), dataset hasta hoy (`01_raw_datasets_2026/`), prueba ciega 2026 de los cinco y el JSON de la pestaña «Modelos» → `RESULTADOS_OPTIMIZADOS/observaciones_sinodal/` |

## Dependencias

`requirements.txt` (además de las de la API). Los análisis de la Etapa 6
documentados en `../RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md`.

> **Nota (2026-10-22).** Documento de trabajo de la **Etapa 4 (protocolo final)**, con los nombres que se usaban entonces. Equivalencias: v1 = Etapa 1 (TT1) · optimización de mayo, "v0", v2 y v3 = Etapa 2 · v4 = Etapa 3 · v5 = Etapa 4 (sus V0–V6 = pasos 4.1–4.7) · v7/"Vía 7" y v8/"Vía 8" = Etapa 5 · análisis de septiembre = Etapa 6 · "walk-forward" = prueba año por año. Referencia: [mapa de experimentos](../../../ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md).

**Presupuesto de búsqueda de hiperparámetros por modelo (todos con el mismo protocolo; F1 medido en 2024, no en test)**

| modelo | metodo | trials | completos | hiperparametros | mejor_f1_dev |
|---|---|---|---|---|---|
| LR | Optuna TPE | 150 | 150 | 5 | 0.3401 |
| XGBoost | Optuna TPE | 150 | 150 | 9 | 0.3871 |
| LSTM | Optuna TPE + MedianPruner | 80 | 54 | 17 | 0.3649 |
| CNN | Optuna TPE + MedianPruner | 80 | 53 | 20 | 0.3626 |
| CNN-LSTM | Optuna TPE + MedianPruner | 80 | 74 | 19 | 0.3621 |

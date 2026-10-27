> **Nota (2026-10-22).** Documento de trabajo de la **Etapa 4 (protocolo final)**, con los nombres que se usaban entonces. Equivalencias: v1 = Etapa 1 (TT1) · optimización de mayo, "v0", v2 y v3 = Etapa 2 · v4 = Etapa 3 · v5 = Etapa 4 (sus V0–V6 = pasos 4.1–4.7) · v7/"Vía 7" y v8/"Vía 8" = Etapa 5 · análisis de septiembre = Etapa 6 · "walk-forward" = prueba año por año. Referencia: [mapa de experimentos](../../../ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md).

**Métricas económicas, Exp B GLOBAL (test 2025)**

| modelo | test_f1_ens | test_f1_std | win_rate | profit_factor | max_dd | sharpe | signal_buy | signal_hold | signal_sell |
|---|---|---|---|---|---|---|---|---|---|
| LR | 0.4036 | 0.0000 | 0.5203 | 1.2695 | -0.4530 | 0.8946 | 20.7000 | 51.7000 | 27.5000 |
| XGBoost | 0.3591 | 0.0046 | 0.4908 | 1.1111 | -0.4985 | 0.4620 | 26.9000 | 31.1000 | 42.0000 |
| LSTM | 0.3688 | 0.0178 | 0.4901 | 0.9225 | -0.6758 | -0.3451 | 18.1000 | 35.8000 | 46.0000 |
| CNN | 0.3590 | 0.0126 | 0.4842 | 0.9001 | -0.7250 | -0.4592 | 15.6000 | 34.6000 | 49.9000 |
| CNN-LSTM | 0.3723 | 0.0420 | 0.4844 | 0.9824 | -0.6213 | -0.0739 | 33.0000 | 39.2000 | 27.8000 |

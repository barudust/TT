**Presupuesto de búsqueda de hiperparámetros por modelo (todos con el mismo protocolo; F1 medido en 2024, no en test)**

| modelo | metodo | trials | completos | hiperparametros | mejor_f1_dev |
|---|---|---|---|---|---|
| LR | Optuna TPE | 150 | 150 | 5 | 0.3401 |
| XGBoost | Optuna TPE | 150 | 150 | 9 | 0.3871 |
| LSTM | Optuna TPE + MedianPruner | 80 | 54 | 17 | 0.3649 |
| CNN | Optuna TPE + MedianPruner | 80 | 53 | 20 | 0.3626 |
| CNN-LSTM | Optuna TPE + MedianPruner | 80 | 74 | 19 | 0.3621 |

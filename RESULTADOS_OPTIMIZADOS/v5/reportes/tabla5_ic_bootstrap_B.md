**F1-macro con IC 95 % (bootstrap de bloques), Exp B GLOBAL, test 2025**

| modelo | f1 | ic_lo | ic_hi |
|---|---|---|---|
| CNN | 0.3590 | 0.3316 | 0.3855 |
| CNN-LSTM | 0.3723 | 0.3464 | 0.3954 |
| LR | 0.4036 | 0.3788 | 0.4279 |
| LSTM | 0.3688 | 0.3408 | 0.3948 |
| XGBoost | 0.3591 | 0.3339 | 0.3812 |

**Diferencias entre pares de modelos**

| modelo_a | modelo_b | dif | ic_lo | ic_hi | significativa |
|---|---|---|---|---|---|
| CNN | CNN-LSTM | -0.0133 | -0.0328 | 0.0110 | False |
| CNN | LR | -0.0446 | -0.0701 | -0.0189 | True |
| CNN | LSTM | -0.0098 | -0.0268 | 0.0061 | False |
| CNN | XGBoost | -0.0001 | -0.0309 | 0.0304 | False |
| CNN-LSTM | LR | -0.0313 | -0.0544 | -0.0103 | True |
| CNN-LSTM | LSTM | 0.0035 | -0.0196 | 0.0239 | False |
| CNN-LSTM | XGBoost | 0.0132 | -0.0186 | 0.0415 | False |
| LR | LSTM | 0.0348 | 0.0078 | 0.0623 | True |
| LR | XGBoost | 0.0446 | 0.0150 | 0.0738 | True |
| LSTM | XGBoost | 0.0097 | -0.0222 | 0.0410 | False |

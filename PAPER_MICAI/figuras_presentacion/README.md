# Figures for the MICAI talk

English, presentation-sized, PNG (300 dpi) and SVG. Only numbers that the
paper reports; the script checks them against Tables 3 and 4.

| File | Shows | Paper | Slide |
|---|---|---|---|
| `P01_benchmark_f1_global` | Macro-F1 of the five global models in A/B/C (Table 3) | §7.1 | 7 |
| `P02_robustness_ci_expB` | Exp B with 95 % CIs under the corrected protocol, plus the Section 7 value (Table 6) | §8 | 12 |
| `P03_feature_preselection` | Δ F1 of keeping all 61 features vs. statistical filters (Table 2) | §6 | 9 |
| `P04_economics_expB` | Sharpe and profit factor, Exp B (Table 4) | §7.1 | 8 |
| `P05_sharpe_variance_decomposition` | Ticker 15.5 % vs model 3.4 % of Sharpe variation | §7.3 | 10 |
| `P06_benchmark_to_corrected_protocol` | Each model from Section 7 to Section 8 (Exp B) | §8 | 12 (alt.) |

Also usable from the paper: `../paper_review/figures/fig_signal_dist.png`
(Figure 1) and `fig_sharpe_heatmap.png` (supplementary S4).

Regenerate:

```bash
python figuras_presentacion/fuente/generar_figuras.py
```

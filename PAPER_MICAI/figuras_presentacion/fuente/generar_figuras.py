"""Figures for the MICAI 2026 talk (English), built only from what the paper reports.

Usage (from the repository root):

    python PAPER_MICAI/figuras_presentacion/fuente/generar_figuras.py

Writes PNG (300 dpi) and SVG to PAPER_MICAI/figuras_presentacion/. Numbers
come from the stored results that the paper cites (Stage 3 benchmark:
RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv; Stage 4 robustness:
RESULTADOS_OPTIMIZADOS/v5/) and, where the paper reports a derived value
(feature pre-selection deltas, Sharpe variance decomposition), from paper.tex.
The script checks that the computed values match the paper's tables.

Colors: one fixed hue per model (LR blue, XGBoost orange, LSTM aqua,
CNN-LSTM yellow, 1-D CNN magenta), validated for color-vision deficiency.
Models are always named on an axis or in a legend, never by color alone.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
RO = RAIZ / "RESULTADOS_OPTIMIZADOS"
SALIDA = Path(__file__).resolve().parents[1]

ORDER = ["LR", "XGBoost", "LSTM", "CNN-LSTM", "CNN"]
LABEL = {"LR": "LR", "XGBoost": "XGBoost", "LSTM": "LSTM", "CNN-LSTM": "CNN-LSTM", "CNN": "1-D CNN"}
COLOR = {"LR": "#2a78d6", "XGBoost": "#eb6834", "LSTM": "#1baf7a", "CNN-LSTM": "#eda100", "CNN": "#e87ba4"}
MARK = {"LR": "o", "XGBoost": "s", "LSTM": "^", "CNN-LSTM": "D", "CNN": "v"}
INK, INK2, FAINT, GRID = "#1f2937", "#52514e", "#8a8f98", "#e6e8ec"
CHANCE = 1 / 3

plt.rcParams.update({
    "font.family": "Arial", "font.size": 11,
    "axes.edgecolor": "#b8bdc6", "axes.labelcolor": INK2,
    "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "legend.frameon": False, "svg.fonttype": "none",
})


def save(fig, name: str) -> None:
    for ext in ("png", "svg"):
        fig.savefig(SALIDA / f"{name}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(name)


def stage3_global() -> pd.DataFrame:
    """Global rows of the Stage 3 benchmark with the look-back chosen as in the paper (best on test)."""
    d = pd.read_csv(RO / "v4" / "resultados_v4.csv")
    d = d[d.ticker == "GLOBAL"].copy()
    idx = d.groupby(["modelo", "experimento"]).test_f1_macro.idxmax()
    return d.loc[idx].set_index(["modelo", "experimento"])


# ---------------------------------------------------------------------------
def p01_benchmark_f1() -> None:
    g = stage3_global().test_f1_macro.unstack()
    paper = {"LR": (0.411, 0.385, 0.401), "XGBoost": (0.396, 0.386, 0.373), "LSTM": (0.389, 0.370, 0.370),
             "CNN-LSTM": (0.376, 0.384, 0.371), "CNN": (0.361, 0.343, 0.373)}
    for m, vals in paper.items():  # Table 3 of the paper
        assert all(abs(round(g.loc[m, e], 3) - v) < 1e-9 for e, v in zip("ABC", vals)), (m, g.loc[m].round(3).tolist())
    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    w = 0.15
    for j, m in enumerate(ORDER):
        xs = [i + (j - 2) * w for i in range(3)]
        vals = [g.loc[m, e] for e in "ABC"]
        ax.bar(xs, vals, width=w * 0.88, color=COLOR[m], label=LABEL[m], edgecolor="white", linewidth=1)
        if m == "LR":
            for x, v in zip(xs, vals):
                ax.text(x, v + 0.003, f"{v:.3f}", ha="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.axhline(CHANCE, color=FAINT, lw=1.2, ls="--")
    ax.text(-0.42, CHANCE + 0.002, "random 1/3", ha="left", fontsize=9.5, color=FAINT)
    ax.set_ylim(0.30, 0.425)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Exp A · 10 training years", "Exp B · 6 years", "Exp C · 4 years"])
    ax.set_ylabel("Macro-F1, test year 2025")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=5)
    ax.set_title("Global models: LR leads on average (0.399)", loc="left")
    fig.tight_layout()
    save(fig, "P01_benchmark_f1_global")


# ---------------------------------------------------------------------------
def p02_robustness_ci() -> None:
    ci = pd.read_csv(RO / "v5" / "v6_ic_B_v1.csv").set_index("modelo")
    s3 = stage3_global().test_f1_macro.unstack()["B"]
    fig, ax = plt.subplots(figsize=(8.0, 3.6))
    for i, m in enumerate(ORDER):
        y = len(ORDER) - 1 - i
        f, lo, hi = ci.loc[m, ["f1", "ic_lo", "ic_hi"]]
        ax.plot([lo, hi], [y, y], color=COLOR[m], lw=2.4, solid_capstyle="round")
        ax.plot(f, y, MARK[m], color=COLOR[m], ms=8, mec="white", mew=1.4, zorder=3)
        ax.plot(s3[m], y, MARK[m], mfc="white", mec=COLOR[m], mew=1.6, ms=7, zorder=2)
        ax.text(0.497, y, f"{f:.3f}  [{lo:.3f}, {hi:.3f}]", va="center", ha="right", fontsize=9.5, color=INK)
    ax.text(0.497, len(ORDER) - 0.4, "macro-F1  [95 % CI]", ha="right", fontsize=9.5, color=INK2, fontweight="bold")
    ax.axvline(CHANCE, color=FAINT, lw=1.2, ls="--")
    ax.set_yticks(range(len(ORDER)))
    ax.set_yticklabels([LABEL[m] for m in reversed(ORDER)])
    ax.set_xlim(0.32, 0.50)
    ax.set_xticks([0.33, 0.35, 0.37, 0.39, 0.41, 0.43])
    ax.set_ylim(-0.6, len(ORDER) - 0.1)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Macro-F1, Exp B global, test year 2025")
    legend = [Line2D([], [], marker="o", ls="", color=INK2, mec="white", ms=8, label="corrected protocol (Sec. 8)"),
              Line2D([], [], marker="o", ls="", mfc="white", mec=INK2, mew=1.5, ms=7, label="benchmark (Sec. 7)")]
    ax.legend(handles=legend, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
    fig.tight_layout()
    save(fig, "P02_robustness_ci_expB")


# ---------------------------------------------------------------------------
def p03_feature_preselection() -> None:
    # Table 2 of the paper: Δ = F1(all 61) − F1(filtered), GLOBAL.
    delta = {"LR": (0.024, 0.026, 0.021), "XGBoost": (0.009, 0.021, 0.022), "LSTM": (0.039, 0.036, -0.006),
             "CNN": (0.035, -0.025, 0.011), "CNN-LSTM": (-0.011, 0.020, -0.026)}
    fig, ax = plt.subplots(figsize=(8.6, 3.7))
    w = 0.15
    for j, m in enumerate(ORDER):
        xs = [i + (j - 2) * w for i in range(3)]
        ax.bar(xs, delta[m], width=w * 0.88, color=COLOR[m], label=LABEL[m], edgecolor="white", linewidth=1)
    ax.axhline(0, color="#7d838c", lw=1.1)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Exp A", "Exp B", "Exp C"])
    ax.set_ylabel("F1 (all 61) − F1 (filtered)")
    ax.text(2.45, 0.036, "keeping all features is better ↑", ha="right", fontsize=10, color=INK2)
    ax.text(2.45, -0.03, "filter is better ↓", ha="right", fontsize=10, color=INK2)
    ax.set_ylim(-0.035, 0.045)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=5)
    ax.set_title("Statistical pre-selection hurts in 11 of 15 cases", loc="left")
    fig.tight_layout()
    save(fig, "P03_feature_preselection")


# ---------------------------------------------------------------------------
def p04_economics_expB() -> None:
    g = stage3_global()
    b = g.xs("B", level="experimento")
    paper = {"LR": (0.755, 1.210), "XGBoost": (0.345, 1.083), "CNN-LSTM": (0.147, 1.041), "LSTM": (0.433, 1.120), "CNN": (0.121, 1.031)}
    for m, (sh, pf) in paper.items():  # Table 4 of the paper
        assert abs(round(b.loc[m, "sharpe_test"], 3) - sh) < 1e-9 and abs(round(b.loc[m, "profit_factor_test"], 3) - pf) < 1e-9, m
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.4), sharey=True)
    ys = [len(ORDER) - 1 - i for i in range(len(ORDER))]
    for ax, col, title, ref in [(axes[0], "sharpe_test", "Annualized Sharpe", 0.0), (axes[1], "profit_factor_test", "Profit factor", 1.0)]:
        vals = [b.loc[m, col] for m in ORDER]
        ax.barh(ys, [v - ref for v in vals], left=ref, color=[COLOR[m] for m in ORDER], height=0.56, edgecolor="white", linewidth=1.5)
        for y, v in zip(ys, vals):
            ax.text(v + (0.02 if col == "sharpe_test" else 0.006), y, f"{v:+.3f}" if col == "sharpe_test" else f"{v:.3f}",
                    va="center", fontsize=9.5, color=INK)
        ax.axvline(ref, color="#7d838c", lw=1.1)
        ax.set_title(title, loc="left", fontsize=11.5)
        ax.grid(axis="y", visible=False)
    axes[0].set_xlim(0, 0.95)
    axes[1].set_xlim(0.98, 1.26)
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([LABEL[m] for m in ORDER])
    fig.text(0.01, -0.04, "Exp B global, test year 2025, Section 7 benchmark, no transaction costs.", fontsize=9, color=INK2)
    fig.tight_layout(w_pad=2)
    save(fig, "P04_economics_expB")


# ---------------------------------------------------------------------------
def p05_sharpe_variance() -> None:
    parts = [("Ticker", 15.5), ("Experiment\n(training years)", 7.0), ("Model", 3.4), ("Interaction\nand noise", 74.1)]
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    ys = list(range(len(parts)))[::-1]
    # One hue (not the model colors): darker = the share the title talks about.
    colors = ["#1c5cab", "#86b6ef", "#86b6ef", "#d4d7dc"]
    ax.barh(ys, [p[1] for p in parts], color=colors, height=0.56, edgecolor="white", linewidth=1.5)
    for y, (_, v) in zip(ys, parts):
        ax.text(v + 1, y, f"{v:.1f} %", va="center", fontsize=10.5, color=INK)
    ax.set_yticks(ys)
    ax.set_yticklabels([p[0] for p in parts])
    ax.set_xlim(0, 85)
    ax.set_xlabel("Share of the total sum of squares of 105 per-ticker Sharpe ratios")
    ax.grid(axis="y", visible=False)
    ax.set_title("The ticker explains ~4.5× more Sharpe variation than the model", loc="left")
    fig.tight_layout()
    save(fig, "P05_sharpe_variance_decomposition")


# ---------------------------------------------------------------------------
def p06_stage3_to_stage4() -> None:
    s3 = stage3_global().test_f1_macro.unstack()["B"]
    ci = pd.read_csv(RO / "v5" / "v6_ic_B_v1.csv").set_index("modelo").f1
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    for m in ORDER:
        ax.plot([0, 1], [s3[m], ci[m]], color=COLOR[m], lw=3 if m == "LR" else 2, marker=MARK[m], ms=8, mec="white", mew=1.2,
                label=LABEL[m], zorder=3 if m == "LR" else 2)
    ax.text(-0.05, s3["LR"], f"{s3['LR']:.3f}", ha="right", va="center", fontsize=10, color=INK, fontweight="bold")
    ax.text(1.05, ci["LR"], f"{ci['LR']:.3f}", ha="left", va="center", fontsize=10, color=INK, fontweight="bold")
    ax.axhline(CHANCE, color=FAINT, lw=1.2, ls="--")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Benchmark (Sec. 7)\nlook-back picked on test", "Corrected protocol (Sec. 8)\nno test-set decisions"])
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(0.33, 0.41)
    ax.set_ylabel("Macro-F1, Exp B global, 2025")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=5, fontsize=10)
    ax.set_title("A serious search does not close the gap", loc="left")
    fig.tight_layout()
    save(fig, "P06_benchmark_to_corrected_protocol")


if __name__ == "__main__":
    p01_benchmark_f1()
    p02_robustness_ci()
    p03_feature_preselection()
    p04_economics_expB()
    p05_sharpe_variance()
    p06_stage3_to_stage4()

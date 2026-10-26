"""Gráficas de resultados para el reporte técnico (G01 a G07).

Uso (desde la raíz del repositorio):

    python REPORTE_TECNICO/graficas/fuente/generar_graficas.py

Lee los resultados guardados en RESULTADOS_OPTIMIZADOS/ (no recalcula nada) y
escribe PNG (300 ppp) y SVG en REPORTE_TECNICO/graficas/. Cada gráfica tiene
su tabla en REPORTE_TECNICO/tablas/TABLAS_NUEVAS.md.

Colores: orden categórico fijo por modelo (LR azul, XGBoost naranja, LSTM
aqua, CNN-LSTM amarillo, CNN 1D magenta), validado para daltonismo con el
validador de la guía de visualización. Como aqua, amarillo y magenta tienen
contraste bajo sobre blanco, el modelo siempre se nombra en el eje o en la
leyenda (nunca solo por color).
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

ORDEN = ["LR", "XGBoost", "LSTM", "CNN-LSTM", "CNN"]
NOMBRE = {"LR": "Regresión Logística", "XGBoost": "XGBoost", "LSTM": "LSTM", "CNN-LSTM": "CNN-LSTM", "CNN": "CNN 1D"}
CORTO = {"LR": "LR", "XGBoost": "XGBoost", "LSTM": "LSTM", "CNN-LSTM": "CNN-LSTM", "CNN": "CNN 1D"}
COLOR = {"LR": "#2a78d6", "XGBoost": "#eb6834", "LSTM": "#1baf7a", "CNN-LSTM": "#eda100", "CNN": "#e87ba4"}
MARCA = {"LR": "o", "XGBoost": "s", "LSTM": "^", "CNN-LSTM": "D", "CNN": "v"}

TINTA = "#1f2937"
TINTA2 = "#52514e"
TENUE = "#8a8f98"
REJILLA = "#e6e8ec"
AZAR = 1 / 3

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 9.5,
    "axes.edgecolor": "#b8bdc6",
    "axes.labelcolor": TINTA2,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
    "axes.titlecolor": TINTA,
    "xtick.color": TINTA2,
    "ytick.color": TINTA2,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": REJILLA,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "legend.frameon": False,
    "svg.fonttype": "none",
})


def guardar(fig, nombre: str) -> None:
    for ext in ("png", "svg"):
        fig.savefig(SALIDA / f"{nombre}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(nombre)


def linea_azar(ax, vertical=True, texto=True) -> None:
    if vertical:
        ax.axvline(AZAR, color=TENUE, lw=1, ls="--", zorder=1)
        if texto:
            ax.text(AZAR, 1.01, "azar", transform=ax.get_xaxis_transform(), ha="center", va="bottom",
                    fontsize=8, color=TENUE)
    else:
        ax.axhline(AZAR, color=TENUE, lw=1, ls="--", zorder=1)
        if texto:
            ax.text(1.0, AZAR, " azar", transform=ax.get_yaxis_transform(), ha="left", va="center",
                    fontsize=8, color=TENUE)


# ---------------------------------------------------------------------------
def g01_f1_intervalos() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.9), sharey=True, sharex=True)
    nombres_exp = {"A": "Experimento A · 10 años", "B": "Experimento B · 6 años (principal)", "C": "Experimento C · 4 años"}
    for ax, exp in zip(axes, "ABC"):
        d = pd.read_csv(RO / "v5" / f"v6_ic_{exp}_v1.csv").set_index("modelo")
        for i, m in enumerate(ORDEN):
            y = len(ORDEN) - 1 - i
            f, lo, hi = d.loc[m, ["f1", "ic_lo", "ic_hi"]]
            ax.plot([lo, hi], [y, y], color=COLOR[m], lw=2, solid_capstyle="round", zorder=2)
            ax.plot(f, y, MARCA[m], color=COLOR[m], ms=6.5, mec="white", mew=1.2, zorder=3)
            if m == "LR":
                ax.text(hi + 0.006, y, f"{f:.3f}", va="center", fontsize=8.5, color=TINTA, fontweight="bold")
        linea_azar(ax)
        ax.set_title(nombres_exp[exp], fontsize=9.2, pad=14)
        ax.set_xlim(0.2, 0.46)
        ax.set_xticks([0.20, 0.30, 0.40])
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("F1-macro (prueba 2025)")
    axes[0].set_yticks(range(len(ORDEN)))
    axes[0].set_yticklabels([CORTO[m] for m in reversed(ORDEN)])
    fig.text(0.01, -0.06, "Punto: F1-macro. Línea: intervalo de confianza del 95 % (bootstrap por bloques de 20 días, 2 000 réplicas). "
             "Mismas 1 736 filas para los cinco.", fontsize=7.8, color=TINTA2)
    fig.tight_layout(w_pad=1.2)
    guardar(fig, "G01_f1_intervalos_etapa4")


# ---------------------------------------------------------------------------
def g02_sharpe_costos() -> None:
    d = pd.read_csv(RO / "v5" / "resultados_finales.csv")
    d = d[(d.tipo == "global") & (d.exp == "B")].set_index("modelo")
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    for i, m in enumerate(ORDEN):
        y = len(ORDEN) - 1 - i
        s0, s10, rot = d.loc[m, ["sharpe", "sharpe_10bp", "turnover_medio"]]
        ax.annotate("", xy=(s10, y), xytext=(s0, y),
                    arrowprops=dict(arrowstyle="-|>", color=COLOR[m], lw=1.8, shrinkA=4, shrinkB=4, mutation_scale=9))
        ax.plot(s0, y, "o", color=COLOR[m], ms=7, mec="white", mew=1.2, zorder=3)
        ax.plot(s10, y, "o", mfc="white", mec=COLOR[m], mew=1.8, ms=6.5, zorder=3)
        ax.text(1.32, y, f"{rot:.2f}", va="center", ha="right", fontsize=8.5, color=TINTA)
        if m in ("LR", "XGBoost"):
            ax.text(s0, y + 0.3, f"{s0:+.2f}", ha="center", fontsize=8, color=TINTA)
            ax.text(s10, y - 0.42, f"{s10:+.2f}", ha="center", fontsize=8, color=TINTA)
    ax.text(1.32, len(ORDEN) - 0.45, "rotación", ha="right", fontsize=8, color=TINTA2, fontweight="bold")
    ax.axvline(0, color="#9aa0a8", lw=1)
    ax.set_yticks(range(len(ORDEN)))
    ax.set_yticklabels([CORTO[m] for m in reversed(ORDEN)])
    ax.set_xlim(-0.75, 1.35)
    ax.set_xticks([-0.5, -0.25, 0, 0.25, 0.5, 0.75, 1.0])
    ax.set_ylim(-0.7, len(ORDEN) - 0.2)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Índice de Sharpe anualizado (Experimento B, prueba 2025)")
    leyenda = [Line2D([], [], marker="o", ls="", color=TINTA2, mec="white", ms=7, label="sin costos"),
               Line2D([], [], marker="o", ls="", mfc="white", mec=TINTA2, mew=1.6, ms=6.5, label="con 10 pb por cambio de posición")]
    ax.legend(handles=leyenda, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2, fontsize=8.3)
    fig.tight_layout()
    guardar(fig, "G02_sharpe_costos_etapa4")


# ---------------------------------------------------------------------------
def _etapa3_global() -> pd.DataFrame:
    """F1 global de la Etapa 3 con el mejor lookback en la prueba (como el paper §7)."""
    d = pd.read_csv(RO / "v4" / "resultados_v4.csv")
    d = d[d.ticker == "GLOBAL"]
    return d.groupby(["modelo", "experimento"]).test_f1_macro.max().unstack()


def g03_etapa3_contra_etapa4() -> None:
    e3 = _etapa3_global()
    d = pd.read_csv(RO / "v5" / "resultados_finales.csv")
    e4 = d[d.tipo == "global"].pivot_table(index="modelo", columns="exp", values="test_f1_ens")
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.2), sharey=True)
    paneles = [("Experimento B", lambda t: t["B"]), ("Promedio de A, B y C", lambda t: t[["A", "B", "C"]].mean(axis=1))]
    for ax, (titulo, fn) in zip(axes, paneles):
        v3, v4 = fn(e3), fn(e4)
        for m in ORDEN:
            lw = 2.6 if m == "LR" else 1.8
            ax.plot([0, 1], [v3[m], v4[m]], color=COLOR[m], lw=lw, marker=MARCA[m], ms=6, mec="white", mew=1, zorder=3 if m == "LR" else 2)
        ax.text(-0.06, v3["LR"], f"{v3['LR']:.3f}", ha="right", va="center", fontsize=8.5, color=TINTA, fontweight="bold")
        ax.text(1.06, v4["LR"], f"{v4['LR']:.3f}", ha="left", va="center", fontsize=8.5, color=TINTA, fontweight="bold")
        linea_azar(ax, vertical=False, texto=False)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Etapa 3\n(ventana de las redes\nelegida con la prueba)", "Etapa 4\n(protocolo final)"], fontsize=8.3)
        ax.set_xlim(-0.35, 1.35)
        ax.set_title(titulo, fontsize=9.5)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("F1-macro (prueba 2025, modelo global)")
    axes[0].set_ylim(0.29, 0.415)
    axes[1].text(1.36, AZAR, "azar", fontsize=8, color=TENUE, va="center")
    leyenda = [Line2D([], [], color=COLOR[m], marker=MARCA[m], lw=2, mec="white", label=CORTO[m]) for m in ORDEN]
    fig.legend(handles=leyenda, loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.06), fontsize=8.5)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    guardar(fig, "G03_etapa3_contra_etapa4")


# ---------------------------------------------------------------------------
def g04_anio_por_anio() -> None:
    d = pd.read_csv(RO / "v5" / "walkforward_v4.csv")
    d = d[d.tipo == "global"].pivot_table(index="anio", columns="modelo", values="test_f1_ens")
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    for m in ORDEN:
        ax.plot(d.index, d[m], color=COLOR[m], lw=2.6 if m == "LR" else 1.8, marker=MARCA[m], ms=6, mec="white", mew=1,
                label=f"{CORTO[m]} (media {d[m].mean():.3f})", zorder=3 if m == "LR" else 2)
    linea_azar(ax, vertical=False)
    ax.set_xticks(d.index)
    ax.set_ylabel("F1-macro del año de prueba")
    ax.set_ylim(0.28, 0.41)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8.3)
    ax.set_title("Prueba año por año con los ajustes fijados de antemano (Etapa 3)", fontsize=9.5, loc="left")
    fig.tight_layout()
    guardar(fig, "G04_anio_por_anio")


# ---------------------------------------------------------------------------
def g05_ciega_2026() -> None:
    d = pd.read_csv(RO / "observaciones_sinodal" / "4_ciega2026.csv").set_index("modelo")
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7), sharey=True)
    ys = [len(ORDEN) - 1 - i for i in range(len(ORDEN))]
    for ax, col, titulo, xlab in [(axes[0], "f1_macro", "Clasificación", "F1-macro"),
                                  (axes[1], "sharpe_0bp", "Simulación económica", "Índice de Sharpe (sin costos)")]:
        vals = [d.loc[m, col] for m in ORDEN]
        ax.barh(ys, vals, color=[COLOR[m] for m in ORDEN], height=0.56, edgecolor="white", linewidth=1.5)
        for y, v in zip(ys, vals):
            if col == "f1_macro":
                # columna de valores a la derecha, fuera de la línea del azar
                ax.text(0.379, y, f"{v:.3f}", va="center", ha="right", fontsize=8.3, color=TINTA)
            else:
                txt = "0.00" if abs(v) < 0.005 else f"{v:+.2f}"
                ax.text(max(v, 0) + 0.03, y, txt, va="center", ha="left", fontsize=8.3, color=TINTA)
        ax.set_title(titulo, fontsize=9.5, loc="left")
        ax.set_xlabel(xlab)
        ax.grid(axis="y", visible=False)
    linea_azar(axes[0])
    axes[0].set_xlim(0.25, 0.38)
    axes[1].axvline(0, color="#9aa0a8", lw=1)
    axes[1].set_xlim(-0.1, 1.05)
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([CORTO[m] for m in ORDEN])
    fig.text(0.01, -0.07, "2 de enero a 22 de octubre de 2026 (1 421 filas), ajustes congelados, entrenamiento 2020–2024. "
             "En F1 solo la diferencia LR − CNN 1D es significativa.", fontsize=7.8, color=TINTA2)
    fig.tight_layout(w_pad=2)
    guardar(fig, "G05_prueba_ciega_2026")


# ---------------------------------------------------------------------------
def g06_multicolinealidad() -> None:
    d = pd.read_csv(RO / "observaciones_sinodal" / "3_multicolinealidad_resumen.csv")
    d = d[d.exp.isin(["A", "B", "C"])].pivot_table(index="exp", columns="modelo", values="delta_todas_menos_filtro")
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    ancho = 0.15
    for j, m in enumerate(ORDEN):
        xs = [i + (j - 2) * ancho for i in range(3)]
        ax.bar(xs, d[m].values, width=ancho * 0.9, color=COLOR[m], label=CORTO[m], edgecolor="white", linewidth=0.8)
    ax.axhline(0, color="#7d838c", lw=1)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Experimento A", "Experimento B", "Experimento C"])
    ax.set_ylabel("F1 con las 61 − F1 con filtro VIF ≤ 10")
    ax.text(2.52, 0.036, "las 61 son mejores ↑", ha="right", fontsize=8.3, color=TINTA2)
    ax.text(2.52, -0.012, "el filtro es mejor ↓", ha="right", fontsize=8.3, color=TINTA2)
    ax.set_ylim(-0.016, 0.044)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=8.3)
    ax.set_title("Las 61 variables ganan en 11 de 15 casos; el filtro perjudica sobre todo a las redes",
                 fontsize=9.3, loc="left")
    fig.tight_layout()
    guardar(fig, "G06_multicolinealidad")


# ---------------------------------------------------------------------------
def g07_global_contra_por_accion() -> None:
    d = pd.read_csv(RO / "analisis_hold" / "4a_global_vs_porticker_por_modelo.csv").set_index("modelo")
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    for i, m in enumerate(ORDEN):
        y = len(ORDEN) - 1 - i
        g, t = d.loc[m, ["f1_global_medio", "f1_por_ticker_medio"]]
        gana, celdas, p = int(d.loc[m, "celdas_gana_global_f1"]), int(d.loc[m, "celdas"]), d.loc[m, "p_signo_f1"]
        ax.plot([t, g], [y, y], color=COLOR[m], lw=2, solid_capstyle="round")
        ax.plot(t, y, "o", mfc="white", mec=COLOR[m], mew=1.8, ms=6.5, zorder=3)
        ax.plot(g, y, "o", color=COLOR[m], mec="white", mew=1.2, ms=7, zorder=3)
        ptxt = "p < 0.001" if p < 0.001 else f"p = {p:.3f}" if p < 0.1 else f"p = {p:.2f}"
        ax.text(0.452, y, f"{gana} de {celdas}   {ptxt}", va="center", ha="right", fontsize=8.3, color=TINTA)
    ax.text(0.452, len(ORDEN) - 0.45, "gana el global", ha="right", fontsize=8, color=TINTA2, fontweight="bold")
    ax.set_yticks(range(len(ORDEN)))
    ax.set_yticklabels([CORTO[m] for m in reversed(ORDEN)])
    ax.set_xlim(0.19, 0.455)
    ax.set_ylim(-0.6, len(ORDEN) - 0.2)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("F1-macro medio en los mismos días (21 pares: 7 acciones × 3 experimentos, prueba 2025)")
    leyenda = [Line2D([], [], marker="o", ls="", color=TINTA2, mec="white", ms=7, label="modelo global"),
               Line2D([], [], marker="o", ls="", mfc="white", mec=TINTA2, mew=1.6, ms=6.5, label="un modelo por acción")]
    ax.legend(handles=leyenda, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2, fontsize=8.3)
    fig.tight_layout()
    guardar(fig, "G07_global_contra_por_accion")


if __name__ == "__main__":
    g01_f1_intervalos()
    g02_sharpe_costos()
    g03_etapa3_contra_etapa4()
    g04_anio_por_anio()
    g05_ciega_2026()
    g06_multicolinealidad()
    g07_global_contra_por_accion()

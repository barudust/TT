# Paper

Todo lo relacionado con el paper académico del proyecto vive aquí. Los
resultados numéricos que lo respaldan (CSVs, logs, modelos entrenados)
**no** están aquí — siguen en
[`../RESULTADOS_OPTIMIZADOS/`](../RESULTADOS_OPTIMIZADOS/), que es de donde
`paper.tex` los cita.

## Qué documento es cuál

- **[`paper.tex`](paper.tex)** — el documento **canónico**: paper académico
  en inglés, formato Springer LNCS (MICAI). Usa la evaluación "splits
  unificados" (v4): F1-macro=0.385, Sharpe=0.755 en Exp B. Es el más
  reciente y riguroso metodológicamente — si vas a citar un número
  específico para la defensa, es este, no `PAPER_FINAL.md`.
- **[`PAPER_FINAL.md`](PAPER_FINAL.md)** — borrador en español (22 de
  mayo), con los números de la evaluación "v1" (F1-macro=0.417,
  Sharpe=1.25 en Exp B) — la que efectivamente entrenó el `.pkl` que corre
  en producción en `api/`. Ver
  [`../STATUS.md`](../STATUS.md) para por qué ambas evaluaciones son
  válidas y la conclusión (LR gana) no cambia entre una y otra.
- **[`borradores/`](borradores/)** — iteraciones previas de
  `PAPER_FINAL.md` (`PAPER.md`, `PAPER_TESIS.md`), conservadas como
  historial, no como referencia vigente.

## Estructura

```
paper/
├── paper.tex          ← documento principal (canónico)
├── figures/            ← figuras .png (7)
├── PAPER_FINAL.md      ← borrador en español (v1)
├── borradores/          ← iteraciones previas (historial)
└── README.md
```

## Compilación de `paper.tex`

El paper usa la clase `llncs.cls` de Springer. Necesitas descargar el template de:
- https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines

Descargas el ZIP del template LNCS y copias `llncs.cls` a esta carpeta. Luego:

```bash
pdflatex paper.tex
pdflatex paper.tex    # segunda pasada para tabla de contenidos / referencias
```

O usa Overleaf: subir la carpeta entera + `llncs.cls`. Funciona directo.

## Notas sobre MICAI

- MICAI usa formato Springer LNCS/LNAI (single column, 12 páginas máximo).
- Inglés obligatorio.
- Bibliografía incluida en el `.tex` (no requiere `.bib` separado).
- 7 figuras en `figures/` (todas en PNG 150 DPI).

## Para enviar a otra conferencia

- **IEEE:** cambiar `\documentclass{llncs}` por `\documentclass[conference]{IEEEtran}` y ajustar referencias.
- **ACM:** usar `\documentclass[sigconf]{acmart}`.

## Figuras incluidas

| Archivo | Descripción | Sección |
|---------|-------------|---------|
| `fig_global_metrics.png` | F1, Win Rate, Profit Factor, Max DD por modelo×exp (GLOBAL) | §6.1 |
| `fig_sharpe_heatmap.png` | Heatmap Sharpe modelo × ticker × exp | §6.3 |
| `fig_f1_heatmap.png` | Heatmap F1 modelo × ticker × exp | Apéndice |
| `fig_signal_dist.png` | Distribución de señales predichas (BUY/HOLD/SELL) | §6.6 |
| `fig_train_years.png` | Efecto del tamaño del train (10/6/4 años) | §6.4 |
| `fig_model_ranking.png` | Ranking de modelos con barras de error | (no usado en paper actual) |
| `fig_sharpe_boxplot.png` | Boxplot Sharpe por ticker | §6.3 |

## Datos fuente

- Tablas: `../RESULTADOS_OPTIMIZADOS/reportes/v4_final/*.csv`
- Resultados primarios: `../RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv`
- Código: `../scripts_opt/`
- Bitácora completa del proceso de optimización:
  `../RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`

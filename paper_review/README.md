# Paper

Todo lo relacionado con el paper académico del proyecto vive aquí. Los
resultados numéricos que lo respaldan (CSVs, logs, modelos entrenados) **no**
están aquí — siguen en
[`../RESULTADOS_OPTIMIZADOS/`](../RESULTADOS_OPTIMIZADOS/), que es de donde
`paper.tex` los cita.

## Qué documento es cuál

- **[`paper.tex`](paper.tex)** — el documento **canónico y único**: paper
  académico en inglés, formato Springer LNCS (MICAI 2026). Contiene la revisión
  que responde a los revisores #2 y #3 (ver más abajo).
- **[`paper.pdf`](paper.pdf)** — el PDF **enviado** a MICAI (12 páginas). Es
  anterior a la revisión: todavía no incluye los cambios de `paper.tex`.
  Recompilar para regenerarlo.

> **Nota histórica.** Hubo dos copias del `.tex` en circulación. La de
> `RESULTADOS_OPTIMIZADOS/paper_latex/paper.tex` (rama `David`, y aún presente en
> el worktree `project-structure-org`) es **anterior**: `paper_review/paper.tex`
> la contiene íntegra y además trae las correcciones de revisión. La copia de
> `paper_latex/` puede borrarse sin perder nada.

## Resultados que cita el paper

| Sección | Fuente |
|---|---|
| Tablas 4–7 y figuras (benchmark v4) | `../RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv` |
| Sección 8 (protocolo corregido, Optuna simétrico, IC bootstrap) | `../RESULTADOS_OPTIMIZADOS/v5/reportes/tabla{1,2,4,5}*.md` |
| Justificación del año de test 2025 | `../tesis_ml_stocks/01_raw_datasets/*.parquet` |
| Expediente completo de la investigación | `../RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md` |

## Figuras

Se generan con **[`../scripts_opt/plots_paper.py`](../scripts_opt/plots_paper.py)**,
que escribe directamente en `figures/` con los nombres que espera el `.tex`:

```bash
python scripts_opt/plots_paper.py
```

Ese script existe porque el revisor #3 señaló que el texto de las figuras era
ilegible. La causa no era el DPI sino la reducción: el `.tex` coloca las figuras
a `\textwidth` (122 mm ≈ 4.8 in) y se estaban creando a 15–19 in de ancho, así
que una anotación de 15 pt acababa impresa a menos de 4 pt. `plots_paper.py`
construye cada figura a un ancho cercano al de la página y calcula los tamaños de
fuente con `ptsize()` a partir del tamaño **impreso** deseado.

| Archivo | Usada en | Notas |
|---|---|---|
| `fig_sharpe_heatmap.png` | §7.3 | Transpuesta (modelos en x, tickers en y) para que las anotaciones quepan |
| `fig_signal_dist.png` | §7.5 | |
| `fig_global_metrics.png` | suplementario | Detrás de `\extrafigs` |
| `fig_sharpe_boxplot.png` | suplementario | Detrás de `\extrafigs` |
| `fig_train_years.png` | suplementario | Detrás de `\extrafigs` |
| `fig_f1_heatmap.png` | suplementario | No referenciada en el `.tex` |
| `fig_model_ranking.png` | — | Sobrante de `plots_extra.py`, no se usa |

### El flag `\extrafigs`

`paper.tex` define en el preámbulo:

```latex
\newif\ifextrafigs
\extrafigsfalse
```

Tres figuras (métricas globales, boxplot de Sharpe, efecto del tamaño del train)
son redundantes con las tablas 4–5 y están envueltas en `\ifextrafigs ... \fi`
para que el paper entre en el límite de páginas. Cambiar a `\extrafigstrue` las
vuelve a insertar en línea, sin tocar nada más.

## Presupuesto de páginas

El PDF enviado tiene **12 páginas**, que es el máximo de MICAI/LNCS. La revisión
añade la sección 8 y queda **estimada en ~13 páginas**. Antes de enviar hay que
compilar y confirmar el número real; si sobra una página, en orden de menor daño:

1. Borrar §7.6 (*Drill-down*) y su Tabla 7 — redundante con §7.3 (≈0.3 pág.)
2. Mover `fig_signal_dist` detrás de `\extrafigs` (≈0.3 pág.)
3. Borrar el párrafo *What actually moved the deep models* de §8 (≈0.3 pág.)

## Compilación

`paper.tex` usa la clase `llncs.cls` de Springer, que **no** está en el repo.
Descargar el template de
<https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines>,
copiar `llncs.cls` a esta carpeta y:

```bash
pdflatex paper.tex
pdflatex paper.tex
```

La segunda pasada es necesaria para las referencias cruzadas. En Overleaf: subir
la carpeta entera junto con `llncs.cls`.

## Notas sobre MICAI

- Formato Springer LNCS/LNAI, una columna, 12 páginas máximo.
- Inglés obligatorio.
- Bibliografía embebida en el `.tex` (`thebibliography`), sin `.bib` aparte.
- El preámbulo **no** carga `caption`/`subcaption`: Springer lo desaconseja con
  `llncs` y el documento no los necesita.

## Para enviar a otra conferencia

- **IEEE:** cambiar `\documentclass{llncs}` por
  `\documentclass[conference]{IEEEtran}` y ajustar referencias.
- **ACM:** usar `\documentclass[sigconf]{acmart}`.

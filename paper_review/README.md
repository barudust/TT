# Paper

Todo lo relacionado con el paper académico del proyecto vive aquí. Los
resultados numéricos que lo respaldan (CSVs, logs, modelos entrenados) **no**
están aquí — siguen en
[`../RESULTADOS_OPTIMIZADOS/`](../RESULTADOS_OPTIMIZADOS/), que es de donde
`paper.tex` los cita.

## Qué documento es cuál

- **[`paper.tex`](paper.tex)** — el documento **canónico**: la versión
  camera-ready **enviada a Springer el 8 de septiembre de 2026** (paquete
  `078.zip`; capítulo 171490174 de MICAI 2026, LNAI). Idéntico a
  `camera_ready/paper.tex`.
- **[`camera_ready/`](camera_ready/)** — el paquete enviado: `paper.tex`,
  `llncs.cls` (v2.26) y las 5 figuras. Compilar desde aquí.
- **[`paper.pdf`](paper.pdf)** — el PDF de 12 páginas de ese envío (`078.pdf`).
- **[`supplementary/`](supplementary/)** — el **material suplementario** que el
  paper cita y que Springer pidió el 2 de octubre de 2026 porque faltaba en el
  paquete (ver abajo).
- **[`figures/`](figures/)** — todas las figuras generadas por
  `scripts_opt/plots_paper.py` (incluye dos que el `.tex` no usa).

### Cambios de la versión enviada (8 sep) respecto a la del 26 de agosto

Para caber en 12 páginas: se quitó la tabla de variables de §3.3 y el mapa de
calor de Sharpe de §7.3 (ambos pasaron al material suplementario), la
bibliografía volvió a una columna (sin `multicol`) y los flotantes usan
`[htbp]`. El resto del texto es igual.

### Material suplementario

El paper lo cita en cinco lugares: §3.3 (tabla completa de las 61 variables),
§5.1 (F1 por clase de las 120 corridas), §7.1 (métricas económicas de Exp A y
Exp C), §7.3 (mapa de calor del Sharpe) y §11 (código, manifiesto de datos,
semillas y versiones). El archivo para Springer es
`supplementary/MICAI2026_ch171490174_supplementary.pdf` (7 páginas): una
sección por mención, y nada más (las figuras que el `.tex` oculta con
`\extrafigsfalse` no se citan en el texto publicado, así que no van). Se genera
con:

```bash
python paper_review/supplementary/build_supplementary.py
```

El script escribe el `.tex` y lo compila con `pdflatex` (MiKTeX:
`winget install MiKTeX.MiKTeX`). Usa la corrida **v4**
(`RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv`), que es la de las tablas del §7
del paper (la v5 solo aparece en §8), con la misma selección del mejor
look-back, y **se detiene si no reproduce las Tablas 4, 5 y 6 del paper** o si
LaTeX deja referencias sin resolver. El suplementario cita la etiqueta de git
`micai2026` como instantánea del código.

**Verificación del paper (2026-10-02):** `camera_ready/paper.tex` compilado con
MiKTeX (pdfTeX 4.23) da 12 páginas con el mismo texto y los mismos saltos de
página que el `paper.pdf` enviado; no hay referencias ni citas sin resolver.
Quedan tres renglones que se salen del margen (0.8, 9.1 y 15.9 pt, en §3.3, §4
y §8), igual que en el PDF enviado.

> Los borradores (`PAPER_FINAL.md`, `paper_latex/`) se eliminaron después del
> envío (commit `da2906d`); siguen en el historial de git si hicieran falta.
>
> **Lo que el paper no incluye** (se hizo después y está en el TT): el
> walk-forward 2020–2025, el análisis del exceso de HOLD y el ajuste del peso
> de clase, la comparación global vs por-ticker sobre las mismas filas y la
> evaluación 2026 fuera de muestra. Ver
> `../RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md`.

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

## Páginas

El límite de MICAI/LNCS es **12 páginas**. La revisión añadió la sección 8 y
el commit `44a93ae` la compactó (espaciado de flotantes, bibliografía a dos
columnas, tablas convertidas en párrafos) hasta quedar en 12 sin quitar
contenido técnico. Si una edición futura se pasa, en orden de menor daño:

1. Borrar §7.6 (*Drill-down*) — redundante con §7.3.
2. Mover `fig_signal_dist` detrás de `\extrafigs`.
3. Borrar el párrafo *What actually moved the deep models* de §8.

## Compilación

```bash
cd paper_review/camera_ready
pdflatex paper.tex
pdflatex paper.tex
```

La segunda pasada resuelve las referencias cruzadas. En Overleaf: subir el
contenido de `camera_ready/` (ya trae `llncs.cls`).

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

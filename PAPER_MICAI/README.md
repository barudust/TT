# PAPER_MICAI — el artículo de MICAI 2026, completo

> *A Benchmark of Five Machine-Learning Architectures for Daily Trading-Signal
> Classification on US Tech Equities* — J. B. Polvo Cuatianquiz, A. Reyes
> Vera, E. Juárez Carbajal, D. Reyes Ramos y M. Aragón García. MICAI 2026,
> Springer *Lecture Notes in Artificial Intelligence*, capítulo 171490174
> (en prensa).

**In English.** This repository holds everything behind the MICAI 2026 paper:
the accepted manuscript and its LaTeX source, the supplementary material, the
code, data and stored results that reproduce every table and figure, and the
conference talk. On daily, free data for seven large-cap US tech stocks, a
regularized logistic regression matches or beats XGBoost, an LSTM, a 1-D CNN
and a CNN-LSTM, and the margin survives a symmetric hyper-parameter search and
bootstrap confidence intervals. Start with
[`paper_review/paper.pdf`](paper_review/paper.pdf); reproduction steps are
under "Reproducir el artículo" below.

Esta carpeta está hecha para funcionar **sola**, como repositorio aparte: no
depende de nada fuera de ella. Mientras siga dentro del repositorio del TT
(`TT/PAPER_MICAI/`), las copias se mantienen al día con
`sincronizar_desde_tt.py` (ver al final).

---

## Lo más usado

| Qué | Dónde |
|---|---|
| El artículo (12 páginas, con el aviso de la licencia) | [`paper_review/paper.pdf`](paper_review/paper.pdf) |
| Material suplementario (7 páginas) | [`paper_review/supplementary/MICAI2026_ch171490174_supplementary.pdf`](paper_review/supplementary/MICAI2026_ch171490174_supplementary.pdf) |
| Presentación del congreso (10 min, plantilla oficial) | [`presentacion_micai/`](presentacion_micai/README.md) |
| Guion para dos expositores, imprimible | `presentacion_micai/GUION_imprimible.pdf` |
| Preguntas probables con respuesta | [`07_PREGUNTAS_MICAI.md`](07_PREGUNTAS_MICAI.md) |
| Estado del envío a Springer y pendientes | [`01_FICHA_Y_ESTADO.md`](01_FICHA_Y_ESTADO.md) |
| Cómo citarlo | [`01_FICHA_Y_ESTADO.md`](01_FICHA_Y_ESTADO.md#cómo-citarlo) y [`CITATION.cff`](CITATION.cff) |

## Qué hay aquí

### Documentos escritos para el artículo

| Archivo | Para qué |
|---|---|
| [`01_FICHA_Y_ESTADO.md`](01_FICHA_Y_ESTADO.md) | Datos del artículo, cronología, estado del envío, licencia, pendientes, cómo citarlo |
| [`02_CONTENIDO_POR_SECCION.md`](02_CONTENIDO_POR_SECCION.md) | Qué dice cada sección (1 a 11), con sus afirmaciones y cifras |
| [`03_TABLAS_Y_CIFRAS.md`](03_TABLAS_Y_CIFRAS.md) | Las 6 tablas y la figura del texto publicado, copiadas exactas |
| [`04_PAPER_VS_TT.md`](04_PAPER_VS_TT.md) | De qué etapa del TT sale cada sección y qué se hizo después del envío |
| [`05_INCLUSION_EN_EL_REPORTE.md`](05_INCLUSION_EN_EL_REPORTE.md) | Cómo citar e incluir el artículo en el reporte técnico del TT |
| [`06_PRESENTACION_MICAI.md`](06_PRESENTACION_MICAI.md) | Versión larga del guion (15 min), de referencia |
| [`07_PREGUNTAS_MICAI.md`](07_PREGUNTAS_MICAI.md) | Preguntas probables del público y de los revisores, en inglés y en español |
| [`presentacion_micai/`](presentacion_micai/README.md) | Diapositivas, guion de 10 min y de 2 min, PDF de respaldo, reglas oficiales y pendientes del viaje |
| [`figuras_presentacion/`](figuras_presentacion/README.md) | Seis gráficas en inglés para diapositivas (PNG y SVG) y su generador |

### Lo que respalda al artículo (copia exacta del TT, mismas rutas)

Las rutas son las mismas que en el repositorio del TT, así los scripts corren
sin cambios y la Tabla S4 del suplementario ("dónde está implementada cada
parte") vale tal cual desde la raíz de esta carpeta.

| Carpeta | Contenido |
|---|---|
| [`paper_review/`](paper_review/README.md) | Fuente LaTeX (`paper.tex`, `camera_ready/` con `llncs.cls` y figuras), PDF público, suplementario y su generador, `compilar_paper.py`, correo pendiente a Springer. Su README explica la compilación, la licencia y el límite de páginas |
| `scripts_v1/` | `01_build_raw_dataset.py`: descarga de Yahoo Finance, las 61 variables y la etiqueta (§3) |
| `scripts_opt/` | El código que cita el artículo: particiones (`common_v4.py`), preselección (`analisis_feature_selection.py`), benchmark (`train_all_v4.py`, `consolidar_v4.py`), robustez (`run_v5.py`, `common_v5.py`, `reporte_v5.py`), figuras (`plots_paper.py`) y comprobación (`replicar_lr_v4.py`), más el módulo común `common.py` |
| `tesis_ml_stocks/01_raw_datasets/` | Los 7 conjuntos de datos (un parquet por acción, 3 017 días cada uno) con los SHA-256 de la Tabla S5 |
| `tesis_ml_stocks/04_models/`, `RESULTADOS_OPTIMIZADOS/modelos_optimizados/` | Resultados de la Etapa 2 que compara la §6 (con y sin preselección) |
| `RESULTADOS_OPTIMIZADOS/v4/` | Las 120 corridas del benchmark (§7) y la réplica de las 24 de LR |
| `RESULTADOS_OPTIMIZADOS/v5/` | Estudio de robustez (§8): búsquedas de Optuna, resultados finales, predicciones guardadas, intervalos bootstrap, registros y tablas |
| `RESULTADOS_OPTIMIZADOS/reportes/` | Tablas y gráficas que producen `consolidar_v4.py` y `analisis_feature_selection.py` |
| `RESULTADOS_OPTIMIZADOS/docs/` | Documentos de trabajo que respaldan §6 y §8 (análisis de la preselección, diagnóstico de las redes, plan de búsqueda, resultados v5) |
| `ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md` | Equivalencia de nombres: v4 = Etapa 3, v5 = Etapa 4, etc. |

Algunos documentos copiados mencionan otros archivos del TT que no viven
aquí (la plataforma, las etapas 5 y 6, la defensa). Están en
https://github.com/barudust/TT.

### Archivos de este repositorio

| Archivo | Para qué |
|---|---|
| `requirements.txt` | Todas las dependencias, con las versiones con que se corrió el artículo |
| `verificar_datos.py` | Comprueba que los parquet son los mismos que usó el artículo (SHA-256, filas y fechas) |
| `sincronizar_desde_tt.py` | Mantiene al día las copias mientras la carpeta esté dentro del TT |
| `CITATION.cff` | Datos de cita (GitHub muestra el botón "Cite this repository") |
| `.gitignore` | Deja fuera lo privado de Springer y los archivos temporales |

---

## Reproducir el artículo

Todo se corre **desde la raíz de este repositorio** (dentro del TT, desde
`PAPER_MICAI/`).

```bash
pip install -r requirements.txt
pip install torch==2.12.* --index-url https://download.pytorch.org/whl/cu128
python verificar_datos.py
```

Para compilar el artículo y el suplementario hace falta `pdflatex` (en
Windows: `winget install MiKTeX.MiKTeX` y luego `miktex packages install
cm-super`).

| Parte del artículo | Comando | Escribe en | Tiempo |
|---|---|---|---|
| Datos (§3) | Ya están en `tesis_ml_stocks/01_raw_datasets/`; volver a descargarlos con `python scripts_v1/01_build_raw_dataset.py` **sobrescribe** los guardados (ver nota) | `tesis_ml_stocks/01_raw_datasets/` | minutos |
| Tabla 1, particiones (§3.4) | Definidas en `scripts_opt/common_v4.py` (`SPLITS_V4`) | — | — |
| Tabla 2, preselección (§6) | `python scripts_opt/analisis_feature_selection.py` | `RESULTADOS_OPTIMIZADOS/reportes/feature_selection/` | segundos |
| Tablas 3–5 y Figura 1 (§7) | `python scripts_opt/train_all_v4.py` y luego `python scripts_opt/consolidar_v4.py` | `RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv`, `RESULTADOS_OPTIMIZADOS/reportes/v4_final/` | horas, con GPU |
| Comprobación de la §7 | `python scripts_opt/replicar_lr_v4.py` (vuelve a correr las 24 de LR y las compara; no toca `resultados_v4.csv`) | `RESULTADOS_OPTIMIZADOS/v4/replica_lr_v4.csv` | ~10 min, CPU |
| Tabla 6, robustez (§8) | `python scripts_opt/run_v5.py replicar`, `ablacion`, `optuna --arch lstm` (y `cnn`, `cnn_lstm`), `clasicos`, `final`, `stats --exp A` (y `B`, `C`); luego `python scripts_opt/reporte_v5.py`. Detalle de cada paso en `RESULTADOS_OPTIMIZADOS/docs/RESULTADOS_V5.md` | `RESULTADOS_OPTIMIZADOS/v5/` | días, con GPU |
| Figuras del artículo | `python scripts_opt/plots_paper.py` | `paper_review/figures/` | segundos |
| Suplementario | `python paper_review/supplementary/build_supplementary.py` (se detiene si no reproduce las tablas del artículo) | `paper_review/supplementary/` | ~1 min |
| El artículo | `python paper_review/compilar_paper.py` (con `--doi …` cuando salga el DOI) | `paper_review/paper.pdf` y `paper_review/_envio_springer/` (privado) | ~1 min |
| Gráficas y presentación del congreso | `python figuras_presentacion/fuente/generar_figuras.py`, `python presentacion_micai/fuente/generar_guion.py`, `python presentacion_micai/fuente/construir_presentacion.py` | `figuras_presentacion/`, `presentacion_micai/` | segundos |

Para revisar los números sin entrenar nada basta con los pasos rápidos: los
resultados de cada corrida ya están guardados, y `analisis_feature_selection.py`,
`consolidar_v4.py`, `reporte_v5.py` y `build_supplementary.py` rehacen las
tablas a partir de ellos.

**Probado el 26 de octubre de 2026** en una copia de esta carpeta fuera del
TT: `verificar_datos.py`, `analisis_feature_selection.py`, `consolidar_v4.py`,
`reporte_v5.py`, `plots_paper.py`, `build_supplementary.py`,
`compilar_paper.py` (12 páginas) y los tres scripts de la presentación corren
sin errores. Las tablas regeneradas son idénticas a las guardadas, byte por
byte. `replicar_lr_v4.py` volvió a dar las 24 corridas de LR idénticas (F1-macro y
por clase, Sharpe, *win rate*, *profit factor* y *drawdown*) con Python 3.13.7.

**Notas:**

- **Datos.** Yahoo Finance corrige a veces su historial (ajustes por
  dividendos y *splits*), así que una descarga nueva puede no ser idéntica.
  Para reproducir el artículo hay que usar los parquet guardados;
  `verificar_datos.py` confirma que son los de la Tabla S5. Los datos vienen
  de Yahoo Finance vía `yfinance`, para uso de investigación.
- **Figuras.** `plots_paper.py` rehace las figuras con los mismos números,
  pero el recorte automático de márgenes cambia unos píxeles según la versión
  de matplotlib y las fuentes instaladas. En la prueba del 26 de octubre, el
  rótulo del eje de `fig_signal_dist.png` quedó cortado arriba. Las figuras
  que usa el artículo son las de `paper_review/camera_ready/figures/`: no
  reemplazarlas sin revisarlas.
- **Etapa 2.** La §6 compara resultados guardados de la Etapa 2 del TT. Los
  scripts que los entrenaron (`scripts_v1/02`–`07` y `scripts_opt/opt_*.py`)
  necesitan carpetas intermedias que no se conservaron y se quedan en el TT.
- **Instantánea.** El suplementario cita la etiqueta `micai2026` del TT
  (https://github.com/barudust/TT/tree/micai2026) como instantánea del código.
  El código de aquí es el mismo; desde esa etiqueta solo cambiaron notas en
  cinco tablas `.md` de `v5/reportes/` y el README de `paper_review/`.

---

## Lo que no se sube (privado)

El `.gitignore` deja fuera lo siguiente; **no forzarlo con `git add -f`**:

- `paper_review/_envio_springer/`: `compilar_paper.py` deja ahí el zip para
  Springer, que lleva el PDF **sin** el aviso de la licencia.
- El formulario de copyright firmado (`*_copyright.pdf`) y el `078.zip`
  original.
- Cualquier otro PDF, salvo los cuatro públicos: el artículo, el
  suplementario, la presentación y el guion.

Una copia del zip corregido está en el release **borrador** `envio-springer`
del repositorio del TT, que solo ven los colaboradores. **No publicarlo.**

---

## Para separarlo como repositorio aparte

**Antes de crear el repositorio, decidir entre los autores:**

1. **Licencia del código y de los datos.** Hoy no tiene ninguna. Sin
   licencia, el código se puede ver pero no reutilizar. MIT es lo más común
   en artículos. El PDF del artículo queda aparte: lo rige la licencia de
   Springer (ver `01_FICHA_Y_ESTADO.md`).
2. **Público o privado.** La licencia de Springer permite el manuscrito
   aceptado en el sitio del autor si lleva el aviso, y `paper.pdf` ya lo
   lleva. Es lo mismo que ya está publicado en el TT.

**Pasos (desde la raíz del TT).** Conservan el historial de esta carpeta:

```bash
git subtree split --prefix=PAPER_MICAI -b paper-micai
```

1. Crear en GitHub un repositorio **vacío**, sin README ni licencia.
2. Subirle la rama del comando anterior:

```bash
git push https://github.com/barudust/NOMBRE-DEL-REPO.git paper-micai:main
```

3. Ya en el repositorio nuevo, actualizar `repository-code` en `CITATION.cff`
   con su dirección.

Desde ese momento **el repositorio nuevo es el original** del artículo.
`sincronizar_desde_tt.py` solo sirve mientras la carpeta esté dentro del TT.
Si después cambia algo del artículo en el TT, se vuelve a correr y se copia
a mano.

### Mientras siga dentro del TT

```bash
python PAPER_MICAI/sincronizar_desde_tt.py            # revisa si las copias están al día
python PAPER_MICAI/sincronizar_desde_tt.py --copiar   # copia lo que cambió en el TT
```

Los cambios a `paper_review/`, `scripts_*`, `RESULTADOS_OPTIMIZADOS/` o
`tesis_ml_stocks/` se hacen **en el TT** y luego se sincronizan. Los
documentos `01`–`07`, `presentacion_micai/` y `figuras_presentacion/` solo
existen aquí y se editan aquí.

## Relación con el TT

- El artículo usa las **Etapas 2, 3 y 4** del TT. El mapa completo está en
  `ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md` §6.
- Lo que se hizo después del envío (prueba año por año, costos, prueba ciega
  2026, plataforma) está resumido en `04_PAPER_VS_TT.md`. Las fuentes están
  en el repositorio del TT: https://github.com/barudust/TT.
- Hay preguntas de defensa sobre el artículo ante sinodales en el TT:
  [`ESTUDIO_TT/D_defensa/D7_PREGUNTAS_PAPER.md`](https://github.com/barudust/TT/blob/main/ESTUDIO_TT/D_defensa/D7_PREGUNTAS_PAPER.md)
  y [`ESTUDIO_TT/C_paper/C1_PAPER_MICAI.md`](https://github.com/barudust/TT/blob/main/ESTUDIO_TT/C_paper/C1_PAPER_MICAI.md).
- El artículo entra en el reporte técnico como producto y anexo
  (`05_INCLUSION_EN_EL_REPORTE.md`). La revisión del reporte está en
  [`REPORTE_TECNICO/`](https://github.com/barudust/TT/tree/main/REPORTE_TECNICO).

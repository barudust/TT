# PAPER_MICAI — todo lo del artículo de MICAI 2026, en un solo lugar

Carpeta aparte del reporte técnico y del estudio, para tener a la mano lo
que hace falta para **presentar el artículo en MICAI**, responder preguntas
sobre él, citarlo en el reporte o reutilizarlo en otros documentos.

> *A Benchmark of Five Machine-Learning Architectures for Daily Trading-Signal
> Classification on US Tech Equities* — J. B. Polvo Cuatianquiz, A. Reyes
> Vera, E. Juárez Carbajal, D. Reyes Ramos y M. Aragón García. MICAI 2026,
> Springer *Lecture Notes in Artificial Intelligence*, capítulo 171490174.

---

## Qué hay aquí

| Archivo | Para qué |
|---|---|
| [`01_FICHA_Y_ESTADO.md`](01_FICHA_Y_ESTADO.md) | Datos del artículo, estado del envío a Springer, licencia, qué falta hacer, cómo citarlo |
| [`02_CONTENIDO_POR_SECCION.md`](02_CONTENIDO_POR_SECCION.md) | Qué dice cada sección (1 a 11), con sus afirmaciones y cifras |
| [`03_TABLAS_Y_CIFRAS.md`](03_TABLAS_Y_CIFRAS.md) | Las 6 tablas y la figura del texto publicado, copiadas exactas, y lo que va en el suplementario |
| [`04_PAPER_VS_TT.md`](04_PAPER_VS_TT.md) | De qué etapa del TT sale cada sección, qué cambió después y los detalles finos que hay que conocer |
| [`05_INCLUSION_EN_EL_REPORTE.md`](05_INCLUSION_EN_EL_REPORTE.md) | **Si conviene y cómo meter el artículo en el reporte técnico** (recomendación y textos listos) |
| [`presentacion_micai/`](presentacion_micai/README.md) | **Presentación lista para el congreso** (10 min, plantilla oficial), guion para dos expositores en inglés sencillo con traducción y pronunciación, PDF de respaldo y pendientes |
| [`06_PRESENTACION_MICAI.md`](06_PRESENTACION_MICAI.md) | Versión larga del guion (15 min), de referencia |
| [`07_PREGUNTAS_MICAI.md`](07_PREGUNTAS_MICAI.md) | Preguntas probables del público y revisores, con respuesta en inglés y en español |
| [`figuras_presentacion/`](figuras_presentacion/) | Seis gráficas en inglés listas para las diapositivas (PNG y SVG) y su generador |

## Dónde están los archivos del artículo (no se duplican aquí)

| Qué | Ruta |
|---|---|
| Fuente LaTeX canónica (camera-ready + corrección del apellido) | `../paper_review/paper.tex` |
| Paquete para Springer (tex, `llncs.cls`, figuras) | `../paper_review/camera_ready/` |
| Copia pública del PDF (12 páginas, con el aviso de la licencia) | `../paper_review/paper.pdf` |
| Material suplementario (7 páginas) y su generador | `../paper_review/supplementary/` |
| Figuras del artículo | `../paper_review/figures/` (genera `../scripts_opt/plots_paper.py`) |
| Correo pendiente a Springer | `../paper_review/correo_springer.txt` |
| Compilar el PDF y el zip para Springer | `python paper_review/compilar_paper.py` |
| Notas técnicas de compilación, licencia y páginas | `../paper_review/README.md` |
| Resultados que cita el artículo | `../RESULTADOS_OPTIMIZADOS/v4/` (§3–§7) y `../RESULTADOS_OPTIMIZADOS/v5/` (§8) |
| Instantánea del código del artículo | etiqueta de git `micai2026` |

## Relación con el resto del repositorio

- El artículo usa las **Etapas 2, 3 y 4** del TT (mapa completo en
  `../ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md` §6).
- Preguntas de defensa sobre el artículo ante sinodales:
  `../ESTUDIO_TT/D_defensa/D7_PREGUNTAS_PAPER.md` y
  `../ESTUDIO_TT/C_paper/C1_PAPER_MICAI.md`.
- Revisión del reporte técnico: `../REPORTE_TECNICO/` (el artículo entra
  como producto y anexo; ver `05_INCLUSION_EN_EL_REPORTE.md`).
- Presentaciones del TT (no del congreso): `../presentaciones/`.

## Lo que **no** va en el repositorio (es público)

El formulario de copyright firmado, el `078.zip` original y el PDF sin el
aviso de la licencia (`paper_review/_envio_springer/`) están excluidos en
`.gitignore`. Una copia del zip corregido está en el release **borrador**
`envio-springer` de GitHub, visible solo para colaboradores.

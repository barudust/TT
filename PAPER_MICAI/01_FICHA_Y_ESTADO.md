# 01 — Ficha del artículo y estado

## Ficha

| | |
|---|---|
| Título | *A Benchmark of Five Machine-Learning Architectures for Daily Trading-Signal Classification on US Tech Equities* |
| Título corto (cabeceras) | *ML Benchmark for Daily Trading Signals* |
| Autores | Jesus Baruc Polvo Cuatianquiz¹, Abdiel Reyes Vera¹, Emmanuel Juárez Carbajal², David Reyes Ramos¹, Maribel Aragón García¹ |
| Afiliaciones | ¹ Escuela Superior de Cómputo, IPN · ² Centro de Investigación en Computación, IPN |
| Autor de correspondencia | J. B. Polvo Cuatianquiz |
| Congreso | MICAI 2026 — *Mexican International Conference on Artificial Intelligence* |
| Publicación | Springer, *Lecture Notes in Artificial Intelligence* (LNAI), capítulo 171490174 |
| Formato | LNCS, una columna, 12 páginas, inglés |
| Palabras clave | Trading signals · Classification · Deep learning · Logistic regression · XGBoost · LSTM · CNN |
| Contenido | 11 secciones, 6 tablas, 1 figura en el texto; material suplementario de 7 páginas |

## Cronología

| Fecha (2026) | Hecho |
|---|---|
| Antes de agosto (verificar la fecha en el sistema del congreso) | Primer envío con la comparación de la Etapa 3 |
| Agosto | Revisión: los revisores piden una búsqueda de hiperparámetros comparable para las redes y figuras legibles. Se hace el diagnóstico de las redes y el protocolo de la Etapa 4, que agrega la §8 |
| 26 de agosto | Versión revisada |
| 8 de septiembre | **Camera-ready enviado a Springer** (paquete `078.zip`) |
| 2 de octubre | Springer pide el material suplementario que el artículo cita; se detecta el apellido mal escrito ("Cuatiaquiz") |
| 2–3 de octubre | Se genera y verifica el suplementario (7 páginas) y el paquete corregido (`078_corrected.zip`) |

## Pendientes (verificar el estado real antes de actuar)

1. **Responder a Springer** en el mismo hilo del correo de Atchaya con el
   suplementario y el zip corregido. Texto listo en
   `paper_review/correo_springer.txt`. *Si ya se envió, marcarlo aquí con
   la fecha.*
2. **Preguntar si hace falta un nuevo formulario de licencia** por el
   apellido corregido (el correo ya lo pregunta).
3. **Cuando salga el DOI** (página del libro en link.springer.com):
   `python paper_review/compilar_paper.py --doi 10.1007/978-3-XXX-XXXXX-X_XX`
   y subir el `paper.pdf` resultante; actualizar la referencia de abajo y la
   del reporte técnico.
4. **Registrar el artículo** donde lo pida la escuela (constancia de
   participación, carta de aceptación) para el expediente del TT.

## Licencia (resumen)

La *Licence to Publish* de Springer (cláusula 4(c)) permite publicar el
**manuscrito aceptado** en el sitio propio del autor desde la aceptación, sin
licencia Creative Commons, sin reformatearlo y con este aviso y el enlace a la
versión publicada (*Version of Record*):

> This version of the contribution has been accepted for publication, after
> peer review (when applicable) but is not the Version of Record and does not
> reflect post-acceptance improvements, or any corrections. The Version of
> Record is available online at: http://dx.doi.org/[insert DOI]. Use of this
> Accepted Version is subject to the publisher's Accepted Manuscript terms of
> use https://www.springernature.com/gp/open-research/policies/accepted-manuscript-terms

`paper_review/paper.pdf` ya lleva el aviso (con el DOI pendiente). Para
incluirlo en el reporte técnico ver `05_INCLUSION_EN_EL_REPORTE.md` §3.

## Cómo citarlo

**IEEE (como el reporte técnico):**

> J. B. Polvo Cuatianquiz, A. Reyes Vera, E. Juárez Carbajal, D. Reyes Ramos
> y M. Aragón García, "A Benchmark of Five Machine-Learning Architectures for
> Daily Trading-Signal Classification on US Tech Equities," en *Advances in
> Computational Intelligence. MICAI 2026*, Lecture Notes in Artificial
> Intelligence. Cham: Springer, 2026 (en prensa).

**Springer / LNCS:**

> Polvo Cuatianquiz, J.B., Reyes Vera, A., Juárez Carbajal, E., Reyes Ramos,
> D., Aragón García, M.: A Benchmark of Five Machine-Learning Architectures
> for Daily Trading-Signal Classification on US Tech Equities. In: MICAI
> 2026. LNAI. Springer, Cham (2026, in press)

Al salir el volumen: agregar editores, número de volumen, páginas y DOI, y
confirmar el título exacto del libro (*Advances in Computational
Intelligence* es el nombre habitual de los volúmenes de MICAI; verificarlo).

## Verificaciones ya hechas (por si alguien pregunta)

- El código actual reproduce las 18 corridas globales de las redes y las 24
  de la LR de la §7 al cuarto decimal (`RESULTADOS_OPTIMIZADOS/v5/g0_replicacion.csv`,
  `scripts_opt/replicar_lr_v4.py`).
- El suplementario se detiene si no reproduce las tablas del artículo y
  coteja las 61 definiciones con el código, los SHA-256 de los datos y las
  semillas (revisión del 3 de octubre).
- `compilar_paper.py` verifica que el PDF tenga 12 páginas y sin referencias
  sin resolver.
- Las gráficas de `figuras_presentacion/` verifican contra las Tablas 3 y 4.

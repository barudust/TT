# 05 — ¿Cómo incluir el artículo en el reporte técnico?

## 1. Conclusión

**Sí es viable y conviene incluirlo, pero como producto del trabajo y
respaldo externo, no como un capítulo más.** El artículo publica una parte del
TT (Etapas 2–4) que el reporte ya explica con más detalle; copiarlo
duplicaría contenido en otro idioma y con otra estructura. Lo que suma es que
**la comparación y su conclusión pasaron revisión por pares** en un congreso
internacional con publicación en Springer.

## 2. Opciones evaluadas

| Opción | Qué implica | Ventajas | Riesgos | Veredicto |
|---|---|---|---|---|
| A. Capítulo nuevo con el artículo traducido | 12 páginas más | Ninguna real: repite los capítulos 4 y 6 | Duplicación; dos versiones de las mismas cifras que hay que mantener iguales; posible problema de licencia al reproducir el texto | **No** |
| B. Mencionarlo solo en la introducción | Una frase | Mínimo trabajo | Se pierde el valor del respaldo; el lector no sabe qué parte se publicó | Insuficiente |
| **C. Producto + citas + anexo corto** | Sección 1.5, citas en los capítulos 3, 4 y 6, y un anexo de 2–3 páginas con la ficha, el resumen, qué parte del TT cubre y qué agregó el TT después | Respaldo visible; trazabilidad entre el artículo y el reporte; sin duplicar | Ninguno relevante | **Recomendada** |
| D. C + el PDF del artículo como anexo completo | Igual que C más el manuscrito aceptado (12 páginas) al final | El sinodal puede leerlo sin buscarlo | Revisar la licencia antes (§3) | Opcional, si la licencia lo permite |

## 3. Licencia: qué se puede reproducir

- La licencia de Springer (*Licence to Publish*, cláusula 4(c)) permite al
  autor publicar el **manuscrito aceptado** en su sitio personal con el aviso
  de la versión de registro (texto en `01_FICHA_Y_ESTADO.md`). El PDF
  `paper_review/paper.pdf` ya lo lleva.
- Las licencias de Springer para capítulos suelen permitir que el autor
  **incluya su contribución en su propia tesis** citando la versión
  publicada. **Antes de usar la opción D, revisar el formulario firmado**
  (no está en el repositorio; lo tiene el autor de correspondencia) y
  confirmar la cláusula de reutilización en tesis. Si no está clara, quedarse
  con la opción C: citar y resumir no requiere permiso.
- Nunca incluir el PDF maquetado por Springer (la *Version of Record*) sin
  esa confirmación.

## 4. Qué poner y dónde (opción C)

| Lugar del reporte | Qué agregar | Texto |
|---|---|---|
| Resumen y abstract | Una frase al final | §5.1 |
| 1.5 Productos del trabajo | El artículo como segundo producto | [`REPORTE_TECNICO/textos/T01_resumen_abstract_intro.md`](https://github.com/barudust/TT/blob/main/REPORTE_TECNICO/textos/T01_resumen_abstract_intro.md) §4 |
| 3.6 Brecha de investigación | "La comparación fue publicada en MICAI 2026 [ref.]" | [`REPORTE_TECNICO/correcciones/C03_ESTADO_DEL_ARTE.md`](https://github.com/barudust/TT/blob/main/REPORTE_TECNICO/correcciones/C03_ESTADO_DEL_ARTE.md) 3-08 |
| 4.6 Mismas características | Citar §6 del artículo (11 de 15) | [`REPORTE_TECNICO/textos/T03_justificaciones_sinodal.md`](https://github.com/barudust/TT/blob/main/REPORTE_TECNICO/textos/T03_justificaciones_sinodal.md) §1 |
| 6.3 Etapa 2 | Citar §6 | — |
| 6.4 Etapa 3 | "Estos resultados se publicaron en [ref., §7]" | [`REPORTE_TECNICO/textos/T06_resultados.md`](https://github.com/barudust/TT/blob/main/REPORTE_TECNICO/textos/T06_resultados.md) §6.4 |
| 6.5 Etapa 4 | "La verificación con el protocolo final se publicó en [ref., §8]" | §5.3 abajo |
| 7.2 Cumplimiento de objetivos | Mencionarlo en el objetivo 3 | §5.4 abajo |
| Referencias | La referencia del artículo | `01_FICHA_Y_ESTADO.md` |
| Anexo A | Ficha, resumen, cobertura | §5.2 abajo |

## 5. Textos listos

### 5.1 Frase para el resumen

> La comparación de los cinco modelos y su verificación con el protocolo
> final se publicaron en la *Mexican International Conference on Artificial
> Intelligence* (MICAI 2026), en la serie *Lecture Notes in Artificial
> Intelligence* de Springer.

### 5.2 Anexo A — Artículo publicado en MICAI 2026

> **Anexo A. Artículo publicado en MICAI 2026**
>
> **Referencia.** J. B. Polvo Cuatianquiz, A. Reyes Vera, E. Juárez
> Carbajal, D. Reyes Ramos y M. Aragón García, "A Benchmark of Five
> Machine-Learning Architectures for Daily Trading-Signal Classification on
> US Tech Equities," en *MICAI 2026*, Lecture Notes in Artificial
> Intelligence, Springer, 2026 (en prensa).
>
> **Proceso.** El artículo se sometió con la comparación en igualdad de
> condiciones (Etapa 3). Los revisores señalaron que las redes no habían
> tenido una búsqueda de hiperparámetros comparable a la de XGBoost; en
> respuesta se diseñó el protocolo final (Etapa 4), cuyo resultado se agregó
> como sección 8. La versión final se entregó el 8 de septiembre de 2026.
>
> **Resumen.** [Pegar el resumen en inglés del artículo o su traducción.]
>
> **Qué parte del trabajo terminal cubre.**
>
> | Sección del artículo | Contenido | Capítulo de este reporte |
> |---|---|---|
> | 3–5 | Datos, etiqueta, modelos y evaluación | 4 |
> | 6 | Preselección estadística de variables | 4.6 y 6.3 |
> | 7 | Comparación de 120 corridas (Etapa 3) | 6.4 |
> | 8 | Protocolo final, búsqueda simétrica e intervalos (Etapa 4) | 6.5 |
>
> **Qué agrega este reporte respecto al artículo.** Los intervalos de
> confianza de los Experimentos A y C, las ocho métricas para los cinco
> modelos, los costos de transacción, la prueba año por año de 2020 a 2025,
> la prueba ciega con datos de 2026, la comparación pareada entre el modelo
> global y el modelo por acción, el análisis de multicolinealidad, el ajuste
> del exceso de la clase mantener y la plataforma web. Las limitaciones que el
> artículo declara —un solo año de prueba y la ausencia de costos— se
> abordan en el capítulo 6 de este documento.
>
> **Diferencias de detalle.** La sección 4 del artículo describe la
> configuración de la Etapa 3 (LSTM bidireccional, Regresión Logística con
> elasticnet); las configuraciones finales de la Etapa 4 se describen en el
> capítulo 4 de este reporte.

### 5.3 Frase para 6.5 (Etapa 4)

> Esta verificación, con el protocolo en el que ninguna decisión usa el año
> de prueba y con una búsqueda de hiperparámetros equivalente para los cinco
> modelos, se publicó como sección 8 del artículo presentado en MICAI 2026
> [ref.]; los intervalos de los Experimentos A y C, los costos de transacción
> y las validaciones en otros años son resultados adicionales de este
> trabajo.

### 5.4 Frase para 7.2 (objetivo específico 3)

> La comparación y su verificación estadística fueron evaluadas por pares y
> publicadas en MICAI 2026 [ref.], lo que constituye una validación externa
> del protocolo y de la conclusión.

## 6. Coherencia obligatoria

Antes de entregar el reporte, comprobar que **toda cifra del artículo que
aparezca en el reporte sea idéntica** a `03_TABLAS_Y_CIFRAS.md` (en
particular 0.399, 0.385, 0.404 [0.379, 0.428], +0.755, +0.895, 11 de 15,
15.5 % / 3.4 %), y que el reporte no atribuya al artículo resultados que no
contiene (`04_PAPER_VS_TT.md` §1).

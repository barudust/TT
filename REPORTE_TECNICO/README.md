# Revisión del reporte técnico — guía para quien lo va a corregir

Esta carpeta tiene **todo lo que hay que cambiar** en el reporte técnico del
TT 2026-B164 para que coincida con lo que realmente se hizo, con el sistema que
está desplegado y con el artículo publicado en MICAI. **No es el documento**:
son instrucciones, datos verificados, borradores de texto y figuras nuevas
para que el documento se corrija sin inventar nada.

- **Versión revisada:** `Reporte_Tecnico.pdf` con fecha 21/10/2026, 105 páginas.
- **Fecha de la revisión:** 26 de octubre de 2026.
- **Cómo se citan las páginas:** con el número impreso al pie (p. 39). En el
  visor de PDF es una más (p. 39 impresa = página 40 del PDF), porque la
  portada no lleva número.

---

## Qué hay aquí

| Archivo o carpeta | Para qué sirve | Cuándo usarlo |
|---|---|---|
| [`00_RESUMEN_EJECUTIVO.md`](00_RESUMEN_EJECUTIVO.md) | Los 12 problemas grandes del documento en una página | **Leer primero** |
| [`01_ESTRUCTURA_PROPUESTA.md`](01_ESTRUCTURA_PROPUESTA.md) | Nuevo índice del documento y qué sección vieja va a dónde | Antes de empezar a editar |
| [`02_CONTRADICCIONES.md`](02_CONTRADICCIONES.md) | Lugares donde el documento se contradice a sí mismo, al sistema o al paper | Para no dejar ninguna |
| [`03_CIFRAS_VIGENTES.md`](03_CIFRAS_VIGENTES.md) | **Todas las cifras que se pueden citar**, con su archivo de origen, y las que no | Cada vez que se escriba un número |
| [`04_GLOSARIO_DE_REDACCION.md`](04_GLOSARIO_DE_REDACCION.md) | Nombres que hay que usar (etapas, experimentos, modelos, clases) y los que ya no | Al redactar |
| [`correcciones/`](correcciones/) | **Lista detallada por capítulo**: qué dice, qué debe decir, por qué y de dónde sale | Es el trabajo principal |
| [`textos/`](textos/) | Borradores de los párrafos y secciones que cambian por completo | Para adaptar, no para pegar sin leer |
| [`tablas/`](tablas/) | Tablas nuevas ya armadas con los datos correctos | Al rehacer los capítulos 4 y 6 |
| [`diagramas/`](diagramas/) | Diagramas nuevos (SVG y PNG) que reemplazan a las figuras 1–6, más los que faltan | Al rehacer los capítulos 4 y 5 |
| [`graficas/`](graficas/) | Gráficas de resultados (el documento no tiene ninguna) | Al rehacer el capítulo 6 |

El artículo de MICAI tiene su propia carpeta, aparte: [`../PAPER_MICAI/`](../PAPER_MICAI/).
Cómo incluirlo en el reporte está en
[`../PAPER_MICAI/05_INCLUSION_EN_EL_REPORTE.md`](../PAPER_MICAI/05_INCLUSION_EN_EL_REPORTE.md).

---

## Orden de trabajo sugerido

1. Leer `00_RESUMEN_EJECUTIVO.md` (10 minutos). Explica por qué el documento
   actual describe sobre todo el trabajo de TT1 y qué cambió.
2. Leer `01_ESTRUCTURA_PROPUESTA.md` y decidir con el equipo si se adopta la
   estructura nueva (recomendado) o solo se corrige la actual.
3. Corregir capítulo por capítulo con `correcciones/C0X_*.md`. Cada archivo
   empieza con una tabla resumen y luego detalla cada punto.
4. Para los capítulos 4, 6 y 7, que cambian casi completos, partir de los
   borradores de `textos/` y de las tablas de `tablas/`.
5. Sustituir las figuras con las de `diagramas/` y agregar las de `graficas/`.
6. Al final, pasar la lista de `02_CONTRADICCIONES.md` como control: cada
   punto tiene que quedar resuelto.
7. Revisar que todos los números coincidan con `03_CIFRAS_VIGENTES.md`.

---

## Cómo están escritas las correcciones

Cada punto tiene un identificador `capítulo-número` (por ejemplo **4-07**) y
una prioridad:

| Prioridad | Significa | ¿Obligatorio? |
|---|---|---|
| **CRÍTICO** | Dato, método o conclusión incorrectos o desactualizados. Un sinodal lo puede señalar como error | Sí |
| **IMPORTANTE** | Contradicción interna, falta algo que se espera, o una afirmación difícil de defender | Sí |
| **FORMA** | Redacción, ortografía, numeración, referencia cruzada, estilo | Recomendable |

Formato de cada punto:

```
### 4-07 · p. 39 · §4.2, Tabla 3 · CRÍTICO
**Dice:** lo que está escrito (cita corta).
**Debe decir / acción:** qué poner o qué hacer.
**Por qué:** la razón.
**Fuente:** archivo del repositorio que lo respalda.
```

---

## Reglas que no se negocian

1. **Ningún número sin fuente.** Si no está en `03_CIFRAS_VIGENTES.md`, se
   busca en el archivo que ahí se indica; si no existe, no se escribe.
2. **Los nombres son los de las etapas** (Etapa 1 a 6), no v1–v8 ni "Vía 7".
   Equivalencias en `04_GLOSARIO_DE_REDACCION.md` y en
   [`../ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md`](../ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md).
3. **El resultado principal es el de la Etapa 4** (LR 0.404 en el
   Experimento B). Las cifras del TT1 (Etapa 1) se presentan solo como punto
   de partida, nunca como el resultado.
4. **Cifras prohibidas:** 0.417 / Sharpe 1.25 (Etapa 2, elegidas con la
   prueba), y los resultados a 5–7 días (otro problema). Ver la sección "No
   citar" de `03_CIFRAS_VIGENTES.md`.
5. **El sistema que se describe es el que está en Render** (SQLite, ETL
   dentro de la API, 7 pantallas). PostgreSQL, el ETL incremental y los tres
   niveles de la interfaz son del diseño de TT1 y solo se mencionan como
   antecedente.
6. **Tono:** impersonal y académico en todo el documento. Las secciones
   5.3.3, 5.4.3, 5.5.3–5.5.5 y 6.6 están escritas en primera persona y con
   tono coloquial; hay que homologarlas (ver `correcciones/C05_SISTEMA.md` y
   `C06_RESULTADOS.md`).

---

## Documentos del repositorio que respaldan todo esto

| Tema | Documento |
|---|---|
| Etapas, experimentos y qué usa el paper | `ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md` |
| Datos y etiqueta | `ESTUDIO_TT/A_modelo/A1_DATOS_Y_ETIQUETA.md` |
| Las 61 + 15 variables | `ESTUDIO_TT/A_modelo/A2_VARIABLES.md` |
| Protocolo, métricas, estadística | `ESTUDIO_TT/A_modelo/A3_PROTOCOLO_Y_METRICAS.md` |
| LR y XGBoost | `ESTUDIO_TT/A_modelo/A4_MODELOS_CLASICOS.md` |
| Redes | `ESTUDIO_TT/A_modelo/A5_REDES_NEURONALES.md` |
| Resultados y límites | `ESTUDIO_TT/A_modelo/A7_RESULTADOS_Y_LIMITES.md` |
| Sistema (arquitectura, API, BD, frontend, despliegue) | `ESTUDIO_TT/B_sistema/B1` a `B5` |
| Diferencias TT1 → TT2 | `ESTUDIO_TT/D_defensa/D1_TT1_VS_TT2.md` |
| Observaciones de la sinodal (26 oct) | `ESTUDIO_TT/D_defensa/D9_OBSERVACIONES_SINODAL.md` |
| Paper | `paper_review/` y `PAPER_MICAI/` |

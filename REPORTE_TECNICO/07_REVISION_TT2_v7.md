# 07 — Cuarta revisión (TT2_v7.pdf, 28 de octubre)

> **Versión revisada:** `TT2_v7.pdf`, 167 páginas, exportado desde Word el
> 28/10/2026 a las 17:30. Las páginas se citan con el número impreso al pie
> (en el visor de PDF es una más).
>
> **En una frase:** las correcciones de la tercera revisión
> ([`06_REVISION_TT2_v5.md`](06_REVISION_TT2_v5.md)) están bien aplicadas en
> el cuerpo del documento, pero **al regenerar los índices se rompieron de
> otra forma**. En Word, el índice de figuras y el de tablas muestran el código
> de campo `TOC \h \z \t "Figuras,1"` delante de cada entrada, y el Contenido
> repite palabras ("Machine LearningMachine Learning", "Trabajo futuro
> futuro"). Quien editó revisó el render de LibreOffice; el problema se ve
> en el PDF exportado desde Word. Arreglarlo lleva diez minutos en Word
> (sección 3).

---

## 1. Estado de la tercera revisión

Comparé palabra por palabra el texto del v5 con el del v7. Los únicos cambios
del cuerpo son los que reporta la persona que editó, así que no se movió nada
más. Las 233 ecuaciones de Word siguen intactas.

| # | Pendiente de `06` | Estado en TT2_v7 |
|---|---|---|
| N-01 | "¡Error! Marcador no definido" en los índices | ✅ Ya no aparece, pero los índices tienen otro problema (V-01 y V-02) |
| N-02 | Faltaban los Anexos B y C, la Tabla 28 y las Tablas 39–47 | ✅ Están todos. Los números de página coinciden con el PDF de Word en las 176 entradas |
| N-03 | Negritas de la Tabla 28 | ✅ Solo lo adoptado, con la nota completa (p. 128) |
| N-04 | Tabla 34 y §7.8.2 | ✅ Ocho correcciones, nueve filas y "entre los pesos". Falta una frase (V-04) |
| N-05 | 28 → 24 combinaciones | ✅ §7.7 (p. 133) y fila 37 del Anexo B |
| N-06 | Cinco F1 de la LR en 2025 | ✅ Notas bajo las Tablas 30 y 32, §4.8.1 y §4.8.2 |
| N-07 | Etapa 3 contra Etapa 4 | ✅ §7.6.1, §7.9, Tabla 37 (con nota) y §8.2 |
| N-08 | Frase repetida en §7.4 | ✅ |
| N-09 | "target, La" | ✅ |
| N-10 | 34 % → 33 % | ✅ |
| N-11 | 4.11.4 → 4.11.2 y 4.11.6 | ✅ |
| N-12 | Resumen del artículo recortado | ✅ Completo, pero termina con código de LaTeX (V-03) |
| N-13 | Enlace del Anexo C si se separa el repositorio | Sin cambio (aviso; se ajusta al separar el repositorio) |
| N-14 | Siglas faltantes | ✅ IC, OHLCV, pb, ROI, HTTP y SPY |
| N-15 | Fecha de consulta de [39], [40] y [42] | ⚠️ Ya trae una fecha; hay que confirmar que sea la real (V-05) |

---

## 2. Problemas nuevos

| # | Página | Dónde | Qué pasa | Prioridad |
|---|---|---|---|---|
| V-01 | 6–9 | Índices de figuras y de tablas | Cada entrada empieza con el texto `TOC \h \z \t "Figuras,1"` o `TOC \h \z \t "Tablas,1"` (75 entradas; solo se salvan la Figura 30 y la Tabla 47). Además, las entradas salen en azul y subrayadas, a diferencia del Contenido | CRÍTICO |
| V-02 | 3–5 | Contenido | Palabras repetidas en seis entradas: "2.2 … (señales de trading)trading)", "2.4 Modelos de Machine LearningMachine Learning", "3.1 … clásicoMachine Learning clásico", "3.4 … Deep LearningMachine Learning vs Deep Learning", "4.5 … (Feature Engineering)Feature Engineering)" y "9.3 Trabajo futuro futuro". Los títulos del cuerpo están bien | CRÍTICO |
| V-03 | 165 | Anexo C.3 | El resumen termina con LaTeX sin convertir: `\keywords{Trading signals \and Classification \and …}` | FORMA |
| V-04 | 135 | §7.8.2, Tabla 34 | La proporción fija de 40 % tiene el mayor Sharpe de la tabla (+0.58) y el texto no dice por qué no se eligió. Esa fila la agregó mi propuesta anterior sin la explicación | IMPORTANTE |
| V-05 | 150 | Referencias [39], [40] y [42] | Las tres dicen "[Consultado: 24 de marzo de 2026]", aunque el mensaje de quien editó dice que la fecha sigue pendiente | AVISO |

### Por qué pasó V-01 y V-02

Los índices se regeneraron con un programa y no con Word:

- **Figuras y tablas:** en el `.docx`, cada entrada abre su propio campo TOC y
  ninguna lo cierra. El documento tiene 309 inicios de campo y 234 cierres; la
  diferencia, 75, son esas entradas. Al encontrar campos sin cerrar, Word
  imprime su código.
- **Contenido:** el programa escribió el título completo y después volvió a
  escribir las partes en cursiva.

---

## 3. Qué hacer

### V-01 y V-02 · Índices, en Word (10 minutos)

Los pies de figura y de tabla están escritos a mano, con los estilos
"Figuras" y "Tablas". No usan *Insertar título*, así que los índices se
construyen por estilo.

1. **Contenido:** clic dentro del Contenido → **F9** → **"Actualizar toda la
   tabla"**. Se reconstruye desde los títulos del cuerpo, que están bien.
2. **Índice de figuras:** no basta con F9, porque los campos están rotos.
   - Seleccionar desde la primera entrada ("Figura 1…") hasta la última
     ("Figura 30… 132") y borrar. Dejar el título "Índice de figuras".
   - Con el cursor debajo del título: *Referencias → Insertar tabla de
     ilustraciones → Opciones… → marcar "Estilo" → elegir **Figuras** →
     Aceptar*.
   - En la ventana principal, dejar "Mostrar números de página", "Alinear
     números de página a la derecha" y el carácter de relleno de puntos.
     Aceptar.
3. **Índice de tablas:** lo mismo, desde "Tabla 1…" hasta "Tabla 47… 166", con
   el estilo **Tablas**.
4. **Ctrl+A → F9** y, en cada índice, "Actualizar toda la tabla". Hay que
   repetirlo porque, sin el código, los índices pueden ocupar una página
   menos y recorrer todos los números.
5. **Comprobar en el PDF exportado desde Word**, no en LibreOffice:
   - ninguna entrada empieza con "TOC";
   - en el Contenido no hay palabras repetidas;
   - la Tabla 28 y las Tablas 39–47 siguen ahí;
   - los números de página coinciden con el cuerpo.

> **Atajo para revisar:** en Word, **Alt+F9** muestra y oculta los códigos de
> campo. Si al volver con Alt+F9 todavía se ve "TOC" en alguna entrada, esa
> entrada sigue rota.

### V-03 · Palabras clave del Anexo C.3

Sustituir `\keywords{Trading signals \and Classification \and Deep learning
\and Logistic regression \and XGBoost \and LSTM \and CNN.}` por:

> **Keywords:** Trading signals · Classification · Deep learning · Logistic
> regression · XGBoost · LSTM · CNN.

### V-04 · Tabla 34: por qué no la proporción fija

**El problema:** en la Tabla 34, la proporción fija de 40 % tiene el mayor
Sharpe de todas las alternativas (+0.58 contra +0.54 del peso × 0.90), y el
texto solo explica por qué no se eligió la proporción móvil. Un sinodal que
lea la tabla con calma lo va a preguntar.

**En §7.8.2,** después de "…por lo que se eligió el peso × 0.90.", agregar:

> La proporción fija de 40 % obtuvo el mayor Sharpe en 2019–2024 (+0.58), pero
> un F1 de 0.337, casi tres centésimas por debajo del peso × 0.90, y menos
> Sharpe en 2025 (+0.88 contra +0.93). Como el F1-macro es la métrica
> principal, se descartó.

Fuente: `RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md` §8.2, donde
están las columnas de 2019–2024 y de 2025.

### V-05 · Fecha de consulta

[39] TrendSpider, [40] Trade Ideas y [42] Scrum Guide dicen "[Consultado: 24
de marzo de 2026]". Si es la fecha real, R-08 queda cerrado. Si se puso de
relleno, hay que cambiarla por la real. Ojo con [42]: la referencia de Scrum
se agregó en la revisión de octubre (`correcciones/C08_REFERENCIAS.md`,
8-04), así que una consulta en marzo solo es correcta si de verdad se leyó
entonces.

---

## 4. Lo que corregí en el repositorio

| Archivo | Corrección |
|---|---|
| `textos/T06_resultados.md` | La frase de V-04 en el párrafo de la corrección de mantener |
| `tablas/TABLAS_NUEVAS.md` | La nota de T-18 explica por qué no la proporción fija |
| `../ESTUDIO_TT/A_modelo/A7_RESULTADOS_Y_LIMITES.md` | La tabla de §4.3 ya tiene las ocho alternativas (faltaban la proporción fija y la de 63 días), con la explicación |
| `../ESTUDIO_TT/D_defensa/D8_PREGUNTAS_TRAMPA.md` | T31 nueva: "la proporción fija tiene más Sharpe, ¿por qué no esa?" |

---

## 5. Orden sugerido

1. **V-01 y V-02** (índices, en Word). Es lo primero que se ve al abrir el
   documento.
2. **V-03 y V-04**: dos pegados de texto.
3. **V-05**: confirmar la fecha.
4. Exportar a PDF **desde Word** y revisar las páginas 3 a 9.

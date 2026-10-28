# 06 — Tercera revisión (TT2_v5.pdf, 28 de octubre)

> **Versión revisada:** `TT2_v5.pdf`, 168 páginas, fecha de portada
> 28/10/2026. Las páginas se citan con el número impreso al pie (en el visor
> de PDF es una más).
>
> **En una frase:** la versión anterior tenía 25 pendientes
> ([`05_REVISION_TT2.md`](05_REVISION_TT2.md)) y quedan 24 resueltos; solo
> falta la fecha de consulta de las referencias web. El blindaje quedó bien
> hecho: §4.1.1, una frase de motivación por etapa, la Tabla 38 con "Cuándo"
> y "Qué la motivó", el Anexo B con las 46 pruebas y el Anexo C con el
> artículo. Lo nuevo que hay que corregir es poco, pero algo se nota mucho:
> **los índices muestran doce "¡Error! Marcador no definido"** y no incluyen
> los Anexos B y C. Además hay **cuatro afirmaciones que su propia tabla
> contradice**, que es justo lo que un sinodal encuentra al revisar con
> calma.
>
> **Aviso:** tres de esos cuatro errores venían de mis textos de la revisión
> anterior (T06, T08 y el Anexo B en Markdown), y el documento los copió tal
> cual. Ya están corregidos en el repositorio (sección 4).

---

## 1. Estado de la revisión anterior

| # | Pendiente de `05` | Estado en TT2_v5 |
|---|---|---|
| R-01 | Apellido de la portada | ✅ "Cuatianquiz" |
| R-02 | Rango 0.314–0.394 mezclado con la Tabla 29 | ✅ §7.9 y §7.10 dicen 0.326 (2024) a 0.393 (2020). Pero la misma mezcla reaparece en otros dos lugares (N-07) |
| R-03 | 186 parámetros, no 231 | ✅ §4.9.1, §4.9.6 y §7.9 |
| R-04 | "Anexo aparte" que no existía | ✅ §4.4 remite a los scripts del repositorio |
| R-05 | Salto 2.3.2 → 2.3.4 | ✅ |
| R-06 | "Se publicó" | ✅ "Aceptada para su publicación" en todo el documento |
| R-07 | Lista de siglas | ✅ p. 12 (faltan algunas: N-14) |
| R-08 | Fecha de consulta de las referencias web | ❌ **Sigue pendiente** (N-15) |
| R-09 | Nota duplicada en la Figura 1 | ✅ Queda solo la de la figura |
| R-10 | El artículo como producto y como anexo | ✅ §1.3 (productos) y Anexo C |
| R-11 | Dirección del repositorio | ✅ Tabla 1, §1.3, §4.4, §4.10.5, RNF-03, Anexos B y C |
| E-01 | 93 variables | ✅ §7.5.3 |
| E-02 | Barrido de la etiqueta | ✅ §7.7 y §9.3, sin cifras "No citar". El número de combinaciones está mal (N-05) |
| E-03 | Reglas de adopción | ✅ §7.5.3 (torneo) y §7.7 (Etapa 5) |
| E-04 | La Etapa 5 se midió sobre 2025 | ✅ §7.7 y Anexo B |
| E-05 | Por qué cinco semillas | ✅ §4.10.5 |
| E-06 | Tabla del torneo | ✅ Tabla 28. Las negritas están mal (N-03) |
| E-07 | Qué respondieron A, B y C | ✅ Final de §7.5.2 |
| E-08 | La LR fue la última en la validación 2024 | ✅ §7.9 |
| E-09 | Calibración isotónica | ✅ §7.7 |
| E-10 | La Etapa 4 la pidieron los revisores | ✅ §4.1.1, §7.5.1 y Anexo C.2 |
| E-11 | Historial del modelo de la plataforma | ✅ §7.8 |
| E-12 | Costos de 5 pb | ✅ §7.5.2 |
| E-13 | LightGBM y filtro de confianza | ✅ §7.3 |
| E-14 | Lista de las "cerca de treinta técnicas" | ✅ Anexo B (46 pruebas) |
| — | §4.1.1, frases de motivación, Tabla 38 ampliada | ✅ |
| — | 13 referencias de las técnicas | ✅ [44]–[56], todas citadas en el texto |

También comprobé contra el repositorio las cifras nuevas: Tabla 23 (columna
por acción), Tabla 28, 93 variables, costos de 5 pb, calibración, mezclas,
SWA, interacciones, Tablas 34–35, Anexo B y la cronología del Anexo C.
Coinciden, salvo lo que se lista abajo. También coincide con el código lo
nuevo del capítulo VI: Flask con flask-cors, SQLAlchemy y 24 pruebas
automáticas. Todos los archivos que citan la Tabla 46 y el Anexo C existen en
el repositorio público.

---

## 2. Problemas nuevos

| # | Página | Sección | Qué pasa | Prioridad |
|---|---|---|---|---|
| N-01 | 6–9 | Índices de figuras y tablas | **Doce "¡Error! Marcador no definido"**: Figuras 10, 11 y 28; Tablas 6, 22, 23, 25, 27, 29, 31, 34 y 37 | CRÍTICO |
| N-02 | 3–9 | Contenido e índice de tablas | No aparecen los **Anexos B y C** ni la **Tabla 28** (el índice salta de la 27 a la 29), ni las Tablas 39–47 | CRÍTICO |
| N-03 | 129 | 7.5.3, Tabla 28 | Las negritas marcan como adoptados el F1 de validación y las ventanas alineadas **de la CNN 1D**. El F1 de validación no se adoptó en la CNN 1D, y las ventanas sí se adoptaron, pero en las tres redes | IMPORTANTE |
| N-04 | 136 | 7.8.2, Tabla 34 | "La mejor en F1, kappa y Sharpe a la vez fue… × 0.90", pero la misma tabla da a la proporción móvil más F1 (0.367) y más kappa (0.070). Además dice "cinco correcciones": la tabla tiene seis y se probaron ocho (el Anexo B dice "siete") | IMPORTANTE |
| N-05 | 134, 162 | 7.7; Anexo B, fila 37 | "28 combinaciones", y en el anexo "6 horizontes × 5 pares (28)": 6 × 5 = 30. Se corrieron **24 combinaciones distintas** (28 corridas, 4 repetidas) | IMPORTANTE |
| N-06 | 68, 69, 131, 134 | 4.8.1, 4.8.2, Tablas 30 y 32 | La LR tiene cinco F1 distintos en 2025 (0.404, 0.373, 0.390, 0.393 y 0.4125) y nunca se explica por qué | IMPORTANTE |
| N-07 | 131, 138, 143 | 7.6.1, 7.9, Tabla 37, 8.2 | Otra vez se mezclan los ajustes de la Etapa 3 y de la Etapa 4, como en R-02 | IMPORTANTE |
| N-08 | 125 | 7.4 | Frase repetida: "con las mismas 61 características para los cinco modelos y la misma prueba en los tres experimentos" aparece dos veces seguidas | FORMA |
| N-09 | 55 | 4.4 | "Definición del target**,** La variable objetivo" → punto en lugar de coma | FORMA |
| N-10 | 114 | 6.6.2 | "contra 34 % del azar"; la Tabla 36 dice 33 | FORMA |
| N-11 | 121 | 6.9.3 | Remite a "la sección 4.11.4" para la aclaración de que la simulación no es una promesa de ganancias; esa aclaración está en 4.11.2 y 4.11.6 | FORMA |
| N-12 | 166 | Anexo C.3 | El resumen del artículo está recortado sin avisarlo (faltan los siete *tickers*, las métricas adicionales y la lista de filtros) | FORMA |
| N-13 | 166 | Anexo C | El enlace apunta a `TT/tree/main/PAPER_MICAI`. Si el artículo se separa en su propio repositorio, hay que actualizarlo (la carpeta del repositorio TT puede quedarse) | AVISO |
| N-14 | 12 | Lista de siglas | Faltan siglas que el texto usa: pb, IC, OHLCV, ROI, HTTP, SPY | FORMA |
| N-15 | 151 | Referencias [39], [40], [42] | Sigue sin fecha de consulta (R-08) | FORMA |

---

## 3. Qué hacer con cada uno

### N-01 y N-02 · Índices (10 minutos)

La causa: esos pies de figura y de tabla se reescribieron o se pegaron desde
otro lado, y perdieron el marcador que usa el índice.

1. Clic dentro de cada índice (contenido, figuras y tablas) → **F9** →
   **"Actualizar toda la tabla"**.
2. Si un elemento sigue con el error, su pie está escrito a mano. Hay que
   borrarlo y volver a insertarlo con *Referencias → Insertar título*.
3. Lo mismo con la **Tabla 28** y las **Tablas 39–47**, si no aparecen.
4. A "Anexo B…" y "Anexo C…" se les da el estilo de Título 1, y a B.1–B.8 y
   C.1–C.5 el de Título 2, para que entren en el Contenido.
5. Al final: Ctrl+A → F9, para actualizar las referencias cruzadas.
   Después hay que comprobar que la numeración no se haya recorrido. El texto
   cita la Tabla 29 (VIF), la 30 (año por año), la 32 (interacciones), la 34
   (MANTENER), la 37 (selección) y la 38 (etapas); si la Tabla 28 estaba
   escrita a mano, Word puede cambiar los números de las siguientes.

### N-03 · Tabla 28: quitar dos negritas y cambiar la nota

**En la tabla:** quitar las negritas de la CNN 1D en "F1 de validación"
(0.328). En la fila "Sí" de ventanas alineadas, poner en negritas los tres
valores o ninguno. Solo debe quedar en negritas lo que se adoptó:

| Decisión | CNN 1D | CNN-LSTM | LSTM |
|---|---|---|---|
| Criterio de época | Pérdida (se queda) | Pérdida (se queda) | **F1 de validación** |
| Ventanas alineadas | **Sí** | **Sí** (por diseño) | **Sí** |
| Lo demás | Se queda lo de la Etapa 3 | Se queda | Se queda |

Fuente: `RESULTADOS_OPTIMIZADOS/v5/v1_decisiones.json` y la configuración
congelada `v5/base_v5.json`.

**Por qué importa:** un sinodal ve +0.027 en la CNN 1D con una regla de
"≥ 0.005" y pregunta por qué no se adoptó. La respuesta está en la regla
completa: la mejora también tiene que superar la desviación entre semillas, y
en la CNN 1D esa desviación es de 0.029.

**Nota nueva** (sustituye a la actual):

> Nota. En negritas, la variante adoptada. Una variante se adoptaba solo si
> mejoraba el F1-macro en al menos 0.005 y más que la mayor de las dos
> desviaciones entre semillas. Por eso, en la CNN 1D no se adoptaron el F1 de
> validación (+0.027) ni el escalador estándar (+0.012): las dos mejoras son
> menores que la desviación entre semillas (0.029 en ambos casos). Las
> ventanas alineadas se adoptaron en las tres redes por diseño, aunque le
> cuestan 0.027 a la CNN-LSTM, porque sin ellas los cinco modelos no se
> evalúan sobre las mismas filas; durante el torneo la CNN-LSTM siguió sin
> alinear, y por eso en las filas siguientes conserva 0.335. El pooling
> temporal se omite: sus alternativas quedaron dentro del ruido (CNN 1D
> 0.308–0.331, CNN-LSTM 0.305–0.306, LSTM 0.336–0.346). Fuente: archivos
> v1_ablaciones.csv y v1_decisiones.json del repositorio del proyecto.

### N-04 · Tabla 34 y §7.8.2

**Texto de §7.8.2.** Sustituir desde "Se compararon cinco correcciones…"
hasta "…multiplicado por 0.90.":

> Se compararon ocho correcciones con un origen rodante de 2019 a 2024, sin
> observar 2025 ni 2026 (Tabla 34). Entre los pesos de reentrenamiento, el de
> MANTENER × 0.90 fue el mejor en F1, kappa y Sharpe a la vez. La proporción
> móvil causal de 252 días obtuvo un F1 y un kappa prácticamente iguales
> (0.367 y 0.070, contra 0.365 y 0.068), pero un Sharpe menor en 2019–2024
> (+0.51 contra +0.54), en 2025 (+0.81 contra +0.93) y en 2026 (+0.16 contra
> +0.29; Tabla 35), por lo que se eligió el peso × 0.90.

**Tabla 34.** Agregar las dos filas que faltan, después de "P(mantener) ×
0.90 al decidir", y renombrar la de 252 días:

| Alternativa | F1 | Kappa | Sharpe | Mantener predicho |
|---|---:|---:|---:|---:|
| Proporción fija por año (40 %) | 0.337 | 0.062 | +0.58 | 45 % |
| Proporción móvil causal (63 días) | 0.365 | 0.061 | +0.42 | 43 % |
| Proporción móvil causal (**252 días**) | 0.367 | 0.070 | +0.51 | 41 % |

Y en la nota de la tabla: "Nota. Proporción real de MANTENER: 40 %. **Se
eligió el peso × 0.90 (véase el texto).**" Fuente:
`RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md` §8.2.

**Anexo B, fila 41.** "Qué se probó":

> Ocho correcciones con origen rodante 2019–2024 (factor fijo al decidir,
> proporción fija de 40 %, proporción móvil de 63 y de 252 días, pesos de
> clase × 0.95 / 0.90 / 0.85 / 0.80)

"Resultado":

> Entre los pesos, × 0.90 es el mejor en F1, kappa y Sharpe a la vez; la
> proporción móvil de 252 días empata en F1 y kappa, con menos Sharpe en
> 2019–2024, 2025 y 2026

### N-05 · Número de combinaciones de la etiqueta

- §7.7: "con **28** combinaciones de horizonte" → "con **24** combinaciones
  de horizonte".
- Anexo B, fila 37: "6 horizontes (1–10 días) × 5 pares de percentiles (28
  configuraciones)" → "**24 combinaciones de 6 horizontes (1–10 días) y 5
  pares de percentiles**".

Fuente: `RESULTADOS_OPTIMIZADOS/v8/target_ablation.csv` y
`target_ablation_ext.csv`.

### N-06 · Por qué la LR tiene cinco F1 distintos en 2025

Un sinodal que hojee las tablas ve 0.404 (Tabla 25), 0.373 (Tabla 30), 0.390
(Tabla 32), 0.393 (§4.8.2) y 0.4125 (§4.8.1), todos "en 2025". Cada uno sale
de un montaje distinto, pero el documento no lo dice. Se arregla con dos
notas y dos aclaraciones:

**Nota bajo la Tabla 30:**

> Nota. La fila de 2025 no coincide con la Tabla 25 porque esta prueba
> entrena con cinco años (2019–2023) y usa los ajustes de la Etapa 3; la
> Tabla 25 entrena con seis (2018–2023) y usa los de la Etapa 4.

**Nota bajo la Tabla 32:**

> Nota. Cifras de la reimplementación que se usó en la Etapa 5 para probar
> variables nuevas sin modificar el código de la Etapa 4 (1 729 filas de
> prueba); por eso la Regresión Logística sin interacciones da 0.390 en 2025
> y no 0.404 (Tabla 25). Lo que se compara es la diferencia dentro de la
> misma tabla.

**§4.8.1**, al final del paréntesis: "(0.4125 contra 0.4086 de F1-macro en
2025**, con las 76 variables de la plataforma**)".

**§4.8.2**, después de "(−0.007)": "**, medido con la Regresión Logística de
producción sin interacciones**".

Fuente: `RESULTADOS_OPTIMIZADOS/docs/VIA8_DATASET.md` (nota del inicio) y
`docs/ANALISIS_HOLD_Y_GLOBAL.md` §1; `scripts_opt/verificar_ventana_redes.py`.

### N-07 · Etapa 3 contra Etapa 4, otra vez

En la prueba año por año hay dos juegos de cifras. Con los ajustes de la
**Etapa 3** (Tabla 30): LR 0.360, XGBoost 0.356; el mejor año de la LR es
2020 (0.393). Con los de la **Etapa 4**: LR 0.350, XGBoost 0.356; el mejor
año de la LR es 2025 (0.394). El documento mezcla los dos juegos en tres
lugares:

**a) §8.2, primera restricción (p. 143).** Dice "el desempeño de 2025 fue el
mejor de la prueba año por año". Con la Tabla 30, 2025 es el tercer año de la
LR (0.373), y §4.7.1 dice que 2025 "no es especialmente favorable".
Sustituir por:

> La señal es débil y cambia entre años: el F1-macro de la prueba principal
> en 2025 (0.404) está por encima de la media de seis años de la prueba año
> por año (0.360), y los resultados no garantizan que los modelos mantengan
> ese desempeño en otras condiciones de mercado.

**b) §7.9, último párrafo, y Tabla 37 (p. 138).** "La primera en el promedio
de seis años de prueba (0.360…)" solo es cierto con los ajustes de la Etapa
3. Cambiar a:

> …la primera en el promedio de seis años de prueba con los ajustes fijados
> de antemano (0.360, en empate estadístico con XGBoost; con los ajustes de
> la Etapa 4, XGBoost queda 0.006 arriba, menos que la variación del mismo
> modelo entre años)…

En la Tabla 37, la decisión de la LR: "primero en el promedio de seis años
**con los ajustes fijados de antemano**". Y en la nota de la tabla, agregar:
"La media 2020–2025 usa los ajustes de la Etapa 3 (Tabla 30)."

**c) §7.6.1 (p. 131).**

- "ningún modelo supera 0.394 en ningún año" → "**ningún modelo llega a 0.40
  en ningún año**". En la Tabla 30 el máximo es 0.393; el 0.394 sale de los
  ajustes de la Etapa 4.
- "el resultado es el mismo: Regresión Logística 0.350, XGBoost 0.356…" →
  "**la conclusión es la misma: los dos modelos clásicos quedan juntos y
  arriba (XGBoost 0.356, Regresión Logística 0.350) y las redes debajo**
  (CNN-LSTM 0.328 en promedio de cinco años, LSTM 0.314 y CNN 1D 0.292)".
  Dicho así, nadie lo puede leer como "la LR vuelve a ganar".

Las respuestas para la defensa sobre N-04, N-06 y N-07 están en
`../ESTUDIO_TT/D_defensa/D8_PREGUNTAS_TRAMPA.md`, T28–T30.

### N-08 a N-15 · Forma

- **N-08** (§7.4): borrar la primera de las dos frases repetidas y empezar en
  "Con las mismas 61 características para los cinco modelos y la misma
  prueba en los tres experimentos (120 corridas…)".
- **N-09** (§4.4): "Definición del target. La variable objetivo…".
- **N-10** (§6.6.2): "contra 33 % del azar".
- **N-11** (§6.9.3): "una aclaración que aparece en las secciones 4.11.2 y
  4.11.6".
- **N-12** (Anexo C.3): titularlo "C.3 Resumen del artículo (versión
  abreviada)" o pegar el resumen completo, que está en
  `PAPER_MICAI/paper_review/` (archivo `.tex`, entorno `abstract`).
- **N-14** (siglas): IC (intervalo de confianza), OHLCV (apertura, máximo,
  mínimo, cierre y volumen; *open, high, low, close, volume*), pb (puntos
  base), ROI (retorno de la inversión; *return on investment*), HTTP
  (protocolo de transferencia de hipertexto), SPY (ETF que replica el S&P
  500).
- **N-15** (referencias [39], [40], [42]): agregar "[Consultado: dd mm
  2026]" antes de "Disponible en".

---

## 4. Lo que corregí en el repositorio

Tres de los errores venían de mis textos, y los corregí en el origen para
que no vuelvan a copiarse:

| Archivo | Corrección |
|---|---|
| `textos/T06_resultados.md` | "Cinco correcciones" → ocho; "la mejor a la vez" → "entre los pesos de reentrenamiento", con el motivo frente a la proporción móvil; "supera 0.394" → "llega a 0.40"; "el resultado es el mismo" → texto explícito |
| `textos/T08_blindaje_experimentos.md` | 28 → 24 combinaciones; negritas de la tabla del torneo y nota con la regla completa |
| `tablas/ANEXO_B_REGISTRO_DE_EXPERIMENTOS.md` | Filas 37 (24 combinaciones) y 41 (ocho correcciones) |
| `tablas/TABLAS_NUEVAS.md` | T-18 con las ocho alternativas y una nota; "llega a 0.40" |
| `05_REVISION_TT2.md` | 28 → 24 en E-02 |
| `../RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md` | Número de combinaciones de la etiqueta |
| `../RESULTADOS_OPTIMIZADOS/docs/VIA7_REFINAMIENTO.md` | Nota al inicio. El documento decía "Única adopción: XGBoost + calibración isotónica" y el reporte dice que no se adoptó. La Tabla 46 cita ese archivo, así que un sinodal que lo abra vería la contradicción |
| `../ESTUDIO_TT/A_modelo/A7…`, `D_defensa/D4…`, `01_PANORAMA…` | La misma precisión sobre el peso × 0.90, para no repetir el error en la defensa |
| `../ESTUDIO_TT/D_defensa/D8_PREGUNTAS_TRAMPA.md` | T28–T30 nuevas; el consejo de "cifras a la mano" ahora distingue Etapa 3 y Etapa 4 |

---

## 5. Orden sugerido

1. **N-01 y N-02** (índices). Es lo primero que se ve al abrir el documento.
   10 minutos.
2. **N-03 a N-07**, con los textos de la sección 3. 30 minutos.
3. **N-08 a N-15**. 15 minutos.
4. Actualizar los índices otra vez y revisar que la numeración de las tablas
   no se haya recorrido.

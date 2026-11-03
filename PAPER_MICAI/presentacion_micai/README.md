# Presentación oral en MICAI 2026

Todo lo necesario para presentar el artículo en el congreso. La versión
principal es para **un solo expositor**; también está lista la alternativa para
dos.

## Cuándo y dónde

| | |
|---|---|
| **Día y hora** | **Jueves 5 de noviembre de 2026, 16:40** (espacio de 16:40 a 17:00) |
| **Sala** | **Room 1104**, Tec de Monterrey, Campus Chihuahua |
| **Sesión** | *Machine Learning & Data Analytics*, oral, de 16:00 a 18:20 |
| **Identificador** | **Paper ID 78** |
| **Tiempo** | 10 minutos de exposición + 5 de preguntas (página de autores) |

Fuente: programa oficial, https://micai.org/2026/activities/#program, consultado
el 2 de noviembre. **El programa advierte que puede cambiar sin aviso**: hay que
revisarlo otra vez el miércoles en la noche y el jueves en la mañana. De 16:20 a
16:40 no aparece ningún artículo, así que conviene estar en la sala desde el
inicio de la sesión por si el moderador recorre los turnos.

## Archivos

| Archivo | Qué es | ¿Imprimir? | ¿USB? |
|---|---|---:|---:|
| [`TARJETAS_UN_EXPOSITOR.pdf`](TARJETAS_UN_EXPOSITOR.pdf) | **Las tarjetas para exponer**: una por diapositiva, con renglones cortos, pronunciación y minuto; más preguntas por tema, frases de apoyo, cifras clave y versión de 2 minutos | **Sí** | Sí |
| [`TARJETAS_DOS_EXPOSITORES.pdf`](TARJETAS_DOS_EXPOSITORES.pdf) | Las mismas tarjetas si al final son dos: separadas por color y con las frases para pasar la palabra | Solo si son dos | Sí |
| [`MICAI2026_benchmark_trading_signals.pptx`](MICAI2026_benchmark_trading_signals.pptx) | **La presentación**: 11 diapositivas + 4 de respaldo, con el guion en las notas del orador | No | **Sí** |
| [`MICAI2026_benchmark_trading_signals.pdf`](MICAI2026_benchmark_trading_signals.pdf) | La misma en PDF, por si la computadora de la sala no abre bien el .pptx | No | **Sí** |
| [`GUION_UN_EXPOSITOR.pdf`](GUION_UN_EXPOSITOR.pdf) ([`.md`](GUION_UN_EXPOSITOR.md)) | Guion completo con **traducción**, para ensayar; incluye la tabla de pronunciación | Opcional | Sí |
| [`GUION_DOS_EXPOSITORES.pdf`](GUION_DOS_EXPOSITORES.pdf) ([`.md`](GUION_DOS_EXPOSITORES.md)) | Lo mismo para dos expositores | Opcional | Sí |
| [`../paper_review/paper.pdf`](../paper_review/paper.pdf) y el suplementario | El artículo y su material suplementario, por si alguien los pide | Opcional | Sí |
| [`fuente/`](fuente/) | Plantilla oficial, logotipos y los scripts que generan todo | No | No |

## Qué imprimir

1. **`TARJETAS_UN_EXPOSITOR.pdf`: 11 hojas carta**, a **tamaño real (100 %, sin
   "ajustar a la página")**, **a una cara**. Mejor en papel grueso (opalina o
   cartulina delgada).
2. Corta cada hoja por la línea punteada del centro: salen **22 tarjetas de media
   carta**.
3. Ordénalas como salen: `Antes`, `1`–`11`, `?`, `Ayuda`, `A`–`F`, `Cifras`, `2 min`.
   Engrápalas o únelas con un anillo por la esquina superior izquierda de cada
   bloque, para que no se revuelvan si se caen: un bloque para la exposición y otro
   para las preguntas.

Si son dos expositores: imprime `TARJETAS_DOS_EXPOSITORES.pdf` completo y **las
hojas 7 a 11 una vez más**, para que cada quien tenga sus preguntas. Cada
expositor se queda con las tarjetas de su color (franja azul: expositor 1; franja
rosa: expositor 2).

Opcional, para ensayar: `GUION_UN_EXPOSITOR.pdf`, con la traducción. No hace falta
llevarlo a la sala.

## Qué llevar en la USB

La regla oficial pide llevar la presentación en una USB. Lleva **dos USB** con lo
mismo, una de ellas en otra bolsa, y prueba que abran en otra computadora. Este
comando copia todo de una vez (cambia `E:` por la letra de tu USB):

```bash
python presentacion_micai/fuente/preparar_usb.py E:/MICAI2026
```

Copia los dos archivos de la presentación, las tarjetas, los guiones, el artículo y
el suplementario (unos 13 MB). Lo indispensable son el `.pptx` y su `.pdf`.

## Lista de pendientes

- [ ] **Revisar el programa** el miércoles en la noche y el jueves en la mañana.
- [ ] Confirmar el **registro y el pago** (el artículo aparece en el programa, buena
      señal, pero el comprobante no está en este repositorio). Llevar el comprobante.
- [ ] Decidir si son uno o dos expositores. Los nombres están en `fuente/guion.py`
      (`NOMBRE_1`, `NOMBRE_2`); por ahora, Baruc Polvo y David Reyes. Si cambian: ver
      "Para cambiar algo".
- [ ] Copiar los archivos a **dos USB**.
- [ ] Imprimir y cortar las tarjetas.
- [ ] Subir el repositorio del artículo a https://github.com/Daivino/PAPER_MICAI
      **antes del jueves**: la diapositiva 11 lo muestra (comandos en `../README.md`).
- [ ] Llevar laptop y adaptador HDMI por si la computadora de la sala falla.
- [ ] Opcional: agregar la foto del expositor en la portada (la plantilla lo permite).
- [ ] El día de la presentación: llegar a la sala a las **15:45**, presentarse con el
      moderador (*session chair*) y cargar la presentación. La frase está en la
      primera tarjeta.

## Cómo ensayar (quedan pocos días)

1. **Martes: entender y pronunciar.** Lee el guion en voz alta con la traducción a la
   vista. Repite cada tarjeta tres veces fijándote en su recuadro de pronunciación.
   Para oír cada frase: el botón de audio de Google Translate o DeepL.
2. **Miércoles: completo y con cronómetro.** Tres pasadas con las diapositivas
   abiertas y las tarjetas en la mano, pasando de diapositiva en cada `CLIC`. **Meta:
   entre 8 y 9:30 minutos.** Grábate una vez con el celular y escúchate. Es válido
   leer: mira al público al final de cada renglón. Si te pasas de 9:30, salta las
   frases marcadas con ✂.
3. **Miércoles en la noche: preguntas.** Que alguien te lea las preguntas de las
   tarjetas `A`–`F` en desorden; tú reconoces la palabra clave, buscas la tarjeta y
   contestas. Practica también *Sorry, could you repeat the question, please?*
4. **Jueves en la mañana:** una pasada completa y una de la versión de 2 minutos.

**En el momento:** habla despacio; señala la gráfica cuando digas un número; si te
pierdes, lee el título de la diapositiva y busca la tarjeta con ese número; si no
entiendes una pregunta, pide que la repitan. Puedes terminar con *We can talk more
after the session.*

## Reglas oficiales

Fuente: página para autores (https://micai.org/2026/authors/), consultada el 26 de
octubre y otra vez el 2 de noviembre de 2026.

| Regla | Detalle | Cómo se cumple aquí |
|---|---|---|
| **Modalidad** | Presencial; al menos un autor registrado debe asistir y presentar | Presenta uno o dos autores |
| **Idioma** | Presentación **en inglés** y diapositivas en inglés | Todo en inglés sencillo |
| **Duración** | **Máximo 10 minutos + 5 de preguntas** (el programa reserva 20 min por artículo) | Guion de unos 8:25 a ritmo lento; unos 9:15 si vas todavía más despacio |
| **Primera diapositiva** | Plantilla oficial (`MICAI2026_Template_Author_upt.potx`) con título, autores con institución y logotipos (foto opcional). No se modifica el encabezado ni el pie | Portada sobre la plantilla, con los tres componentes y los logos del IPN y de ESCOM |
| **Resto de diapositivas** | Formato libre | Diseño "Blank" de la plantilla |
| **Archivo** | El autor lleva la presentación en **USB** el día del evento | Ver "Qué llevar en la USB" |
| **Registro** | Un pago por artículo; fecha límite: 16 de octubre | Confirmar el comprobante |

No se encontró en la página: proporción de pantalla (se usó 16:9, igual que la
plantilla), si habrá computadora en la sala (se asume que sí, por la regla de la
USB) ni presentación remota (es presencial).

## Las diapositivas

Tiempos a ritmo lento (95 palabras por minuto + 5 s por diapositiva). La columna
"Si son dos" indica quién habla en la alternativa.

| # | Diapositiva | Tiempo | Si son dos |
|---:|---|---:|---:|
| 1 | Portada (plantilla oficial) | 0:34 | 1 |
| 2 | Do deep networks beat simple models? | 0:50 | 1 |
| 3 | One signal per day, seven tech stocks | 1:02 | 1 |
| 4 | Five models, one protocol | 0:52 | 1 |
| 5 | Result 1 · Logistic regression leads on average | 1:00 | 2 |
| 6 | Result 2 · Do not pre-filter the features | 0:31 | 2 |
| 7 | Result 3 · The stock matters more than the model | 0:42 | 2 |
| 8 | Was it fair? We rebuilt the protocol | 0:44 | 2 |
| 9 | Result 4 · The gap does not close | 0:48 | 2 |
| 10 | Why does a linear model win here? | 0:47 | 1 |
| 11 | Takeaways · Thank you · Questions? | 0:34 | 1 |
| 12–15 | Respaldo: Tabla 6, "since submission", Tablas 3–5, búsqueda de hiperparámetros | solo si preguntan | — |

- Las gráficas son **nativas de PowerPoint** (clic derecho → Editar datos) y usan
  exactamente los números del artículo.
- Los números van en Calibri porque la fuente de la plantilla (Corbel) dibuja las
  cifras como "minúsculas" y se leen peor.
- Cada diapositiva tiene en sus **notas** el minuto, el texto en inglés, la
  traducción y qué cambia si son dos expositores. Con la vista del moderador de
  PowerPoint se ven en la laptop, no en la pantalla grande, si la sala lo permite.
- Para saltar a otra diapositiva durante la presentación: número + **Enter**.

Se dejaron así por tiempo, respecto a `../06_PRESENTACION_MICAI.md` (15 minutos): los
datos y la etiqueta en una sola diapositiva; la economía dentro del resultado 1; por
qué gana la LR junto con las limitaciones; las tablas completas como respaldo.

## Para cambiar algo

Todo se genera con scripts; **no editar a mano** el `.pptx`, los guiones ni las
tarjetas si se quiere poder regenerarlos. El texto vive en `fuente/guion.py`.

```bash
# Desde la raíz de este repositorio (dentro del TT, desde PAPER_MICAI/)
python presentacion_micai/fuente/generar_guion.py
python presentacion_micai/fuente/generar_tarjetas.py
python presentacion_micai/fuente/construir_presentacion.py
```

Después de `construir_presentacion.py` hay que volver a exportar el PDF desde
PowerPoint (*Archivo → Exportar → PDF*).

Requisitos: `pip install python-pptx lxml`; Chrome o Edge para los PDF del guion y de
las tarjetas. `generar_tarjetas.py` ajusta la letra de cada tarjeta y se detiene si
algo no cabe.

Un cambio pequeño de último momento (un número, una palabra) se puede hacer directo
en PowerPoint o, en las tarjetas, con pluma. Si lo haces, anótalo también en `fuente/`
para no perderlo la próxima vez que se regenere.

## Origen de los archivos de `fuente/`

- `plantilla/MICAI2026_Template_Author_upt.potx`: plantilla oficial, descargada de
  https://micai.org/docs/MICAI2026_Template_Author_upt.potx el 26 de octubre de 2026.
- `logos/ipn.png`, `logos/escom.png`: tomados de la portada del reporte técnico del TT.

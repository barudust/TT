# Presentación oral en MICAI 2026

Todo lo necesario para presentar el artículo en el congreso: las diapositivas
listas (sobre la plantilla oficial), el guion para dos expositores en inglés
sencillo con traducción y pronunciación, las preguntas probables y la lista de
pendientes.

| Archivo | Qué es |
|---|---|
| [`MICAI2026_benchmark_trading_signals.pptx`](MICAI2026_benchmark_trading_signals.pptx) | **La presentación**: 11 diapositivas + 4 de respaldo, con el guion en las notas del orador |
| `MICAI2026_benchmark_trading_signals.pdf` | La misma en PDF, de respaldo en la USB por si la computadora del congreso no abre el .pptx |
| [`GUION_DOS_EXPOSITORES.md`](GUION_DOS_EXPOSITORES.md) | Guion completo: qué dice cada quien, tiempos, traducción, pronunciación, preguntas y frases de apoyo |
| `GUION_imprimible.pdf` | El guion en formato para imprimir (texto grande en inglés, traducción en gris) |
| [`fuente/`](fuente/) | Plantilla oficial, logotipos y los scripts que generan todo (ver "Para cambiar algo") |

---

## 1. Reglas oficiales (investigadas el 26 de octubre de 2026)

Fuente: página para autores de MICAI 2026 (https://micai.org/2026/authors/) y
página principal (https://micai.org/2026/).

| Regla | Detalle | Cómo se cumple aquí |
|---|---|---|
| **Fechas y sede** | 2–6 de noviembre de 2026, Tec de Monterrey Campus Chihuahua. Talleres y tutoriales el 2–3; presentaciones de artículos el 4–6 (verificar en el programa) | — |
| **Modalidad** | Presencial; al menos un autor registrado debe asistir y presentar | Presentan dos autores |
| **Idioma** | Presentación **en inglés** y diapositivas en inglés | Todo en inglés; guion en inglés sencillo |
| **Duración** | **10 minutos de exposición + 5 de preguntas** | Guion de 8 min 20 s a ritmo lento (margen de 1 min 40 s) |
| **Primera diapositiva** | Debe usar la plantilla oficial (`MICAI2026_Template_Author_upt.potx`) con tres componentes: título del artículo, autores con institución, logotipos de la institución (foto del expositor opcional). No modificar el encabezado ni el pie | Portada hecha sobre la plantilla, con los tres componentes y los logos del IPN y de ESCOM |
| **Resto de diapositivas** | Formato libre | Se usó el diseño "Blank" de la plantilla para mantener el estilo |
| **Archivo** | El autor lleva la presentación en **USB** el día del evento | Llevar `.pptx` y `.pdf` (ver lista) |
| **Horario** | La fecha y hora de cada presentación se publican en el programa unos días antes | **Pendiente: revisar https://micai.org/2026/activities/#program** |
| **Registro** | Un pago por artículo; fecha límite de pago y registro de autores: 16 de octubre | Verificar que el registro quedó completo |

No se encontró en la página: proporción de pantalla (se usó 16:9, igual que la
plantilla), si habrá computadora de la sede (se asume que sí, por la regla de
la USB) ni presentación remota (no se menciona; es presencial).

---

## 2. Las diapositivas

| # | Diapositiva | Expositor | Tiempo |
|---:|---|---|---:|
| 1 | Portada (plantilla oficial) | 1 | 0:30 |
| 2 | Do deep networks beat simple models? | 1 | 0:50 |
| 3 | One signal per day, seven tech stocks | 1 | 1:10 |
| 4 | Five models, one protocol | 1 | 0:55 |
| 5 | Result 1 · Logistic regression leads on average | 2 | 1:00 |
| 6 | Result 2 · Do not pre-filter the features | 2 | 0:30 |
| 7 | Result 3 · The stock matters more than the model | 2 | 0:30 |
| 8 | Was it fair? We rebuilt the protocol | 2 | 0:45 |
| 9 | Result 4 · The gap does not close | 2 | 0:50 |
| 10 | Why does a linear model win here? | 1 | 0:45 |
| 11 | Takeaways · Thank you · Questions? | 1 | 0:35 |
| 12–15 | Respaldo: Tabla 6, "since submission", Tablas 3–5, búsqueda de hiperparámetros | — | solo si preguntan |

- Las gráficas son **nativas de PowerPoint** (se pueden editar con clic
  derecho → Editar datos) y usan exactamente los números del artículo.
- Los números se escriben en Calibri porque la fuente de la plantilla
  (Corbel) dibuja las cifras como "minúsculas" y se leen peor.
- Cada diapositiva tiene en sus **notas** quién habla, cuánto tiempo, el texto
  en inglés y la traducción. En la vista del moderador de PowerPoint se ven en
  la laptop, no en la pantalla grande (si la sede lo permite).

---

## 3. Por qué este orden (y no el de 15 minutos de `../06_PRESENTACION_MICAI.md`)

El guion de `06_PRESENTACION_MICAI.md` se escribió suponiendo 15 minutos; la
regla real es de 10. Se recortó así: los datos y la etiqueta en una sola
diapositiva; la economía (Sharpe y profit factor) dentro del resultado 1; la
explicación de por qué gana la LR junto con las limitaciones. Las tablas
completas pasaron a diapositivas de respaldo.

---

## 4. Lista de pendientes antes del viaje

- [ ] Poner los nombres reales en el guion (diapositiva 1: *My name is [NAME]…*)
      y decidir quién es Expositor 1 y quién Expositor 2.
- [ ] Revisar el **programa** (https://micai.org/2026/activities/#program): día,
      hora y sala de la presentación; anotar si es en la mañana o en la tarde
      (*Good morning* / *Good afternoon*).
- [ ] Confirmar que el **registro y el pago** quedaron completos.
- [ ] Opcional: agregar la foto del expositor en la portada (la plantilla lo
      permite; un círculo junto a los logos).
- [ ] Copiar a **dos USB** (una por expositor): el `.pptx`, el `.pdf` y el
      `GUION_imprimible.pdf`. Probar que la USB abre en otra computadora.
- [ ] Imprimir el `GUION_imprimible.pdf` (una copia por expositor).
- [ ] Llevar laptop y adaptador HDMI por si la computadora de la sede falla.
- [ ] Ensayar al menos **tres veces completas con cronómetro** (ver §5), y
      una vez la **versión de 2 minutos** del guion, por si la sesión va
      retrasada y el moderador pide recortar.
- [ ] Revisar `../07_PREGUNTAS_MICAI.md` y las respuestas cortas del guion.
- [ ] El día de la presentación: llegar a la sala **15 minutos antes** de la
      sesión, presentarse con el moderador (*session chair*) y cargar la
      presentación en la computadora de la sala.

---

## 5. Cómo ensayar (nivel A2)

1. **Día 1 — leer y entender.** Leer el guion en voz alta con la traducción a
   la vista. Marcar las palabras difíciles y repasar la tabla de
   pronunciación.
2. **Días 2–3 — por partes.** Cada expositor ensaya solo su parte cinco veces
   con las diapositivas abiertas. Grabarse con el celular y escucharse. Es
   válido leer de las notas: se recomienda mirar al público al final de cada
   frase.
3. **Días 4–5 — completo y con cronómetro.** Ensayar los dos juntos, con los
   cambios de expositor. Meta: **entre 8 y 9 minutos**. Si se pasa de 9:30,
   quitar las frases que no estén en **negritas** en la diapositiva (lo
   importante ya está escrito en ella).
4. **Preguntas.** Uno lee una pregunta de la lista y el otro contesta con la
   respuesta corta. Practicar también: *Sorry, could you repeat the question,
   please?*
5. **Ayuda para la pronunciación.** Escuchar cada frase en un traductor con
   voz (por ejemplo, el botón de audio de Google Translate o DeepL) y
   repetirla en voz alta.

**Consejos para el momento:** hablar despacio (con nervios todos aceleran);
señalar la gráfica cuando se diga un número; si se olvida algo, leer el título
de la diapositiva y seguir; si no se entiende una pregunta, pedir que la
repitan o pedírsela por escrito al moderador; contestar corto y, si hace falta,
decir *We can talk more after the session.*

---

## 6. Para cambiar algo

Todo se genera con scripts; **no editar a mano** el `.pptx` ni el guion si se
quiere poder regenerarlos.

```bash
# Cambiar el texto del guion o de las notas: editar fuente/guion.py, luego:
python presentacion_micai/fuente/generar_guion.py
python presentacion_micai/fuente/construir_presentacion.py

# Cambiar el diseño o los datos de una diapositiva: editar fuente/construir_presentacion.py
```

Requisitos: `pip install python-pptx lxml`; Chrome o Edge para el PDF del
guion. El PDF de las diapositivas se exportó con PowerPoint (*Archivo →
Exportar → PDF*).

Cambios pequeños de último momento (un número, una palabra) se pueden hacer
directo en PowerPoint; en ese caso, anotarlos también en `fuente/` para no
perderlos la próxima vez que se regenere.

## 7. Origen de los archivos de `fuente/`

- `plantilla/MICAI2026_Template_Author_upt.potx`: plantilla oficial,
  descargada de https://micai.org/docs/MICAI2026_Template_Author_upt.potx el
  26 de octubre de 2026.
- `logos/ipn.png`, `logos/escom.png`: tomados de la portada del reporte técnico
  del TT.

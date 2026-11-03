"""Guion de la presentación de MICAI 2026: una sola fuente para las notas del
orador (.pptx), los guiones (GUION_*.md y .pdf) y las tarjetas (TARJETAS_*.pdf).

Inglés sencillo a propósito (nivel A2–B1): frases cortas, palabras comunes,
números dichos completos. Hay dos versiones:

- "uno": un solo expositor (la principal).
- "dos": alternativa para dos expositores. Expositor 1 abre y cierra;
  Expositor 2 presenta los resultados.

Tiempos a ritmo lento (~95 palabras por minuto + 5 s por cambio de diapositiva),
con más de un minuto de margen sobre el límite oficial de 10 minutos.

Marcado en los textos en inglés (lo interpretan las tarjetas; `plano()` lo quita):
    |          cambio de renglón: una pausa pequeña para respirar
    **x**      cifra o palabra clave, en negritas
    {x}        la cifra como se ve en la diapositiva, en gris; no se lee
    [[x]]      indicación en español, por ejemplo qué señalar; no se lee
    ✂          al inicio: frase que se puede saltar si vas tarde
"""

from __future__ import annotations

import re

# Si cambia quién presenta, basta con cambiar estos dos nombres y regenerar.
NOMBRE_1 = "Baruc Polvo"
NOMBRE_2 = "David Reyes"

# Datos del programa oficial (https://micai.org/2026/activities/#program),
# consultado el 2 de noviembre de 2026. El programa puede cambiar: revisarlo otra vez.
SESION = {
    "dia": "Jueves 5 de noviembre de 2026",
    "sala": "Room 1104",
    "sede": "Tec de Monterrey, Campus Chihuahua",
    "nombre": "Machine Learning & Data Analytics",
    "horario": "16:00–18:20",
    "turno": "16:40",
    "paper_id": "78",
}

E1 = "Expositor 1"
E2 = "Expositor 2"


def plano(t: str) -> str:
    """El texto tal como se dice: sin el marcado de las tarjetas."""
    t = re.sub(r"\[\[.*?\]\]", "", t)
    t = re.sub(r"\{.*?\}", "", t)
    t = t.replace("**", "").replace("✂", "").replace("|", " ")
    return re.sub(r"\s+", " ", t).strip()


def segundos(frases: list[str]) -> int:
    """Tiempo a ritmo lento: 95 palabras por minuto + 5 s por cambio de diapositiva."""
    palabras = sum(len(plano(f).split()) for f in frases)
    return round(palabras / 95 * 60 + 5)


# Cada diapositiva:
#   en / es          texto para dos expositores (y para uno, si no hay en_uno)
#   en_uno / es_uno  lo que cambia si presenta una sola persona
#   pase / pase_es   frase para pasar la palabra (solo con dos expositores)
#   titulo_en        el título que se ve en la diapositiva, para no perderse
#   idea             la idea en español, por si te quedas en blanco
#   pron             palabras difíciles de esa tarjeta
DIAPOSITIVAS = [
    {
        "n": 1, "titulo": "Portada", "quien": E1,
        "titulo_en": "A Benchmark of Five Machine-Learning Architectures…",
        "en": [
            "[[Respira y mira al público]]**Good afternoon**, everyone.",
            f"My name is {NOMBRE_1}, | and this is my colleague {NOMBRE_2}.",
            "We are from ESCOM, | at the Instituto Politécnico Nacional, | in Mexico City.",
            "Today we present a benchmark | of five machine learning models | for daily trading signals.",
        ],
        "es": [
            "Buenas tardes a todos.",
            f"Me llamo {NOMBRE_1} y conmigo está mi colega {NOMBRE_2}.",
            "Somos de ESCOM, del Instituto Politécnico Nacional, en la Ciudad de México.",
            "Hoy presentamos una comparación de cinco modelos de aprendizaje automático para señales diarias de trading.",
        ],
        "en_uno": [
            "[[Respira y mira al público]]**Good afternoon**, everyone.",
            f"My name is {NOMBRE_1}. | I am from ESCOM, | at the Instituto Politécnico Nacional, | in Mexico City.",
            "Today I will present our benchmark | of five machine learning models | for daily trading signals.",
            "This is joint work with my colleagues | from ESCOM and CIC.",
        ],
        "es_uno": [
            "Buenas tardes a todos.",
            f"Me llamo {NOMBRE_1}. Soy de ESCOM, del Instituto Politécnico Nacional, en la Ciudad de México.",
            "Hoy voy a presentar nuestra comparación de cinco modelos de aprendizaje automático para señales diarias de trading.",
            "Es un trabajo conjunto con mis colegas de ESCOM y del CIC.",
        ],
        "idea": "Saludo, quién soy, de dónde vengo y de qué trata.",
        "pron": [("afternoon", "af-ter-NÚN"), ("everyone", "ÉV-ri-uan"), ("benchmark", "BÉNCH-mark"),
                 ("machine learning", "ma-SHÍN LÉR-ning"), ("trading signals", "TRÉI-ding SÍG-nals"),
                 ("colleague(s)", "CÓ-lig(s)")],
    },
    {
        "n": 2, "titulo": "La pregunta", "quien": E1,
        "titulo_en": "Do deep networks beat simple models?",
        "en": [
            "Our question is simple: | do deep networks beat simple models | for daily trading signals?",
            "Many papers compare | only one or two models.",
            "They often report accuracy or RMSE. | These numbers do not tell us | if a strategy makes money.",
            "And many papers remove features | with statistical filters, | but they do not check if this helps.",
            "So we made a **fair test** with five models, | measured as classification | and as a trading strategy.",
        ],
        "es": [
            "Nuestra pregunta es simple: ¿las redes profundas le ganan a los modelos simples en señales diarias de trading?",
            "Muchos artículos comparan solo uno o dos modelos.",
            "Muchas veces reportan accuracy o RMSE. Esos números no dicen si una estrategia gana dinero.",
            "Y muchos artículos quitan variables con filtros estadísticos, pero no revisan si eso ayuda.",
            "Así que hicimos una prueba justa con cinco modelos, medida como clasificación y como estrategia de trading.",
        ],
        "idea": "La pregunta y los 3 huecos de otros artículos. Nuestra meta: una prueba justa.",
        "pron": [("deep networks", "DIP NÉT-uorks"), ("accuracy", "Á-kiu-ra-si"), ("RMSE", "ar-em-es-Í"),
                 ("features", "FÍ-chers"), ("statistical", "sta-TÍS-ti-cal"), ("measured", "MÉ-shurd"),
                 ("classification", "cla-si-fi-KÉI-shon"), ("strategy", "STRÁ-te-yi")],
    },
    {
        "n": 3, "titulo": "Datos y etiqueta", "quien": E1,
        "titulo_en": "One signal per day, seven tech stocks",
        "en": [
            "We use seven big tech stocks: | Apple, NVIDIA, Tesla, Amazon, | Microsoft, Google and Meta.",
            "The data is free, from Yahoo Finance, | from 2013 to 2025.",
            "Every day, each stock gets one label: | **buy, hold or sell**.",
            "We compare tomorrow's return | with the last **252** days.",
            "Top 30 percent: the label is buy. | Bottom 30 percent: the label is sell. | The rest is hold. [[Señala BUY, SELL y HOLD]]",
            "So the label changes with the volatility, | and it only uses past data.",
            "✂ The input is 61 features: | technical indicators, | plus the S&P 500 and the VIX.",
        ],
        "es": [
            "Usamos siete acciones tecnológicas grandes: Apple, NVIDIA, Tesla, Amazon, Microsoft, Google y Meta.",
            "Los datos son gratis, de Yahoo Finance, de 2013 a 2025.",
            "Cada día, cada acción recibe una etiqueta: comprar, mantener o vender.",
            "Comparamos el retorno de mañana con los últimos 252 días.",
            "El 30 % más alto: la etiqueta es comprar. El 30 % más bajo: la etiqueta es vender. Lo demás es mantener.",
            "Así la etiqueta se adapta a la volatilidad y solo usa datos del pasado.",
            "La entrada son 61 variables: indicadores técnicos, más el S&P 500 y el VIX.",
        ],
        "idea": "Qué acciones, qué datos y cómo se etiqueta (30/40/30) sin ver el futuro.",
        "pron": [("NVIDIA", "en-VÍ-dia"), ("Yahoo Finance", "YÁ-ju FÁI-nans"), ("2013", "tuén-ti zer-TÍN"),
                 ("2025", "tuén-ti tuén-ti FÁIV"), ("label", "LÉI-bel"), ("tomorrow's return", "tu-MÓ-rous ri-TÉRN"),
                 ("252", "tu JÁN-dred FÍF-ti TU"), ("volatility", "vo-la-TÍ-li-ti"),
                 ("S&P 500", "es-and-PÍ FÁIV JÁN-dred"), ("VIX", "VIKS")],
    },
    {
        "n": 4, "titulo": "Modelos y protocolo", "quien": E1,
        "titulo_en": "Five models, one protocol",
        "en": [
            "We compare **five models**.",
            "Two classical models: | logistic regression and XGBoost.",
            "And three deep networks: | an LSTM, a one-dimensional CNN, | and a hybrid CNN-LSTM.",
            "We use three splits. | All of them test on the same year, **2025**. | Only the training history changes: | ten, six or four years. [[Señala las barras]]",
            "We train one global model | and one model per stock. | In total, **120 runs**.",
            "Our main metric is macro-F1, | and we also simulate | a simple trading strategy.",
        ],
        "es": [
            "Comparamos cinco modelos.",
            "Dos modelos clásicos: regresión logística y XGBoost.",
            "Y tres redes profundas: una LSTM, una CNN de una dimensión y una híbrida CNN-LSTM.",
            "Usamos tres particiones. Todas prueban en el mismo año, 2025. Solo cambia la historia de entrenamiento: diez, seis o cuatro años.",
            "Entrenamos un modelo global y un modelo por acción. En total, 120 corridas.",
            "Nuestra métrica principal es F1-macro y también simulamos una estrategia de trading sencilla.",
        ],
        "pase": "Now, my colleague will show the results.",
        "pase_es": "Ahora mi colega va a mostrar los resultados.",
        "idea": "5 modelos, 3 particiones, la misma prueba en 2025, 120 corridas.",
        "pron": [("logistic regression", "lo-YÍS-tic ri-GRÉ-shon"), ("XGBoost", "ex-yi-BÚST"), ("LSTM", "el-es-ti-ÉM"),
                 ("one-dimensional", "uán-di-MÉN-sho-nal"), ("CNN", "si-en-ÉN"), ("hybrid", "JÁI-brid"),
                 ("history", "JÍS-to-ri"), ("120", "uán JÁN-dred TUÉN-ti"), ("macro-F1", "MÁ-cro ef-UÁN"),
                 ("simulate", "SÍ-miu-leit")],
    },
    {
        "n": 5, "titulo": "Resultado 1", "quien": E2,
        "titulo_en": "Result 1 · Logistic regression leads on average",
        "en": [
            "Thank you. Here is the **first result**.",
            "Each group is one split. | The blue bar is logistic regression. [[Señala una barra azul]]",
            "It has the best average macro-F1: | **zero point three nine nine**. {0.399}",
            "It wins in splits A and C. | In split B, XGBoost is very slightly better.",
            "The dashed line is random guessing: | **zero point three three three**. {0.333} [[Señala la línea punteada]] | So the signal is small, but it is there.",
            "In the trading simulation of split B, | logistic regression is the best: | Sharpe ratio **zero point seven six**, {0.76} | and profit factor **one point two one**. {1.21}",
        ],
        "es": [
            "Gracias. Aquí está el primer resultado.",
            "Cada grupo es una partición. La barra azul es la regresión logística.",
            "Tiene el mejor F1-macro promedio: 0.399.",
            "Gana en las particiones A y C. En la B, XGBoost es apenas un poco mejor.",
            "La línea punteada es adivinar al azar: 0.333. La señal es pequeña, pero existe.",
            "En la simulación de trading de la partición B, la regresión logística es la mejor: Sharpe 0.76 y profit factor 1.21.",
        ],
        "en_uno": [
            "Here is the **first result**.",
            "Each group is one split. | The blue bar is logistic regression. [[Señala una barra azul]]",
            "It has the best average macro-F1: | **zero point three nine nine**. {0.399}",
            "It wins in splits A and C. | In split B, XGBoost is very slightly better.",
            "The dashed line is random guessing: | **zero point three three three**. {0.333} [[Señala la línea punteada]] | So the signal is small, but it is there.",
            "In the trading simulation of split B, | logistic regression is the best: | Sharpe ratio **zero point seven six**, {0.76} | and profit factor **one point two one**. {1.21}",
        ],
        "es_uno": [
            "Aquí está el primer resultado.",
            "Cada grupo es una partición. La barra azul es la regresión logística.",
            "Tiene el mejor F1-macro promedio: 0.399.",
            "Gana en las particiones A y C. En la B, XGBoost es apenas un poco mejor.",
            "La línea punteada es adivinar al azar: 0.333. La señal es pequeña, pero existe.",
            "En la simulación de trading de la partición B, la regresión logística es la mejor: Sharpe 0.76 y profit factor 1.21.",
        ],
        "idea": "La LR gana en promedio (0.399) y en la simulación. La señal es pequeña, pero real.",
        "pron": [("average", "Á-ve-rich"), ("slightly", "SLÁIT-li"), ("dashed line", "DASHT LÁIN"),
                 ("random guessing", "RÁN-dom GUÉ-sing"), ("simulation", "si-miu-LÉI-shon"),
                 ("Sharpe ratio", "SHARP RÉI-shio"), ("profit factor", "PRÓ-fit FÁC-tor")],
    },
    {
        "n": 6, "titulo": "Resultado 2", "quien": E2,
        "titulo_en": "Result 2 · Do not pre-filter the features",
        "en": [
            "**Second result.** | Many studies filter the features | before training.",
            "We tested the common filters: | Pearson, VIF, SHAP and Spearman.",
            "In **eleven of fifteen** cases, {11 / 15} [[Señala el 11 / 15]] | keeping all 61 features was better.",
            "The model's own regularization | selects features better | than an external filter.",
        ],
        "es": [
            "Segundo resultado. Muchos estudios filtran las variables antes de entrenar.",
            "Probamos los filtros comunes: Pearson, VIF, SHAP y Spearman.",
            "En 11 de 15 casos, conservar las 61 variables fue mejor.",
            "La regularización del propio modelo elige mejor que un filtro externo.",
        ],
        "idea": "En 11 de 15 casos conviene dejar las 61 variables.",
        "pron": [("filter", "FÍL-ter"), ("Pearson", "PÍR-son"), ("VIF", "vi-ai-ÉF"), ("SHAP", "SHAP"),
                 ("Spearman", "SPÍR-man"), ("eleven", "i-LÉ-ven"), ("fifteen", "fif-TÍN"),
                 ("regularization", "re-guiu-la-ri-SÉI-shon"), ("external", "ex-TÉR-nal")],
    },
    {
        "n": 7, "titulo": "Resultado 3", "quien": E2,
        "titulo_en": "Result 3 · The stock matters more than the model",
        "en": [
            "**Third result.** | We split the variation of the Sharpe ratio.",
            "The stock explains | **fifteen point five percent**. {15.5 %} | The model explains only | **three point four percent**. {3.4 %}",
            "So, choosing the stock matters | about **four and a half times** more | than choosing the model.",
            "✂ For example, Amazon does well | with almost any model, | and Google does badly | with almost any model.",
        ],
        "es": [
            "Tercer resultado. Dividimos la variación del Sharpe.",
            "La acción explica 15.5 %. El modelo explica solo 3.4 %.",
            "Elegir la acción importa unas cuatro veces y media más que elegir el modelo.",
            "Por ejemplo, a Amazon le va bien con casi cualquier modelo y a Google le va mal con casi cualquiera.",
        ],
        "idea": "La acción pesa 4.5 veces más que el modelo.",
        "pron": [("variation", "ve-ri-ÉI-shon"), ("explains", "ex-PLÉINS"), ("fifteen point five", "fif-TÍN point FÁIV"),
                 ("three point four", "ZRI point FOR"), ("choosing", "CHÚ-sing"), ("Amazon", "Á-ma-zon"), ("Google", "GÚ-gol")],
    },
    {
        "n": 8, "titulo": "¿Fue justo?", "quien": E2,
        "titulo_en": "Was it fair? We rebuilt the protocol",
        "en": [
            "But was the comparison **fair**? | The reviewers asked a good question.",
            "XGBoost had a bigger search, | and the input window of the networks | was chosen on the test set.",
            "So we rebuilt everything. [[Señala dev y final]] | All decisions use 2024. | The test year, 2025, is used only one time.",
            "All five models use | the same search tool, Optuna, | and the same **1,736** test rows.",
        ],
        "es": [
            "¿Pero la comparación fue justa? Los revisores hicieron una buena pregunta.",
            "XGBoost tuvo una búsqueda más grande, y la ventana de entrada de las redes se eligió con la prueba.",
            "Así que rehicimos todo. Todas las decisiones usan 2024. El año de prueba, 2025, se usa una sola vez.",
            "Los cinco modelos usan la misma herramienta de búsqueda, Optuna, y las mismas 1,736 filas de prueba.",
        ],
        "idea": "Lo rehicimos sin ventajas: todo se decide con 2024; 2025 se usa una sola vez.",
        "pron": [("fair", "FER"), ("reviewers", "ri-VIÚ-ers"), ("search", "SERCH"), ("chosen", "CHÓU-sen"),
                 ("rebuilt", "ri-BÍLT"), ("2024", "tuén-ti tuén-ti FOR"), ("Optuna", "op-TÚ-na"),
                 ("1,736", "uán ZÁU-sand SÉ-ven JÁN-dred ZÉR-ti SIKS")],
    },
    {
        "n": 9, "titulo": "Resultado 4", "quien": E2,
        "titulo_en": "Result 4 · The gap does not close",
        "en": [
            "And the result? | **The gap does not close.**",
            "Logistic regression gets | **zero point four zero four**, {0.404} | with a 95 percent confidence interval | from zero point three seven nine {0.379} | to zero point four two eight. {0.428}",
            "It is **significantly better** | than the other four models.",
            "The validation loss of the networks | never goes clearly below the random level.",
            "✂ A very small LSTM | gives the same result as a big one.",
        ],
        "es": [
            "¿Y el resultado? La diferencia no se cierra.",
            "La regresión logística obtiene 0.404, con un intervalo de confianza del 95 % de 0.379 a 0.428.",
            "Es significativamente mejor que los otros cuatro modelos.",
            "La pérdida de validación de las redes nunca baja claramente del nivel del azar.",
            "Una LSTM muy pequeña da lo mismo que una grande.",
        ],
        "pase": "Now my colleague will explain why.",
        "pase_es": "Ahora mi colega va a explicar por qué.",
        "idea": "Aun con una búsqueda justa, la LR sigue arriba: 0.404, significativamente mejor.",
        "pron": [("95", "NÁIN-ti FÁIV"), ("confidence interval", "CÓN-fi-dens ÍN-ter-val"),
                 ("significantly", "sig-NÍ-fi-cant-li"), ("validation loss", "va-li-DÉI-shon LOS"),
                 ("clearly", "CLÍR-li"), ("level", "LÉ-vel")],
    },
    {
        "n": 10, "titulo": "¿Por qué gana?", "quien": E1,
        "titulo_en": "Why does a linear model win here?",
        "en": [
            "Thank you. | Why does a simple linear model | win here?",
            "**First**, the data is small for deep models: | about ten thousand rows.",
            "**Second**, the one-day label is very noisy.",
            "**Third**, our features | already summarize many days, | so a linear model can use them well.",
            "We also have **limitations**: | we test only one year, | we do not include transaction costs, | and we use only seven stocks | from one sector.",
        ],
        "es": [
            "Gracias. ¿Por qué gana aquí un modelo lineal simple?",
            "Primero, los datos son pocos para modelos profundos: unas diez mil filas.",
            "Segundo, la etiqueta de un día tiene mucho ruido.",
            "Tercero, nuestras variables ya resumen muchos días, así que un modelo lineal las aprovecha bien.",
            "También tenemos limitaciones: probamos un solo año, no incluimos costos de transacción y usamos solo siete acciones de un sector.",
        ],
        "en_uno": [
            "So, why does a simple linear model | win here?",
            "**First**, the data is small for deep models: | about ten thousand rows.",
            "**Second**, the one-day label is very noisy.",
            "**Third**, our features | already summarize many days, | so a linear model can use them well.",
            "We also have **limitations**: | we test only one year, | we do not include transaction costs, | and we use only seven stocks | from one sector.",
        ],
        "es_uno": [
            "Entonces, ¿por qué gana aquí un modelo lineal simple?",
            "Primero, los datos son pocos para modelos profundos: unas diez mil filas.",
            "Segundo, la etiqueta de un día tiene mucho ruido.",
            "Tercero, nuestras variables ya resumen muchos días, así que un modelo lineal las aprovecha bien.",
            "También tenemos limitaciones: probamos un solo año, no incluimos costos de transacción y usamos solo siete acciones de un sector.",
        ],
        "idea": "Pocos datos, etiqueta con ruido, variables que ya resumen. Y nuestras limitaciones.",
        "pron": [("linear", "LÍ-ni-ar"), ("thousand", "ZÁU-sand"), ("noisy", "NÓI-si"), ("summarize", "SÁ-ma-rais"),
                 ("limitations", "li-mi-TÉI-shons"), ("transaction costs", "tran-SÁC-shon COSTS"), ("sector", "SÉC-tor")],
    },
    {
        "n": 11, "titulo": "Cierre", "quien": E1,
        "titulo_en": "Takeaways · Thank you · Questions?",
        "en": [
            "To finish, **three messages**.",
            "**One:** a well-regularized logistic regression | is a strong and cheap baseline.",
            "**Two:** do not filter the features | before training.",
            "**Three:** the stock matters | more than the model.",
            "Our code and data are public. | **Thank you.** | We are happy to answer your questions.",
        ],
        "es": [
            "Para terminar, tres mensajes.",
            "Uno: una regresión logística bien regularizada es un punto de partida fuerte y barato.",
            "Dos: no filtren las variables antes de entrenar.",
            "Tres: la acción importa más que el modelo.",
            "Nuestro código y datos son públicos. Gracias. Con gusto respondemos sus preguntas.",
        ],
        "en_uno": [
            "To finish, **three messages**.",
            "**One:** a well-regularized logistic regression | is a strong and cheap baseline.",
            "**Two:** do not filter the features | before training.",
            "**Three:** the stock matters | more than the model.",
            "Our code and data are public. | **Thank you.** | I am happy to answer your questions.",
        ],
        "es_uno": [
            "Para terminar, tres mensajes.",
            "Uno: una regresión logística bien regularizada es un punto de partida fuerte y barato.",
            "Dos: no filtren las variables antes de entrenar.",
            "Tres: la acción importa más que el modelo.",
            "Nuestro código y datos son públicos. Gracias. Con gusto respondo sus preguntas.",
        ],
        "idea": "Los tres mensajes y gracias. Deja esta diapositiva puesta durante las preguntas.",
        "pron": [("messages", "MÉ-si-yis"), ("well-regularized", "uel RÉ-guiu-la-raisd"), ("cheap", "CHIIP"),
                 ("baseline", "BÉIS-lain"), ("public", "PÁ-blic"), ("questions", "CUÉS-chons")],
    },
]


def guion(modo: str = "uno") -> list[dict]:
    """Las diapositivas ya resueltas para `modo` ("uno" o "dos"), con su minuto de inicio y de fin."""
    if modo not in ("uno", "dos"):
        raise ValueError(modo)
    out, t = [], 0
    for d in DIAPOSITIVAS:
        r = dict(d)
        if modo == "uno":
            r["en"] = d.get("en_uno", d["en"])
            r["es"] = d.get("es_uno", d["es"])
            r["pase"] = r["pase_es"] = None
            r["quien"] = None
        r["seg"] = segundos(r["en"] + ([r["pase"]] if r.get("pase") else []))
        r["ini"], r["fin"] = t, t + r["seg"]
        t = r["fin"]
        out.append(r)
    return out


# Diapositivas de respaldo: solo se muestran si una pregunta lo pide.
RESPALDO = {
    12: "Corrected protocol, full Table 6 (hyper-parameters, intervals, Sharpe).",
    13: "Since submission: six test years, transaction costs, unseen 2026 data.",
    14: "Benchmark tables 3–5 (global, economics, per-stock).",
    15: "Hyper-parameter search: trials and search space per model.",
}

PRONUNCIACION = [
    ("afternoon", "af-ter-NÚN"),
    ("logistic regression", "lo-YÍS-tic ri-GRÉ-shon"),
    ("benchmark", "BÉNCH-mark"),
    ("machine learning", "ma-SHÍN LÉR-ning"),
    ("deep networks", "DIP NÉT-uorks"),
    ("trading signals", "TRÉI-ding SÍG-nals"),
    ("macro-F1", "MÁ-cro ef-UÁN"),
    ("Sharpe ratio", "SHARP RÉI-shio"),
    ("profit factor", "PRÓ-fit FÁC-tor"),
    ("percent", "per-SÉNT"),
    ("percentile", "per-SÉN-tail"),
    ("volatility", "vo-la-TÍ-li-ti"),
    ("regularization", "re-guiu-la-ri-SÉI-shon"),
    ("confidence interval", "CÓN-fi-dens ÍN-ter-val"),
    ("significantly", "sig-NÍ-fi-cant-li"),
    ("validation loss", "va-li-DÉI-shon LOS"),
    ("XGBoost", "ex-yi-BÚST"),
    ("LSTM", "el-es-ti-ÉM"),
    ("CNN", "si-en-ÉN"),
    ("one-dimensional", "uán-di-MÉN-sho-nal"),
    ("hybrid", "JÁI-brid"),
    ("Optuna", "op-TÚ-na"),
    ("Yahoo Finance", "YÁ-ju FÁI-nans"),
    ("NVIDIA", "en-VÍ-dia"),
    ("reviewers", "ri-VIÚ-ers"),
    ("noisy", "NÓI-si"),
    ("baseline", "BÉIS-lain"),
    ("features", "FÍ-chers"),
    ("history", "JÍS-to-ri"),
    ("thousand", "ZÁU-sand"),
    ("2025", "tuén-ti tuén-ti FÁIV"),
    ("2024", "tuén-ti tuén-ti FOR"),
    ("0.404", "SÍ-ro point FOR SÍ-ro FOR"),
    ("1,736", "uán ZÁU-sand SÉ-ven JÁN-dred ZÉR-ti SIKS"),
    ("252", "tu JÁN-dred FÍF-ti TU"),
]

# Preguntas probables, agrupadas por tema (una tarjeta por tema).
#   claves    las palabras que hay que reconocer al oír la pregunta
#   a / a_es  respuesta corta en inglés sencillo y su traducción
#   quien     con dos expositores, quién la contesta (el otro puede completar)
#   respaldo  diapositiva que ayuda a responder (número + Enter)
TEMAS_PREGUNTAS = [
    ("A", "¿La señal es real?", [
        {"quien": E2, "claves": "signal · random · luck · efficient market",
         "q": "Is there a real signal, or is it random?",
         "q_es": "¿Hay señal real o es azar?",
         "a": "Yes, there is a signal, but it is small. Logistic regression gets 0.404. Random is 0.333. The confidence interval does not include 0.333. We do not say that you can make money with it.",
         "a_es": "Sí hay señal, pero es pequeña; el intervalo no incluye el azar. No decimos que se pueda ganar dinero con ella."},
        {"quien": E2, "claves": "overlap · intervals · significant", "respaldo": 12,
         "q": "The intervals overlap. Why do you say significant?",
         "q_es": "Los intervalos se enciman. ¿Por qué dicen que es significativo?",
         "a": "Because we test paired differences, on the same rows. Logistic regression minus each model has an interval that does not include zero. For example, plus 0.045 against XGBoost.",
         "a_es": "Porque probamos diferencias pareadas, en las mismas filas; el intervalo de la diferencia no incluye el cero."},
        {"quien": E2, "claves": "bootstrap · block · resamples",
         "q": "What kind of bootstrap did you use?",
         "q_es": "¿Qué bootstrap usaron?",
         "a": "A block bootstrap on the test rows: blocks of 20 rows and 2,000 resamples. We use blocks because the days are not independent.",
         "a_es": "Bootstrap de bloques: bloques de 20 filas y 2,000 remuestreos, porque los días no son independientes."},
    ]),
    ("B", "¿Por qué gana la LR?", [
        {"quien": E1, "claves": "why linear · deep networks · overfitting", "respaldo": 10,
         "q": "Why does a linear model beat deep networks?",
         "q_es": "¿Por qué un modelo lineal le gana a las redes?",
         "a": "The data is small for deep models, the one-day label is very noisy, and our features already summarize many days. The validation loss of the networks stays near the random level, and a small LSTM does the same as a big one.",
         "a_es": "Pocos datos, etiqueta con ruido y variables que ya resumen. La pérdida de validación se queda cerca del azar."},
        {"quien": E2, "claves": "Transformer · GRU · random forest · SVM · other models",
         "q": "Why not Transformers, GRU or other models?",
         "q_es": "¿Por qué no Transformers, GRU u otros modelos?",
         "a": "We did not test them. We chose a linear model, a tree model and three sequence networks. Transformers need much more data. In our tests, very different networks give the same result, so the limit is the data, not the architecture.",
         "a_es": "No los probamos. Los Transformers necesitan muchos más datos. Redes muy distintas dan lo mismo: el límite son los datos."},
        {"quien": E1, "claves": "elastic net · L2 · C · regularization", "respaldo": 15,
         "q": "Which regularization did you use?",
         "q_es": "¿Qué regularización usaron?",
         "a": "In Section 7 we use elastic net. In Section 8, Optuna could choose L1, L2 or elastic net. It chose L2 with very strong regularization: C equal to 0.000165.",
         "a_es": "Elastic net en la §7. En la §8 Optuna eligió L2 con regularización muy fuerte: C = 0.000165."},
    ]),
    ("C", "¿Fue justo?", [
        {"quien": E2, "claves": "fair · search · tuning · hyper-parameters", "respaldo": 15,
         "q": "Did the deep models get a fair hyper-parameter search?",
         "q_es": "¿Las redes tuvieron una búsqueda justa de hiperparámetros?",
         "a": "Yes. In Section 8 all models use the same Optuna sampler, the same decision year and the same test rows. The networks search 17 to 20 hyper-parameters. The gap is bigger, not smaller.",
         "a_es": "Sí: mismo muestreador, mismo año de decisión y mismas filas. Las redes buscan 17 a 20 hiperparámetros y la diferencia crece."},
        {"quien": E2, "claves": "look-back · window · test set · oracle",
         "q": "Was the look-back chosen on the test set?",
         "q_es": "¿La ventana se eligió con la prueba?",
         "a": "Yes, in Section 7, and we say it in the paper. It helps the networks, not logistic regression. Section 8 removes this problem.",
         "a_es": "Sí, en la §7, y el artículo lo dice. Favorece a las redes. La §8 lo quita."},
        {"quien": E1, "claves": "leakage · look-ahead · future data · scaler · bidirectional",
         "q": "Is there data leakage?",
         "q_es": "¿Hay fuga de datos?",
         "a": "The label thresholds use only past data, shifted by one day. The scalers are fitted on the training data. In Section 8, no decision uses 2025. And a bidirectional LSTM only reads a closed window of past days.",
         "a_es": "Umbrales con datos pasados, escaladores ajustados con entrenamiento, ninguna decisión con 2025. La LSTM bidireccional solo lee días pasados."},
    ]),
    ("D", "Limitaciones", [
        {"quien": E2, "claves": "one year · 2025 · special · walk-forward", "respaldo": 13,
         "q": "You test only one year. Is 2025 special?",
         "q_es": "Solo prueban un año. ¿2025 es especial?",
         "a": "It is our main limitation. 2025 is not an easy year: the return is below the median and the volatility is high. After the paper, we tested six years, 2020 to 2025. Logistic regression and XGBoost are similar, and both are better than the networks.",
         "a_es": "Es la limitación principal. Después del artículo probamos seis años: LR y XGBoost son parecidos y superan a las redes."},
        {"quien": E2, "claves": "costs · transaction · fees · slippage", "respaldo": 13,
         "q": "What about transaction costs?",
         "q_es": "¿Y los costos de transacción?",
         "a": "They are not in the paper. After the paper we tested 10 basis points. Logistic regression keeps a Sharpe ratio of 0.62. XGBoost goes to almost zero, because it trades more.",
         "a_es": "No están en el artículo. Con 10 puntos base la LR conserva Sharpe 0.62 y XGBoost cae casi a cero porque opera más."},
        {"quien": E1, "claves": "survivorship · bias · only tech · other markets",
         "q": "What about survivorship bias? Only seven tech stocks.",
         "q_es": "¿Y el sesgo de supervivencia? Solo siete acciones tecnológicas.",
         "a": "Yes, it is a limitation. We compare models on the same data. We do not say the results are true for the whole market.",
         "a_es": "Sí, es una limitación. Comparamos modelos con los mismos datos; no decimos que valga para todo el mercado."},
    ]),
    ("E", "Decisiones de diseño", [
        {"quien": E1, "claves": "accuracy · macro-F1 · why this metric",
         "q": "Why macro-F1 and not accuracy?",
         "q_es": "¿Por qué F1-macro y no accuracy?",
         "a": "If a model always says hold, the accuracy is about 40 percent. Macro-F1 gives the same weight to buy, hold and sell.",
         "a_es": "Si un modelo siempre dice mantener, la exactitud es de 40 %. F1-macro le da el mismo peso a las tres clases."},
        {"quien": E1, "claves": "one day · horizon · percentile · 30/70 · label",
         "q": "Why a one-day horizon and this label?",
         "q_es": "¿Por qué un horizonte de un día y esta etiqueta?",
         "a": "We want a daily signal, and one day is the most difficult case. The percentiles adapt to the volatility, so we do not choose a fixed threshold. Longer horizons are a different problem, for future work.",
         "a_es": "Queremos una señal diaria y es el caso más difícil. Los percentiles se adaptan a la volatilidad. Otros horizontes son trabajo futuro."},
        {"quien": E2, "claves": "global · per stock · one model",
         "q": "Global model or one model per stock?",
         "q_es": "¿Modelo global o uno por acción?",
         "a": "We tested both. The global model has seven times more data, and it is better or equal.",
         "a_es": "Probamos los dos. El global tiene siete veces más datos y es mejor o igual."},
    ]),
    ("F", "Uso y siguiente paso", [
        {"quien": E1, "claves": "trade · real money · profit · buy and hold",
         "q": "Can people use this to trade?",
         "q_es": "¿Se puede usar para invertir?",
         "a": "It is a comparison, not a trading system. We do not say that it beats the market. But for daily data, a simple regularized model is a good starting point.",
         "a_es": "Es una comparación, no un sistema de inversión. No decimos que le gane al mercado. Un modelo simple regularizado es un buen punto de partida."},
        {"quien": E1, "claves": "reproduce · code · data · GitHub",
         "q": "Can I reproduce your results?",
         "q_es": "¿Puedo reproducir sus resultados?",
         "a": "Yes. The data is free from Yahoo Finance. The code, the seeds and the library versions are public. The link is on this slide.",
         "a_es": "Sí. Datos gratis; código, semillas y versiones públicos. El enlace está en esta diapositiva."},
        {"quien": E1, "claves": "future work · next steps · what now",
         "q": "What is the next step?",
         "q_es": "¿Cuál es el siguiente paso?",
         "a": "We want more stocks and sectors, longer horizons, and richer data, like news. We already extended the test to six years and to 2026 data.",
         "a_es": "Más acciones y sectores, otros horizontes y datos más ricos. Ya lo extendimos a seis años y a datos de 2026."},
    ]),
]

PREGUNTAS = [p for _, _, ps in TEMAS_PREGUNTAS for p in ps]

# (inglés, español, cómo se dice, solo_dos)
FRASES_DE_APOYO = [
    ("Sorry, could you repeat the question, please?", "¿Perdón, puede repetir la pregunta, por favor?", "SÓ-ri, cud yu ri-PÍT de CUÉS-chon, plis?", False),
    ("Could you speak a little more slowly, please?", "¿Podría hablar un poco más despacio?", "cud yu SPIK a LÍ-tel mor SLÓU-li, plis?", False),
    ("You are asking about transaction costs, right?", "¿Pregunta por los costos, verdad? (repite la palabra clave para ganar tiempo)", "yu ar ÁS-king a-BÁUT …, ráit?", False),
    ("Thank you for the question.", "Gracias por la pregunta.", "ZÉNK yu for de CUÉS-chon.", False),
    ("That is a good question. My colleague will answer.", "Buena pregunta. Mi colega va a responder.", "dat is a gud CUÉS-chon. mai CÓ-lig uil ÁN-ser.", True),
    ("We have more details in the paper.", "Tenemos más detalles en el artículo.", "ui jav mor DÍ-teils in de PÉI-per.", False),
    ("We did not test that. It is future work.", "No lo probamos. Es trabajo futuro.", "ui did not test dat. it is FIÚ-cher uork.", False),
    ("Let me show you a backup slide.", "Le muestro una diapositiva de respaldo.", "let mi SHOU yu a BÁK-ap slaid.", False),
    ("We can talk more after the session.", "Podemos platicar más al final de la sesión.", "ui can tok mor ÁF-ter de SÉ-shon.", False),
]

# Lo que puede decir el moderador durante la exposición, y qué hacer.
MODERADOR = [
    ("“Two minutes left.”", "Salta lo marcado con ✂ y sigue."),
    ("“Please wrap up.” / “Please finish.”", "Escribe 11 + Enter y di los tres mensajes."),
    ("“You only have five minutes.” / “We are late.”", "Usa la tarjeta de la versión corta."),
    ("“Time is up.”", "Di “Thank you” y termina."),
]

# Cifras para contestar preguntas. Todas salen del artículo, salvo el último bloque.
CIFRAS = [
    ("Sección 7: el benchmark (120 corridas)", [
        ("Azar (random)", "0.333"),
        ("LR global", "A 0.411 · B 0.385 · C 0.401 · promedio 0.399"),
        ("XGBoost global", "A 0.396 · B 0.386 · C 0.373 · promedio 0.385"),
        ("Simulación de LR en B", "Sharpe +0.76 · profit factor 1.21"),
        ("Filtros de variables", "11 de 15 casos: mejor las 61"),
        ("Variación del Sharpe", "acción 15.5 % · modelo 3.4 % · partición 7.0 % · resto 74.1 %"),
    ]),
    ("Sección 8: el protocolo corregido (partición B)", [
        ("LR", "0.404 [0.379, 0.428] · Sharpe +0.895"),
        ("Los otros", "CNN-LSTM 0.372 · LSTM 0.369 · XGBoost 0.359 · CNN 0.359"),
        ("Diferencia de LR", "+0.045 XGBoost · +0.035 LSTM · +0.031 CNN-LSTM · +0.045 CNN"),
        ("Búsqueda con Optuna", "150 ensayos LR y XGBoost · 80 ensayos cada red · 17–20 hiperparámetros en las redes, 9 XGBoost, 5 LR"),
        ("LR elegida", "L2, C = 0.000165"),
        ("Redes", "pérdida de validación ≈ ln 3 = 1.099 · LSTM de 592 k a 10 k parámetros: igual"),
    ]),
    ("Datos", [
        ("Tamaño", "7 acciones · 3,017 días cada una · 61 variables · ≈ 10,500 filas de entrenamiento en B · 1,736 filas de prueba"),
        ("Particiones", "entrenan 10, 6 o 4 años · validan 2024 · prueban 2025"),
    ]),
    ("Después del artículo (empieza con: Since we submitted the paper…)", [
        ("Seis años, 2020–2025", "LR 0.360 · XGBoost 0.356, sin diferencia significativa · redes 0.326–0.338"),
        ("Costos de 10 puntos base", "Sharpe LR +0.89 → +0.62 · XGBoost +0.46 → +0.01"),
        ("Datos no vistos, 2026", "LR primera con 0.346; sin diferencia significativa con XGBoost, LSTM y CNN-LSTM"),
    ]),
]

# Versión de 2 minutos, por si la sesión va retrasada y el moderador pide
# recortar. La dice una sola persona y solo se muestran cuatro diapositivas
# (en PowerPoint: escribir el número y Enter). ~170 palabras a ritmo lento.
VERSION_CORTA = [
    {
        "n": 1,
        "en": [
            f"Good afternoon. My name is {NOMBRE_1}, | from the Instituto Politécnico Nacional, in Mexico City.",
            "Our question is simple: | for daily trading signals, | do deep networks beat simple models?",
            "Each day we predict one signal, | buy, hold or sell, | for seven big tech stocks, | with free data from Yahoo Finance.",
        ],
        "es": [
            f"Buenas tardes. Me llamo {NOMBRE_1}, del Instituto Politécnico Nacional, en la Ciudad de México.",
            "Nuestra pregunta es simple: para señales diarias de trading, ¿las redes profundas le ganan a los modelos simples?",
            "Cada día predecimos una señal, comprar, mantener o vender, para siete acciones grandes de tecnología, con datos gratis de Yahoo Finance.",
        ],
    },
    {
        "n": 5,
        "en": [
            "We compared five models: | logistic regression, XGBoost, LSTM, CNN and CNN-LSTM. | Same data, same test year: 2025.",
            "Logistic regression was the best on average, | with a macro F1 of **zero point three nine nine**. {0.399}",
        ],
        "es": [
            "Comparamos cinco modelos: regresión logística, XGBoost, LSTM, CNN y CNN-LSTM. Mismos datos, mismo año de prueba: 2025.",
            "La regresión logística fue la mejor en promedio, con un F1-macro de 0.399.",
        ],
    },
    {
        "n": 9,
        "en": [
            "Then we gave all five models | the same hyper-parameter search tool. | The gap did not close.",
            "Logistic regression got **zero point four zero four**, {0.404} | significantly better than the other four models.",
        ],
        "es": [
            "Después les dimos a los cinco modelos la misma herramienta de búsqueda de hiperparámetros. La diferencia no se cerró.",
            "La regresión logística obtuvo 0.404, significativamente mejor que los otros cuatro modelos.",
        ],
    },
    {
        "n": 11,
        "en": [
            "Three messages. | **One:** a simple linear model is hard to beat here.",
            "**Two:** do not filter the features before training. | **Three:** the stock matters more than the model.",
            "**Thank you.** Questions?",
        ],
        "es": [
            "Tres mensajes. Uno: aquí es difícil ganarle a un modelo lineal simple.",
            "Dos: no filtren las variables antes de entrenar. Tres: la acción importa más que el modelo.",
            "Gracias. ¿Preguntas?",
        ],
    },
]

"""Diagramas del sistema (capítulo 5): D01 a D07."""

from __future__ import annotations

from estilo import (AMBER, AMBER_L, BLUE, BLUE_D, BLUE_L, BLUE_M, FRAME, GRAY, GRAY_L, GREEN,
                    GREEN_L, INK, LINE, MONO, MUTED, ORANGE, ORANGE_L, RED, RED_L, SLATE,
                    SLATE_L, WHITE, Lienzo, caja, chip, circulo, etiqueta, flecha, linea, marco,
                    rect, texto)


# ---------------------------------------------------------------------------
# D01 · Arquitectura general
# ---------------------------------------------------------------------------
def d01_arquitectura() -> Lienzo:
    c = Lienzo(1600, 1000, "Arquitectura del sistema")

    # Banda superior: investigación
    marco(c, 25, 30, 1550, 270, "INVESTIGACIÓN · fuera de línea (una vez, con GPU)")
    y, h = 95, 150
    cajas = [
        (45, 220, "Yahoo Finance", ["OHLCV diario 2013–2025", "7 acciones · SPY · VIX"], GRAY_L, LINE, None),
        (300, 280, "01_build_raw_dataset.py", ["61 características", "+ etiqueta 30/70", "7 parquet · 21 119 filas"], SLATE_L, SLATE, "scripts_v1/"),
        (615, 320, "Etapas 3 a 6", ["5 modelos en igualdad de condiciones", "Optuna · intervalos · año por año", "gana la Regresión Logística"], SLATE_L, SLATE, "scripts_opt/"),
        (970, 290, "entrenar_produccion.py", ["LR L2, C = 0.000165", "76 variables · mantener × 0.90", "datos 2018–2025"], SLATE_L, SLATE, "scripts_opt/"),
        (1295, 260, "Modelo (.pkl)", ["modelo + escalador", "+ lista de 76 variables", "+ metadatos y versión"], ORANGE_L, ORANGE, "api/ml/artifacts/"),
    ]
    for x, w, t, ls, f, s, sobre in cajas:
        caja(c, x, y, w, h, t, ls, fill=f, stroke=s, sobre=sobre, tsize=16, lsize=14)
    for (x1, w1, *_), (x2, *_r) in zip(cajas, cajas[1:]):
        flecha(c, [(x1 + w1, y + h / 2), (x2, y + h / 2)])

    # Banda inferior: plataforma
    marco(c, 25, 360, 1550, 615, "PLATAFORMA · en línea (Render, cada día hábil)")

    caja(c, 50, 440, 270, 120, "Yahoo Finance", ["~3 años de OHLCV", "7 acciones · SPY · VIX"], fill=GRAY_L)
    caja(c, 1265, 440, 290, 130, "SQLite · 4 tablas", ["assets · ohlcv_daily", "predictions · metrics", "registro reconstruible"],
         fill=WHITE, stroke=BLUE)

    # API
    rect(c, 375, 410, 830, 420, fill=BLUE_L, stroke=BLUE, sw=2)
    texto(c, 790, 443, "API Flask · Docker + gunicorn (1 worker)", size=17, color=BLUE_D, weight="bold", anchor="middle")
    cols = [400, 665, 930]
    cw = 250
    fila1 = [
        ("Programador", ["16:30 Nueva York, lun–vie", "al arrancar · reintento 2 min"]),
        ("ml/features.py", ["61 + 15 = 76 características", "mismo código del entrenamiento"]),
        ("ml/model.py", ["LR-v8-interactions-holdw090", "3 probabilidades por día"]),
    ]
    fila2 = [
        ("ml/target.py", ["etiqueta real (día siguiente)", "acierto o «pendiente»"]),
        ("Métricas", ["ventanas de 30, 60 y 90 días", "F1, Sharpe, win rate, capital"]),
        ("Caché en memoria", ["las respuestas salen de aquí", "candado: una actualización"]),
    ]
    for (t, ls), x in zip(fila1, cols):
        caja(c, x, 465, cw, 100, t, ls, fill=WHITE, stroke=BLUE_M, tsize=15, lsize=13)
    for (t, ls), x in zip(fila2, cols):
        caja(c, x, 585, cw, 100, t, ls, fill=WHITE, stroke=BLUE_M, tsize=15, lsize=13)
    caja(c, 400, 705, 780, 100, "API REST",
         ["9 rutas GET + POST /admin/refresh", "respuestas {success, data} · CORS habilitado"],
         fill=WHITE, stroke=BLUE_M, tsize=15, lsize=13)

    caja(c, 375, 870, 830, 90, "Aplicación web · sitio estático",
         ["React 18 + TypeScript + Vite + Tailwind + Recharts",
          "Hoy · Detalle · Resultados · Modelos · Aprende · Ayuda · Acerca de"],
         fill=BLUE_L, stroke=BLUE, tsize=16, lsize=13.5)
    caja(c, 1265, 875, 290, 80, "Usuario", ["navegador o celular"], fill=WHITE)

    # Flechas de la plataforma
    flecha(c, [(320, 500), (375, 500)])
    etiqueta(c, 347, 490, "descarga", size=12)
    flecha(c, [(1205, 505), (1265, 505)], doble=True)
    etiqueta(c, 1235, 495, "upsert", size=12)
    flecha(c, [(790, 830), (790, 870)])
    etiqueta(c, 860, 855, "HTTP · JSON", size=12)
    flecha(c, [(1205, 915), (1265, 915)], doble=True)

    # Del artefacto a la API
    flecha(c, [(1425, 245), (1425, 330), (1100, 330), (1100, 410)], color=ORANGE, sw=2.2)
    etiqueta(c, 1262, 322, "se carga al arrancar (lo único que pasa de un lado al otro)", size=12.5, color=ORANGE)
    return c


# ---------------------------------------------------------------------------
# D02 · De la investigación al modelo en producción
# ---------------------------------------------------------------------------
def d02_investigacion_a_produccion() -> Lienzo:
    c = Lienzo(1600, 900, "Del dataset al modelo en producción")

    # Fila 1: datos
    texto(c, 40, 50, "1 · Datos", size=15, color=MUTED, weight="bold")
    caja(c, 40, 70, 260, 120, "Yahoo Finance", ["desde 2013-01-01", "auto_adjust = True"], fill=GRAY_L)
    caja(c, 360, 70, 420, 120, "01_build_raw_dataset.py",
         ["61 características en 9 familias", "etiqueta 30/70 (252 días, shift 1) · r_forward"],
         fill=SLATE_L, stroke=SLATE, sobre="scripts_v1/")
    caja(c, 840, 70, 420, 120, "7 archivos parquet",
         ["2013-12-31 a 2025-12-29 · 21 119 filas", "2026 aparte, solo para la prueba ciega"],
         fill=WHITE, stroke=SLATE, sobre="tesis_ml_stocks/01_raw_datasets/")
    caja(c, 1320, 70, 240, 120, "Etapas 1–2", ["scripts_v1/02–08", "scripts_opt/opt_*.py", "(antecedente)"],
         fill=GRAY_L, stroke=GRAY, dash="6 5", tsize=15, lsize=13)
    flecha(c, [(300, 130), (360, 130)])
    flecha(c, [(780, 130), (840, 130)])

    # Fila 2: etapas
    texto(c, 40, 265, "2 · Comparación y decisiones (scripts_opt/)", size=15, color=MUTED, weight="bold")
    y, h, w = 285, 250, 340
    xs = [40, 425, 810, 1195]
    etapas = [
        ("Etapa 3", "Igualdad de condiciones", ["common_v4.py · train_all_v4.py", "61 variables para los cinco", "A/B/C con prueba 2025", "120 corridas"], SLATE_L, SLATE, "paper §3–§7"),
        ("Etapa 4", "Protocolo final", ["common_v5.py · run_v5.py", "dev/final: nada con la prueba", "Optuna para los cinco", "IC bootstrap · costos · año por año"], ORANGE_L, ORANGE, "paper §8 · resultado principal"),
        ("Etapa 5", "Búsqueda de mejoras", ["via7_refinamiento.py", "via8_dataset.py", "calibración, mezclas, SWA…", "se adoptan 15 interacciones"], SLATE_L, SLATE, None),
        ("Etapa 6", "Modelo de la plataforma", ["ajuste_hold_rolling.py", "peso de mantener × 0.90", "global contra por acción", "prueba ciega 2026"], SLATE_L, SLATE, None),
    ]
    for x, (n, t, ls, f, s, tag) in zip(xs, etapas):
        caja(c, x, y, w, h, t, ls, fill=f, stroke=s, sobre=n, sobre_color=s, tsize=17, lsize=14,
             sw=2.4 if n == "Etapa 4" else 1.5)
        if tag:
            chip(c, x + w / 2, y + h - 2, tag, fill=ORANGE if n == "Etapa 4" else SLATE, color=WHITE, size=12, anchor="middle")
    for x1, x2 in zip(xs, xs[1:]):
        flecha(c, [(x1 + w, y + h / 2), (x2, y + h / 2)])
    flecha(c, [(1050, 190), (1050, 240), (210, 240), (210, 285)])
    etiqueta(c, 630, 245, "mismos datos para todas las etapas", size=12.5)

    # Fila 3: producción
    texto(c, 40, 640, "3 · Producción", size=15, color=MUTED, weight="bold")
    caja(c, 40, 660, 430, 170, "entrenar_produccion.py",
         ["7 acciones, 2018–2025 (14 063 filas)", "+ 15 interacciones · RobustScaler global",
          "pesos balanceados, mantener × 0.90", "LogisticRegression(L2, C = 0.000165)"],
         fill=SLATE_L, stroke=SLATE, sobre="scripts_opt/", tsize=17)
    caja(c, 560, 660, 460, 170, "lr_elasticnet_global_expB.pkl",
         ["modelo + escalador + 76 variables", "metadatos: versión, rango, evidencia",
          "+ .metrics.json · interaction_pairs.json", "(el nombre «elasticnet» es histórico)"],
         fill=ORANGE_L, stroke=ORANGE, sobre="api/ml/artifacts/", tsize=16)
    caja(c, 1110, 660, 450, 170, "API (api/ml/model.py)",
         ["carga el archivo una sola vez", "verifica que estén las 76 variables",
          "MODEL_VERSION = LR-v8-interactions-holdw090", "una prueba exige que coincidan"],
         fill=BLUE_L, stroke=BLUE, tsize=17)
    flecha(c, [(1365, 535), (1365, 600), (255, 600), (255, 660)])
    etiqueta(c, 810, 605, "configuración elegida", size=12.5)
    flecha(c, [(470, 745), (560, 745)], color=ORANGE, sw=2)
    flecha(c, [(1020, 745), (1110, 745)], color=ORANGE, sw=2)
    texto(c, 800, 870, "Para cambiar de modelo basta sustituir el .pkl y actualizar MODEL_VERSION; la API no cambia.",
          size=13.5, color=MUTED, anchor="middle")
    return c


# ---------------------------------------------------------------------------
# D03 · Actualización diaria
# ---------------------------------------------------------------------------
def d03_actualizacion_diaria() -> Lienzo:
    c = Lienzo(1500, 1240, "Actualización diaria dentro de la API")

    # Disparadores
    texto(c, 750, 40, "Cuándo corre", size=15, color=MUTED, weight="bold", anchor="middle")
    disp = ["Al arrancar el servidor", "16:30 Nueva York, lun–vie", "Cada 2 min si falta una acción", "POST /admin/refresh"]
    xs = [180, 470, 760, 1050]
    for x, s in zip(xs, disp):
        caja(c, x, 60, 270, 56, s, (), fill=BLUE_L, stroke=BLUE, tsize=14, rx=28)
        flecha(c, [(x + 135, 116), (x + 135, 140), (750, 140), (750, 165)], cabeza=(x == xs[0]))
    caja(c, 520, 165, 460, 60, "initialize_data()", ["un candado evita dos actualizaciones a la vez"],
         fill=WHITE, stroke=BLUE, tsize=15, lsize=12.5, mono_titulo=True)

    pasos = [
        ("1", "Descargar ~3 años", "7 acciones + SPY + VIX con yfinance · 3 reintentos por descarga"),
        ("2", "¿El mercado sigue abierto?", "sí → se descarta la vela del día: su precio todavía no es un cierre"),
        ("3", "Calcular 76 características", "ml/features.py: 61 base + 15 interacciones, mismo código del entrenamiento"),
        ("4", "Predecir", "ml/model.py: 3 probabilidades por día · la recomendación es la más alta"),
        ("5", "Evaluar", "ml/target.py: etiqueta real del día siguiente · el último día queda «pendiente»"),
        ("6", "Calcular métricas", "ventanas de 30, 60 y 90 días por acción (misma definición que la tesis)"),
        ("7", "Guardar", "caché en memoria + upsert en SQLite (una transacción por acción)"),
        ("8", "Servir", "GET /stocks, /stocks/:s/history, /metrics… responden desde la caché"),
    ]
    x, w, h, gap = 330, 840, 96, 28
    y = 260
    for i, (n, t, d) in enumerate(pasos):
        rect(c, x, y, w, h, fill=WHITE if n not in ("7", "8") else BLUE_L, stroke=BLUE if n in ("7", "8") else LINE)
        circulo(c, x + 48, y + h / 2, 22, BLUE)
        texto(c, x + 48, y + h / 2 + 6, n, size=17, color=WHITE, weight="bold", anchor="middle")
        texto(c, x + 90, y + 40, t, size=17, weight="bold", maxw=w - 110)
        texto(c, x + 90, y + 68, d, size=14, color=MUTED, maxw=w - 110)
        if i < len(pasos) - 1:
            flecha(c, [(x + w / 2, y + h), (x + w / 2, y + h + gap)])
        y += h + gap
    flecha(c, [(750, 225), (750, 260)])

    # Notas laterales
    caja(c, 30, 384, 270, 220, "Por qué todo y no solo el día nuevo",
         ["cuesta segundos de cómputo", "todo lo mostrado sale", "del modelo vigente",
          "si se reentrena, la historia", "se actualiza sola", "la base se puede", "reconstruir siempre"],
         fill=SLATE_L, stroke=SLATE, tsize=14, lsize=13.5)
    caja(c, 1200, 384, 270, 330, "Si algo falla",
         ["una acción falla → se omite", "y se reintenta cada 2 min", "",
          "SPY o VIX fallan → se omiten", "todas (sin contexto no hay", "características válidas)", "",
          "la base falla → rollback de", "esa acción; se sirve desde", "memoria", "", "nunca se inventan datos"],
         fill=AMBER_L, stroke=AMBER, tsize=14, lsize=13.5)
    return c


# ---------------------------------------------------------------------------
# D04 · Modelo entidad-relación
# ---------------------------------------------------------------------------
def _tabla(c: Lienzo, x, y, w, nombre, filas, color=BLUE) -> float:
    """Dibuja una tabla de base de datos. Devuelve su alto."""
    hh, rh = 44, 30
    h = hh + rh * len(filas) + 8
    rect(c, x, y, w, h, fill=WHITE, stroke=color, sw=2, rx=10)
    c.add(f'<path d="M{x},{y + hh} L{x},{y + 10} Q{x},{y} {x + 10},{y} L{x + w - 10},{y} '
          f'Q{x + w},{y} {x + w},{y + 10} L{x + w},{y + hh} Z" fill="{color}"/>')
    texto(c, x + w / 2, y + 29, nombre, size=17, color=WHITE, weight="bold", anchor="middle", family=MONO)
    yy = y + hh
    for i, (col, tipo) in enumerate(filas):
        if i % 2 == 1:
            c.add(f'<rect x="{x + 1.5}" y="{yy}" width="{w - 3}" height="{rh}" fill="{GRAY_L}"/>')
        texto(c, x + 14, yy + 20, col, size=13.5, family=MONO, maxw=w * 0.6)
        texto(c, x + w - 14, yy + 20, tipo, size=12.5, color=MUTED, anchor="end")
        yy += rh
    return h


def d04_entidad_relacion() -> Lienzo:
    c = Lienzo(1600, 900, "Modelo entidad-relación")
    ha = _tabla(c, 60, 330, 300, "assets", [
        ("id", "PK"), ("ticker", "único"), ("name", "texto"), ("sector", "texto"), ("industry", "texto")])
    ho = _tabla(c, 560, 40, 430, "ohlcv_daily", [
        ("id", "PK"), ("asset_id", "FK → assets.id"), ("date", "fecha"),
        ("open, high, low, close", "numérico"), ("volume", "entero"), ("(asset_id, date)", "único")])
    hp = _tabla(c, 560, 330, 430, "predictions", [
        ("id", "PK"), ("asset_id", "FK → assets.id"), ("date", "fecha del cierre"),
        ("signal", "buy / hold / sell"), ("prob_buy, prob_hold, prob_sell", "numérico"),
        ("confidence", "derivada"), ("actual_price", "derivada"),
        ("correct", "0 / 1 · nulo = pendiente"), ("model_version", "texto"), ("created_at", "UTC"),
        ("(asset_id, date)", "único")])
    hm = _tabla(c, 1100, 330, 450, "metrics", [
        ("id", "PK"), ("asset_id", "FK → assets.id"), ("window_days", "30 / 60 / 90"),
        ("model_version", "texto"), ("accuracy, f1_macro, f1_buy, f1_sell", "clasificación"),
        ("cumulative_return, return_vs_bh", "estrategia"), ("sharpe_ratio, max_drawdown", "estrategia"),
        ("win_rate, profit_factor, number_of_trades", ""), ("exposure, final_capital", "estrategia"),
        ("signal_buy/hold/sell_pct", "distribución"), ("updated_at", "UTC"),
        ("(asset_id, window_days)", "único")])

    def card(x1, y1, x2, y2, pts):
        flecha(c, pts, cabeza=False, color=BLUE, sw=2)
        texto(c, x1, y1, "1", size=14, color=BLUE_D, weight="bold")
        texto(c, x2, y2, "N", size=14, color=BLUE_D, weight="bold")

    card(372, 418, 535, 146, [(360, 430), (460, 430), (460, 160), (560, 160)])
    card(372, 472, 535, 520, [(360, 485), (560, 485)])
    card(372, 525, 1075, 520, [(360, 540), (450, 540), (450, 860), (1060, 860), (1060, 500), (1100, 500)])

    caja(c, 1100, 40, 450, 250, "Integridad", [
        "llaves foráneas hacia assets (1 : N)",
        "restricciones únicas: sin duplicados + índices",
        "upsert: recalcular no duplica filas",
        "borrado en cascada desde assets",
        "columnas derivadas a propósito: registro",
        "de lo que la plataforma calculó y mostró",
        "funciona igual en PostgreSQL (DATABASE_URL)"],
        fill=SLATE_L, stroke=SLATE, align="left", tsize=15, lsize=13.5)
    return c


# ---------------------------------------------------------------------------
# D05 · Mapa de pantallas
# ---------------------------------------------------------------------------
def d05_pantallas() -> Lienzo:
    c = Lienzo(1600, 1010, "Pantallas de la aplicación web")
    rect(c, 30, 25, 1540, 64, fill=WHITE, stroke=FRAME, rx=12)
    texto(c, 55, 64, "Señales diarias · Magnificent 7", size=17, weight="bold")
    x = 520
    for s in ["Hoy", "Resultados", "Modelos", "Aprende", "Ayuda", "Acerca de"]:
        w = chip(c, x, 43, s, fill=BLUE_L if s != "Hoy" else BLUE, color=BLUE_D if s != "Hoy" else WHITE, size=14)
        x += w + 14
    texto(c, 1545, 64, "tema claro / oscuro", size=13, color=MUTED, anchor="end")

    tarjetas = [
        ("/", "Hoy", ["una tarjeta por empresa", "recomendación + frase corta", "«Podría subir / bajar»,", "«Mejor esperar»", "precio y seguridad en palabras", "para qué sesión es", "modelo elegido → «Modelos»"], ["GET /stocks", "GET /market-status"]),
        ("/stock/:symbol", "Detalle", ["recomendación y seguridad", "las 3 probabilidades", "precio con un punto por día", "«¿Qué habría pasado con $1,000?»", "aciertos y ganancia", "últimas 10 recomendaciones", "ventanas 30 / 60 / 90 días"], ["GET /stocks/:s", ".../history", ".../metrics"]),
        ("/performance", "Resultados", ["resumen de las 7 empresas", "ganancia contra comprar", "y esperar cada acción", "F1 por empresa contra el azar", "tabla ordenable con unidades", "ventanas 30 / 60 / 90 días"], ["GET /metrics"]),
        ("/modelos", "Modelos", ["modelo elegido y por qué", "igualdad de condiciones", "prueba 2025 (A / B / C)", "intervalos · año por año", "prueba ciega 2026", "dinero con y sin comisión", "global contra por acción", "multicolinealidad"], ["comparacion_modelos.json"]),
        ("/aprende", "Aprende", ["qué es comprar, vender en corto", "y mantener (un solo día)", "barra: mueve el precio y ve", "qué pasa con $1,000", "venta en corto en 4 pasos", "juego con los últimos", "30 días reales"], ["GET /stocks/:s/history"]),
        ("/ayuda", "Ayuda", ["guía rápida por pantalla", "escala de seguridad", "cuándo se actualiza", "glosario buscable", "por categorías", "cada «?» lleva aquí"], []),
        ("/about", "Acerca de", ["descripción y metodología", "ficha del modelo leída", "de la API", "aviso legal y créditos"], ["GET /model"]),
    ]
    w, h = 360, 400
    pos = [(30, 120), (423, 120), (816, 120), (1209, 120), (30, 560), (423, 560), (816, 560)]
    for (ruta, nombre, ls, eps), (x, y) in zip(tarjetas, pos):
        principal = nombre in ("Hoy", "Detalle", "Modelos")
        rect(c, x, y, w, h, fill=WHITE, stroke=BLUE if principal else FRAME, sw=2 if principal else 1.5, rx=14)
        chip(c, x + 18, y + 18, ruta, fill=GRAY_L, color=SLATE, size=12, mono=True, bold=False)
        texto(c, x + 20, y + 78, nombre, size=21, weight="bold", color=BLUE_D if principal else INK)
        yy = y + 112
        for s in ls:
            texto(c, x + 22, yy, s, size=14, color=INK, maxw=w - 40)
            yy += 25
        yy = y + h - 22
        for e in reversed(eps):
            chip(c, x + 18, yy - 18, e, fill=BLUE_L, color=BLUE_D, size=11.5, mono=True, bold=False)
            yy -= 30
    flecha(c, [(390, 330), (423, 330)], color=BLUE, sw=2)
    etiqueta(c, 406, 318, "clic", size=12, color=BLUE)

    caja(c, 1209, 560, 360, 400, "Decisiones de diseño", [
        "seguridad en palabras:", "«Nada / Poco / Medianamente", "segura» (37 / 38 / 42 de 100)", "",
        "verde comprar · rojo vender ·", "ámbar mantener; seguridad en azul", "",
        "ejes con título y unidades", "dinero además de porcentaje", "",
        "sin datos fijos ni simulados", "aviso legal: no es asesoría"],
        fill=SLATE_L, stroke=SLATE, align="left", tsize=17, lsize=14)
    return c


# ---------------------------------------------------------------------------
# D06 · Diagrama de secuencia
# ---------------------------------------------------------------------------
def d06_secuencia() -> Lienzo:
    c = Lienzo(1600, 1260, "Diagrama de secuencia")
    actores = [("Usuario", 140, GRAY_L, LINE), ("Aplicación web", 470, BLUE_L, BLUE),
               ("API Flask", 860, BLUE_L, BLUE), ("Caché + SQLite", 1180, WHITE, BLUE), ("Yahoo Finance", 1460, GRAY_L, LINE)]
    for n, x, f, s in actores:
        caja(c, x - 115, 30, 230, 60, n, (), fill=f, stroke=s, tsize=16)
        linea(c, x, 90, x, 1215, color=FRAME, sw=1.6, dash="6 6")
    ax = {n: x for n, x, *_ in actores}

    def banda(y, h, s):
        rect(c, 20, y, 1560, h, fill=GRAY_L, stroke="none", rx=10, opacity=0.6)
        texto(c, 34, y + 22, s, size=14, color=SLATE, weight="bold")

    def msg(a, b, y, s, respuesta=False, mono=True):
        x1, x2 = ax[a], ax[b]
        flecha(c, [(x1, y), (x2 + (-8 if x2 > x1 else 8), y)], dash="6 5" if respuesta else None,
               color=LINE if respuesta else BLUE, sw=1.8)
        etiqueta(c, (x1 + x2) / 2, y - 8, s, size=13, color=MUTED if respuesta else INK)

    def propio(a, y, s):
        x = ax[a]
        flecha(c, [(x, y), (x + 60, y), (x + 60, y + 26), (x + 8, y + 26)], color=BLUE)
        etiqueta(c, x + 70, y + 18, s, size=13, anchor="start", color=INK)

    banda(110, 230, "Actualización programada (16:30 Nueva York, al arrancar o con POST /admin/refresh)")
    msg("API Flask", "Yahoo Finance", 165, "descargar ~3 años: 7 acciones + SPY + VIX")
    msg("Yahoo Finance", "API Flask", 205, "OHLCV diario", respuesta=True)
    propio("API Flask", 225, "76 características · predicción · etiqueta · métricas")
    msg("API Flask", "Caché + SQLite", 300, "guardar en memoria + upsert")

    banda(360, 400, "Abrir «Hoy»")
    msg("Usuario", "Aplicación web", 415, "abre la página")
    msg("Aplicación web", "API Flask", 455, "GET /market-status")
    msg("API Flask", "Aplicación web", 490, "200 · sesión y horario", respuesta=True)
    msg("Aplicación web", "API Flask", 530, "GET /stocks")
    msg("API Flask", "Caché + SQLite", 555, "lee la caché", mono=False)
    msg("API Flask", "Aplicación web", 590, "200 · 7 recomendaciones", respuesta=True)
    rect(c, 300, 615, 720, 130, fill="none", stroke=AMBER, rx=8, dash="5 4")
    texto(c, 312, 637, "si la lista llega vacía (arranque en frío y Yahoo falló)", size=13, color=AMBER, weight="bold")
    msg("Aplicación web", "API Flask", 670, "POST /admin/refresh")
    msg("API Flask", "Aplicación web", 700, "200", respuesta=True)
    msg("Aplicación web", "API Flask", 730, "GET /stocks")

    banda(780, 300, "Abrir el detalle de una acción")
    msg("Usuario", "Aplicación web", 835, "clic en la tarjeta de AAPL")
    msg("Aplicación web", "API Flask", 875, "GET /stocks/AAPL")
    msg("Aplicación web", "API Flask", 915, "GET /stocks/AAPL/history?days=30")
    msg("Aplicación web", "API Flask", 955, "GET /stocks/AAPL/metrics?days=30")
    msg("API Flask", "Aplicación web", 995, "200 · JSON (desde la caché)", respuesta=True)
    msg("Aplicación web", "Usuario", 1040, "gráficas, aciertos y $1,000", respuesta=True)

    banda(1100, 100, "«Acerca de»")
    msg("Aplicación web", "API Flask", 1150, "GET /model")
    msg("API Flask", "Aplicación web", 1185, "200 · ficha leída del .pkl", respuesta=True)

    texto(c, 800, 1245, "No hay consulta periódica: la recomendación cambia una vez al día. En el plan gratuito, la primera carga después de 15 min sin tráfico tarda 20–40 s.",
          size=13, color=MUTED, anchor="middle")
    return c


# ---------------------------------------------------------------------------
# D07 · Despliegue
# ---------------------------------------------------------------------------
def d07_despliegue() -> Lienzo:
    c = Lienzo(1600, 880, "Despliegue en Render")
    caja(c, 30, 300, 300, 170, "GitHub", ["barudust/TT", "rama main", "render.yaml (Blueprint)"], fill=GRAY_L, tsize=18)
    caja(c, 30, 520, 300, 200, "Verificación", ["GET /health →", "stocksLoaded: 7", "", "GET /model →", "LR-v8-interactions-holdw090"],
         fill=WHITE, stroke=GREEN, tcolor=GREEN, tsize=15, lsize=13.5)
    flecha(c, [(330, 385), (400, 385)], sw=2.2)
    etiqueta(c, 365, 372, "push", size=12.5)

    marco(c, 400, 40, 820, 800, "RENDER · plan gratuito · despliegue automático")
    rect(c, 440, 95, 740, 370, fill=BLUE_L, stroke=BLUE, sw=2)
    texto(c, 465, 135, "tt-api · servicio web (Docker)", size=19, color=BLUE_D, weight="bold")
    ls = ["imagen python:3.13-slim · versiones fijas (scikit-learn 1.7.2)",
          "gunicorn --workers 1 --timeout 300 wsgi:app",
          "1 instancia: el programador de tareas vive en el proceso",
          "SQLite en /data: efímera, se reconstruye al arrancar",
          "variables: DATABASE_URL, REFRESH_HOUR = 16, REFRESH_MINUTE = 30",
          "ruta de salud: /health"]
    yy = 175
    for s in ls:
        texto(c, 470, yy, "• " + s, size=14.5, maxw=690)
        yy += 36
    chip(c, 470, 405, "https://tt-api-jc7n.onrender.com", fill=WHITE, color=BLUE_D, size=13, mono=True)

    rect(c, 440, 500, 740, 300, fill=BLUE_L, stroke=BLUE, sw=2)
    texto(c, 465, 540, "tt-frontend · sitio estático", size=19, color=BLUE_D, weight="bold")
    ls = ["compila: cd Frontend && npm ci && npm run build",
          "publica: Frontend/dist (siempre disponible, sin dormir)",
          "regla: /* → /index.html (navegación de React)",
          "VITE_API_URL = URL de tt-api (se fija en el panel)"]
    yy = 580
    for s in ls:
        texto(c, 470, yy, "• " + s, size=14.5, maxw=690)
        yy += 36
    chip(c, 470, 740, "https://tt-frontend-womf.onrender.com", fill=WHITE, color=BLUE_D, size=13, mono=True)

    caja(c, 1290, 150, 280, 110, "Yahoo Finance", ["datos diarios"], fill=GRAY_L)
    caja(c, 1290, 560, 280, 110, "Usuario", ["navegador o celular"], fill=WHITE)
    flecha(c, [(1180, 205), (1290, 205)])
    etiqueta(c, 1235, 195, "descarga", size=12.5)
    flecha(c, [(1290, 615), (1180, 615)])
    etiqueta(c, 1235, 605, "HTTPS", size=12.5)
    flecha(c, [(1360, 560), (1360, 420), (1180, 420)])
    etiqueta(c, 1340, 470, "JSON + CORS", size=12.5)
    caja(c, 1240, 700, 330, 140, "Plan gratuito", ["se duerme tras ~15 min sin tráfico", "primera carga: 20–40 s",
                                                   "la actualización corre solo", "si el servicio está despierto"],
         fill=AMBER_L, stroke=AMBER, tsize=15, lsize=13)
    return c

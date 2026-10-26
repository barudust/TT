"""Diagramas de metodología (capítulos 2 y 4): D08 a D12."""

from __future__ import annotations

import math
import random

from estilo import (AMBER, AMBER_L, AMBER_M, BLUE, BLUE_D, BLUE_L, BLUE_M, FRAME, GRAY, GRAY_L,
                    GREEN, GREEN_L, INK, LINE, MONO, MUTED, ORANGE, ORANGE_L, RED, RED_L, SLATE,
                    SLATE_L, WHITE, Lienzo, caja, chip, circulo, etiqueta, flecha, linea, marco,
                    rect, texto)


# ---------------------------------------------------------------------------
# D08 · Las seis etapas
# ---------------------------------------------------------------------------
def d08_etapas() -> Lienzo:
    c = Lienzo(1600, 620, "Etapas del proyecto")
    etapas = [
        ("1", "Línea base (TT1)", "hasta mayo",
         ["¿Funciona el sistema", "completo con 5 modelos?"],
         ["Sí. XGBoost primero en F1,", "pero cada modelo recibía", "variables distintas"], None),
        ("2", "Primeras mejoras", "mayo–junio",
         ["¿Se puede mejorar", "cada modelo?"],
         ["Poco. Filtrar variables", "empeora en 11 de 15;", "falta un protocolo limpio"], "paper §6"),
        ("3", "Igualdad de condiciones", "junio",
         ["¿Quién gana si todos", "reciben lo mismo?"],
         ["La LR (0.399), XGBoost", "cerca; 120 corridas con", "las mismas 61 variables"], "paper §3–§7"),
        ("4", "Protocolo final", "agosto",
         ["¿Sobrevive a un protocolo", "estricto?"],
         ["Sí: la LR gana con", "significancia en A, B y C", "(0.404 en B)"], "paper §8"),
        ("5", "Búsqueda de mejoras", "fin de agosto",
         ["¿Algo más mejora sin", "cambiar el problema?"],
         ["Casi nada; se adoptan", "15 interacciones como", "equivalentes"], None),
        ("6", "Plataforma y validación", "septiembre–octubre",
         ["¿Cómo se comporta con", "datos nuevos?"],
         ["Se corrige el exceso de", "mantener; 2026: LR", "primera en clasificación"], None),
    ]
    xs = [140, 404, 668, 932, 1196, 1460]
    yl = 210
    linea(c, 70, yl, 1530, yl, color=FRAME, sw=4)
    flecha(c, [(1500, yl), (1560, yl)], sw=4)
    for (n, nombre, cuando, preg, resp, tag), x in zip(etapas, xs):
        principal = n == "4"
        col = ORANGE if principal else BLUE
        texto(c, x, 78, f"Etapa {n}", size=14, color=col, weight="bold", anchor="middle")
        texto(c, x, 104, nombre, size=17, weight="bold", anchor="middle", maxw=250)
        texto(c, x, 128, cuando, size=13.5, color=MUTED, anchor="middle")
        circulo(c, x, yl, 34 if principal else 28, col, stroke=WHITE, sw=4)
        texto(c, x, yl + 8, n, size=22 if principal else 19, color=WHITE, weight="bold", anchor="middle")
        bx, bw = x - 120, 240
        rect(c, bx, 280, bw, 262, fill=ORANGE_L if principal else WHITE, stroke=ORANGE if principal else FRAME,
             sw=2.2 if principal else 1.5, rx=12)
        texto(c, bx + 16, 312, "Pregunta", size=12.5, color=MUTED, weight="bold")
        yy = 336
        for s in preg:
            texto(c, bx + 16, yy, s, size=14, color=INK, maxw=bw - 30)
            yy += 21
        texto(c, bx + 16, yy + 18, "Respuesta", size=12.5, color=MUTED, weight="bold")
        yy += 42
        for s in resp:
            texto(c, bx + 16, yy, s, size=14, color=INK, weight="bold" if principal else "normal", maxw=bw - 30)
            yy += 21
        if tag:
            chip(c, x, 505, tag, fill=SLATE if not principal else ORANGE, color=WHITE, size=12.5, anchor="middle")
        if principal:
            chip(c, x, 245, "RESULTADO PRINCIPAL", fill=ORANGE, color=WHITE, size=12, anchor="middle")
    texto(c, 800, 590, "Los Experimentos A, B y C se repiten dentro de las etapas 1 a 4: no son etapas. "
                       "Cada etapa es una vuelta del ciclo de CRISP-DM.", size=13.5, color=MUTED, anchor="middle")
    return c


# ---------------------------------------------------------------------------
# D09 · Particiones temporales
# ---------------------------------------------------------------------------
def d09_particiones() -> Lienzo:
    c = Lienzo(1600, 900, "Particiones temporales y validaciones")
    x0, x1 = 360, 1560
    anios = list(range(2014, 2027))
    ancho = (x1 - x0) / len(anios)

    def xa(a, frac=0.0):
        return x0 + (a - 2014 + frac) * ancho

    # Encabezado de años
    for a in anios:
        texto(c, xa(a, 0.5), 52, str(a), size=13.5, color=MUTED, anchor="middle", weight="bold")
        linea(c, xa(a), 62, xa(a), 815, color="#e5e8ee", sw=1)
    linea(c, xa(2027), 62, xa(2027), 815, color="#e5e8ee", sw=1)

    COL = {"E": (BLUE, WHITE), "V": (AMBER_M, INK), "P": (BLUE_M, INK), "T": (ORANGE, WHITE),
           "O": (GREEN, WHITE), "H": ("url(#rayado)", INK)}

    def barra(y, a_ini, a_fin, tipo, txt="", frac_fin=1.0):
        fill, tc = COL[tipo]
        xs, xe = xa(a_ini), xa(a_fin, frac_fin)
        c.add(f'<rect x="{xs + 2:.1f}" y="{y:.1f}" width="{xe - xs - 4:.1f}" height="26" rx="6" fill="{fill}"/>')
        if txt:
            texto(c, (xs + xe) / 2, y + 18, txt, size=12.5, color=tc, weight="bold", anchor="middle")

    y = 90
    rh = 40

    def grupo(nombre):
        nonlocal y
        texto(c, 30, y + 18, nombre, size=14, color=SLATE, weight="bold")
        y += 34

    def fila(nombre, segmentos, destacado=False):
        nonlocal y
        texto(c, 46, y + 18, nombre, size=14, color=INK, weight="bold" if destacado else "normal", maxw=300)
        for s in segmentos:
            barra(y, *s)
        y += rh

    grupo("Experimentos (Etapas 3 y 4)")
    fila("A · 10 años", [(2014, 2023, "E", "entrenamiento"), (2024, 2024, "V", "valid."), (2025, 2025, "T", "prueba")])
    fila("B · 6 años (principal)", [(2018, 2023, "E", "entrenamiento"), (2024, 2024, "V", "valid."), (2025, 2025, "T", "prueba")], True)
    fila("C · 4 años", [(2020, 2023, "E", "entrenamiento"), (2024, 2024, "V", "valid."), (2025, 2025, "T", "prueba")])
    grupo("Protocolo final (Etapa 4)")
    fila("modo dev (decide)", [(2018, 2022, "E", "entrenamiento"), (2023, 2023, "P", "época"), (2024, 2024, "V", "config.")])
    fila("modo final (evalúa)", [(2018, 2023, "E", "entrenamiento"), (2024, 2024, "P", "época"), (2025, 2025, "T", "una vez")])
    grupo("Prueba año por año (Etapa 4)")
    for t in range(2020, 2026):
        fila(f"año de prueba {t}", [(t - 6, t - 2, "E", "5 años"), (t - 1, t - 1, "V", ""), (t, t, "T", "")])
    grupo("Etapa 6")
    fila("prueba ciega 2026", [(2020, 2024, "E", "entrenamiento"), (2025, 2025, "V", "valid."), (2026, 2026, "T", "ene–oct", 0.82)])
    fila("modelo de la plataforma", [(2018, 2025, "E", "entrenamiento (14 063 filas)"), (2026, 2026, "O", "en uso", 0.82)])
    grupo("Antecedente")
    fila("Exp A de TT1 (Etapas 1–2)", [(2014, 2021, "H", "entrenamiento"), (2022, 2023, "H", "validación"), (2024, 2025, "H", "prueba")])

    # Leyenda
    ly = y + 25
    items = [("E", "Entrenamiento"), ("V", "Validación / elección de configuración"), ("P", "Elección de la época (redes)"),
             ("T", "Prueba"), ("O", "Operación"), ("H", "Partición antigua (no comparable)")]
    lx = 46
    for tipo, s in items:
        fill, _ = COL[tipo]
        c.add(f'<rect x="{lx}" y="{ly}" width="26" height="18" rx="4" fill="{fill}"/>')
        texto(c, lx + 34, ly + 14, s, size=13, color=INK)
        lx += 60 + len(s) * 7.3
    return c


# ---------------------------------------------------------------------------
# D10 · Construcción de la etiqueta
# ---------------------------------------------------------------------------
def d10_etiqueta() -> Lienzo:
    c = Lienzo(1600, 790, "Construcción de la etiqueta por percentiles")
    rnd = random.Random(7)
    n = 72
    rets = [rnd.gauss(0, 1) * (1.0 + 0.5 * math.sin(i / 9)) for i in range(n)]

    # Serie de retornos (ilustrativa)
    x0, base, esc = 60, 240, 26
    paso = 11
    texto(c, 60, 50, "Retornos diarios r_fwd de una acción (ilustrativo)", size=15, color=MUTED, weight="bold")
    ventana_ini, t = 8, 64
    rect(c, x0 + ventana_ini * paso - 4, 80, (t - ventana_ini) * paso + 2, 300, fill=BLUE_L, stroke=BLUE, rx=8, dash="6 4")
    texto(c, x0 + (ventana_ini + t) / 2 * paso, 105, "252 días anteriores: t − 252 … t − 1", size=14, color=BLUE_D,
          weight="bold", anchor="middle")
    linea(c, x0 - 10, base, x0 + n * paso + 10, base, color=FRAME, sw=1.4)
    for i, r in enumerate(rets):
        h = r * esc
        color = BLUE if ventana_ini <= i < t else GRAY
        if i == t:
            color = ORANGE
        if i > t:
            color = "#d7dbe2"
        y = base - max(h, 0)
        c.add(f'<rect x="{x0 + i * paso:.1f}" y="{y:.1f}" width="{paso - 3}" height="{abs(h):.1f}" fill="{color}"/>')
    xt = x0 + t * paso + (paso - 3) / 2
    linea(c, xt, 120, xt, 390, color=ORANGE, sw=2, dash="4 3")
    texto(c, xt, 412, "día t", size=14, color=ORANGE, weight="bold", anchor="middle")
    texto(c, xt, 432, "r_fwd(t) = ln(C t+1 / C t)", size=13, color=ORANGE, anchor="middle")
    texto(c, x0 + (ventana_ini + t) / 2 * paso, 412, "con shift(1): el umbral del día t no usa r_fwd(t)", size=13,
          color=BLUE_D, anchor="middle")

    # Histograma con percentiles
    hx0, hy0, hw, hh = 1000, 90, 540, 300
    texto(c, hx0, 50, "Distribución de r_fwd en la ventana", size=15, color=MUTED, weight="bold")
    bins = 24
    vals = [math.exp(-((i - bins / 2 + 0.5) / 4.6) ** 2) for i in range(bins)]
    bw = hw / bins
    q30, q70 = int(bins * 0.36), int(bins * 0.64)
    for i, v in enumerate(vals):
        h = v * (hh - 40)
        if i < q30:
            col = RED
        elif i >= q70:
            col = GREEN
        else:
            col = AMBER_M
        c.add(f'<rect x="{hx0 + i * bw + 1:.1f}" y="{hy0 + hh - h:.1f}" width="{bw - 2:.1f}" height="{h:.1f}" fill="{col}" fill-opacity="0.85"/>')
    linea(c, hx0, hy0 + hh, hx0 + hw, hy0 + hh, color=FRAME)
    for qi, nombre in ((q30, "Q30"), (q70, "Q70")):
        xq = hx0 + qi * bw
        linea(c, xq, hy0 + 10, xq, hy0 + hh + 8, color=INK, sw=2)
        texto(c, xq, hy0 + hh + 28, nombre, size=14, weight="bold", anchor="middle")
    texto(c, hx0 + q30 * bw / 2, hy0 + 30, "VENDER · 30 %", size=14, color=RED, weight="bold", anchor="middle")
    texto(c, hx0 + (q30 + q70) / 2 * bw, hy0 + 30, "MANTENER · 40 %", size=14, color=AMBER, weight="bold", anchor="middle")
    texto(c, hx0 + (q70 + bins) / 2 * bw, hy0 + 30, "COMPRAR · 30 %", size=14, color=GREEN, weight="bold", anchor="middle")

    flecha(c, [(xt + 20, 250), (990, 250)], color=ORANGE, sw=2.2)
    etiqueta(c, (xt + 990) / 2 + 10, 240, "se compara r_fwd(t) con Q30(t) y Q70(t)", size=13, color=ORANGE)

    # Regla
    rect(c, 60, 480, 1480, 270, fill=SLATE_L, stroke=SLATE, rx=12)
    texto(c, 90, 520, "Regla (scripts_v1/01_build_raw_dataset.py y api/ml/target.py)", size=15, color=SLATE, weight="bold")
    ls = [
        ("r_fwd = ln(close.shift(-1) / close)", "retorno del día siguiente"),
        ("Q70(t) = percentil 70 de r_fwd en [t − 252, t − 1]   (rolling 252, mínimo 126, shift 1)", "umbral para comprar"),
        ("Q30(t) = percentil 30 de r_fwd en [t − 252, t − 1]", "umbral para vender"),
        ("COMPRAR (2) si r_fwd(t) ≥ Q70(t) · VENDER (0) si r_fwd(t) ≤ Q30(t) · MANTENER (1) en otro caso", ""),
    ]
    yy = 560
    for f, d in ls:
        texto(c, 90, yy, f, size=15, family=MONO, color=INK)
        if d:
            texto(c, 1510, yy, d, size=13.5, color=MUTED, anchor="end")
        yy += 38
    texto(c, 90, yy + 4, "El umbral se adapta al régimen: en un año agitado los percentiles se abren; en uno tranquilo se cierran.",
          size=13.5, color=MUTED)
    return c


# ---------------------------------------------------------------------------
# D11 · Protocolo anidado dev / final
# ---------------------------------------------------------------------------
def d11_protocolo() -> Lienzo:
    c = Lienzo(1600, 640, "Protocolo anidado de la Etapa 4")
    x0, x1 = 300, 1560
    anios = list(range(2018, 2026))
    an = (x1 - x0) / len(anios)

    def xa(a):
        return x0 + (a - 2018) * an

    for a in anios:
        texto(c, xa(a) + an / 2, 55, str(a), size=15, color=MUTED, weight="bold", anchor="middle")

    def bloque(y, a1, a2, fill, stroke, titulo, sub=None, tc=INK):
        rect(c, xa(a1) + 4, y, xa(a2 + 1) - xa(a1) - 8, 110, fill=fill, stroke=stroke, rx=10, sw=1.8)
        cx = (xa(a1) + xa(a2 + 1)) / 2
        texto(c, cx, y + (48 if sub else 62), titulo, size=16, weight="bold", color=tc, anchor="middle")
        if sub:
            texto(c, cx, y + 76, sub, size=13, color=tc, anchor="middle")

    # dev
    texto(c, 30, 140, "Modo dev", size=18, weight="bold")
    texto(c, 30, 166, "aquí se toman", size=14, color=MUTED)
    texto(c, 30, 186, "todas las decisiones", size=14, color=MUTED)
    bloque(95, 2018, 2022, BLUE, BLUE, "Entrenamiento", "2018–2022", tc=WHITE)
    bloque(95, 2023, 2023, BLUE_M, BLUE, "Época", "redes")
    bloque(95, 2024, 2024, AMBER_M, AMBER, "Configuración", "Optuna")
    rect(c, xa(2025) + 4, 95, an - 8, 110, fill="url(#rayado)", stroke=GRAY, rx=10)
    etiqueta(c, xa(2025) + an / 2, 157, "no se usa", size=14, color=MUTED, weight="bold")

    # final
    texto(c, 30, 330, "Modo final", size=18, weight="bold")
    texto(c, 30, 356, "configuración", size=14, color=MUTED)
    texto(c, 30, 376, "congelada", size=14, color=MUTED)
    bloque(285, 2018, 2023, BLUE, BLUE, "Entrenamiento", "2018–2023 (clásicos: + 2024)", tc=WHITE)
    bloque(285, 2024, 2024, BLUE_M, BLUE, "Época", "redes")
    bloque(285, 2025, 2025, ORANGE, ORANGE, "Prueba", "una sola vez", tc=WHITE)

    flecha(c, [(xa(2024) + an / 2, 205), (xa(2024) + an / 2, 245), (xa(2021), 245), (xa(2021), 285)], color=AMBER, sw=2.2)
    etiqueta(c, (xa(2024) + an / 2 + xa(2021)) / 2, 237, "configuración congelada", size=13, color=AMBER, weight="bold")

    rect(c, 30, 440, 1530, 170, fill=SLATE_L, stroke=SLATE, rx=12)
    notas = [
        "Ninguna decisión (hiperparámetros, arquitectura, ventana, escalador, época) usa 2025.",
        "Los clásicos se reentrenan con entrenamiento + validación antes de la prueba; las redes no (las empeoraba −0.024 a −0.047).",
        "Antes de cambiar nada se verificó que el código nuevo reproduce la Etapa 3: 18 de 18 celdas idénticas.",
        "Evaluación final con cinco semillas (42, 1, 7, 2024, 100) y probabilidades promediadas.",
    ]
    yy = 480
    for s in notas:
        texto(c, 55, yy, "• " + s, size=15, maxw=1480)
        yy += 34
    return c


# ---------------------------------------------------------------------------
# D12 · Mismas filas para los cinco modelos
# ---------------------------------------------------------------------------
def d12_mismas_filas() -> Lienzo:
    c = Lienzo(1600, 770, "Mismas filas de prueba para los cinco modelos")
    xv0, xv1, xt1 = 330, 860, 1540   # validación 2024 | prueba 2025
    dias = 248

    def xt(d):
        return xv1 + (xt1 - xv1) * d / dias

    def ejes(y):
        rect(c, xv0, y, xv1 - xv0, 30, fill=AMBER_L, stroke=AMBER, rx=6)
        texto(c, (xv0 + xv1) / 2, y + 21, "validación 2024", size=13.5, color=AMBER, weight="bold", anchor="middle")
        rect(c, xv1, y, xt1 - xv1, 30, fill=ORANGE_L, stroke=ORANGE, rx=6)
        texto(c, (xv1 + xt1) / 2, y + 21, "prueba 2025 (248 días hábiles por acción)", size=13.5, color=ORANGE,
              weight="bold", anchor="middle")

    # Antes
    texto(c, 30, 50, "Etapas 1 a 3: cada conjunto se cortaba por separado", size=18, weight="bold")
    ejes(70)
    filas = [("LR y XGBoost", 0, "248 días"), ("Redes, ventana de 20", 20, "228 días"), ("Redes, ventana de 60", 60, "188 días")]
    y = 125
    for nombre, perdidos, txt in filas:
        texto(c, 30, y + 20, nombre, size=14.5)
        if perdidos:
            rect(c, xt(0), y, xt(perdidos) - xt(0), 28, fill="url(#rayado)", stroke=GRAY, rx=5)
        rect(c, xt(perdidos), y, xt1 - xt(perdidos), 28, fill=BLUE if not perdidos else BLUE_M, stroke="none", rx=5)
        texto(c, xt1 - 10, y + 19, txt, size=13.5, color=WHITE if not perdidos else INK, weight="bold", anchor="end")
        y += 42
    texto(c, 30, y + 18, "Los primeros días de prueba no tenían ventana completa y se descartaban: cada modelo se evaluaba sobre días distintos.",
          size=14, color=RED)

    # Después
    y0 = 330
    texto(c, 30, y0, "Etapa 4: ventanas sobre la serie continua, asignadas por la fecha de la etiqueta", size=18, weight="bold")
    ejes(y0 + 20)
    y = y0 + 75
    for nombre in ("LR y XGBoost", "LSTM y CNN 1D (ventana de 10)", "CNN-LSTM (ventana de 20)"):
        texto(c, 30, y + 20, nombre, size=14.5)
        rect(c, xt(0), y, xt1 - xt(0), 28, fill=BLUE, stroke="none", rx=5)
        texto(c, xt1 - 10, y + 19, "248 días", size=13.5, color=WHITE, weight="bold", anchor="end")
        y += 42
    # ventana del primer día de prueba
    yw = y + 14
    w = 20
    xs = xt(0) - (xt1 - xv1) * w / dias
    rect(c, xs, yw, xt(0) - xs, 26, fill=BLUE_L, stroke=BLUE, rx=4, dash="4 3")
    flecha(c, [(xt(0) + 2, yw + 13), (xt(0) + 40, yw + 13)], color=BLUE)
    texto(c, xt(0) + 48, yw + 18, "ventana del primer día de prueba: usa días de validación (solo pasado; no es fuga)",
          size=13.5, color=BLUE_D)
    caja(c, 30, yw + 60, 1510, 120, None,
         ["Resultado: los cinco modelos se evalúan sobre las mismas 1 736 filas (7 acciones × 248 días) y con las mismas ocho métricas.",
          "Detalle: para la fila del día t la ventana abarca t − W … t − 1, así que las redes no ven el día t (la LR sí).",
          "Medido con la LR: quitarle el día t le cuesta ≈ 0.007 de F1, mucho menos que la diferencia con las redes."],
         fill=SLATE_L, stroke=SLATE, align="left", lsize=14.5)
    return c

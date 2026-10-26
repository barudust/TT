"""Estilo común y primitivas SVG para los diagramas del reporte técnico.

Todos los diagramas usan la misma paleta, tipografía y forma de cajas y
flechas, para que se vean como un solo sistema. Se genera SVG puro (se puede
abrir y editar en Inkscape, Illustrator o draw.io) y luego se exporta a PNG
con Chrome sin interfaz (ver generar_diagramas.py).
"""

from __future__ import annotations

from xml.sax.saxutils import escape

FONT = "Arial, Helvetica, sans-serif"
MONO = "Consolas, 'Courier New', monospace"

INK = "#1f2937"       # texto principal
MUTED = "#6b7280"     # texto secundario
LINE = "#8a94a6"      # flechas y bordes neutros
FRAME = "#c3cad6"     # marcos punteados

BLUE = "#2a78d6"      # plataforma / Regresión Logística
BLUE_D = "#1c518f"
BLUE_L = "#eaf2fd"
BLUE_M = "#a9c9f2"
SLATE = "#475569"     # investigación
SLATE_L = "#f1f4f8"
ORANGE = "#eb6834"    # resultado principal / artefacto / prueba
ORANGE_L = "#fdeee6"
AMBER = "#c27c0e"     # validación / elección / mantener
AMBER_L = "#fdf3e1"
AMBER_M = "#f1c36b"
GREEN = "#1f8a4c"     # comprar / operación
GREEN_L = "#e7f5ed"
RED = "#c0392b"       # vender
RED_L = "#fbeceb"
GRAY = "#9aa3ae"
GRAY_L = "#f3f4f6"
WHITE = "#ffffff"

# Anchos aproximados de caracteres de Arial (fracción del tamaño de letra),
# solo para avisar si un texto no cabe en su caja.
_NARROW = set("iljtf.,:;!|'()[]Ií·")
_WIDE = set("mwMW@%")


def ancho_texto(s: str, size: float, bold: bool = False) -> float:
    total = 0.0
    for ch in s:
        if ch in _NARROW:
            total += 0.30
        elif ch in _WIDE:
            total += 0.85
        elif ch.isupper() or ch.isdigit():
            total += 0.64
        elif ch == " ":
            total += 0.28
        else:
            total += 0.54
    return total * size * (1.06 if bold else 1.0)


AVISOS: list[str] = []


def _avisar(s: str, size: float, disponible: float, bold: bool = False) -> None:
    w = ancho_texto(s, size, bold)
    if w > disponible:
        AVISOS.append(f"No cabe ({w:.0f} > {disponible:.0f}px): {s!r}")


class Lienzo:
    """Acumula elementos SVG y los escribe con un encabezado común."""

    def __init__(self, ancho: int, alto: int, titulo: str):
        self.ancho = ancho
        self.alto = alto
        self.titulo = titulo
        self.partes: list[str] = []

    def add(self, s: str) -> None:
        self.partes.append(s)

    def svg(self) -> str:
        defs = f"""<defs>
  <marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/>
  </marker>
  <marker id="flecha-azul" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/>
  </marker>
  <marker id="flecha-naranja" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{ORANGE}"/>
  </marker>
  <marker id="flecha-ambar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{AMBER}"/>
  </marker>
  <pattern id="rayado" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="8" height="8" fill="{GRAY_L}"/>
    <line x1="0" y1="0" x2="0" y2="8" stroke="{GRAY}" stroke-width="2"/>
  </pattern>
</defs>"""
        cuerpo = "\n".join(self.partes)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.ancho}" height="{self.alto}" '
            f'viewBox="0 0 {self.ancho} {self.alto}" font-family="{FONT}">\n'
            f"<title>{escape(self.titulo)}</title>\n{defs}\n"
            f'<rect x="0" y="0" width="{self.ancho}" height="{self.alto}" fill="{WHITE}"/>\n'
            f"{cuerpo}\n</svg>\n"
        )


def texto(c: Lienzo, x, y, s, size=14, color=INK, weight="normal", anchor="start",
          family=None, italic=False, maxw=None) -> None:
    if maxw is not None:
        _avisar(s, size, maxw, weight == "bold")
    fam = f' font-family="{family}"' if family else ""
    est = ' font-style="italic"' if italic else ""
    c.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
          f'font-weight="{weight}" text-anchor="{anchor}"{fam}{est}>{escape(s)}</text>')


def rect(c: Lienzo, x, y, w, h, fill=WHITE, stroke=LINE, sw=1.5, rx=10, dash=None, opacity=None) -> None:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    c.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
          f'fill="{fill}"{o} stroke="{stroke}" stroke-width="{sw}"{d}/>')


def caja(c: Lienzo, x, y, w, h, titulo=None, lineas=(), fill=WHITE, stroke=LINE,
         tcolor=INK, lcolor=INK, tsize=16, lsize=14, rx=10, align="center", sw=1.5,
         sobre=None, sobre_color=MUTED, mono_titulo=False, dash=None) -> None:
    """Caja con título opcional y líneas de texto centradas verticalmente."""
    rect(c, x, y, w, h, fill=fill, stroke=stroke, rx=rx, sw=sw, dash=dash)
    filas = []
    if sobre:
        filas.append(("sobre", sobre, 12))
    if titulo:
        filas.append(("titulo", titulo, tsize))
    for ln in lineas:
        filas.append(("linea", ln, lsize))
    alto_filas = [s * 1.38 for _, _, s in filas]
    total = sum(alto_filas)
    yy = y + (h - total) / 2
    pad = 14
    for (tipo, s, size), hf in zip(filas, alto_filas):
        base = yy + hf * 0.74
        if align == "center":
            xx, anchor = x + w / 2, "middle"
        else:
            xx, anchor = x + pad, "start"
        if tipo == "titulo":
            texto(c, xx, base, s, size=size, color=tcolor, weight="bold", anchor=anchor,
                  family=MONO if mono_titulo else None, maxw=w - 2 * pad)
        elif tipo == "sobre":
            texto(c, xx, base, s, size=size, color=sobre_color, anchor=anchor, maxw=w - 2 * pad)
        else:
            texto(c, xx, base, s, size=size, color=lcolor, anchor=anchor, maxw=w - 2 * pad)
        yy += hf


def flecha(c: Lienzo, puntos, color=LINE, sw=1.8, dash=None, cabeza=True, doble=False,
           marcador=None) -> None:
    d = " ".join(("M" if i == 0 else "L") + f"{px:.1f},{py:.1f}" for i, (px, py) in enumerate(puntos))
    m = marcador or ("flecha" if color == LINE else "flecha-azul" if color == BLUE else
                     "flecha-naranja" if color == ORANGE else "flecha-ambar" if color == AMBER else "flecha")
    fin = f' marker-end="url(#{m})"' if cabeza else ""
    ini = f' marker-start="url(#{m})"' if doble else ""
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    c.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{ds}{fin}{ini}/>')


def etiqueta(c: Lienzo, x, y, s, size=12.5, color=MUTED, anchor="middle", fondo=True, weight="normal") -> None:
    """Texto pequeño sobre una flecha, con fondo blanco para que se lea."""
    if fondo:
        w = ancho_texto(s, size) + 10
        x0 = x - w / 2 if anchor == "middle" else (x - w + 5 if anchor == "end" else x - 5)
        c.add(f'<rect x="{x0:.1f}" y="{y - size * 0.95:.1f}" width="{w:.1f}" height="{size * 1.35:.1f}" '
              f'fill="{WHITE}" rx="3"/>')
    texto(c, x, y, s, size=size, color=color, anchor=anchor, weight=weight)


def marco(c: Lienzo, x, y, w, h, nombre, color=FRAME, tcolor=MUTED, fill="none") -> None:
    """Marco punteado que agrupa una zona del diagrama, con su nombre arriba."""
    c.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="16" '
          f'fill="{fill}" stroke="{color}" stroke-width="1.6" stroke-dasharray="7 6"/>')
    tw = ancho_texto(nombre, 13, True) + 16
    c.add(f'<rect x="{x + 18:.1f}" y="{y - 10:.1f}" width="{tw:.1f}" height="20" fill="{WHITE}"/>')
    texto(c, x + 26, y + 5, nombre, size=13, color=tcolor, weight="bold")


def chip(c: Lienzo, x, y, s, fill=BLUE_L, color=BLUE_D, size=12, mono=False, anchor="start", bold=True) -> float:
    """Etiqueta redondeada. Devuelve su ancho."""
    # Consolas es de ancho fijo: cada carácter mide ~0.55 del tamaño.
    w = (len(s) * size * 0.56 if mono else ancho_texto(s, size, bold)) + 18
    x0 = x if anchor == "start" else x - w / 2 if anchor == "middle" else x - w
    c.add(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{size + 10}" rx="{(size + 10) / 2}" fill="{fill}"/>')
    texto(c, x0 + w / 2, y + size + 2.5, s, size=size, color=color, weight="bold" if bold else "normal",
          anchor="middle", family=MONO if mono else None)
    return w


def circulo(c: Lienzo, x, y, r, fill, stroke=None, sw=2) -> None:
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{st}/>')


def linea(c: Lienzo, x1, y1, x2, y2, color=LINE, sw=1.5, dash=None) -> None:
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    c.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}"{ds}/>')

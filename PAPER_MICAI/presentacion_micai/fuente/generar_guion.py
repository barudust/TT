"""Genera el guion de la presentación de MICAI en Markdown y en una versión
imprimible (HTML → PDF con Chrome o Edge), a partir de guion.py.

Uso (desde la raíz del repositorio):

    python PAPER_MICAI/presentacion_micai/fuente/generar_guion.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from guion import DIAPOSITIVAS, FRASES_DE_APOYO, PREGUNTAS, PRONUNCIACION, RESPALDO  # noqa: E402

SALIDA = AQUI.parent


def mmss(seg: int) -> str:
    return f"{seg // 60}:{seg % 60:02d}"


def acumulados():
    t = 0
    for d in DIAPOSITIVAS:
        ini = t
        t += d["seg"]
        yield d, ini, t


def markdown() -> str:
    total = sum(d["seg"] for d in DIAPOSITIVAS)
    out = [
        "# Guion para dos expositores — MICAI 2026",
        "",
        "> Generado desde `fuente/guion.py` (no editar a mano: cambiar ahí y volver a correr",
        "> `generar_guion.py`). Inglés sencillo, frases cortas. Debajo de cada bloque en inglés",
        "> va la traducción, solo para que sepan qué están diciendo: **en el congreso se dice",
        "> solo el inglés**.",
        "",
        f"**Duración total: {mmss(total)} min** (límite oficial: 10 min de exposición + 5 de preguntas).",
        "El margen es para hablar despacio, respirar y cambiar de expositor sin prisa.",
        "",
        "| Expositor | Diapositivas | Tiempo |",
        "|---|---|---:|",
    ]
    for quien in ("Expositor 1", "Expositor 2"):
        ns = [d["n"] for d in DIAPOSITIVAS if d["quien"] == quien]
        seg = sum(d["seg"] for d in DIAPOSITIVAS if d["quien"] == quien)
        rangos = ", ".join(str(n) for n in ns)
        out.append(f"| **{quien}** | {rangos} | {mmss(seg)} |")
    out += [
        "",
        "- **Expositor 1** abre (portada, pregunta, datos, modelos) y cierra (por qué gana, mensajes finales).",
        "- **Expositor 2** presenta los cuatro resultados y la comparación justa.",
        "- Cambian de expositor **dos veces**; la frase para pasar la palabra está marcada con →.",
        "- Si solo presenta una persona, el guion es el mismo: se omiten las frases de cambio.",
        "- Reemplazar **[NAME]** por los nombres reales en la diapositiva 1.",
        "- Si la sesión es después de las 12:00, decir *Good afternoon, everyone* (gud af-ter-NÚN).",
        "",
        "---",
        "",
    ]
    for d, ini, fin in acumulados():
        out += [
            f"## Diapositiva {d['n']} · {d['titulo']} — {d['quien']} · {d['seg']} s "
            f"(minuto {mmss(ini)} → {mmss(fin)})",
            "",
        ]
        for en in d["en"]:
            out.append(f"> **{en}**  ")
        if d.get("pase"):
            out += [">", f"> → **{d['pase']}**"]
        out += ["", "<details><summary>Traducción</summary>", ""]
        for es in d["es"]:
            out.append(f"- {es}")
        if d.get("pase_es"):
            out.append(f"- → {d['pase_es']}")
        out += ["", "</details>", ""]
    out += ["---", "", "## Diapositivas de respaldo (solo si una pregunta las necesita)", ""]
    for n, desc in RESPALDO.items():
        out.append(f"- **{n}.** {desc}")
    out += [
        "",
        "Para saltar a una diapositiva en PowerPoint durante la presentación: escribir el número",
        "y presionar **Enter** (por ejemplo `13` + Enter). Para volver: el número de la última.",
        "",
        "---",
        "",
        "## Pronunciación (aproximada, para hispanohablantes)",
        "",
        "La sílaba en MAYÚSCULAS es la que se acentúa.",
        "",
        "| Palabra | Se dice |",
        "|---|---|",
    ]
    for w, pr in PRONUNCIACION:
        out.append(f"| {w} | {pr} |")
    out += [
        "",
        "**Números:** el punto decimal se dice *point* y cada dígito por separado: 0.404 = "
        "*zero point four zero four*. Los porcentajes: 15.5 % = *fifteen point five percent*.",
        "",
        "---",
        "",
        "## Preguntas probables (respuestas cortas)",
        "",
        "Quién contesta cada una es una sugerencia por tema; el otro puede completar.",
        "",
    ]
    for i, q in enumerate(PREGUNTAS, 1):
        out += [
            f"### {i}. {q['q']}",
            f"*{q['q_es']}* — contesta **{q['quien']}**",
            "",
            f"> **{q['a']}**",
            "",
            f"{q['a_es']}",
            "",
        ]
    out += [
        "Respuestas más completas: `../07_PREGUNTAS_MICAI.md`.",
        "",
        "---",
        "",
        "## Frases de apoyo (para cualquier momento)",
        "",
        "| Inglés | Español | Se dice |",
        "|---|---|---|",
    ]
    for en, es, pr in FRASES_DE_APOYO:
        out.append(f"| **{en}** | {es} | {pr} |")
    out.append("")
    return "\n".join(out)


CSS = """
@page { size: Letter; margin: 14mm 14mm 16mm 14mm; }
body { font-family: Calibri, Arial, sans-serif; color: #1f2937; font-size: 12.5pt; line-height: 1.35; }
h1 { color: #1f3c88; font-size: 22pt; margin: 0 0 4pt; }
h2 { color: #1f3c88; font-size: 15pt; margin: 18pt 0 6pt; page-break-after: avoid; }
.meta { color: #4b5563; margin-bottom: 10pt; }
.slide { border: 1px solid #d7dce5; border-radius: 8px; padding: 10pt 12pt; margin: 0 0 10pt; page-break-inside: avoid; }
.cab { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6pt; }
.cab b { font-size: 14pt; color: #1f3c88; }
.who { font-weight: bold; padding: 1pt 8pt; border-radius: 10pt; color: #fff; font-size: 10.5pt; }
.e1 { background: #2a78d6; } .e2 { background: #d81b60; }
.t { color: #4b5563; font-size: 10.5pt; }
.en { font-size: 15pt; margin: 3pt 0; }
.pase { font-size: 15pt; font-weight: bold; color: #d81b60; margin-top: 6pt; }
.es { color: #6b7280; font-size: 10.5pt; margin-top: 6pt; border-top: 1px dashed #d7dce5; padding-top: 4pt; }
table { border-collapse: collapse; width: 100%; font-size: 11pt; }
td, th { border: 1px solid #d7dce5; padding: 3pt 6pt; text-align: left; }
th { background: #1f3c88; color: #fff; }
.q { page-break-inside: avoid; margin-bottom: 8pt; }
.q .en { font-size: 13pt; }
.salto { page-break-before: always; }
"""


def html() -> str:
    total = sum(d["seg"] for d in DIAPOSITIVAS)
    h = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>MICAI 2026 script</title>"
         f"<style>{CSS}</style></head><body>",
         "<h1>MICAI 2026 · Guion para dos expositores</h1>",
         f"<div class='meta'>Total {mmss(total)} min (límite 10 min + 5 de preguntas). "
         "En el congreso se dice solo el texto grande, en inglés. El gris es la traducción.</div>"]
    for d, ini, fin in acumulados():
        cls = "e1" if d["quien"] == "Expositor 1" else "e2"
        h.append("<div class='slide'><div class='cab'>"
                 f"<b>{d['n']} · {escape(d['titulo'])}</b>"
                 f"<span><span class='who {cls}'>{escape(d['quien'])}</span> "
                 f"<span class='t'>{d['seg']} s · {mmss(ini)} → {mmss(fin)}</span></span></div>")
        for en in d["en"]:
            h.append(f"<div class='en'>{escape(en)}</div>")
        if d.get("pase"):
            h.append(f"<div class='pase'>→ {escape(d['pase'])}</div>")
        es = " ".join(d["es"]) + (f" → {d['pase_es']}" if d.get("pase_es") else "")
        h.append(f"<div class='es'>{escape(es)}</div></div>")
    h.append("<h2 class='salto'>Preguntas probables</h2>")
    for i, q in enumerate(PREGUNTAS, 1):
        h.append(f"<div class='q'><b>{i}. {escape(q['q'])}</b> <span class='t'>({escape(q['q_es'])} · "
                 f"{escape(q['quien'])})</span><div class='en'>{escape(q['a'])}</div>"
                 f"<div class='es'>{escape(q['a_es'])}</div></div>")
    h.append("<h2>Frases de apoyo</h2><table><tr><th>Inglés</th><th>Español</th><th>Se dice</th></tr>")
    for en, es, pr in FRASES_DE_APOYO:
        h.append(f"<tr><td><b>{escape(en)}</b></td><td>{escape(es)}</td><td>{escape(pr)}</td></tr>")
    h.append("</table><h2>Pronunciación</h2><table><tr><th>Palabra</th><th>Se dice</th></tr>")
    for w, pr in PRONUNCIACION:
        h.append(f"<tr><td>{escape(w)}</td><td>{escape(pr)}</td></tr>")
    h.append("</table></body></html>")
    return "\n".join(h)


NAVEGADORES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "msedge",
]


def a_pdf(html_path: Path, pdf_path: Path) -> bool:
    for n in NAVEGADORES:
        nav = n if Path(n).exists() else shutil.which(n)
        if nav:
            subprocess.run([nav, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                           check=True, capture_output=True, timeout=120)
            return True
    return False


if __name__ == "__main__":
    (SALIDA / "GUION_DOS_EXPOSITORES.md").write_text(markdown(), encoding="utf-8")
    hp = AQUI / "guion_imprimible.html"
    hp.write_text(html(), encoding="utf-8")
    ok = a_pdf(hp, SALIDA / "GUION_imprimible.pdf")
    print("guion listo" + ("" if ok else " (sin PDF: no se encontró Chrome ni Edge)"))

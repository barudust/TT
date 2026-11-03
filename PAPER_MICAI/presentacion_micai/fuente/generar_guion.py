"""Genera el guion de la presentación de MICAI en Markdown y en una versión
imprimible (HTML → PDF con Chrome o Edge), a partir de guion.py. Una salida
para un expositor (la principal) y otra para dos.

Uso (desde la raíz del repositorio del artículo; dentro del TT, PAPER_MICAI/):

    python presentacion_micai/fuente/generar_guion.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from guion import (E1, E2, FRASES_DE_APOYO, MODERADOR, NOMBRE_1, NOMBRE_2, PRONUNCIACION,  # noqa: E402
                   RESPALDO, SESION, TEMAS_PREGUNTAS, VERSION_CORTA, guion, plano)

SALIDA = AQUI.parent
NOMBRES = {"uno": "GUION_UN_EXPOSITOR", "dos": "GUION_DOS_EXPOSITORES"}
TITULOS = {"uno": "Guion para un expositor", "dos": "Guion para dos expositores"}


def mmss(seg: int) -> str:
    return f"{seg // 60}:{seg % 60:02d}"


def frases_apoyo(modo: str):
    return [f for f in FRASES_DE_APOYO if modo == "dos" or not f[3]]


def markdown(modo: str) -> str:
    dias = guion(modo)
    total = dias[-1]["fin"]
    otro = "dos" if modo == "uno" else "uno"
    out = [
        f"# {TITULOS[modo]} — MICAI 2026",
        "",
        "> Generado desde `fuente/guion.py` (no editar a mano: cambiar ahí y volver a correr",
        "> `generar_guion.py`). Inglés sencillo, frases cortas. Debajo de cada bloque en inglés",
        "> va la traducción, para saber qué se está diciendo: **en el congreso se dice solo el",
        "> inglés**. Para tenerlo a la mano al presentar están las tarjetas (`TARJETAS_*.pdf`).",
        "",
        f"**Cuándo y dónde:** {SESION['dia']}, {SESION['turno']} h, {SESION['sala']}, {SESION['sede']}. "
        f"Sesión *{SESION['nombre']}* ({SESION['horario']}), Paper ID {SESION['paper_id']}.",
        "",
        f"**Duración total: {mmss(total)} min** (límite oficial: 10 min de exposición + 5 de preguntas).",
        f"El margen es para hablar despacio y respirar. Versión alternativa: `{NOMBRES[otro]}.md`.",
        "",
    ]
    if modo == "dos":
        out += ["| Expositor | Diapositivas | Tiempo |", "|---|---|---:|"]
        for quien, nombre in ((E1, NOMBRE_1), (E2, NOMBRE_2)):
            ns = [d["n"] for d in dias if d["quien"] == quien]
            seg = sum(d["seg"] for d in dias if d["quien"] == quien)
            out.append(f"| **{quien}** ({nombre}) | {', '.join(str(n) for n in ns)} | {mmss(seg)} |")
        out += [
            "",
            "- **Expositor 1** abre (portada, pregunta, datos, modelos) y cierra (por qué gana, mensajes finales).",
            "- **Expositor 2** presenta los cuatro resultados y la comparación justa.",
            "- Cambian de expositor **dos veces**; la frase para pasar la palabra está marcada con →.",
            "",
        ]
    out += [
        "- ✂ marca una frase que se puede saltar si vas tarde (la información ya está en la diapositiva).",
        "",
        "---",
        "",
    ]
    for d in dias:
        quien = f" — {d['quien']}" if d["quien"] else ""
        out += [f"## Diapositiva {d['n']} · {d['titulo']}{quien} · {d['seg']} s (minuto {mmss(d['ini'])} → {mmss(d['fin'])})", ""]
        for en in d["en"]:
            marca = "✂ " if en.startswith("✂") else ""
            out.append(f"> **{marca}{plano(en)}**  ")
        if d.get("pase"):
            out += [">", f"> → **{d['pase']}**"]
        out += ["", "<details><summary>Traducción</summary>", ""]
        out += [f"- {es}" for es in d["es"]]
        if d.get("pase_es"):
            out.append(f"- → {d['pase_es']}")
        out += ["", "</details>", ""]
    out += [
        "---",
        "",
        "## Versión de 2 minutos (solo si el moderador pide recortar)",
        "",
        "Si la sesión va retrasada y piden acortar, la dice **una sola persona** y solo se muestran",
        "las diapositivas " + ", ".join(str(b["n"]) for b in VERSION_CORTA) + " (escribir el número y **Enter**).",
        "",
    ]
    for b in VERSION_CORTA:
        out += [f"**Diapositiva {b['n']}**", ""]
        out += [f"> **{plano(en)}**  " for en in b["en"]]
        out += ["", "<details><summary>Traducción</summary>", ""]
        out += [f"- {es}" for es in b["es"]]
        out += ["", "</details>", ""]
    out += ["---", "", "## Diapositivas de respaldo (solo si una pregunta las necesita)", ""]
    out += [f"- **{n}.** {desc}" for n, desc in RESPALDO.items()]
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
    out += [f"| {w} | {pr} |" for w, pr in PRONUNCIACION]
    out += [
        "",
        "**Números:** el punto decimal se dice *point* y cada dígito por separado: 0.404 = "
        "*zero point four zero four*. Los porcentajes: 15.5 % = *fifteen point five percent*.",
        "",
        "---",
        "",
        "## Preguntas probables (respuestas cortas)",
        "",
        "Las palabras clave son las que hay que reconocer al oír la pregunta.",
        "",
    ]
    i = 0
    for letra, tema, ps in TEMAS_PREGUNTAS:
        out += [f"### {letra}. {tema}", ""]
        for q in ps:
            i += 1
            contesta = f" — contesta **{q['quien']}**" if modo == "dos" else ""
            out += [f"**{i}. {q['q']}**  ", f"*{q['q_es']}*{contesta}  ", f"Si oyes: {q['claves']}", ""]
            out += [f"> **{q['a']}**", "", q["a_es"]]
            if q.get("respaldo"):
                out[-1] += f" (Ayuda: diapositiva {q['respaldo']}.)"
            out.append("")
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
    out += [f"| **{en}** | {es} | {pr} |" for en, es, pr, _ in frases_apoyo(modo)]
    out += ["", "## Si el moderador te dice…", "", "| Oyes | Haces |", "|---|---|"]
    out += [f"| {oyes} | {haces} |" for oyes, haces in MODERADOR]
    out.append("")
    return "\n".join(out)


CSS = """
@page { size: Letter; margin: 14mm 14mm 16mm 14mm; }
body { font-family: Calibri, Arial, sans-serif; color: #1f2937; font-size: 12.5pt; line-height: 1.35; }
h1 { color: #1f3c88; font-size: 22pt; margin: 0 0 4pt; }
h2 { color: #1f3c88; font-size: 15pt; margin: 18pt 0 6pt; page-break-after: avoid; }
h3 { color: #1f3c88; font-size: 13pt; margin: 12pt 0 4pt; page-break-after: avoid; }
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
.claves { color: #4b5563; font-size: 10.5pt; }
.salto { page-break-before: always; }
"""


def html(modo: str) -> str:
    dias = guion(modo)
    total = dias[-1]["fin"]
    h = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>MICAI 2026 script</title>"
         f"<style>{CSS}</style></head><body>",
         f"<h1>MICAI 2026 · {TITULOS[modo]}</h1>",
         f"<div class='meta'>{escape(SESION['dia'])}, {SESION['turno']} h, {SESION['sala']}. "
         f"Total {mmss(total)} min (límite 10 min + 5 de preguntas). "
         "En el congreso se dice solo el texto grande, en inglés. El gris es la traducción. "
         "✂ = se puede saltar si vas tarde.</div>"]
    for d in dias:
        cls = "e1" if d["quien"] == E1 else "e2"
        quien = f"<span class='who {cls}'>{escape(d['quien'])}</span> " if d["quien"] else ""
        h.append("<div class='slide'><div class='cab'>"
                 f"<b>{d['n']} · {escape(d['titulo'])}</b>"
                 f"<span>{quien}<span class='t'>{d['seg']} s · {mmss(d['ini'])} → {mmss(d['fin'])}</span></span></div>")
        for en in d["en"]:
            marca = "✂ " if en.startswith("✂") else ""
            h.append(f"<div class='en'>{marca}{escape(plano(en))}</div>")
        if d.get("pase"):
            h.append(f"<div class='pase'>→ {escape(d['pase'])}</div>")
        es = " ".join(d["es"]) + (f" → {d['pase_es']}" if d.get("pase_es") else "")
        h.append(f"<div class='es'>{escape(es)}</div></div>")
    h.append("<h2 class='salto'>Versión de 2 minutos (solo si piden recortar)</h2>"
             "<div class='meta'>Una sola persona; solo las diapositivas "
             + ", ".join(str(b["n"]) for b in VERSION_CORTA) + " (número + Enter).</div>")
    for b in VERSION_CORTA:
        h.append(f"<div class='slide'><div class='cab'><b>Diapositiva {b['n']}</b></div>")
        h += [f"<div class='en'>{escape(plano(en))}</div>" for en in b["en"]]
        h.append(f"<div class='es'>{escape(' '.join(b['es']))}</div></div>")
    h.append("<h2 class='salto'>Preguntas probables</h2>")
    i = 0
    for letra, tema, ps in TEMAS_PREGUNTAS:
        h.append(f"<h3>{letra}. {escape(tema)}</h3>")
        for q in ps:
            i += 1
            quien = f" · {escape(q['quien'])}" if modo == "dos" else ""
            ayuda = f" (Ayuda: diapositiva {q['respaldo']}.)" if q.get("respaldo") else ""
            h.append(f"<div class='q'><b>{i}. {escape(q['q'])}</b> <span class='t'>({escape(q['q_es'])}{quien})</span>"
                     f"<div class='claves'>Si oyes: {escape(q['claves'])}</div>"
                     f"<div class='en'>{escape(q['a'])}</div>"
                     f"<div class='es'>{escape(q['a_es'])}{ayuda}</div></div>")
    h.append("<h2>Frases de apoyo</h2><table><tr><th>Inglés</th><th>Español</th><th>Se dice</th></tr>")
    for en, es, pr, _ in frases_apoyo(modo):
        h.append(f"<tr><td><b>{escape(en)}</b></td><td>{escape(es)}</td><td>{escape(pr)}</td></tr>")
    h.append("</table><h2>Si el moderador te dice…</h2><table><tr><th>Oyes</th><th>Haces</th></tr>")
    for oyes, haces in MODERADOR:
        h.append(f"<tr><td>{escape(oyes)}</td><td>{escape(haces)}</td></tr>")
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
    for modo, nombre in NOMBRES.items():
        (SALIDA / f"{nombre}.md").write_text(markdown(modo), encoding="utf-8")
        hp = AQUI / f"{nombre}.html"
        hp.write_text(html(modo), encoding="utf-8")
        ok = a_pdf(hp, SALIDA / f"{nombre}.pdf")
        if ok:
            hp.unlink()
        print(f"{nombre}: {mmss(guion(modo)[-1]['fin'])} min" + ("" if ok else " (sin PDF: no se encontró Chrome ni Edge)"))

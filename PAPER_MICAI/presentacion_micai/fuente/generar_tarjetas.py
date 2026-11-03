"""Genera las tarjetas para exponer en MICAI 2026, listas para imprimir:

    presentacion_micai/TARJETAS_UN_EXPOSITOR.pdf     (la versión principal)
    presentacion_micai/TARJETAS_DOS_EXPOSITORES.pdf  (la alternativa)

Hoja carta horizontal con dos tarjetas de media carta por cara: se imprime a
tamaño real, a una cara, y se corta por la línea punteada. Cada tarjeta trae el
texto en inglés, un renglón por pausa; las palabras difíciles con su
pronunciación; qué señalar y en qué minuto se debe ir. Después vienen las
preguntas probables por tema, las frases de apoyo y la versión de 2 minutos.

Todo el texto sale de guion.py. El tamaño de letra de cada tarjeta se ajusta solo
(lo más grande que quepa) y el script se detiene si algo no cabe.

Uso (desde la raíz del repositorio del artículo; dentro del TT, PAPER_MICAI/):

    python presentacion_micai/fuente/generar_tarjetas.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from html import escape
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from generar_guion import NAVEGADORES, frases_apoyo, mmss  # noqa: E402
from guion import (CIFRAS, E1, E2, MODERADOR, NOMBRE_1, NOMBRE_2, RESPALDO, SESION,  # noqa: E402
                   TEMAS_PREGUNTAS, VERSION_CORTA, guion)

SALIDA = AQUI.parent
ARCHIVOS = {"uno": "TARJETAS_UN_EXPOSITOR", "dos": "TARJETAS_DOS_EXPOSITORES"}
COLOR = {E1: "#1f3c88", E2: "#d81b60"}
NOMBRE = {E1: NOMBRE_1.split()[0], E2: NOMBRE_2.split()[0]}

CSS = """
@page { size: 11in 8.5in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; color: #111827;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.hoja { position: relative; width: 11in; height: 8.5in; display: flex; overflow: hidden; page-break-after: always; }
.hoja:last-child { page-break-after: auto; }
.hoja::after { content: ""; position: absolute; top: 0; bottom: 0; left: 5.5in; border-left: 1px dashed #9ca3af; }
.tarjeta { position: relative; width: 5.5in; height: 8.5in; padding: .3in .32in .27in; display: flex; flex-direction: column; overflow: hidden; }
.banda { position: absolute; left: 0; right: 0; top: 0; height: .13in; }
header { display: flex; gap: .13in; align-items: center; border-bottom: 2px solid #1f3c88; padding-bottom: .08in; margin-bottom: .12in; flex: none; }
.num { flex: none; min-width: .58in; height: .58in; padding: 0 .08in; border-radius: .09in; background: #1f3c88; color: #fff;
       font-size: 29pt; font-weight: bold; display: flex; align-items: center; justify-content: center; }
.num.chico { font-size: 13pt; }
.tit { flex: 1; min-width: 0; }
.t1 { font-size: 13pt; font-weight: bold; color: #1f3c88; line-height: 1.12; }
.t2 { font-size: 10.5pt; color: #4b5563; margin-top: 2pt; }
.quien { flex: none; color: #fff; font-weight: bold; font-size: 10pt; border-radius: .08in; padding: .03in .08in; text-align: center; line-height: 1.1; }
.cuerpo { flex: 1 1 auto; min-height: 0; overflow: hidden; line-height: 1.2; }
.fr { margin-bottom: .38em; }
.l { padding-left: .5em; text-indent: -.5em; }
.cort { position: relative; border-left: 3px solid #9ca3af; padding-left: .95em; color: #374151; }
.cort .marca { position: absolute; left: .18em; top: .02em; font-size: .78em; color: #6b7280; }
b { color: #1f3c88; }
.dig { font-size: .62em; color: #6b7280; margin-left: .2em; white-space: nowrap; }
.acc { font-size: .58em; color: #9a3412; font-style: italic; line-height: 1.2; margin: .08em 0 .14em; }
.pron { flex: none; font-size: 10.25pt; line-height: 1.25; background: #f3f4f6; border-radius: .06in; padding: .05in .09in; margin-top: .07in; }
.pron b { color: #111827; }
.pie { flex: none; display: flex; justify-content: space-between; align-items: flex-end; gap: .14in; margin-top: .07in; font-size: 10.5pt; color: #4b5563; line-height: 1.2; }
.idea { flex: 1; font-style: italic; }
.clic { flex: none; font-weight: bold; color: #1f3c88; font-size: 12.5pt; white-space: nowrap; }
.pase { margin-top: .1em; padding-top: .28em; border-top: 2px solid #d81b60; color: #d81b60; font-weight: bold; }
.pase small { display: block; font-size: .58em; font-weight: normal; color: #4b5563; margin-top: .15em; }

/* Tarjetas de texto (antes de empezar, frases, si algo falla) */
.grande { font-size: 1.32em; font-weight: bold; color: #1f3c88; line-height: 1.15; margin-bottom: .2em; }
.nota { color: #4b5563; font-size: .86em; margin-bottom: .5em; }
h4 { margin: .55em 0 .22em; font-size: 1.02em; color: #1f3c88; border-bottom: 1px solid #d1d5db; padding-bottom: .08em; }
ul { margin: 0; padding-left: 1.05em; }
li { margin-bottom: .26em; }
.en { font-weight: bold; color: #111827; }
.pr { color: #6b7280; font-size: .84em; }
.es2 { color: #4b5563; font-size: .84em; }
.f { margin-bottom: .34em; }
.dup { display: grid; grid-template-columns: 2.25em 1fr; column-gap: .3em; row-gap: .28em; }
.dup .k { font-weight: bold; color: #1f3c88; }

/* Preguntas */
.qa { margin-bottom: .62em; padding-bottom: .46em; border-bottom: 1px solid #d1d5db; }
.qa:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.oyes { font-size: .78em; color: #4b5563; margin-bottom: .1em; }
.oyes b { color: #9a3412; }
.q { font-size: .82em; font-style: italic; color: #374151; margin-bottom: .12em; }
.a { line-height: 1.19; }
.a span.nb { font-weight: bold; color: #1f3c88; }
.gist { font-size: .74em; color: #6b7280; margin-top: .14em; line-height: 1.15; }
.ayuda { font-size: .74em; color: #9a3412; font-style: italic; margin-top: .1em; }
.cont { display: inline-block; color: #fff; font-size: .68em; font-weight: bold; border-radius: .3em; padding: 0 .4em; margin-right: .3em; font-style: normal; }
"""

# Ajusta cada .cuerpo a lo más grande que quepa, sin pasar de su máximo.
JS = """
document.querySelectorAll('.cuerpo').forEach(function (c) {
  var maxi = parseFloat(c.dataset.max), mini = parseFloat(c.dataset.min), s = maxi;
  c.style.fontSize = s + 'pt';
  while (c.scrollHeight > c.clientHeight + 0.5 && s > mini) { s -= 0.25; c.style.fontSize = s + 'pt'; }
  c.dataset.final = s;
  c.dataset.sobra = c.scrollHeight > c.clientHeight + 0.5 ? '1' : '0';
});
"""


def _en_linea(t: str) -> str:
    """**negritas** y {cifra en gris} dentro de un renglón."""
    t = escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\{(.+?)\}", r"<span class='dig'>\1</span>", t)
    return t


def frase(s: str) -> str:
    """Una frase del guion: un renglón por cada |, y las indicaciones [[…]] aparte."""
    cortable = s.startswith("✂")
    s = s.lstrip("✂ ").strip()
    partes = []
    for renglon in s.split("|"):
        for trozo in re.split(r"(\[\[.*?\]\])", renglon):
            trozo = trozo.strip()
            if not trozo:
                continue
            if trozo.startswith("[["):
                partes.append(f"<div class='acc'>► {escape(trozo[2:-2], quote=False)}</div>")
            else:
                partes.append(f"<div class='l'>{_en_linea(trozo)}</div>")
    html = "".join(partes)
    if cortable:
        return f"<div class='fr cort'><span class='marca'>✂</span>{html}</div>"
    return f"<div class='fr'>{html}</div>"


def tarjeta(num: str, t1: str, t2: str, cuerpo: str, *, maxi=20.0, mini=15.0, pron="", pie="", quien=None,
            num_chico=False) -> str:
    banda = f"<div class='banda' style='background:{COLOR[quien]}'></div>" if quien else ""
    etiqueta = (f"<div class='quien' style='background:{COLOR[quien]}'>{escape(quien.upper())}<br>{escape(NOMBRE[quien])}</div>"
                if quien else "")
    return (f"<section class='tarjeta'>{banda}<header>"
            f"<div class='num{' chico' if num_chico else ''}'{f' style=background:{COLOR[quien]}' if quien else ''}>{num}</div>"
            f"<div class='tit'><div class='t1'>{escape(t1)}</div><div class='t2'>{t2}</div></div>{etiqueta}</header>"
            f"<div class='cuerpo' data-max='{maxi}' data-min='{mini}'>{cuerpo}</div>{pron}{pie}</section>")


def tarjeta_antes(modo: str) -> str:
    s = SESION
    frase_mod = ("Good afternoon. We are presenting paper 78. May we load our slides?" if modo == "dos"
                 else "Good afternoon. I am presenting paper 78. May I load my slides?")
    pron_mod = ("gud af-ter-NÚN. ui ar pri-SÉN-ting PÉI-per SÉ-ven-ti ÉIT. mei ui LOUD áur SLÁIDS?" if modo == "dos"
                else "gud af-ter-NÚN. ai am pri-SÉN-ting PÉI-per SÉ-ven-ti ÉIT. mei ai LOUD mai SLÁIDS?")
    total = mmss(guion(modo)[-1]["fin"])
    quienes = ""
    if modo == "dos":
        g = guion("dos")
        n1 = ", ".join(str(d["n"]) for d in g if d["quien"] == E1)
        n2 = ", ".join(str(d["n"]) for d in g if d["quien"] == E2)
        quienes = (f"<h4>Quién dice qué</h4><ul><li><b>Expositor 1 ({escape(NOMBRE_1)}):</b> {n1}.</li>"
                   f"<li><b>Expositor 2 ({escape(NOMBRE_2)}):</b> {n2}.</li>"
                   "<li>Separa las tarjetas por color. Las de preguntas sirven a los dos: imprímelas dos veces.</li></ul>")
    c = (f"<div class='grande'>{escape(s['dia'].replace(' de 2026', ''))}<br>{s['turno']} h · {escape(s['sala'])}</div>"
         f"<div class='nota'>Sesión <i>{escape(s['nombre'])}</i> ({s['horario']}), {escape(s['sede'])}. "
         f"Paper ID <b>{s['paper_id']}</b>. 10 min + 5 de preguntas. Tu meta: {total}.</div>"
         "<h4>Antes de tu turno</h4><ul>"
         "<li>El programa puede cambiar: revísalo el miércoles en la noche y el jueves en la mañana "
         "(micai.org/2026/activities).</li>"
         "<li>Llega a la sala a las <b>15:45</b> y quédate desde el inicio: de 16:20 a 16:40 el programa está "
         "vacío y podrían adelantarte.</li>"
         f"<li>Busca al moderador y dile: <span class='en'>{escape(frase_mod)}</span> "
         f"<span class='pr'>{escape(pron_mod)}</span></li>"
         "<li>Carga el .pptx de la USB y revisa las diapositivas 5 y 9 (tienen gráficas). Si algo se ve mal, usa el .pdf.</li>"
         "<li>Cronómetro a la vista, celular en silencio, agua cerca.</li></ul>"
         f"{quienes}"
         "<h4>Cómo leer las tarjetas</h4><ul>"
         "<li>Cada renglón es una pausa: habla despacio, los nervios aceleran.</li>"
         "<li><span style='color:#9a3412;font-style:italic'>► Naranja:</span> qué hacer; no se lee.</li>"
         "<li><span class='dig' style='margin:0'>0.399</span> gris: la cifra que se ve en pantalla; no se lee.</li>"
         "<li>✂ La frase se puede saltar si vas tarde.</li>"
         "<li>Números: 0.404 = <i>zero point four zero four</i> · 15.5 % = <i>fifteen point five percent</i>.</li></ul>"
         "<h4>Para imprimir</h4><div class='nota' style='margin:0'>Tamaño real (100 %), a una cara, hoja carta. "
         "Corta por la línea punteada.</div>")
    return tarjeta("Antes", "Antes de empezar", "Tu turno en MICAI 2026", c, maxi=15, mini=11.5, num_chico=True)


def tarjetas_diapositivas(modo: str) -> list[str]:
    dias = guion(modo)
    out = []
    for i, d in enumerate(dias):
        cuerpo = "".join(frase(s) for s in d["en"])
        if d.get("pase"):
            sigue = dias[i + 1]
            nombre = NOMBRE[sigue["quien"]]
            cuerpo += (f"<div class='pase'>→ {escape(d['pase'])}"
                       f"<small>Pasa la palabra. {escape(nombre)} sigue con la diapositiva {sigue['n']}.</small></div>")
        pron = ("<div class='pron'><b>Pronuncia:</b> "
                + " · ".join(f"<b>{escape(w)}</b> {escape(p)}" for w, p in d["pron"]) + "</div>")
        if i + 1 < len(dias):
            clic = f"CLIC ▶ {dias[i + 1]['n']}"
        else:
            clic = "Deja esta diapositiva"
        pie = f"<div class='pie'><div class='idea'>Idea: {escape(d['idea'])}</div><div class='clic'>{clic}</div></div>"
        t2 = f"Diapositiva {d['n']} de {len(dias)} · minuto {mmss(d['ini'])} → <b>{mmss(d['fin'])}</b>"
        out.append(tarjeta(str(d["n"]), d["titulo_en"], t2, cuerpo, pron=pron, pie=pie, quien=d["quien"]))
    return out


def tarjeta_indice_preguntas(modo: str) -> str:
    filas = "".join(f"<div class='k'>{letra}</div><div><b>{escape(tema)}</b><br>"
                    f"<span class='pr'>{escape(' · '.join(c for q in ps for c in q['claves'].split(' · ')[:2]))}</span></div>"
                    for letra, tema, ps in TEMAS_PREGUNTAS)
    respaldo = "".join(f"<li><b>{n}</b> + Enter: {escape(desc)}</li>" for n, desc in RESPALDO.items())
    c = ("<h4 style='margin-top:0'>Cómo contestar</h4><ul>"
         "<li>Deja puesta la diapositiva 11: ahí está el enlace al código.</li>"
         "<li>Escucha una <b>palabra clave</b>. Si no la oíste, pide que repitan.</li>"
         "<li>Busca la letra de abajo y lee la respuesta corta.</li>"
         "<li>Si piden una cifra exacta: tarjeta <b>Cifras</b>.</li>"
         "<li>Contesta corto. Si no sabes: <span class='en'>We can talk more after the session.</span></li></ul>"
         f"<h4>Por tema</h4><div class='dup'>{filas}</div>"
         f"<h4>Diapositivas de respaldo</h4><ul>{respaldo}</ul>")
    return tarjeta("?", "Preguntas: índice", "5 minutos después de exponer", c, maxi=15.5, mini=11.5)


def tarjeta_frases(modo: str) -> str:
    frases = "".join(f"<div class='f'><span class='en'>{escape(en)}</span><br><span class='pr'>{escape(pr)}</span> "
                     f"<span class='es2'>· {escape(es)}</span></div>" for en, es, pr, _ in frases_apoyo(modo))
    mod = "".join(f"<li><b>{escape(o)}</b> {escape(h)}</li>" for o, h in MODERADOR)
    falla = ("<li><b>No abre el .pptx o se ve mal:</b> abre el .pdf de la USB.</li>"
             "<li><b>Te perdiste:</b> lee el título de la diapositiva y busca la tarjeta con ese número.</li>"
             "<li><b>Se te fue una palabra:</b> señala la gráfica y di el número.</li>")
    c = (f"<h4 style='margin-top:0'>Frases de apoyo</h4>{frases}"
         f"<h4>Si el moderador te dice…</h4><ul>{mod}</ul>"
         f"<h4>Si algo falla</h4><ul>{falla}</ul>")
    return tarjeta("Ayuda", "Frases y emergencias", "Para cualquier momento", c, maxi=14.5, mini=10.5, num_chico=True)


def _respuesta(a: str) -> str:
    """Una oración por renglón y las cifras en negritas."""
    oraciones = re.split(r"(?<=[.?!:])\s+(?=[A-Z])", a)
    out = []
    for o in oraciones:
        o = escape(o, quote=False)
        o = re.sub(r"(?<![\w.,])(?<!Section )(\d[\d.,]*\d|\d)(?![\w])", r"<span class='nb'>\1</span>", o)
        out.append(f"<div class='l'>{o}</div>")
    return "".join(out)


def tarjetas_preguntas(modo: str) -> list[str]:
    out = []
    for letra, tema, ps in TEMAS_PREGUNTAS:
        c = ""
        for q in ps:
            cont = ""
            if modo == "dos":
                cont = f"<span class='cont' style='background:{COLOR[q['quien']]}'>{escape(NOMBRE[q['quien']])}</span>"
            ayuda = ""
            if q.get("respaldo"):
                ayuda = (f"<div class='ayuda'>► Ayuda: {q['respaldo']} + Enter. "
                         "Di: Let me show you a backup slide.</div>") if q["respaldo"] != 10 else (
                         f"<div class='ayuda'>► Ayuda: {q['respaldo']} + Enter.</div>")
            c += (f"<div class='qa'><div class='oyes'>{cont}Si oyes: <b>{escape(q['claves'])}</b></div>"
                  f"<div class='q'>{escape(q['q'])}</div><div class='a'>{_respuesta(q['a'])}</div>"
                  f"<div class='gist'>{escape(q['a_es'])}</div>{ayuda}</div>")
        out.append(tarjeta(letra, tema, "Preguntas probables", c, maxi=17, mini=12.5))
    return out


def tarjeta_cifras(modo: str) -> str:
    c = ""
    for i, (bloque, filas) in enumerate(CIFRAS):
        estilo = " style='margin-top:0'" if i == 0 else ""
        c += f"<h4{estilo}>{escape(bloque)}</h4>"
        c += "".join(f"<div class='f'><b>{escape(k)}:</b> {escape(v)}</div>" for k, v in filas)
    return tarjeta("Cifras", "Cifras clave", "Para contestar preguntas; no se leen en la exposición", c,
                   maxi=14, mini=10.5, num_chico=True)


def tarjeta_corta(modo: str) -> str:
    c = ""
    for b in VERSION_CORTA:
        c += f"<div class='acc' style='font-size:.72em;font-weight:bold'>► {b['n']} + Enter</div>"
        c += "".join(frase(s) for s in b["en"])
    return tarjeta("2 min", "Versión de 2 minutos", "Solo si el moderador pide recortar. La dice una persona.",
                   c, maxi=18, mini=13, num_chico=True)


def documento(modo: str) -> str:
    tarjetas = [tarjeta_antes(modo)] + tarjetas_diapositivas(modo) + [tarjeta_indice_preguntas(modo), tarjeta_frases(modo)]
    tarjetas += tarjetas_preguntas(modo) + [tarjeta_cifras(modo), tarjeta_corta(modo)]
    if len(tarjetas) % 2:
        tarjetas.append("<section class='tarjeta'></section>")
    hojas = "".join(f"<div class='hoja'>{tarjetas[i]}{tarjetas[i + 1]}</div>" for i in range(0, len(tarjetas), 2))
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>{ARCHIVOS[modo]}</title>"
            f"<style>{CSS}</style></head><body>{hojas}<script>{JS}</script></body></html>")


def navegador() -> str:
    import shutil
    for n in NAVEGADORES:
        nav = n if Path(n).exists() else shutil.which(n)
        if nav:
            return nav
    sys.exit("No se encontró Chrome ni Edge para generar el PDF.")


def generar(modo: str) -> None:
    nombre = ARCHIVOS[modo]
    hp = AQUI / f"{nombre}.html"
    hp.write_text(documento(modo), encoding="utf-8")
    nav = navegador()
    base = [nav, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=4000"]
    # 1) Comprueba que todo cabe, con el mismo tamaño de hoja que el PDF.
    dom = subprocess.run(base + ["--dump-dom", hp.as_uri()], check=True, capture_output=True, timeout=120,
                         encoding="utf-8", errors="replace").stdout
    finales = re.findall(r'data-final="([\d.]+)" data-sobra="(\d)"', dom)
    if not finales:
        sys.exit("No se pudo medir el tamaño de las tarjetas.")
    sobran = [i + 1 for i, (_, sobra) in enumerate(finales) if sobra == "1"]
    if sobran:
        sys.exit(f"{nombre}: no cabe el texto de las tarjetas {sobran} (se conserva {hp.name} para revisarlo).")
    # 2) El PDF.
    pdf = SALIDA / f"{nombre}.pdf"
    subprocess.run(base + [f"--print-to-pdf={pdf}", hp.as_uri()], check=True, capture_output=True, timeout=120)
    hp.unlink()
    tamanos = [float(f) for f, _ in finales]
    print(f"{nombre}: {len(tamanos)} tarjetas, {(len(tamanos) + 1) // 2} hojas · letra de {min(tamanos):g} a {max(tamanos):g} pt")
    print("   por tarjeta:", " ".join(f"{t:g}" for t in tamanos))


if __name__ == "__main__":
    for modo in ARCHIVOS:
        generar(modo)

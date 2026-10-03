"""
Compila el paper MICAI 2026 (paper_review/camera_ready/) y genera:

1. El paquete para Springer, en paper_review/_envio_springer/ (carpeta
   ignorada por git; NO se sube):
       078_corrected.zip  ->  paper.tex, llncs.cls, figures/, 078.pdf
   Misma estructura que el paquete 078.zip enviado el 8-sep-2026.

2. La copia pública del repositorio, paper_review/paper.pdf: el mismo PDF con
   el aviso que exige la Licence to Publish (cláusula 4(c)) al pie de la
   primera página. La licencia permite publicar el Accepted Manuscript en el
   sitio personal del autor desde la aceptación, siempre que lleve ese aviso
   con el enlace a la Version of Record. Cuando Springer publique el capítulo:
       python paper_review/compilar_paper.py --doi 10.1007/XXXXX
   y subir el paper.pdf resultante.

Requiere pdflatex (MiKTeX con el paquete cm-super para fuentes vectoriales) y
pypdf (pip install pypdf).
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

AQUI = Path(__file__).resolve().parent
FUENTE = AQUI / "camera_ready"
ENVIO = AQUI / "_envio_springer"
PUBLICO = AQUI / "paper.pdf"

AVISO = (
    r"This version of the contribution has been accepted for publication, after peer review "
    r"(when applicable) but is not the Version of Record and does not reflect post-acceptance "
    r"improvements, or any corrections. {vor} Use of this Accepted Version is subject to the "
    r"publisher's Accepted Manuscript terms of use "
    r"\url{{https://www.springernature.com/gp/open-research/policies/accepted-manuscript-terms}}."
)


def pdflatex() -> str:
    exe = shutil.which("pdflatex")
    if exe:
        return exe
    miktex = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64" / "pdflatex.exe"
    if miktex.exists():
        return str(miktex)
    sys.exit("No se encontró pdflatex (winget install MiKTeX.MiKTeX; luego: miktex packages install cm-super).")


def compilar(carpeta: Path, archivo: str) -> Path:
    for _ in range(2):
        r = subprocess.run([pdflatex(), "-interaction=nonstopmode", "-halt-on-error", archivo],
                           cwd=carpeta, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(r.stdout[-3000:])
            sys.exit(f"pdflatex falló con {archivo}")
    log = (carpeta / Path(archivo).with_suffix(".log")).read_text(encoding="utf-8", errors="replace")
    malas = [l for l in log.splitlines() if "Warning" in l and ("undefined" in l.lower() or "Rerun to get" in l)]
    if malas:
        sys.exit("Referencias sin resolver:\n" + "\n".join(malas))
    return carpeta / Path(archivo).with_suffix(".pdf")


def capa_aviso(ancho_pt: float, alto_pt: float, doi: str | None, tmp: Path) -> Path:
    """Página del mismo tamaño que el paper, vacía salvo el aviso al pie."""
    vor = (rf"The Version of Record is available online at: \url{{http://dx.doi.org/{doi}}}."
           if doi else r"The Version of Record will be available online at: http://dx.doi.org/ "
                       r"(DOI to be added upon publication).")
    tex = rf"""\documentclass{{article}}
\usepackage[T1]{{fontenc}}
\usepackage[paperwidth={ancho_pt}bp,paperheight={alto_pt}bp,margin=0pt]{{geometry}}
\usepackage[hyphens]{{url}}
\pagestyle{{empty}}
\begin{{document}}
\vspace*{{\fill}}
\begin{{center}}\begin{{minipage}}{{122mm}}\scriptsize\raggedright
\rule{{\linewidth}}{{0.3pt}}\\[1pt]
{AVISO.format(vor=vor)}
\end{{minipage}}\end{{center}}
\vspace*{{14mm}}
\end{{document}}
"""
    (tmp / "aviso.tex").write_text(tex, encoding="utf-8")
    return compilar(tmp, "aviso.tex")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doi", help="DOI del capítulo publicado (p. ej. 10.1007/978-3-...)")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        shutil.copytree(FUENTE, tmp / "paper")
        pdf = compilar(tmp / "paper", "paper.tex")
        n = len(PdfReader(pdf).pages)
        if n > 12:
            sys.exit(f"El paper tiene {n} páginas (límite LNCS: 12).")

        # 1) Paquete para Springer (sin aviso)
        ENVIO.mkdir(exist_ok=True)
        destino = ENVIO / "078_corrected.zip"
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(pdf, "078.pdf")
            z.write(FUENTE / "paper.tex", "paper.tex")
            z.write(FUENTE / "llncs.cls", "llncs.cls")
            for fig in sorted((FUENTE / "figures").glob("*.png")):
                z.write(fig, f"figures/{fig.name}")
        print(f"Paquete Springer: {destino} ({n} páginas)")

        # 2) Copia pública con el aviso de la licencia en la página 1
        caja = PdfReader(pdf).pages[0].mediabox
        capa = capa_aviso(float(caja.width), float(caja.height), args.doi, tmp)
        lector = PdfReader(pdf)
        salida = PdfWriter()
        for i, pagina in enumerate(lector.pages):
            if i == 0:
                pagina.merge_page(PdfReader(capa).pages[0])
            salida.add_page(pagina)
        with open(PUBLICO, "wb") as f:
            salida.write(f)
        print(f"Copia pública:    {PUBLICO} ({'con DOI ' + args.doi if args.doi else 'DOI pendiente'})")


if __name__ == "__main__":
    main()

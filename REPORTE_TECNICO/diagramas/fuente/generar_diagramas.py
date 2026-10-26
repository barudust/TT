"""Genera los diagramas del reporte técnico en SVG y PNG.

Uso (desde la raíz del repositorio):

    python REPORTE_TECNICO/diagramas/fuente/generar_diagramas.py
    python REPORTE_TECNICO/diagramas/fuente/generar_diagramas.py D05   # solo uno

Escribe `REPORTE_TECNICO/diagramas/Dxx_nombre.svg` y `.png`. El PNG se
exporta con Chrome (o Edge) sin interfaz, al doble de resolución. Si no hay
navegador, solo se escriben los SVG (Word 365 los inserta directamente).
Para cambiar un texto, editar `diagramas_sistema.py` o
`diagramas_metodologia.py` y volver a correr este script.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import estilo  # noqa: E402
import diagramas_metodologia as dm  # noqa: E402
import diagramas_sistema as ds  # noqa: E402

SALIDA = AQUI.parent

DIAGRAMAS = {
    "D01_arquitectura": ds.d01_arquitectura,
    "D02_investigacion_a_produccion": ds.d02_investigacion_a_produccion,
    "D03_actualizacion_diaria": ds.d03_actualizacion_diaria,
    "D04_entidad_relacion": ds.d04_entidad_relacion,
    "D05_pantallas": ds.d05_pantallas,
    "D06_secuencia": ds.d06_secuencia,
    "D07_despliegue": ds.d07_despliegue,
    "D08_etapas": dm.d08_etapas,
    "D09_particiones": dm.d09_particiones,
    "D10_etiqueta": dm.d10_etiqueta,
    "D11_protocolo": dm.d11_protocolo,
    "D12_mismas_filas": dm.d12_mismas_filas,
}

NAVEGADORES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "msedge",
]


def navegador() -> str | None:
    for n in NAVEGADORES:
        if Path(n).exists():
            return n
        ruta = shutil.which(n)
        if ruta:
            return ruta
    return None


def exportar_png(nav: str, svg: Path, png: Path, ancho: int, alto: int) -> None:
    # Una página HTML mínima evita márgenes y fija el tamaño exacto.
    html = svg.with_suffix(".tmp.html")
    html.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        "html,body{margin:0;padding:0;background:#fff}img{display:block}"
        f"</style></head><body><img src='{svg.name}' width='{ancho}' height='{alto}'></body></html>",
        encoding="utf-8")
    try:
        subprocess.run([nav, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--window-size={ancho},{alto}",
                        f"--screenshot={png}", html.as_uri()],
                       check=True, capture_output=True, timeout=120)
    finally:
        html.unlink(missing_ok=True)


def main(solo: list[str]) -> None:
    nav = navegador()
    if nav is None:
        print("Aviso: no se encontró Chrome ni Edge; solo se escriben los SVG.")
    for nombre, fn in DIAGRAMAS.items():
        if solo and not any(nombre.startswith(s) for s in solo):
            continue
        estilo.AVISOS.clear()
        lienzo = fn()
        svg = SALIDA / f"{nombre}.svg"
        svg.write_text(lienzo.svg(), encoding="utf-8")
        if nav:
            exportar_png(nav, svg, SALIDA / f"{nombre}.png", lienzo.ancho, lienzo.alto)
        print(f"{nombre}: {lienzo.ancho}×{lienzo.alto}" + (f"  ({len(estilo.AVISOS)} avisos)" if estilo.AVISOS else ""))
        for a in estilo.AVISOS:
            print("   ", a)


if __name__ == "__main__":
    main(sys.argv[1:])

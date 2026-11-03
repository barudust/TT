"""Copia a una carpeta, o directo a la USB, lo que hay que llevar al congreso.

Uso (desde la raíz del repositorio del artículo; dentro del TT, PAPER_MICAI/):

    python presentacion_micai/fuente/preparar_usb.py              # a presentacion_micai/para_usb/
    python presentacion_micai/fuente/preparar_usb.py E:/MICAI2026  # a la USB
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

PRES = Path(__file__).resolve().parents[1]
RAIZ = PRES.parent

# (origen, nombre en la USB, para qué)
ARCHIVOS = [
    (PRES / "MICAI2026_benchmark_trading_signals.pptx", None, "la presentación"),
    (PRES / "MICAI2026_benchmark_trading_signals.pdf", None, "respaldo por si el .pptx no abre o se ve mal"),
    (PRES / "TARJETAS_UN_EXPOSITOR.pdf", None, "tarjetas, por si hay que volver a imprimirlas"),
    (PRES / "TARJETAS_DOS_EXPOSITORES.pdf", None, "tarjetas, alternativa para dos"),
    (PRES / "GUION_UN_EXPOSITOR.pdf", None, "guion con traducción"),
    (PRES / "GUION_DOS_EXPOSITORES.pdf", None, "guion con traducción, alternativa para dos"),
    (RAIZ / "paper_review" / "paper.pdf", "MICAI2026_articulo.pdf", "el artículo"),
    (RAIZ / "paper_review" / "supplementary" / "MICAI2026_ch171490174_supplementary.pdf", None, "material suplementario"),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else PRES / "para_usb"
    destino.mkdir(parents=True, exist_ok=True)
    total = 0
    for origen, nombre, para in ARCHIVOS:
        final = destino / (nombre or origen.name)
        shutil.copy2(origen, final)
        total += final.stat().st_size
        print(f"{final.stat().st_size / 1e6:6.1f} MB  {final.name}  ({para})")
    print(f"{total / 1e6:6.1f} MB en {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

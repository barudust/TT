"""Comprueba que los datos guardados son los mismos que usó el artículo.

Compara el SHA-256 de cada `tesis_ml_stocks/01_raw_datasets/<TICKER>_raw.parquet`
con el que publica la Tabla S5 del material suplementario, y cuenta filas y
fechas. Si todo coincide, cualquier script de `scripts_opt/` parte de los mismos
datos que el artículo.

Uso (desde la raíz del repositorio del artículo; dentro del TT, PAPER_MICAI/):

    python verificar_datos.py
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "tesis_ml_stocks" / "01_raw_datasets"
SUPLEMENTARIO = AQUI / "paper_review" / "supplementary" / "MICAI2026_ch171490174_supplementary.tex"
FILA = re.compile(r"^([A-Z]+) & (\d{4}-\d{2}-\d{2}) & (\d{4}-\d{2}-\d{2}) & ([\d,]+) & .*\\texttt\{([0-9a-f]{64})\}")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    esperado = {m[1]: m.groups()[1:] for l in SUPLEMENTARIO.read_text(encoding="utf-8").splitlines()
                if (m := FILA.match(l))}
    if len(esperado) != 7:
        sys.exit(f"No se encontraron las 7 filas de la Tabla S5 en {SUPLEMENTARIO.name}")

    try:
        import pandas as pd
    except ImportError:
        pd = None

    errores = 0
    for ticker, (ini, fin, filas, sha) in esperado.items():
        p = DATOS / f"{ticker}_raw.parquet"
        if not p.exists():
            print(f"✗ {ticker}: falta {p.relative_to(AQUI)}")
            errores += 1
            continue
        ok = hashlib.sha256(p.read_bytes()).hexdigest() == sha
        detalle = ""
        if pd is not None:
            df = pd.read_parquet(p)
            idx = pd.to_datetime(df.index if "date" not in df.columns else df["date"])
            real = (str(idx.min().date()), str(idx.max().date()), f"{len(df):,}")
            ok = ok and real == (ini, fin, filas)
            detalle = f" · {real[2]} filas, {real[0]} a {real[1]}"
        print(f"{'✓' if ok else '✗'} {ticker}: SHA-256 {'coincide' if ok else 'NO coincide'}{detalle}")
        errores += not ok

    print("\nTodo coincide con la Tabla S5." if not errores else f"\n{errores} archivo(s) no coinciden.")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())

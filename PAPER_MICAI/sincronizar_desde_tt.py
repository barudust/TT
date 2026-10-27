"""Copia al repositorio del artículo los archivos del TT que el artículo cita.

Las carpetas `paper_review/`, `scripts_v1/`, `scripts_opt/`,
`RESULTADOS_OPTIMIZADOS/`, `tesis_ml_stocks/` y `ESTUDIO_TT/` de este
repositorio son **copia exacta** de las del repositorio del TT
(https://github.com/barudust/TT), con las mismas rutas. Así los scripts corren
sin cambios desde la raíz de este repositorio y las rutas de la Tabla S4 del
material suplementario siguen siendo válidas.

Solo funciona cuando esta carpeta está dentro del repositorio del TT
(`TT/PAPER_MICAI/`). Solo copia archivos **versionados** en el TT
(`git ls-files`), así que nunca trae lo que el TT excluye por privado (el
formulario de copyright, el `078.zip`, `paper_review/_envio_springer/`).

Uso (desde cualquier carpeta):

    python PAPER_MICAI/sincronizar_desde_tt.py            # solo revisa diferencias
    python PAPER_MICAI/sincronizar_desde_tt.py --copiar   # copia lo que cambió
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TT = AQUI.parent

# Rutas relativas a la raíz del TT. Una carpeta trae todos sus archivos versionados.
COPIAS = [
    # Artículo: LaTeX, PDF público, suplementario, figuras y scripts de compilación
    "paper_review",
    # Datos, variables y etiqueta (§3)
    "scripts_v1/01_build_raw_dataset.py",
    "tesis_ml_stocks/01_raw_datasets",
    # Código del artículo (Tabla S4 del suplementario) y su módulo común
    "scripts_opt/common.py",
    "scripts_opt/common_v4.py",
    "scripts_opt/common_v5.py",
    "scripts_opt/analisis_feature_selection.py",
    "scripts_opt/train_all_v4.py",
    "scripts_opt/consolidar_v4.py",
    "scripts_opt/run_v5.py",
    "scripts_opt/reporte_v5.py",
    "scripts_opt/plots_paper.py",
    "scripts_opt/replicar_lr_v4.py",
    # Preselección de variables (§6): resultados de la Etapa 2 que compara
    # analisis_feature_selection.py y lo que produce
    "tesis_ml_stocks/04_models/logistic_regression/resultados_lr.csv",
    "tesis_ml_stocks/04_models/xgboost/resultados_xgb.csv",
    "tesis_ml_stocks/04_models/lstm/resultados_lstm.csv",
    "tesis_ml_stocks/04_models/cnn_lstm/resultados_cnn_lstm.csv",
    "RESULTADOS_OPTIMIZADOS/modelos_optimizados/lr/resultados_lr_opt.csv",
    "RESULTADOS_OPTIMIZADOS/modelos_optimizados/xgboost/resultados_xgb_opt.csv",
    "RESULTADOS_OPTIMIZADOS/modelos_optimizados/lstm/resultados_lstm_opt.csv",
    "RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_lstm/resultados_cnn_lstm_opt.csv",
    "RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_puro/resultados_cnn_puro.csv",
    "RESULTADOS_OPTIMIZADOS/modelos_optimizados/cnn_puro_filtradas/resultados_cnn_puro_filtradas.csv",
    "RESULTADOS_OPTIMIZADOS/reportes/feature_selection",
    # Benchmark (§7) y estudio de robustez (§8)
    "RESULTADOS_OPTIMIZADOS/v4",
    "RESULTADOS_OPTIMIZADOS/reportes/v4_final",
    "RESULTADOS_OPTIMIZADOS/v5",
    # Documentos de trabajo que respaldan §6 y §8
    "RESULTADOS_OPTIMIZADOS/docs/ANALISIS_FEATURE_SELECTION.md",
    "RESULTADOS_OPTIMIZADOS/docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md",
    "RESULTADOS_OPTIMIZADOS/docs/PLAN_MAESTRO_BUSQUEDA.md",
    "RESULTADOS_OPTIMIZADOS/docs/RESULTADOS_V5.md",
    "RESULTADOS_OPTIMIZADOS/docs/diag_deep_resultados.json",
    # Equivalencia de nombres (v4 = Etapa 3, v5 = Etapa 4…) que citan los documentos de arriba
    "ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md",
]

CARPETAS_COPIA = sorted({c.split("/")[0] for c in COPIAS})


def versionados() -> list[str]:
    r = subprocess.run(["git", "ls-files", "-z", "--", *COPIAS], cwd=TT,
                       capture_output=True, check=True)
    return sorted(p for p in r.stdout.decode("utf-8").split("\0") if p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--copiar", action="store_true", help="copiar los archivos nuevos o distintos")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if not (TT / ".git").exists() or not (TT / "scripts_opt").is_dir():
        sys.exit("Esta carpeta no está dentro del repositorio del TT; no hay de dónde copiar.")

    rutas = versionados()
    faltan = [c for c in COPIAS if not any(p == c or p.startswith(c + "/") for p in rutas)]
    if faltan:
        sys.exit("No están versionados en el TT:\n  " + "\n  ".join(faltan))

    nuevos, distintos = [], []
    for p in rutas:
        destino = AQUI / p
        if not destino.exists():
            nuevos.append(p)
        elif not filecmp.cmp(TT / p, destino, shallow=False):
            distintos.append(p)

    esperados = set(rutas)
    sobran = sorted(
        str(f.relative_to(AQUI)).replace("\\", "/")
        for c in CARPETAS_COPIA if (AQUI / c).exists()
        for f in (AQUI / c).rglob("*")
        if f.is_file() and "__pycache__" not in f.parts
        and str(f.relative_to(AQUI)).replace("\\", "/") not in esperados
    )

    print(f"{len(rutas)} archivos en la lista · {len(nuevos)} nuevos · {len(distintos)} distintos · "
          f"{len(sobran)} que ya no están en el TT")
    for titulo, lista in (("Nuevos", nuevos), ("Distintos", distintos), ("Ya no están en el TT", sobran)):
        if lista:
            print(f"\n{titulo}:")
            for p in lista[:40]:
                print(f"  {p}")
            if len(lista) > 40:
                print(f"  … y {len(lista) - 40} más")

    if not args.copiar:
        if nuevos or distintos or sobran:
            print("\nPara copiar: python PAPER_MICAI/sincronizar_desde_tt.py --copiar")
            return 1
        return 0

    for p in nuevos + distintos:
        (AQUI / p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(TT / p, AQUI / p)
    if sobran:
        print("\nLos que ya no están en el TT no se borran solos: revisarlos y borrarlos a mano.")
    print(f"\nCopiados {len(nuevos) + len(distintos)} archivos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

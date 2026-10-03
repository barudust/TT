"""
Verificación de reproducibilidad de las 24 corridas de LR del benchmark v4
(Sección 7 del paper MICAI 2026).

Ejecuta run_lr() de train_all_v4.py SIN modificarlo y compara contra
RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv. torch y xgboost se sustituyen por
módulos vacíos porque run_lr no los usa (así corre sin GPU), y la salida de
train_all_v4 se redirige: nunca escribe sobre resultados_v4.csv.

Resultado el 2026-10-02 (Python 3.13.5, scikit-learn 1.7.2): 24 de 24 corridas
idénticas en F1-macro, F1 por clase, Sharpe, win rate, profit factor y max
drawdown (diferencia máxima 0.000000).

Uso (desde la raíz del repo, ~10 min en CPU):
    python scripts_opt/replicar_lr_v4.py
Salida: RESULTADOS_OPTIMIZADOS/v4/replica_lr_v4.csv
"""
import os
import platform
import sys
import types
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "RESULTADOS_OPTIMIZADOS" / "v4" / "replica_lr_v4.csv"

# Módulos vacíos para torch y xgboost (train_all_v4 los importa al inicio)
torch = types.ModuleType("torch")
torch.device = lambda x: x
torch.cuda = types.SimpleNamespace(is_available=lambda: False)
nn = types.ModuleType("torch.nn")
nn.Module = object
torch.nn = nn
datos = types.ModuleType("torch.utils.data")
datos.DataLoader = datos.TensorDataset = object
for nombre, mod in {"torch": torch, "torch.nn": nn,
                    "torch.nn.functional": types.ModuleType("torch.nn.functional"),
                    "torch.optim": types.ModuleType("torch.optim"),
                    "torch.utils": types.ModuleType("torch.utils"),
                    "torch.utils.data": datos,
                    "xgboost": types.ModuleType("xgboost")}.items():
    sys.modules[nombre] = mod

os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ / "scripts_opt"))
import pandas as pd  # noqa: E402
import sklearn  # noqa: E402
import train_all_v4 as T  # noqa: E402

T.RESULTS_CSV = SALIDA.with_suffix(".tmp.csv")   # nunca sobre resultados_v4.csv


def main():
    resultados = []
    for exp in ["A", "B", "C"]:
        T.run_lr(exp, resultados)
    T.RESULTS_CSV.unlink(missing_ok=True)

    nuevo = pd.DataFrame(resultados)
    orig = pd.read_csv(RAIZ / "RESULTADOS_OPTIMIZADOS" / "v4" / "resultados_v4.csv")
    orig = orig[orig.modelo == "LR"]
    cols = ["test_f1_macro", "test_f1_buy", "test_f1_hold", "test_f1_sell", "sharpe_test",
            "win_rate_test", "profit_factor_test", "max_drawdown_test"]
    m = orig.merge(nuevo, on=["tipo", "ticker", "experimento"], suffixes=("_publicado", "_replica"))
    filas = []
    for c in cols:
        filas.append({"metrica": c, "corridas": len(m),
                      "max_abs_diferencia": float((m[c + "_publicado"] - m[c + "_replica"]).abs().max())})
    res = pd.DataFrame(filas)
    res["python"] = platform.python_version()
    res["scikit_learn"] = sklearn.__version__
    res.to_csv(SALIDA, index=False)
    print(res.to_string(index=False))
    ok = len(m) == 24 and (res.max_abs_diferencia == 0).all()
    print("\nREPRODUCCIÓN EXACTA" if ok else "\nHAY DIFERENCIAS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

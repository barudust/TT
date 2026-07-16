import re

# Lista de tus 4 scripts
files = [
    "04_train_logistic_regression.py",
    "05_train_xgboost.py",
    "06_train_lstm.py",
    "07_train_cnn_lstm.py"
]

for f in files:
    try:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
            
        # 1. Quitar la restricción de la ventana de 90 días (ahora evalúa todo el test)
        content = re.sub(
            r"n = min\(ventana, len\(y_pred\), len\(r_forward\)\)",
            r"n = min(len(y_pred), len(r_forward))",
            content
        )
        
        # 2. Cambiar los nombres de las llaves del diccionario para reflejar que es el total
        content = re.sub(r'f"cumul_return_\{ventana\}d"', r'"cumul_return_test"', content)
        content = re.sub(r'f"return_vs_bh_\{ventana\}d"', r'"return_vs_bh_test"', content)
        content = re.sub(r'f"sharpe_\{ventana\}d"', r'"sharpe_test"', content)
        content = re.sub(r'f"max_drawdown_\{ventana\}d"', r'"max_drawdown_test"', content)
        content = re.sub(r'f"win_rate_\{ventana\}d"', r'"win_rate_test"', content)
        content = re.sub(r'f"profit_factor_\{ventana\}d"', r'"profit_factor_test"', content)

        # 3. Actualizar la extracción en los diccionarios finales (filas)
        old_list = r'for k in \[f"cumul_return_.*?\]:'
        new_list = 'for k in ["cumul_return_test", "return_vs_bh_test", "sharpe_test", "max_drawdown_test", "win_rate_test", "profit_factor_test"]:'
        content = re.sub(old_list, new_list, content, flags=re.DOTALL)
        
        # 4. Actualizar las columnas del resumen final impreso en consola
        old_resumen = r'f"cumul_return_\{VENTANA_ECON(OMICA)?\}d",\s*f"sharpe_\{VENTANA_ECON(OMICA)?\}d",\s*f"win_rate_\{VENTANA_ECON(OMICA)?\}d"'
        new_resumen = '"cumul_return_test", "sharpe_test", "win_rate_test"'
        content = re.sub(old_resumen, new_resumen, content)
        
        with open(f, "w", encoding="utf-8") as file:
            file.write(content)
            
        print(f"✓ Corregido exitosamente: {f}")
    except FileNotFoundError:
        print(f"⚠ Archivo no encontrado: {f}")

print("\n¡Todos los archivos han sido parcheados! Ahora las métricas económicas evalúan el 100% del test.")
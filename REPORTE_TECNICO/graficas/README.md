# Gráficas de resultados

El reporte actual no tiene ninguna gráfica de resultados. Estas siete van en el
capítulo 6, cada una con su tabla en `../tablas/TABLAS_NUEVAS.md` (la tabla
lleva los números exactos; la gráfica, el mensaje). PNG a 300 ppp y SVG.

| Archivo | Qué muestra | Sección | Tabla |
|---|---|---|---|
| `G01_f1_intervalos_etapa4` | F1-macro con intervalos del 95 % de los cinco modelos en A, B y C (resultado principal) | 6.5 | T-09 |
| `G02_sharpe_costos_etapa4` | Sharpe sin costos y con 10 pb, y rotación (Experimento B) | 6.5 | T-10 |
| `G03_etapa3_contra_etapa4` | Cómo cambia cada modelo al pasar al protocolo final (B y promedio de A/B/C) | 6.5 | T-07, T-09 |
| `G04_anio_por_anio` | F1-macro de cada año de prueba 2020–2025, ajustes fijos de antemano | 6.6 | T-12 |
| `G05_prueba_ciega_2026` | F1-macro y Sharpe de los cinco en la prueba ciega 2026 | 6.6 | T-13 |
| `G06_multicolinealidad` | Diferencia de F1 entre usar las 61 variables y el filtro VIF ≤ 10 | 4.6 / 6.3 | T-11 |
| `G07_global_contra_por_accion` | Modelo global contra uno por acción en los mismos días | 6.8 | T-17 |

**Pies sugeridos** (adaptar la numeración):

- **G01.** *F1-macro de los cinco modelos en la prueba 2025 con el protocolo
  final, modelo global. La línea es el intervalo de confianza del 95 %
  (bootstrap por bloques de 20 días). La Regresión Logística es
  significativamente mejor que los otros cuatro en los tres experimentos.*
- **G02.** *Índice de Sharpe de la simulación en el Experimento B sin costos
  (punto lleno) y con 10 puntos base por cambio de posición (punto vacío). A la
  derecha, la rotación (cambio medio de posición por día).*
- **G03.** *F1-macro de cada modelo en la Etapa 3 (ventana de las redes elegida
  con la prueba) y en la Etapa 4 (protocolo final).*
- **G04.** *Prueba año por año: F1-macro del modelo global en cada año de
  prueba, entrenando con los cinco años previos al de validación.*
- **G05.** *Prueba ciega con datos de enero a octubre de 2026, no usados en
  ninguna decisión.*
- **G06.** *Diferencia de F1-macro entre usar las 61 características y usar el
  filtro VIF ≤ 10 (45 características), con el protocolo final. Positivo: las
  61 son mejores.*
- **G07.** *F1-macro medio del modelo global y del modelo por acción sobre los
  mismos días (21 pares) y número de pares en que gana el global, con el valor
  p de la prueba de signo.*

**Colores:** un color fijo por modelo en todas las gráficas (LR azul, XGBoost
naranja, LSTM verde agua, CNN-LSTM amarillo, CNN 1D rosa), validado para
daltonismo. Los modelos siempre se nombran en el eje o en la leyenda.

**Para regenerar** (lee los resultados guardados, no recalcula nada):

```bash
python REPORTE_TECNICO/graficas/fuente/generar_graficas.py
```

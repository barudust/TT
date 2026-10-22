# C0 — Resumen de la sección "El paper" (3 minutos)

- **Qué:** *"A Benchmark of Five Machine-Learning Architectures for Daily
  Trading-Signal Classification on US Tech Equities"*, **MICAI 2026**,
  Springer LNAI. Camera-ready enviado el 8 de septiembre de 2026.
- **Qué publica:**
  - §7 (**Etapa 3**, comparación en igualdad): LR 0.399 de promedio, Sharpe
    +0.76 en el experimento B.
  - §8 (**Etapa 4**, protocolo final): LR 0.404 [0.379, 0.428],
    significativamente mejor que los otros cuatro.
  - §6 (**Etapa 2**): filtrar variables empeora en 11 de 15 casos (corrido con
    las particiones de TT1; ver el punto 1 de los puntos a cuidar del
    [mapa](../03_MAPA_DE_EXPERIMENTOS.md#8-puntos-a-cuidar-para-la-estrategia-de-defensa)).
  - La acción explica 4.5 veces más el Sharpe que el modelo.
- **Revisión:** los revisores pidieron una búsqueda seria para las redes →
  se hizo la Etapa 4 y se agregó la §8.
- **Relación con el TT:** producto extra. No usa los resultados del TT1 ni
  las etapas 5 y 6; el TT además tiene costos, prueba año por año, 2026,
  análisis de MANTENER y la plataforma.
- **Detalle a conocer:** el paper dice que la CNN-LSTM recibe 5 canales OHLCV
  (diseño del TT1), pero el código de la Etapa 3 no los usa.
- **Pendiente:** responder a Springer con el material suplementario.

→ [C1 completo](C1_PAPER_MICAI.md)

// Glosario de la aplicación: cada término que aparece en pantalla, explicado
// para alguien sin conocimientos de finanzas ni de aprendizaje automático.
// El `id` se usa en los enlaces "?" de las métricas (/ayuda?tab=glosario#id).

export interface TerminoGlosario {
  id: string;
  termino: string;
  /** Otros nombres con los que puede aparecer (técnicos o en inglés). */
  tambien?: string;
  definicion: string;
  ejemplo?: string;
  categoria: "Recomendaciones" | "Precios y mercado" | "Qué tan bien acierta" | "Dinero y riesgo" | "Cómo se comparan los modelos";
}

export const GLOSARIO: TerminoGlosario[] = [
  // ── Recomendaciones ──────────────────────────────────────────────────────
  {
    id: "recomendacion",
    termino: "Recomendación del día",
    tambien: "señal de trading",
    categoria: "Recomendaciones",
    definicion: "Lo que el modelo sugiere hacer con una acción en la siguiente sesión de la bolsa: comprar, vender o mantener.",
  },
  {
    id: "comprar",
    termino: "Comprar",
    tambien: "posición larga, BUY",
    categoria: "Recomendaciones",
    definicion: "El modelo cree que el precio podría subir bastante al día siguiente.",
  },
  {
    id: "vender",
    termino: "Vender",
    tambien: "venta en corto, posición corta, SELL",
    categoria: "Recomendaciones",
    definicion:
      "El modelo cree que el precio podría bajar bastante. En la simulación es una venta en corto: pides prestada una acción, la vendes hoy y la recompras mañana; ganas si el precio baja. La página «Aprende» lo muestra paso a paso.",
  },
  {
    id: "mantener",
    termino: "Mantener",
    tambien: "no operar, HOLD",
    categoria: "Recomendaciones",
    definicion: "El modelo no ve hacia dónde va el precio, así que lo mejor es no mover nada. Sale más cuando el mercado está tranquilo.",
  },
  {
    id: "seguridad",
    termino: "Seguridad de la recomendación",
    tambien: "confianza del modelo",
    categoria: "Recomendaciones",
    definicion:
      "Qué tan decidido estaba el modelo, medido por cuánto ha atinado antes cuando estaba igual de decidido. Nada segura: 37 de cada 100. Poco segura: 38 de cada 100. Medianamente segura: 42 de cada 100. Adivinando se atina 33 de cada 100.",
    ejemplo: "No hay un nivel «Segura» porque ninguno atina ni la mitad de las veces.",
  },
  {
    id: "probabilidades",
    termino: "Cómo se repartió la decisión",
    tambien: "probabilidades del modelo",
    categoria: "Recomendaciones",
    definicion: "El modelo reparte 100 % entre comprar, mantener y vender, y recomienda la que tenga más. Si las tres andan cerca de 33 %, está indeciso.",
    ejemplo: "Comprar 30 %, mantener 38 %, vender 32 %: recomienda mantener, pero por poquito.",
  },
  {
    id: "lo-que-convenia",
    termino: "Lo que convenía hacer",
    tambien: "resultado real",
    categoria: "Recomendaciones",
    definicion:
      "Lo correcto según lo que pasó al día siguiente: comprar si la acción subió más de lo normal para ella, vender si bajó más de lo normal, y mantener si se movió poco. «Más de lo normal» quiere decir entre el 30 % de sus movimientos más grandes del último año.",
  },
  {
    id: "pendiente",
    termino: "Pendiente",
    categoria: "Recomendaciones",
    definicion: "La recomendación más reciente todavía no se puede calificar porque falta que cierre el día siguiente.",
  },
  {
    id: "modelo",
    termino: "Modelo",
    tambien: "Regresión Logística",
    categoria: "Recomendaciones",
    definicion: "El programa que da las recomendaciones. Aprendió con datos de 2018 a 2025 y fue el mejor de los cinco tipos de modelo que comparamos.",
  },

  // ── Precios y mercado ────────────────────────────────────────────────────
  {
    id: "accion",
    termino: "Acción (y su clave)",
    tambien: "ticker",
    categoria: "Precios y mercado",
    definicion:
      "Un pedacito de una empresa que se compra y vende en la bolsa. Cada una tiene una clave: AAPL es Apple, MSFT Microsoft, GOOGL Google, AMZN Amazon, TSLA Tesla, META Meta y NVDA NVIDIA.",
  },
  {
    id: "precio-cierre",
    termino: "Precio al cierre",
    categoria: "Precios y mercado",
    definicion: "El último precio del día, cuando cierra la bolsa (16:00 de Nueva York). Está en dólares.",
  },
  {
    id: "sesion",
    termino: "Sesión o día hábil",
    categoria: "Precios y mercado",
    definicion: "Un día en que abre la Bolsa de Nueva York: de lunes a viernes, menos los días festivos.",
  },
  {
    id: "cambio-dia-siguiente",
    termino: "Cambio al día siguiente",
    categoria: "Precios y mercado",
    definicion: "Cuánto subió (+) o bajó (−) el precio de un cierre al siguiente.",
    ejemplo: "+1.20 %: una acción de $100 cerró al otro día en $101.20.",
  },
  {
    id: "mercado",
    termino: "Bolsa abierta o cerrada",
    tambien: "NYSE",
    categoria: "Precios y mercado",
    definicion: "Si la Bolsa de Nueva York está operando en este momento. Las recomendaciones solo cambian una vez al día, después del cierre.",
  },
  {
    id: "periodo",
    termino: "30, 60 o 90 días",
    categoria: "Precios y mercado",
    definicion: "Cuántos días hábiles hacia atrás se usan para las gráficas y los resultados. 30 son como mes y medio; 90, unos cuatro meses.",
  },

  // ── Qué tan bien acierta ────────────────────────────────────────────────
  {
    id: "aciertos",
    termino: "Acertó",
    tambien: "accuracy, exactitud",
    categoria: "Qué tan bien acierta",
    definicion: "En cuántos de los días ya calificados la recomendación coincidió con lo que convenía hacer.",
    ejemplo: "12 de 29 (41 %).",
  },
  {
    id: "f1",
    termino: "Calificación (F1)",
    tambien: "F1-macro",
    categoria: "Qué tan bien acierta",
    definicion:
      "Una calificación de 0 a 100 % que le da el mismo peso a comprar, mantener y vender, para que el modelo no salga bien solo por repetir la opción más común. Adivinando saldría alrededor de 33 %.",
  },
  {
    id: "azar",
    termino: "Adivinar (33 %)",
    tambien: "azar",
    categoria: "Qué tan bien acierta",
    definicion: "Con tres opciones, escoger una al azar atina más o menos 1 de cada 3 veces. Es el mínimo que el modelo tiene que superar.",
  },
  {
    id: "frecuencia-recomendaciones",
    termino: "Qué recomendó",
    categoria: "Qué tan bien acierta",
    definicion: "En qué porcentaje de los días dijo comprar, mantener o vender.",
  },

  // ── Dinero y riesgo ─────────────────────────────────────────────────────
  {
    id: "estrategia",
    termino: "Hacerle caso al modelo",
    tambien: "estrategia del modelo",
    categoria: "Dinero y riesgo",
    definicion:
      "Una simulación: si dice comprar, compras al cierre y vendes al cierre siguiente; si dice vender, haces lo contrario (venta en corto); si dice mantener, no haces nada. No incluye comisiones.",
  },
  {
    id: "roi",
    termino: "Ganancia",
    tambien: "rendimiento de la inversión, ROI, retorno",
    categoria: "Dinero y riesgo",
    definicion: "Cuánto ganaste (+) o perdiste (−) en el periodo, en porcentaje de lo que pusiste al inicio.",
    ejemplo: "+5 % con $1,000 = terminas con $1,050.",
  },
  {
    id: "comprar-y-esperar",
    termino: "Comprar y esperar",
    tambien: "buy & hold",
    categoria: "Dinero y riesgo",
    definicion: "Comprar la acción el primer día y no tocarla. Sirve para saber si hacerle caso al modelo valió la pena.",
  },
  {
    id: "diferencia",
    termino: "Diferencia",
    categoria: "Dinero y riesgo",
    definicion: "La ganancia de hacerle caso al modelo menos la de comprar y esperar, en puntos. Si es positiva, ganó el modelo.",
  },
  {
    id: "sharpe",
    termino: "Ganancia vs. riesgo",
    tambien: "razón de Sharpe",
    categoria: "Dinero y riesgo",
    definicion:
      "Compara lo que ganaste con qué tanto se movió tu dinero en el camino. Arriba de 0 vas ganando; arriba de 1 es bueno; negativo es pérdida. Con menos de 5 días invertidos no se calcula.",
  },
  {
    id: "drawdown",
    termino: "Peor caída",
    tambien: "máximo drawdown",
    categoria: "Dinero y riesgo",
    definicion: "La bajada más grande que tuvo tu dinero desde su mejor momento. Es el peor rato que habrías pasado.",
    ejemplo: "−8 %: en algún momento tus $1,000 valieron 8 % menos que en su mejor punto.",
  },
  {
    id: "win-rate",
    termino: "Días con ganancia",
    tambien: "win rate",
    categoria: "Dinero y riesgo",
    definicion: "De los días en que sí se invirtió (sin contar mantener), en cuántos se ganó dinero. 50 % es como echar un volado.",
  },
  // ── Cómo se comparan los modelos ────────────────────────────────────────
  {
    id: "validacion",
    termino: "Entrenamiento, validación y prueba",
    categoria: "Cómo se comparan los modelos",
    definicion:
      "Los años se separan en orden. Con el entrenamiento el modelo aprende; con la validación se eligen sus ajustes; la prueba se usa una sola vez al final para calificarlo, como un examen que no se vio antes.",
  },
  {
    id: "anio-por-anio",
    termino: "Prueba año por año",
    tambien: "walk-forward",
    categoria: "Cómo se comparan los modelos",
    definicion:
      "Repetir la evaluación tomando como prueba cada año de 2020 a 2025, para comprobar que el resultado no depende de un solo año.",
  },
  {
    id: "intervalo",
    termino: "Intervalo de confianza",
    tambien: "bootstrap",
    categoria: "Cómo se comparan los modelos",
    definicion:
      "El rango donde probablemente está el valor real si se repitiera la prueba con otros días parecidos. Si dos modelos difieren y el intervalo de su diferencia no incluye el cero, la diferencia no es suerte.",
  },
  {
    id: "kappa",
    termino: "Kappa",
    categoria: "Cómo se comparan los modelos",
    definicion: "Cuánto acierta el modelo por encima de lo que acertaría por casualidad. 0 = igual que el azar; 1 = perfecto.",
  },
  {
    id: "auc",
    termino: "AUC",
    categoria: "Cómo se comparan los modelos",
    definicion:
      "Qué tan bien ordena el modelo sus probabilidades: la probabilidad de que le dé más puntaje a un día de una clase que a uno de otra. 0.5 = azar.",
  },
  {
    id: "log-loss",
    termino: "Log-loss",
    tambien: "pérdida logarítmica",
    categoria: "Cómo se comparan los modelos",
    definicion: "Castiga estar muy seguro y equivocarse. Menor es mejor; el azar con tres opciones da 1.10.",
  },
  {
    id: "multicolinealidad",
    termino: "Multicolinealidad",
    tambien: "VIF",
    categoria: "Cómo se comparan los modelos",
    definicion:
      "Cuando varias variables dicen casi lo mismo (por ejemplo, dos medias móviles cercanas). El VIF mide qué tanto se puede adivinar una variable con las demás; arriba de 10 se considera alto. Complica leer cada coeficiente, pero no necesariamente empeora las predicciones.",
  },
];

export const CATEGORIAS_GLOSARIO = ["Recomendaciones", "Precios y mercado", "Qué tan bien acierta", "Dinero y riesgo", "Cómo se comparan los modelos"] as const;

export type IdGlosario = (typeof GLOSARIO)[number]["id"];

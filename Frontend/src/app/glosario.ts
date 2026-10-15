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
  categoria: "Recomendaciones" | "Precios y mercado" | "Qué tan bien acierta" | "Dinero y riesgo";
}

export const GLOSARIO: TerminoGlosario[] = [
  // ── Recomendaciones ──────────────────────────────────────────────────────
  {
    id: "recomendacion",
    termino: "Recomendación del día",
    tambien: "señal de trading",
    categoria: "Recomendaciones",
    definicion:
      "Lo que el modelo sugiere hacer con una acción durante la siguiente sesión del mercado: COMPRAR, VENDER o MANTENER. Se calcula después del cierre del mercado con los precios de ese día.",
  },
  {
    id: "comprar",
    termino: "COMPRAR",
    tambien: "posición larga, BUY",
    categoria: "Recomendaciones",
    definicion:
      "El modelo espera que el precio suba de forma notable en la siguiente sesión. Comprar la acción hoy y venderla al cierre de mañana daría ganancia si sube.",
  },
  {
    id: "vender",
    termino: "VENDER",
    tambien: "venta en corto, posición corta, SELL",
    categoria: "Recomendaciones",
    definicion:
      "El modelo espera que el precio baje de forma notable. Quien ya tiene la acción podría venderla; un inversionista avanzado puede 'vender en corto' (vender acciones prestadas para recomprarlas más baratas), que gana si el precio baja.",
  },
  {
    id: "mantener",
    termino: "MANTENER",
    tambien: "no operar, HOLD",
    categoria: "Recomendaciones",
    definicion:
      "El modelo no ve una dirección clara: no conviene abrir una operación nueva. Aparece sobre todo cuando el mercado está tranquilo. No significa 'vas a ganar' ni 'vas a perder'.",
  },
  {
    id: "seguridad",
    termino: "Seguridad de la recomendación",
    tambien: "confianza del modelo",
    categoria: "Recomendaciones",
    definicion:
      "Qué tan decidido estaba el modelo y qué tan seguido acertó en el pasado cuando estaba igual de decidido. Tiene tres niveles: Nada segura (acertó 37 de cada 100 veces), Poco segura (38 de cada 100) y Medianamente segura (42 de cada 100). Escoger al azar acertaría 33 de cada 100. No hay un nivel «Segura» porque ningún nivel acierta ni la mitad de las veces.",
    ejemplo: "Una recomendación «Medianamente segura» es la mejor opinión que puede dar el modelo, pero aun así falla más de la mitad de las veces.",
  },
  {
    id: "probabilidades",
    termino: "Probabilidades del modelo",
    categoria: "Recomendaciones",
    definicion:
      "El modelo reparte 100 % entre COMPRAR, MANTENER y VENDER, y recomienda la opción con más porcentaje. Si las tres están cerca de 33 %, el modelo está casi indeciso.",
    ejemplo: "COMPRAR 30 %, MANTENER 38 %, VENDER 32 % → recomienda MANTENER, pero con poca diferencia.",
  },
  {
    id: "lo-que-convenia",
    termino: "Lo que convenía hacer",
    tambien: "resultado real, etiqueta real",
    categoria: "Recomendaciones",
    definicion:
      "Lo que habría sido correcto según cómo se movió el precio al día siguiente: COMPRAR si la subida estuvo entre el 30 % de las mayores subidas del último año de esa acción, VENDER si la bajada estuvo entre el 30 % de las mayores bajadas, y MANTENER si el movimiento fue normal.",
  },
  {
    id: "pendiente",
    termino: "Pendiente",
    categoria: "Recomendaciones",
    definicion:
      "La recomendación más reciente todavía no se puede calificar porque el mercado aún no cierra el día siguiente.",
  },
  {
    id: "modelo",
    termino: "Modelo",
    tambien: "Regresión Logística",
    categoria: "Recomendaciones",
    definicion:
      "El programa que genera las recomendaciones. Aprendió de 8 años de datos (2018–2025) de las 7 acciones. Se eligió después de comparar cinco tipos de modelos; fue el que mejor resultado dio.",
  },

  // ── Precios y mercado ────────────────────────────────────────────────────
  {
    id: "accion",
    termino: "Acción (y su clave)",
    tambien: "ticker",
    categoria: "Precios y mercado",
    definicion:
      "Una parte de una empresa que se compra y vende en la bolsa. Cada una tiene una clave corta: AAPL es Apple, MSFT Microsoft, GOOGL Alphabet (Google), AMZN Amazon, TSLA Tesla, META Meta (Facebook) y NVDA NVIDIA.",
  },
  {
    id: "precio-cierre",
    termino: "Precio de cierre",
    categoria: "Precios y mercado",
    definicion:
      "El último precio de la acción al terminar la sesión del mercado (16:00 hora de Nueva York). Está en dólares estadounidenses (USD).",
  },
  {
    id: "sesion",
    termino: "Sesión o día hábil",
    categoria: "Precios y mercado",
    definicion:
      "Un día en que abre la Bolsa de Nueva York: de lunes a viernes, de 9:30 a 16:00 hora de Nueva York, excepto feriados. Sábados, domingos y feriados no hay precios.",
  },
  {
    id: "cambio-dia-siguiente",
    termino: "Cambio al día siguiente",
    categoria: "Precios y mercado",
    definicion: "Cuánto subió (+) o bajó (−) el precio de cierre de ese día al cierre del siguiente día hábil, en porcentaje.",
    ejemplo: "+1.20 % quiere decir que una acción de $100 cerró al día siguiente en $101.20.",
  },
  {
    id: "mercado",
    termino: "Mercado abierto / cerrado",
    tambien: "NYSE",
    categoria: "Precios y mercado",
    definicion:
      "Si en este momento la Bolsa de Nueva York está operando. Las recomendaciones se calculan solo con precios de cierre, así que se actualizan una vez al día, después del cierre.",
  },
  {
    id: "periodo",
    termino: "Periodo de 30, 60 o 90 días",
    categoria: "Precios y mercado",
    definicion:
      "Cuántos días hábiles hacia atrás se usan para calcular las gráficas y los resultados. 30 días hábiles son aproximadamente un mes y medio; 90, unos cuatro meses.",
  },

  // ── Qué tan bien acierta ────────────────────────────────────────────────
  {
    id: "aciertos",
    termino: "Recomendaciones acertadas",
    tambien: "accuracy, exactitud",
    categoria: "Qué tan bien acierta",
    definicion: "De los días que ya se pueden calificar, en cuántos la recomendación coincidió con lo que convenía hacer.",
    ejemplo: "12 de 29 (41 %).",
  },
  {
    id: "f1",
    termino: "Calificación del modelo",
    tambien: "F1-macro",
    categoria: "Qué tan bien acierta",
    definicion:
      "Una calificación de 0 % a 100 % que mide qué tan bien acierta el modelo en las tres recomendaciones por igual, sin dejarse engañar si una de ellas es muy frecuente. Al azar se obtendría alrededor de 33 %; más arriba es mejor.",
  },
  {
    id: "f1-clase",
    termino: "Calificación por recomendación",
    tambien: "F1 de COMPRAR, MANTENER o VENDER",
    categoria: "Qué tan bien acierta",
    definicion:
      "La misma calificación, pero solo para una de las recomendaciones: combina qué tan seguido acierta cuando la da y qué tantos de esos días logra detectar.",
  },
  {
    id: "azar",
    termino: "Azar (33 %)",
    categoria: "Qué tan bien acierta",
    definicion:
      "Con tres opciones, escoger una al azar acertaría aproximadamente 1 de cada 3 veces. Es la referencia mínima: un modelo útil debe estar por encima.",
  },
  {
    id: "frecuencia-recomendaciones",
    termino: "Cuántas veces recomendó cada opción",
    categoria: "Qué tan bien acierta",
    definicion: "Qué porcentaje de los días del periodo el modelo dijo COMPRAR, MANTENER o VENDER.",
  },

  // ── Dinero y riesgo ─────────────────────────────────────────────────────
  {
    id: "estrategia",
    termino: "Seguir las recomendaciones",
    tambien: "estrategia del modelo",
    categoria: "Dinero y riesgo",
    definicion:
      "Una simulación: cada día con COMPRAR se compra al cierre y se vende al cierre siguiente; con VENDER se vende en corto de la misma forma; con MANTENER no se hace nada. No incluye comisiones.",
  },
  {
    id: "roi",
    termino: "Rendimiento de la inversión",
    tambien: "retorno, ROI, retorno acumulado",
    categoria: "Dinero y riesgo",
    definicion:
      "Cuánto ganaste (+) o perdiste (−) en todo el periodo, como porcentaje de lo que invertiste al inicio.",
    ejemplo: "+5 % con $1,000 iniciales = terminas con $1,050 (ganancia de $50).",
  },
  {
    id: "capital-final",
    termino: "Si hubieras invertido $1,000",
    tambien: "capital final",
    categoria: "Dinero y riesgo",
    definicion: "Cuánto dinero tendrías al final del periodo si hubieras empezado con $1,000 y seguido las recomendaciones.",
  },
  {
    id: "comprar-y-esperar",
    termino: "Comprar y esperar",
    tambien: "buy & hold",
    categoria: "Dinero y riesgo",
    definicion:
      "La comparación más sencilla: comprar la acción el primer día del periodo y no hacer nada más. Sirve para saber si seguir las recomendaciones fue mejor que no hacer nada.",
  },
  {
    id: "diferencia",
    termino: "Diferencia contra comprar y esperar",
    categoria: "Dinero y riesgo",
    definicion:
      "Rendimiento de seguir las recomendaciones menos el rendimiento de comprar y esperar, en puntos porcentuales. Positivo: las recomendaciones dieron más.",
  },
  {
    id: "sharpe",
    termino: "Ganancia ajustada al riesgo",
    tambien: "razón de Sharpe",
    categoria: "Dinero y riesgo",
    definicion:
      "Compara la ganancia con qué tanto subió y bajó el dinero en el camino. Mayor que 0: ganó más de lo que arriesgó en promedio; mayor que 1: bueno; negativo: perdió. No se calcula con menos de 5 días invertidos porque no sería confiable.",
  },
  {
    id: "drawdown",
    termino: "Peor caída",
    tambien: "máximo drawdown",
    categoria: "Dinero y riesgo",
    definicion: "La mayor pérdida desde un punto alto hasta el punto más bajo siguiente, en porcentaje. Mide el peor momento que habrías vivido.",
    ejemplo: "−8 %: en algún momento tus $1,000 llegaron a valer 8 % menos que su mejor valor anterior.",
  },
  {
    id: "win-rate",
    termino: "Operaciones con ganancia",
    tambien: "win rate, tasa de acierto económico",
    categoria: "Dinero y riesgo",
    definicion: "De los días en que se compró o vendió (sin contar MANTENER), en qué porcentaje se ganó dinero. 50 % es como lanzar una moneda.",
  },
  {
    id: "profit-factor",
    termino: "Ganancias por cada dólar perdido",
    tambien: "factor de beneficio, profit factor",
    categoria: "Dinero y riesgo",
    definicion: "Suma de lo ganado dividida entre la suma de lo perdido. Mayor que 1 significa que se ganó más de lo que se perdió.",
    ejemplo: "1.30 = por cada $1 perdido se ganaron $1.30.",
  },
  {
    id: "exposicion",
    termino: "Días con dinero invertido",
    tambien: "exposición",
    categoria: "Dinero y riesgo",
    definicion: "En qué porcentaje de los días se compró o vendió (no fue MANTENER). Menos días invertidos significa menos riesgo, pero también menos oportunidades.",
  },
];

export const CATEGORIAS_GLOSARIO = ["Recomendaciones", "Precios y mercado", "Qué tan bien acierta", "Dinero y riesgo"] as const;

export type IdGlosario = (typeof GLOSARIO)[number]["id"];

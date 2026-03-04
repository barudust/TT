import * as kv from "./kv_store.tsx";

/**
 * FORMATO DE DATOS PARA LA APLICACIÓN
 * ====================================
 * 
 * Este archivo contiene datos simulados y muestra el formato exacto
 * que tus modelos de Deep Learning deben generar y almacenar.
 * 
 * INSTRUCCIONES PARA INTEGRAR TUS MODELOS:
 * 
 * 1. SEÑALES DIARIAS (stocks:list)
 *    Después de que tus modelos generen predicciones al cierre del mercado,
 *    guarda los datos en el KV store con la clave "stocks:list":
 * 
 *    await kv.set("stocks:list", [
 *      {
 *        symbol: "AAPL",
 *        name: "Apple Inc.",
 *        currentPrice: 175.30,
 *        signal: "buy",  // "buy", "sell", o "hold"
 *        confidence: 0.78,  // 0-1 (78% de confianza)
 *        lastUpdate: "2026-03-02T18:00:00Z"
 *      },
 *      // ... más acciones
 *    ]);
 * 
 * 2. DATOS HISTÓRICOS (stocks:{SYMBOL}:history:{DAYS})
 *    Almacena el historial de precios para cada acción:
 * 
 *    await kv.set("stocks:AAPL:history:90", [
 *      { date: "2025-12-01", close: 170.50, prediction: "buy", actualDirection: "up" },
 *      { date: "2025-12-02", close: 172.30, prediction: "buy", actualDirection: "up" },
 *      // ... más días
 *    ]);
 * 
 * 3. MÉTRICAS DE RENDIMIENTO (stocks:{SYMBOL}:metrics)
 *    Guarda las métricas de tu modelo para cada acción:
 * 
 *    await kv.set("stocks:AAPL:metrics", {
 *      accuracy: 0.72,
 *      buyPrecision: 0.68,
 *      sellPrecision: 0.75,
 *      holdPrecision: 0.70,
 *      f1Score: 0.71,
 *      evaluationPeriod: 30,  // días
 *      totalPredictions: 150,
 *      correctPredictions: 108
 *    });
 * 
 * 4. HISTORIAL DE SEÑALES (stocks:{SYMBOL}:signals)
 *    Guarda el historial de señales para comparación:
 * 
 *    await kv.set("stocks:AAPL:signals", [
 *      {
 *        date: "2026-03-01",
 *        signal: "buy",
 *        predictedPrice: 176.50,
 *        actualPrice: 177.20,
 *        correct: true
 *      },
 *      // ... más señales
 *    ]);
 */

// Definición de las 7 acciones a seguir
const STOCKS = [
  { symbol: "AAPL", name: "Apple Inc." },
  { symbol: "MSFT", name: "Microsoft Corporation" },
  { symbol: "GOOGL", name: "Alphabet Inc." },
  { symbol: "AMZN", name: "Amazon.com Inc." },
  { symbol: "TSLA", name: "Tesla Inc." },
  { symbol: "META", name: "Meta Platforms Inc." },
  { symbol: "NVDA", name: "NVIDIA Corporation" },
];

// Función para generar datos históricos simulados
function generateHistoricalData(symbol: string, days: number) {
  const data = [];
  const basePrice = getBasePrice(symbol);
  let currentPrice = basePrice;
  const today = new Date("2026-03-02");

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // Simular variación de precio (-3% a +3%)
    const variation = (Math.random() - 0.5) * 0.06;
    currentPrice = currentPrice * (1 + variation);
    
    // Generar señal aleatoria pero realista
    const rand = Math.random();
    let prediction, actualDirection;
    
    if (variation > 0.01) {
      actualDirection = "up";
      prediction = rand > 0.3 ? "buy" : (rand > 0.15 ? "hold" : "sell");
    } else if (variation < -0.01) {
      actualDirection = "down";
      prediction = rand > 0.3 ? "sell" : (rand > 0.15 ? "hold" : "buy");
    } else {
      actualDirection = "neutral";
      prediction = rand > 0.5 ? "hold" : (rand > 0.25 ? "buy" : "sell");
    }
    
    data.push({
      date: date.toISOString().split("T")[0],
      close: parseFloat(currentPrice.toFixed(2)),
      prediction,
      actualDirection,
    });
  }
  
  return data;
}

// Función para obtener precio base de cada acción
function getBasePrice(symbol: string): number {
  const prices: Record<string, number> = {
    AAPL: 175.00,
    MSFT: 410.00,
    GOOGL: 140.00,
    AMZN: 175.00,
    TSLA: 195.00,
    META: 485.00,
    NVDA: 875.00,
  };
  return prices[symbol] || 100;
}

// Función para generar métricas simuladas
function generateMetrics(historicalData: any[]) {
  let correct = 0;
  let buyCorrect = 0, buyTotal = 0;
  let sellCorrect = 0, sellTotal = 0;
  let holdCorrect = 0, holdTotal = 0;
  
  historicalData.forEach((day) => {
    const predictionCorrect = 
      (day.prediction === "buy" && day.actualDirection === "up") ||
      (day.prediction === "sell" && day.actualDirection === "down") ||
      (day.prediction === "hold" && day.actualDirection === "neutral");
    
    if (predictionCorrect) correct++;
    
    if (day.prediction === "buy") {
      buyTotal++;
      if (day.actualDirection === "up") buyCorrect++;
    } else if (day.prediction === "sell") {
      sellTotal++;
      if (day.actualDirection === "down") sellCorrect++;
    } else if (day.prediction === "hold") {
      holdTotal++;
      if (day.actualDirection === "neutral") holdCorrect++;
    }
  });
  
  return {
    accuracy: parseFloat((correct / historicalData.length).toFixed(2)),
    buyPrecision: buyTotal > 0 ? parseFloat((buyCorrect / buyTotal).toFixed(2)) : 0,
    sellPrecision: sellTotal > 0 ? parseFloat((sellCorrect / sellTotal).toFixed(2)) : 0,
    holdPrecision: holdTotal > 0 ? parseFloat((holdCorrect / holdTotal).toFixed(2)) : 0,
    f1Score: parseFloat((correct / historicalData.length * 0.95).toFixed(2)),
    evaluationPeriod: historicalData.length,
    totalPredictions: historicalData.length,
    correctPredictions: correct,
  };
}

// Obtener lista de todas las acciones con señales actuales
export async function getStockList() {
  // Intentar obtener de KV store
  let stocks = await kv.get("stocks:list");
  
  // Si no existe, generar datos simulados
  if (!stocks) {
    stocks = STOCKS.map((stock) => {
      const historicalData = generateHistoricalData(stock.symbol, 30);
      const lastDay = historicalData[historicalData.length - 1];
      const signals = ["buy", "sell", "hold"];
      const signal = signals[Math.floor(Math.random() * signals.length)];
      
      return {
        symbol: stock.symbol,
        name: stock.name,
        currentPrice: lastDay.close,
        signal,
        confidence: parseFloat((0.6 + Math.random() * 0.3).toFixed(2)),
        lastUpdate: new Date().toISOString(),
      };
    });
    
    // Guardar en KV store
    await kv.set("stocks:list", stocks);
  }
  
  return stocks;
}

// Obtener detalle de una acción específica
export async function getStockDetail(symbol: string) {
  const stocks = await getStockList();
  const stock = stocks.find((s: any) => s.symbol === symbol);
  
  if (!stock) {
    throw new Error(`Stock ${symbol} not found`);
  }
  
  // Obtener historial de señales
  let signals = await kv.get(`stocks:${symbol}:signals`);
  
  if (!signals) {
    signals = Array.from({ length: 10 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (10 - i));
      const signalTypes = ["buy", "sell", "hold"];
      const signal = signalTypes[Math.floor(Math.random() * signalTypes.length)];
      const basePrice = stock.currentPrice;
      const variation = (Math.random() - 0.5) * 0.05;
      
      return {
        date: date.toISOString().split("T")[0],
        signal,
        predictedPrice: parseFloat((basePrice * (1 + variation)).toFixed(2)),
        actualPrice: parseFloat((basePrice * (1 + variation + (Math.random() - 0.5) * 0.02)).toFixed(2)),
        correct: Math.random() > 0.3,
      };
    });
    
    await kv.set(`stocks:${symbol}:signals`, signals);
  }
  
  return {
    ...stock,
    recentSignals: signals,
  };
}

// Obtener datos históricos de precios
export async function getHistoricalData(symbol: string, days: number = 30) {
  const key = `stocks:${symbol}:history:${days}`;
  let history = await kv.get(key);
  
  if (!history) {
    history = generateHistoricalData(symbol, days);
    await kv.set(key, history);
  }
  
  return history;
}

// Obtener métricas de rendimiento de una acción
export async function getPerformanceMetrics(symbol: string) {
  const key = `stocks:${symbol}:metrics`;
  let metrics = await kv.get(key);
  
  if (!metrics) {
    const history = await getHistoricalData(symbol, 30);
    metrics = generateMetrics(history);
    await kv.set(key, metrics);
  }
  
  return metrics;
}

// Obtener métricas de todas las acciones
export async function getAllPerformanceMetrics() {
  const stocks = await getStockList();
  const allMetrics = [];
  
  for (const stock of stocks) {
    const metrics = await getPerformanceMetrics(stock.symbol);
    allMetrics.push({
      symbol: stock.symbol,
      name: stock.name,
      ...metrics,
    });
  }
  
  return allMetrics;
}

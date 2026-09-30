// Tipos de las respuestas de la API (ver docs/API.md). Todo lo que se muestra
// en la interfaz viene de estos campos: no hay valores fijos ni simulados.

export type Signal = "buy" | "hold" | "sell";

export interface Probabilities {
  buy: number;
  hold: number;
  sell: number;
}

export interface Stock {
  symbol: string;
  name: string;
  currentPrice: number;
  signal: Signal;
  confidence: number;
  probabilities?: Probabilities;
  dataDate?: string; // fecha del cierre con el que se calculó la señal
  lastUpdate: string; // momento (UTC) en que la API recalculó las señales
  modelVersion?: string;
}

export interface RecentSignal {
  date: string;
  signal: Signal;
  confidence: number;
  actualPrice: number;
  actualSignal: Signal | null; // etiqueta real del movimiento al día siguiente
  nextReturn: number | null; // % del cierre de ese día al siguiente
  correct: boolean | null; // null = todavía sin cierre siguiente
}

export interface StockDetail extends Stock {
  recentSignals: RecentSignal[];
}

export interface HistoryRow {
  date: string;
  open: number;
  close: number;
  high: number;
  low: number;
  volume: number;
  prediction: Signal;
  confidence: number;
  probabilities?: Probabilities;
  actualSignal: Signal | null;
  nextReturn: number | null;
  correct: boolean | null;
}

export interface WindowMetrics {
  windowDays: number;
  periodStart: string;
  periodEnd: string;
  totalPredictions: number;
  evaluatedPredictions: number;
  pendingPredictions: number;
  avgConfidence: number;
  signal_buy_pct: number;
  signal_hold_pct: number;
  signal_sell_pct: number;
  // Solo existen si hay al menos un día con resultado conocido
  correctPredictions?: number;
  accuracy?: number; // fracción 0-1
  f1_macro?: number; // fracción 0-1
  f1_buy?: number;
  f1_hold?: number;
  f1_sell?: number;
  cumulativeReturn?: number; // %
  bh_return?: number; // %
  return_vs_bh?: number; // puntos %
  sharpeRatio?: number | null; // null con menos de 5 días con posición
  bh_sharpe?: number;
  maxDrawdown?: number; // % (positivo = caída)
  winRate?: number | null; // % (null si no hubo operaciones)
  profitFactor?: number | null;
  numberOfTrades?: number;
  exposure?: number; // % de días con posición
  finalCapital?: number;
}

export interface StockMetrics extends WindowMetrics {
  symbol: string;
  name: string;
}

export interface ModelInfo {
  version: string;
  configId: string;
  algorithm: string;
  penalty: string | null;
  C: number | null;
  classWeight: string | null;
  scaler: string;
  nFeatures: number;
  nFeaturesBase: number;
  nInteractions: number;
  classes: Signal[];
  trainRange: string | null;
  nTrainSamples: number | null;
  trainedAt: string | null;
  strategy: string;
  tickers: string[];
  target: {
    horizonDays: number;
    percentileSell: number;
    percentileBuy: number;
    rollingWindowDays: number;
  };
}

export interface MarketStatusInfo {
  isOpen: boolean;
  isTradingDay: boolean;
  nowNewYork: string;
  regularHours: string;
  dailyRefresh: string;
}

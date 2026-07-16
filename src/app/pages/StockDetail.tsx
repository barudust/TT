import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { ArrowLeft, ArrowUp, ArrowDown, Circle, TrendingUp, Calendar } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { toast } from "sonner";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { API_BASE_URL } from "../../config/api";

interface MetricCardProps {
  label: string;
  value: string;
  color?: string;
}

function MetricCard({ label, value, color = "" }: MetricCardProps) {
  return (
    <div className="bg-muted p-4 rounded-lg">
      <div className="text-sm text-muted-foreground mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
    </div>
  );
}
interface StockDetailType {
  symbol: string;
  name: string;
  currentPrice: number;
  signal: "buy" | "sell" | "hold";
  confidence: number;
  lastUpdate: string;
  recentSignals: Array<{
    date: string;
    signal: string;
    actualPrice: number;
    correct: boolean;
  }>;
}

interface HistoricalData {
  date: string;
  close: number;
  prediction?: string;
  actualDirection?: string;
}

interface Metrics {
  // clasificación
  accuracy: number;
  f1Score: number;
  f1_buy?: number;
  f1_sell?: number;
  f1_macro?: number;
  // estrategia
  cumulativeReturn: number; // porcentaje
  return_vs_bh?: number; // porcentaje
  sharpeRatio: number;
  winRate: number; // porcentaje
  profitFactor?: number;
  maxDrawdown: number; // porcentaje
  numberOfTrades?: number;
  exposure?: number;
  finalCapital?: number;
  evaluationPeriod?: number;
  totalPredictions?: number;
  correctPredictions?: number;
  // señales
  signal_buy_pct?: number;
  signal_hold_pct?: number;
  signal_sell_pct?: number;
}

export default function StockDetail() {
  const { symbol } = useParams();
  const navigate = useNavigate();

  const [stock, setStock] = useState<StockDetailType | null>(null);
  const [history, setHistory] = useState<HistoricalData[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    fetchStockData();
  }, [symbol, selectedPeriod]);

  const fetchStockData = async () => {
    try {
      setLoading(true);
      const baseUrl = API_BASE_URL;

      const detailResponse = await fetch(`${baseUrl}/stocks/${symbol}`);
      const detailData = await detailResponse.json();

      const historyResponse = await fetch(`${baseUrl}/stocks/${symbol}/history?days=${selectedPeriod}`);
      const historyData = await historyResponse.json();

      const metricsResponse = await fetch(`${baseUrl}/stocks/${symbol}/metrics`);
      const metricsData = await metricsResponse.json();

      if (detailData && detailData.success && historyData && historyData.success && metricsData && metricsData.success) {
        setStock(detailData.data);
        setHistory(historyData.data);
        setMetrics(metricsData.data);
      } else if (detailData && historyData && metricsData && Array.isArray(historyData) && metricsData) {
        // fallback if API returns raw objects
        setStock(detailData.data || detailData);
        setHistory(historyData.data || historyData || []);
        setMetrics(metricsData.data || metricsData);
      } else {
        throw new Error("Error al cargar datos");
      }
    } catch (error) {
      console.error("Error fetching stock detail:", error);
      toast.error("Error al cargar los detalles de la acción");
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stock || !metrics) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p className="mt-4 text-muted-foreground">Cargando datos...</p>
      </div>
    );
  }

  const signalConfig = {
    buy: {
      icon: ArrowUp,
      label: "COMPRAR (LARGO)",
      color: "text-emerald-600 dark:text-emerald-400",
      bgColor: "bg-muted",
      borderColor: "border-emerald-500 dark:border-emerald-400",
    },
    sell: {
      icon: ArrowDown,
      label: "VENDER (CORTO)",
      color: "text-red-600 dark:text-red-400",
      bgColor: "bg-muted",
      borderColor: "border-red-500 dark:border-red-400",
    },
    hold: {
      icon: Circle,
      label: "MANTENER",
      color: "text-amber-600 dark:text-amber-400",
      bgColor: "bg-muted",
      borderColor: "border-amber-500 dark:border-amber-400",
    },
  } as const;

  const config = signalConfig[stock.signal];
  const Icon = config.icon;

  const chartData = history.map((item) => ({ date: item.date, price: item.close, prediction: item.prediction }));

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (!payload || !payload.prediction) return null;
    const predictionColors: Record<string, string> = { buy: "#22c55e", sell: "#ef4444", hold: "#eab308" };
    return (
      <circle cx={cx} cy={cy} r={3} fill={predictionColors[payload.prediction]} stroke="white" strokeWidth={1} />
    );
  };

  const fmtPct = (key: string, val: any, decimals = 1) => {
    if (val === null || val === undefined || Number.isNaN(val)) return "NaN%";
    const fractionKeys = ["f1_macro", "f1_buy", "f1_sell", "accuracy"];
    try {
      if (fractionKeys.includes(key)) {
        return `${(Number(val) * 100).toFixed(decimals)}%`;
      }
      // already percentage numbers for these keys
      const pctKeys = ["cumulativeReturn", "return_vs_bh", "maxDrawdown", "winRate", "signal_buy_pct", "signal_hold_pct", "signal_sell_pct"];
      if (pctKeys.includes(key)) {
        return `${Number(val).toFixed(decimals)}%`;
      }
      // profitFactor and ratios
      if (key === "profitFactor") return `${Number(val).toFixed(2)}x`;
      if (key === "sharpeRatio") return `${Number(val).toFixed(2)}`;
      return String(val);
    } catch (e) {
      return "NaN%";
    }
  };

  return (
    <div>
      <Button onClick={() => navigate("/")} variant="ghost" size="sm" className="mb-4 gap-2">
        <ArrowLeft className="w-4 h-4" /> Volver
      </Button>

      <Card className="p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-foreground">{stock.symbol}</h1>
            <p className="text-muted-foreground mt-1">{stock.name}</p>
            <div className="text-4xl font-bold text-foreground mt-4">${stock.currentPrice.toFixed(2)}</div>
          </div>
          <div className={`flex flex-col items-center gap-2 px-6 py-4 rounded-xl ${config.bgColor} border-2 ${config.borderColor}`}>
            <Icon className={`w-8 h-8 ${config.color}`} />
            <span className={`text-sm font-bold ${config.color}`}>{config.label}</span>
            <span className="text-xs text-gray-600">{(stock.confidence * 100).toFixed(0)}% confianza</span>
          </div>
        </div>
      </Card>

      <div className="flex gap-2 mb-4">
        {[30, 60, 90].map((days) => (
          <Button key={days} onClick={() => setSelectedPeriod(days)} variant={selectedPeriod === days ? "default" : "outline"} size="sm">
            {days} días
          </Button>
        ))}
      </div>

      <Card className="p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-xl font-bold text-foreground">Historial de Precios</h2>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => {
                const d = new Date(v);
                return `${d.getMonth() + 1}/${d.getDate()}`;
              }} />
              <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
              <Tooltip contentStyle={{ backgroundColor: "var(--color-background)", border: "1px solid var(--color-border)", borderRadius: 8, color: "var(--color-foreground)" }} formatter={(value: any) => [`$${value.toFixed(2)}`, "Precio"]} />
              <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={<CustomDot />} name="Precio de Cierre" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex gap-4 text-xs">
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#10b981]"></div><span className="text-muted-foreground">Señal COMPRAR</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#ef4444]"></div><span className="text-muted-foreground">Señal VENDER</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-[#f59e0b]"></div><span className="text-muted-foreground">Señal MANTENER</span></div>
        </div>
      </Card>

      {/* Métricas Unificadas (copiadas de Performance) */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold text-foreground">Métricas Unificadas (90d / Último mes)</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3 lg:grid-cols-5">
          <MetricCard label="Retorno Acumulado (90d)" value={`${fmtPct("cumulativeReturn", metrics.cumulativeReturn, 1)}`} color="text-[#f59e0b]" />
          <MetricCard label="Return vs Buy&Hold (90d)" value={`${fmtPct("return_vs_bh", metrics.return_vs_bh, 1)}`} color="text-[#3b82f6]" />
          <MetricCard label="Sharpe (90d)" value={`${fmtPct("sharpeRatio", metrics.sharpeRatio, 2)}`} color="text-[#06b6d4]" />
          <MetricCard label="Max Drawdown (90d)" value={`${fmtPct("maxDrawdown", metrics.maxDrawdown, 2)}`} color="text-[#ef4444]" />
          <MetricCard label="Win Rate (90d)" value={`${fmtPct("winRate", metrics.winRate, 1)}`} color="text-[#10b981]" />
          <MetricCard label="Profit Factor (90d)" value={`${fmtPct("profitFactor", metrics.profitFactor, 2)}`} color="text-[#06b6d4]" />
          <MetricCard label="F1 Macro (último mes)" value={`${fmtPct("f1_macro", metrics.f1_macro, 1)}`} color="text-[#8b5cf6]" />
          <MetricCard label="F1 Buy+Sell (últ. mes)" value={`${((metrics.f1_buy ?? 0) + (metrics.f1_sell ?? 0)) > 0 ? (((metrics.f1_buy ?? 0) + (metrics.f1_sell ?? 0)) * 100).toFixed(1) + '%' : fmtPct("f1_buy", metrics.f1_buy, 1)}`} color="text-[#3b82f6]" />

          <div className="bg-muted p-4 rounded-lg">
            <div className="text-sm text-muted-foreground mb-1">Signal Distribution (90d)</div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-2 bg-emerald-600 text-white px-1 py-0.5 rounded text-xs">
                <span className="w-2 h-2 rounded-full bg-white/30" />
                <span className="font-semibold">BUY</span>
                <span className="ml-1 font-medium">{fmtPct("signal_buy_pct", metrics.signal_buy_pct, 1)}</span>
              </span>

              <span className="inline-flex items-center gap-2 bg-amber-500 text-white px-1 py-0.5 rounded text-xs">
                <span className="w-2 h-2 rounded-full bg-white/30" />
                <span className="font-semibold">HOLD</span>
                <span className="ml-1 font-medium">{fmtPct("signal_hold_pct", metrics.signal_hold_pct, 1)}</span>
              </span>

              <span className="inline-flex items-center gap-2 bg-red-600 text-white px-1 py-0.5 rounded text-xs">
                <span className="w-2 h-2 rounded-full bg-white/30" />
                <span className="font-semibold">SELL</span>
                <span className="ml-1 font-medium">{fmtPct("signal_sell_pct", metrics.signal_sell_pct, 1)}</span>
              </span>
            </div>
            <div className="text-xs text-muted-foreground mt-2">BUY / HOLD / SELL (promedio %)</div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5 text-[#3b82f6]" />
          <h2 className="text-xl font-bold text-foreground">Historial de Señales (Últimas 10)</h2>
        </div>
        <div className="overflow-x-auto mb-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b-2 border-border bg-muted">
                <th className="text-left py-2 px-3 font-semibold text-foreground">Fecha</th>
                <th className="text-center py-2 px-3 font-semibold text-foreground">Señal</th>
                <th className="text-center py-2 px-3 font-semibold text-foreground">Correcta</th>
                <th className="text-right py-2 px-3 font-semibold text-foreground">Precio Cierre</th>
              </tr>
            </thead>
            <tbody>
              {stock.recentSignals.slice(0, 10).map((signal, index) => (
                <tr key={index} className="border-b border-border hover:bg-muted">
                  <td className="py-3 px-3 text-foreground">{signal.date}</td>
                  <td className="py-3 px-3 text-center"><span className={`px-2 py-1 rounded text-xs font-bold inline-block ${signal.signal === "buy" ? "bg-muted text-emerald-600 dark:text-emerald-400" : signal.signal === "sell" ? "bg-muted text-red-600 dark:text-red-400" : "bg-muted text-amber-600 dark:text-amber-400"}`}>{signal.signal === "buy" ? "COMPRAR" : signal.signal === "sell" ? "VENDER" : "MANTENER"}</span></td>
                  <td className="py-3 px-3 text-center">{signal.correct ? (<div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center mx-auto border border-[#10b981]"><span className="text-[#10b981] text-sm font-bold">✓</span></div>) : (<div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center mx-auto border border-[#ef4444]"><span className="text-[#ef4444] text-sm font-bold">✗</span></div>)}</td>
                  <td className="py-3 px-3 text-right text-foreground font-semibold">${signal.actualPrice.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pt-4 border-t border-border flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-muted border border-[#10b981]"></div>
            <span className="text-muted-foreground">Correctas: {stock.recentSignals.slice(0, 10).filter(s => s.correct).length}/10</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-muted border border-[#ef4444]"></div>
            <span className="text-muted-foreground">Incorrectas: {stock.recentSignals.slice(0, 10).filter(s => !s.correct).length}/10</span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-muted border border-[#f59e0b] rounded text-xs text-muted-foreground">
          <strong>Nota:</strong> Las señales se generan después del cierre del mercado. La simulación asume operaciones al cierre del día siguiente. Se muestra el precio de cierre real para contexto.
        </div>
      </Card>

      {/* Sección adicional eliminada: muestra unificada ya está arriba. */}
    </div>
  );
}

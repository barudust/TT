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
  Legend,
  ResponsiveContainer,
  Dot,
} from "recharts";
import { API_BASE_URL } from "../../config/api";

interface StockDetail {
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
  prediction: string;
  actualDirection: string;
}

interface Metrics {
  accuracy: number;
  buyPrecision: number;
  sellPrecision: number;
  holdPrecision: number;
  f1Score: number;
  evaluationPeriod: number;
  totalPredictions: number;
  correctPredictions: number;
  cumulativeReturn: number;
  sharpeRatio: number;
  winRate: number;
  profitFactor: number;
  maxDrawdown: number;
  numberOfTrades: number;
  exposure: number;
  finalCapital: number;
}

export default function StockDetail() {
  const { symbol } = useParams();
  const navigate = useNavigate();
  const [stock, setStock] = useState<StockDetail | null>(null);
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

      // Fetch stock detail
      const detailResponse = await fetch(`${baseUrl}/stocks/${symbol}`);
      const detailData = await detailResponse.json();

      // Fetch historical data
      const historyResponse = await fetch(
        `${baseUrl}/stocks/${symbol}/history?days=${selectedPeriod}`
      );
      const historyData = await historyResponse.json();

      // Fetch metrics
      const metricsResponse = await fetch(`${baseUrl}/stocks/${symbol}/metrics`);
      const metricsData = await metricsResponse.json();

      if (detailData.success && historyData.success && metricsData.success) {
        setStock(detailData.data);
        setHistory(historyData.data);
        setMetrics(metricsData.data);
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
  };

  const config = signalConfig[stock.signal];
  const Icon = config.icon;

  // Preparar datos para el gráfico
  const chartData = history.map((item) => ({
    date: item.date,
    price: item.close,
    prediction: item.prediction,
  }));

  // Custom dot para mostrar predicciones
  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (!payload.prediction) return null;

    const predictionColors = {
      buy: "#22c55e",
      sell: "#ef4444",
      hold: "#eab308",
    };

    return (
      <circle
        cx={cx}
        cy={cy}
        r={3}
        fill={predictionColors[payload.prediction as keyof typeof predictionColors]}
        stroke="white"
        strokeWidth={1}
      />
    );
  };

  return (
    <div>
      <Button
        onClick={() => navigate("/")}
        variant="ghost"
        size="sm"
        className="mb-4 gap-2"
      >
        <ArrowLeft className="w-4 h-4" />
        Volver
      </Button>
      <Card className="p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-foreground">{stock.symbol}</h1>
            <p className="text-muted-foreground mt-1">{stock.name}</p>
            <div className="text-4xl font-bold text-foreground mt-4">
              ${stock.currentPrice.toFixed(2)}
            </div>
          </div>
          <div
            className={`flex flex-col items-center gap-2 px-6 py-4 rounded-xl ${config.bgColor} border-2 ${config.borderColor}`}
          >
            <Icon className={`w-8 h-8 ${config.color}`} />
            <span className={`text-sm font-bold ${config.color}`}>{config.label}</span>
            <span className="text-xs text-gray-600">
              {(stock.confidence * 100).toFixed(0)}% confianza
            </span>
          </div>
        </div>
      </Card>
      <div className="flex gap-2 mb-4">
        {[30, 60, 90].map((days) => (
          <Button
            key={days}
            onClick={() => setSelectedPeriod(days)}
            variant={selectedPeriod === days ? "default" : "outline"}
            size="sm"
          >
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
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-background)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "8px",
                  color: "var(--color-foreground)",
                }}
                formatter={(value: any) => [`$${value.toFixed(2)}`, "Precio"]}
              />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={<CustomDot />}
                name="Precio de Cierre"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#10b981]"></div>
            <span className="text-muted-foreground">Señal COMPRAR</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ef4444]"></div>
            <span className="text-muted-foreground">Señal VENDER</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#f59e0b]"></div>
            <span className="text-muted-foreground">Señal MANTENER</span>
          </div>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Métricas del Modelo</h2>
        {/* Métricas de Clasificación */}
        <div className="mb-6">
          <h3 className="font-semibold text-foreground mb-3 text-sm">Métricas de Clasificación</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-muted p-4 rounded-lg">
              <div className="text-3xl font-bold text-[#3b82f6]">
                {(metrics.accuracy * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground mt-1">Accuracy</div>
            </div>
            <div className="bg-muted p-4 rounded-lg">
              <div className="text-3xl font-bold text-[#8b5cf6]">
                {(metrics.f1Score * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground mt-1">F1-Score</div>
            </div>
            <div className="bg-muted p-4 rounded-lg">
              <div className="text-3xl font-bold text-[#10b981]">
                {(metrics.buyPrecision * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground mt-1">Precisión BUY</div>
            </div>
            <div className="bg-muted p-4 rounded-lg">
              <div className="text-3xl font-bold text-[#ef4444]">
                {(metrics.sellPrecision * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground mt-1">Precisión SELL</div>
            </div>
            <div className="bg-muted p-4 rounded-lg">
              <div className="text-3xl font-bold text-[#f59e0b]">
                {(metrics.holdPrecision * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground mt-1">Precisión HOLD</div>
            </div>
          </div>
        </div>
        <div className="border-t border-border pt-6">
          <h3 className="font-semibold text-foreground mb-3 text-sm">Rendimiento de la Estrategia</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-muted p-4 rounded-lg border border-[#10b981]">
              <div className="text-3xl font-bold text-[#10b981]">
                {metrics.cumulativeReturn.toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground mt-1">Retorno Acumulado</div>
            </div>
            <div className="bg-muted p-4 rounded-lg border border-[#3b82f6]">
              <div className="text-3xl font-bold text-[#3b82f6]">
                {metrics.sharpeRatio.toFixed(2)}
              </div>
              <div className="text-sm text-muted-foreground mt-1">Sharpe Ratio</div>
            </div>
            <div className="bg-muted p-4 rounded-lg border border-[#8b5cf6]">
              <div className="text-3xl font-bold text-[#8b5cf6]">
                {metrics.winRate.toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground mt-1">Win Rate</div>
            </div>
            <div className="bg-muted p-4 rounded-lg border border-[#f59e0b]">
              <div className="text-3xl font-bold text-[#f59e0b]">
                {metrics.profitFactor.toFixed(2)}x
              </div>
              <div className="text-sm text-muted-foreground mt-1">Profit Factor</div>
            </div>
            <div className="bg-muted p-4 rounded-lg border border-[#ef4444]">
              <div className="text-3xl font-bold text-[#ef4444]">
                -{metrics.maxDrawdown.toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground mt-1">Max Drawdown</div>
            </div>
            <div className="bg-muted p-4 rounded-lg border border-[#06b6d4]">
              <div className="text-3xl font-bold text-[#06b6d4]">
                {metrics.numberOfTrades}
              </div>
              <div className="text-sm text-muted-foreground mt-1">Operaciones</div>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-border grid gap-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Capital Final (simulado):</span>
            <span className="font-semibold text-foreground">${metrics.finalCapital.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Días en Mercado:</span>
            <span className="font-semibold text-foreground">{metrics.exposure.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Período de Evaluación:</span>
            <span className="font-semibold text-foreground">Últimos {metrics.evaluationPeriod} días</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Predicciones Totales:</span>
            <span className="font-semibold text-foreground">{metrics.totalPredictions}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Predicciones Correctas:</span>
            <span className="font-semibold text-[#10b981]">{metrics.correctPredictions}</span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-muted border border-[#3b82f6] rounded text-xs text-muted-foreground">
          <strong>Nota:</strong> Capital Final es una simulación con capital inicial ficticio ($1000).
          Se incluye un costo de transacción del 0.1% por operación. Este es un proyecto académico, no asesoría financiera.
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
                  <td className="py-3 px-3 text-center">
                    <span
                      className={`px-2 py-1 rounded text-xs font-bold inline-block ${
                        signal.signal === "buy"
                          ? "bg-muted text-emerald-600 dark:text-emerald-400"
                          : signal.signal === "sell"
                          ? "bg-muted text-red-600 dark:text-red-400"
                          : "bg-muted text-amber-600 dark:text-amber-400"
                      }`}
                    >
                      {signal.signal === "buy"
                        ? "COMPRAR"
                        : signal.signal === "sell"
                        ? "VENDER"
                        : "MANTENER"}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-center">
                    {signal.correct ? (
                      <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center mx-auto border border-[#10b981]">
                        <span className="text-[#10b981] text-sm font-bold">✓</span>
                      </div>
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center mx-auto border border-[#ef4444]">
                        <span className="text-[#ef4444] text-sm font-bold">✗</span>
                      </div>
                    )}
                  </td>
                  <td className="py-3 px-3 text-right text-foreground font-semibold">
                    ${signal.actualPrice.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pt-4 border-t border-border flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-muted border border-[#10b981]"></div>
            <span className="text-muted-foreground">
              Correctas: {stock.recentSignals.slice(0, 10).filter(s => s.correct).length}/10
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-muted border border-[#ef4444]"></div>
            <span className="text-muted-foreground">
              Incorrectas: {stock.recentSignals.slice(0, 10).filter(s => !s.correct).length}/10
            </span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-muted border border-[#f59e0b] rounded text-xs text-muted-foreground">
          <strong>Nota:</strong> Las señales se generan después del cierre del mercado.
          La simulación asume operaciones al cierre del día siguiente. Se muestra el precio de cierre real para contexto.
        </div>
      </Card>
    </div>
  );
}

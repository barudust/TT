import { useState, useEffect } from "react";
import { Card } from "../components/ui/card";
import { toast } from "sonner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ArrowUpDown, TrendingUp } from "lucide-react";
import { API_BASE_URL } from "../../config/api";

interface StockMetrics {
  symbol: string;
  name: string;
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

type SortKey = keyof StockMetrics;

interface MetricCardProps {
  label: string;
  value: string;
  color: string;
}

function MetricCard({ label, value, color }: MetricCardProps) {
  return (
    <Card className="p-4">
      <div className="text-sm text-muted-foreground mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
    </Card>
  );
}

export default function Performance() {
  const [metrics, setMetrics] = useState<StockMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<SortKey>("accuracy");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/metrics`);

      if (!response.ok) {
        throw new Error("Error al obtener métricas");
      }

      const data = await response.json();

      if (data.success) {
        setMetrics(data.data);
      } else {
        throw new Error(data.error || "Error desconocido");
      }
    } catch (error) {
      console.error("Error fetching metrics:", error);
      toast.error("No se pudieron cargar las métricas");
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setSortOrder("desc");
    }
  };

  const sortedMetrics = [...metrics].sort((a, b) => {
    const aValue = a[sortBy];
    const bValue = b[sortBy];

    if (typeof aValue === "number" && typeof bValue === "number") {
      return sortOrder === "asc" ? aValue - bValue : bValue - aValue;
    }

    return 0;
  });

  const chartData = metrics.map((m) => ({
    symbol: m.symbol,
    Precisión: parseFloat((m.accuracy * 100).toFixed(1)),
    "F1-Score": parseFloat((m.f1Score * 100).toFixed(1)),
    "Win Rate": parseFloat(m.winRate.toFixed(1)),
  }));

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-muted-foreground">Cargando métricas...</p>
      </div>
    );
  }

  const avgAccuracy = metrics.length > 0
    ? (metrics.reduce((sum, m) => sum + m.accuracy, 0) / metrics.length * 100).toFixed(1)
    : "0";

  const avgF1 = metrics.length > 0
    ? (metrics.reduce((sum, m) => sum + m.f1Score, 0) / metrics.length * 100).toFixed(1)
    : "0";

  const avgWinRate = metrics.length > 0
    ? (metrics.reduce((sum, m) => sum + m.winRate, 0) / metrics.length).toFixed(1)
    : "0";

  const avgSharpe = metrics.length > 0
    ? (metrics.reduce((sum, m) => sum + m.sharpeRatio, 0) / metrics.length).toFixed(2)
    : "0";

  const avgReturn = metrics.length > 0
    ? (metrics.reduce((sum, m) => sum + m.cumulativeReturn, 0) / metrics.length).toFixed(1)
    : "0";

  const avgDrawdown = metrics.length > 0
    ? (metrics.reduce((sum, m) => sum + m.maxDrawdown, 0) / metrics.length).toFixed(2)
    : "0";

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Rendimiento Global</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Análisis completo de métricas de clasificación y estrategia para todas las acciones
        </p>
      </div>

      {/* Chart */}
      <Card className="p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-[#3b82f6]" />
          <h3 className="text-lg font-bold text-foreground">
            Comparación de Métricas (Clasificación y Estrategia)
          </h3>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis dataKey="symbol" tick={{ fontSize: 12 }} stroke="currentColor" opacity={0.5} />
              <YAxis tick={{ fontSize: 12 }} stroke="currentColor" opacity={0.5} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-background)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "8px",
                  color: "var(--color-foreground)",
                }}
                formatter={(value: any) => `${value}%`}
              />
              <Legend />
              <Bar dataKey="Precisión" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="F1-Score" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Win Rate" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Métricas de Clasificación */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold text-foreground mb-4">Métricas de Clasificación</h3>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          <MetricCard
            label="Accuracy Promedio"
            value={`${avgAccuracy}%`}
            color="text-[#3b82f6]"
          />
          <MetricCard
            label="F1-Score Promedio"
            value={`${avgF1}%`}
            color="text-[#8b5cf6]"
          />
          <MetricCard
            label="Precisión BUY Promedio"
            value={
              metrics.length > 0
                ? `${(metrics.reduce((sum, m) => sum + m.buyPrecision, 0) / metrics.length * 100).toFixed(1)}%`
                : "0%"
            }
            color="text-[#10b981]"
          />
          <MetricCard
            label="Precisión SELL Promedio"
            value={
              metrics.length > 0
                ? `${(metrics.reduce((sum, m) => sum + m.sellPrecision, 0) / metrics.length * 100).toFixed(1)}%`
                : "0%"
            }
            color="text-[#ef4444]"
          />
          <MetricCard
            label="Precisión HOLD Promedio"
            value={
              metrics.length > 0
                ? `${(metrics.reduce((sum, m) => sum + m.holdPrecision, 0) / metrics.length * 100).toFixed(1)}%`
                : "0%"
            }
            color="text-[#f59e0b]"
          />
        </div>
      </Card>

      {/* Métricas de Rendimiento de Estrategia */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold text-foreground mb-4">Rendimiento de Estrategia</h3>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-6">
          <MetricCard
            label="Retorno Acumulado (%)"
            value={`${avgReturn}%`}
            color="text-[#f59e0b]"
          />
          <MetricCard
            label="Sharpe Ratio Promedio"
            value={avgSharpe}
            color="text-[#06b6d4]"
          />
          <MetricCard
            label="Win Rate Promedio"
            value={`${avgWinRate}%`}
            color="text-[#10b981]"
          />
          <MetricCard
            label="Profit Factor Promedio"
            value={
              metrics.length > 0
                ? (metrics.reduce((sum, m) => sum + m.profitFactor, 0) / metrics.length).toFixed(2)
                : "0"
            }
            color="text-[#06b6d4]"
          />
          <MetricCard
            label="Max Drawdown Promedio"
            value={`-${avgDrawdown}%`}
            color="text-[#ef4444]"
          />
          <MetricCard
            label="Trades Promedio"
            value={
              metrics.length > 0
                ? Math.round(metrics.reduce((sum, m) => sum + m.numberOfTrades, 0) / metrics.length).toString()
                : "0"
            }
            color="text-[#8b5cf6]"
          />
        </div>
      </Card>

      {/* Tabla Detallada */}
      <Card className="p-6">
        <h3 className="text-lg font-bold text-foreground mb-4">
          Tabla de Métricas Detalladas (Todas las Acciones)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("symbol")}
                    className="flex items-center gap-1 hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    Acción
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("accuracy")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    Acc%
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("f1Score")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    F1%
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("buyPrecision")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    Buy%
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("sellPrecision")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    Sell%
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("holdPrecision")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    Hold%
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("sharpeRatio")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    Sharpe
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("winRate")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    WinRate%
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("cumulativeReturn")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    Return%
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("maxDrawdown")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    Drawdown%
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">
                  <button
                    onClick={() => handleSort("numberOfTrades")}
                    className="flex items-center gap-1 hover:text-[#3b82f6] justify-end ml-auto"
                  >
                    Trades
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedMetrics.map((stock, index) => (
                <tr
                  key={stock.symbol}
                  className={`border-b border-border ${
                    index % 2 === 0 ? "bg-muted dark:bg-muted/50" : "bg-background"
                  } hover:bg-muted transition-colors`}
                >
                  <td className="py-3 px-2">
                    <div className="font-semibold text-foreground">{stock.symbol}</div>
                    <div className="text-xs text-muted-foreground truncate max-w-[120px]">
                      {stock.name}
                    </div>
                  </td>
                  <td className="text-right py-3 px-2">
                    <span className={`font-semibold ${
                      stock.accuracy >= 0.7
                        ? "text-[#10b981]"
                        : stock.accuracy >= 0.6
                        ? "text-[#f59e0b]"
                        : "text-[#ef4444]"
                    }`}>
                      {(stock.accuracy * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">
                    {(stock.f1Score * 100).toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">
                    {(stock.buyPrecision * 100).toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">
                    {(stock.sellPrecision * 100).toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">
                    {(stock.holdPrecision * 100).toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">
                    {stock.sharpeRatio.toFixed(2)}
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">
                    {stock.winRate.toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">
                    {stock.cumulativeReturn.toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-[#ef4444]">
                    -{stock.maxDrawdown.toFixed(2)}%
                  </td>
                  <td className="text-right py-3 px-2 text-muted-foreground">
                    {stock.numberOfTrades}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

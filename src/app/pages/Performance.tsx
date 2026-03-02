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
      const response = await fetch(
        "http://localhost:8000/metrics"
      );

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

  // Preparar datos para el gráfico
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
        <p className="mt-4 text-gray-600">Cargando métricas...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Rendimiento Global</h2>
        <p className="text-sm text-gray-500 mt-1">
          Comparación de métricas entre todas las acciones
        </p>
      </div>

      {/* Chart */}
      <Card className="p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-bold text-gray-900">
            Comparación de Métricas (Clasificación y Estrategia)
          </h3>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="symbol" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
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

      {/* Metrics Table */}
      <Card className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          Tabla de Métricas Detalladas
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-2 font-semibold text-gray-700">
                  <button
                    onClick={() => handleSort("symbol")}
                    className="flex items-center gap-1 hover:text-blue-600"
                  >
                    Acción
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-gray-700">
                  <button
                    onClick={() => handleSort("accuracy")}
                    className="flex items-center gap-1 justify-end hover:text-blue-600 ml-auto"
                  >
                    Precisión
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-gray-700">
                  <button
                    onClick={() => handleSort("buyPrecision")}
                    className="flex items-center gap-1 justify-end hover:text-blue-600 ml-auto"
                  >
                    Buy
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-gray-700">
                  <button
                    onClick={() => handleSort("sellPrecision")}
                    className="flex items-center gap-1 justify-end hover:text-blue-600 ml-auto"
                  >
                    Sell
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-gray-700">
                  <button
                    onClick={() => handleSort("f1Score")}
                    className="flex items-center gap-1 justify-end hover:text-blue-600 ml-auto"
                  >
                    F1
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
                <th className="text-right py-3 px-2 font-semibold text-gray-700">
                  <button
                    onClick={() => handleSort("totalPredictions")}
                    className="flex items-center gap-1 justify-end hover:text-blue-600 ml-auto"
                  >
                    Total
                    <ArrowUpDown className="w-3 h-3" />
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedMetrics.map((stock, index) => (
                <tr
                  key={stock.symbol}
                  className={`border-b border-gray-100 ${
                    index % 2 === 0 ? "bg-gray-50" : "bg-white"
                  } hover:bg-blue-50 transition-colors`}
                >
                  <td className="py-3 px-2">
                    <div className="font-semibold text-gray-900">{stock.symbol}</div>
                    <div className="text-xs text-gray-500 truncate max-w-[120px]">
                      {stock.name}
                    </div>
                  </td>
                  <td className="text-right py-3 px-2">
                    <span
                      className={`font-semibold ${
                        stock.accuracy >= 0.7
                          ? "text-green-600"
                          : stock.accuracy >= 0.6
                          ? "text-yellow-600"
                          : "text-red-600"
                      }`}
                    >
                      {(stock.accuracy * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="text-right py-3 px-2 text-gray-700">
                    {(stock.buyPrecision * 100).toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-gray-700">
                    {(stock.sellPrecision * 100).toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-gray-700">
                    {(stock.f1Score * 100).toFixed(1)}%
                  </td>
                  <td className="text-right py-3 px-2 text-gray-600">
                    {stock.totalPredictions}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        <Card className="p-4">
          <div className="text-sm text-gray-600 mb-1">Precisión Promedio</div>
          <div className="text-2xl font-bold text-blue-600">
            {(
              (metrics.reduce((sum, m) => sum + m.accuracy, 0) / metrics.length) *
              100
            ).toFixed(1)}
            %
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 mb-1">F1-Score Promedio</div>
          <div className="text-2xl font-bold text-purple-600">
            {(
              (metrics.reduce((sum, m) => sum + m.f1Score, 0) / metrics.length) *
              100
            ).toFixed(1)}
            %
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 mb-1">Win Rate Promedio</div>
          <div className="text-2xl font-bold text-green-600">
            {(
              metrics.reduce((sum, m) => sum + m.winRate, 0) / metrics.length
            ).toFixed(1)}
            %
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600 mb-1">Retorno Acumulado Promedio</div>
          <div className="text-2xl font-bold text-orange-600">
            {(
              metrics.reduce((sum, m) => sum + m.cumulativeReturn, 0) / metrics.length
            ).toFixed(1)}
            %
          </div>
        </Card>
      </div>
    </div>
  );
}

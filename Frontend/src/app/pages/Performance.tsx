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
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { ArrowUpDown, TrendingUp } from "lucide-react";
import { API_BASE_URL } from "../../config/api";

interface StockMetrics {
  symbol: string;
  name: string;
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
  // señal
  signal_buy_pct?: number;
  signal_hold_pct?: number;
  signal_sell_pct?: number;
}

type SortKey = keyof StockMetrics;

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

export default function Performance() {
  const [metrics, setMetrics] = useState<StockMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<SortKey>("symbol" as SortKey);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/metrics`);
      if (!res.ok) throw new Error("Error al obtener métricas");
      const data = await res.json();
      if (data && data.success) setMetrics(data.data || []);
      else if (data && Array.isArray(data)) setMetrics(data as StockMetrics[]);
      else throw new Error("Respuesta de métricas inválida");
    } catch (err) {
      console.error(err);
      toast.error("No se pudieron cargar las métricas");
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (key: SortKey) => {
    if (sortBy === key) setSortOrder((s) => (s === "asc" ? "desc" : "asc"));
    else {
      setSortBy(key);
      setSortOrder("desc");
    }
  };

  const sortedMetrics = [...metrics].sort((a, b) => {
    const av = a[sortBy] as any;
    const bv = b[sortBy] as any;
    if (typeof av === "number" && typeof bv === "number") return sortOrder === "asc" ? av - bv : bv - av;
    if (typeof av === "string" && typeof bv === "string") return sortOrder === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    return 0;
  });

  const chartData = metrics.map((m) => ({
    symbol: m.symbol,
    Precisión: parseFloat((m.accuracy * 100).toFixed(1)),
    Retorno: parseFloat(m.cumulativeReturn?.toFixed(1) ?? "0"),
    Sharpe: parseFloat(m.sharpeRatio?.toFixed(2) ?? "0"),
    "Win Rate": parseFloat(m.winRate?.toFixed(1) ?? "0"),
  }));

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-muted-foreground">Cargando métricas...</p>
      </div>
    );

  const avg = (fn: (m: StockMetrics) => number, decimals = 1) => {
    if (metrics.length === 0) return "0";
    const v = metrics.reduce((s, m) => s + fn(m), 0) / metrics.length;
    return v.toFixed(decimals);
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Rendimiento Global</h2>
        <p className="text-sm text-muted-foreground mt-1">Análisis completo de métricas de clasificación y estrategia para todas las acciones</p>
      </div>

      {/* Chart */}
      <Card className="p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-[#3b82f6]" />
          <h3 className="text-lg font-bold text-foreground">Comparación de Métricas (Clasificación y Estrategia)</h3>
        </div>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis dataKey="symbol" tick={{ fontSize: 12 }} stroke="currentColor" opacity={0.5} />
              <YAxis tick={{ fontSize: 12 }} stroke="currentColor" opacity={0.5} />
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
              <Bar dataKey="Retorno" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Sharpe" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Win Rate" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Métricas Unificadas (Clasificación + Estrategia) */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold text-foreground">Métricas Unificadas (90d / Último mes)</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3 lg:grid-cols-5">
          <MetricCard label="Retorno Acumulado (90d)" value={`${avg((m)=>m.cumulativeReturn,1)}%`} color="text-[#f59e0b]" />
          <MetricCard label="Return vs Buy&Hold (90d)" value={`${avg((m)=>m.return_vs_bh||0,1)}%`} color="text-[#3b82f6]" />
          <MetricCard label="Sharpe (90d)" value={`${avg((m)=>m.sharpeRatio,2)}`} color="text-[#06b6d4]" />
          <MetricCard label="Max Drawdown (90d)" value={`${avg((m)=>m.maxDrawdown,2)}%`} color="text-[#ef4444]" />
          <MetricCard label="Win Rate (90d)" value={`${avg((m)=>m.winRate,1)}%`} color="text-[#10b981]" />
          <MetricCard label="Profit Factor (90d)" value={`${avg((m)=>m.profitFactor||0,2)}`} color="text-[#06b6d4]" />
          <MetricCard label="F1 Macro (último mes)" value={`${(parseFloat(avg((m)=>m.f1_macro||0,3))*100).toFixed(1)}%`} color="text-[#8b5cf6]" />
          <MetricCard label="F1 Buy+Sell (últ. mes)" value={`${(parseFloat(avg((m)=>((m.f1_buy||0)+(m.f1_sell||0))/1,3))*100).toFixed(1)}%`} color="text-[#3b82f6]" />
          <div className="bg-muted p-4 rounded-lg">
            <div className="text-sm text-muted-foreground mb-1">Signal Distribution (90d)</div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-2 bg-emerald-600 text-white px-1 py-0.5 rounded text-xs">
                <span className="w-2 h-2 rounded-full bg-white/30" />
                <span className="font-semibold">BUY</span>
                <span className="ml-1 font-medium">{avg((m) => m.signal_buy_pct || 0, 1)}%</span>
              </span>

              <span className="inline-flex items-center gap-2 bg-amber-500 text-white px-1 py-0.5 rounded text-xs">
                <span className="w-2 h-2 rounded-full bg-white/30" />
                <span className="font-semibold">HOLD</span>
                <span className="ml-1 font-medium">{avg((m) => m.signal_hold_pct || 0, 1)}%</span>
              </span>

              <span className="inline-flex items-center gap-2 bg-red-600 text-white px-1 py-0.5 rounded text-xs">
                <span className="w-2 h-2 rounded-full bg-white/30" />
                <span className="font-semibold">SELL</span>
                <span className="ml-1 font-medium">{avg((m) => m.signal_sell_pct || 0, 1)}%</span>
              </span>
            </div>
            <div className="text-xs text-muted-foreground mt-2">BUY / HOLD / SELL (promedio %)</div>
          </div>
        </div>
      </Card>

      {/* Tabla Detallada */}
      <Card className="p-6">
        <h3 className="text-lg font-bold text-foreground mb-4">Tabla de Métricas Detalladas (Todas las Acciones)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-2 font-semibold text-foreground">Acción</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">Retorno (90d)</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">Return vs BH (90d)</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">Sharpe (90d)</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">Max Drawdown (90d)</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">Win Rate (90d)</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">Profit Factor (90d)</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">F1 Macro (últ. mes)</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">F1 Buy+Sell (últ. mes)</th>
                <th className="text-right py-3 px-2 font-semibold text-foreground">Signal (B/H/S)</th>
              </tr>
            </thead>
            <tbody>
              {sortedMetrics.map((stock, index) => (
                <tr key={stock.symbol} className={`border-b border-border ${index % 2 === 0 ? "bg-muted dark:bg-muted/50" : "bg-background"} hover:bg-muted transition-colors`}>
                  <td className="py-3 px-2">
                    <div className="font-semibold text-foreground">{stock.symbol}</div>
                    <div className="text-xs text-muted-foreground truncate max-w-[120px]">{stock.name}</div>
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">{(stock.cumulativeReturn ?? 0).toFixed(1)}%</td>
                  <td className="text-right py-3 px-2 text-foreground">{(stock.return_vs_bh ?? 0).toFixed(1)}%</td>
                  <td className="text-right py-3 px-2 text-foreground">{(stock.sharpeRatio ?? 0).toFixed(2)}</td>
                  <td className="text-right py-3 px-2 text-[#ef4444]">-{(stock.maxDrawdown ?? 0).toFixed(2)}%</td>
                  <td className="text-right py-3 px-2 text-foreground">{(stock.winRate ?? 0).toFixed(1)}%</td>
                  <td className="text-right py-3 px-2 text-foreground">{(stock.profitFactor ?? 0).toFixed(2)}</td>
                  <td className="text-right py-3 px-2 text-foreground">{((stock.f1_macro ?? 0) * 100).toFixed(1)}%</td>
                  <td className="text-right py-3 px-2 text-foreground">{(((stock.f1_buy ?? 0) + (stock.f1_sell ?? 0)) * 100).toFixed(1)}%</td>
                  <td className="text-right py-3 px-2 text-foreground">
                    <div className="text-xs">B:{(stock.signal_buy_pct ?? 0).toFixed(1)}%</div>
                    <div className="text-xs">H:{(stock.signal_hold_pct ?? 0).toFixed(1)}%</div>
                    <div className="text-xs">S:{(stock.signal_sell_pct ?? 0).toFixed(1)}%</div>
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

import { useState, useEffect } from "react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { Target, Wallet } from "lucide-react";
import { API_BASE_URL } from "../../config/api";
import { SIGNAL_CONFIG, dd, fecha, frac, num, pct } from "../format";
import type { StockMetrics } from "../types";

interface MetricCardProps {
  label: string;
  value: string;
  hint?: string;
  color?: string;
}

function MetricCard({ label, value, hint, color = "text-foreground" }: MetricCardProps) {
  return (
    <div className="bg-muted p-4 rounded-lg">
      <div className="text-sm text-muted-foreground mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      {hint && <div className="text-xs text-muted-foreground mt-1">{hint}</div>}
    </div>
  );
}

type SortKey = "symbol" | "f1_macro" | "accuracy" | "cumulativeReturn" | "bh_return" | "sharpeRatio" | "maxDrawdown" | "winRate" | "signal_hold_pct";

const tooltipStyle = {
  backgroundColor: "var(--color-background)",
  border: "1px solid var(--color-border)",
  borderRadius: "8px",
  color: "var(--color-foreground)",
};

export default function Performance() {
  const [metrics, setMetrics] = useState<StockMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [sortBy, setSortBy] = useState<SortKey>("symbol");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  useEffect(() => {
    fetchMetrics();
  }, [days]);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/metrics?days=${days}`);
      if (!res.ok) throw new Error("Error al obtener métricas");
      const data = await res.json();
      if (data && data.success) setMetrics(data.data || []);
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

  const avg = (fn: (m: StockMetrics) => number | null | undefined): number | undefined => {
    const vals = metrics.map(fn).filter((v): v is number => typeof v === "number" && Number.isFinite(v));
    if (vals.length === 0) return undefined;
    return vals.reduce((s, v) => s + v, 0) / vals.length;
  };

  if (loading)
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-muted-foreground">Cargando métricas...</p>
      </div>
    );

  const ref = metrics[0];
  const returnData = metrics.map((m) => ({
    symbol: m.symbol,
    Estrategia: m.cumulativeReturn ?? 0,
    "Buy & hold": m.bh_return ?? 0,
  }));
  const f1Data = metrics.map((m) => ({ symbol: m.symbol, "F1-macro": +((m.f1_macro ?? 0) * 100).toFixed(1) }));

  const header = (key: SortKey, label: string, align = "text-right") => (
    <th className={`${align} py-3 px-2 font-semibold text-foreground cursor-pointer select-none whitespace-nowrap`} onClick={() => handleSort(key)}>
      {label}{sortBy === key ? (sortOrder === "asc" ? " ▲" : " ▼") : ""}
    </th>
  );

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-foreground">Rendimiento Global</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Señales del modelo evaluadas contra lo que realmente pasó al día siguiente
          {ref ? ` · ${fecha(ref.periodStart)} – ${fecha(ref.periodEnd)}` : ""}
        </p>
      </div>

      <div className="flex gap-2 mb-6">
        {[30, 60, 90].map((d) => (
          <Button key={d} onClick={() => setDays(d)} variant={days === d ? "default" : "outline"} size="sm">
            {d} días
          </Button>
        ))}
      </div>

      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold text-foreground mb-4">Promedio de las 7 acciones</h3>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          <MetricCard label="F1-macro" value={frac(avg((m) => m.f1_macro))} hint="Azar ≈ 33 %" color="text-[#8b5cf6]" />
          <MetricCard label="Aciertos" value={frac(avg((m) => m.accuracy))} />
          <MetricCard label="Retorno estrategia" value={pct(avg((m) => m.cumulativeReturn), 1, true)} hint={`Buy & hold: ${pct(avg((m) => m.bh_return), 1, true)}`} />
          <MetricCard label="Sharpe estrategia" value={num(avg((m) => m.sharpeRatio), 2, true)} hint={`${metrics.filter((m) => typeof m.sharpeRatio === "number").length} de ${metrics.length} acciones con ≥5 días con posición · Buy & hold: ${num(avg((m) => m.bh_sharpe), 2, true)}`} color="text-[#06b6d4]" />
          <MetricCard label="Máx. drawdown" value={dd(avg((m) => m.maxDrawdown))} color="text-red-600 dark:text-red-400" />
          <MetricCard label="Win rate" value={pct(avg((m) => m.winRate), 1)} />
          <MetricCard label="Exposición" value={pct(avg((m) => m.exposure), 1)} hint="Días con posición abierta" />
          <div className="bg-muted p-4 rounded-lg">
            <div className="text-sm text-muted-foreground mb-2">Señales emitidas</div>
            <div className="flex flex-wrap gap-1">
              {(["buy", "hold", "sell"] as const).map((s) => (
                <span key={s} className="text-white px-2 py-0.5 rounded text-xs font-semibold" style={{ backgroundColor: SIGNAL_CONFIG[s].hex }}>
                  {SIGNAL_CONFIG[s].short} {pct(avg((m) => m[`signal_${s}_pct` as const]), 0)}
                </span>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Wallet className="w-5 h-5 text-[#06b6d4]" />
          <h3 className="text-lg font-bold text-foreground">Retorno de la estrategia vs. buy & hold (%)</h3>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={returnData}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis dataKey="symbol" tick={{ fontSize: 12 }} stroke="currentColor" opacity={0.5} />
              <YAxis tick={{ fontSize: 12 }} stroke="currentColor" opacity={0.5} unit="%" />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: any) => `${Number(v).toFixed(1)} %`} />
              <Legend />
              <ReferenceLine y={0} stroke="currentColor" opacity={0.4} />
              <Bar dataKey="Estrategia" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Buy & hold" fill="#94a3b8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-5 h-5 text-[#8b5cf6]" />
          <h3 className="text-lg font-bold text-foreground">F1-macro por acción (%)</h3>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={f1Data}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis dataKey="symbol" tick={{ fontSize: 12 }} stroke="currentColor" opacity={0.5} />
              <YAxis tick={{ fontSize: 12 }} stroke="currentColor" opacity={0.5} unit="%" domain={[0, 60]} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: any) => `${v} %`} />
              <ReferenceLine y={33.3} stroke="#ef4444" strokeDasharray="4 4" label={{ value: "azar", position: "right", fontSize: 11, fill: "#ef4444" }} />
              <Bar dataKey="F1-macro" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-bold text-foreground mb-4">Detalle por acción</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                {header("symbol", "Acción", "text-left")}
                {header("f1_macro", "F1-macro")}
                {header("accuracy", "Aciertos")}
                {header("cumulativeReturn", "Retorno")}
                {header("bh_return", "Buy & hold")}
                {header("sharpeRatio", "Sharpe")}
                {header("maxDrawdown", "Máx. DD")}
                {header("winRate", "Win rate")}
                {header("signal_hold_pct", "C / M / V")}
              </tr>
            </thead>
            <tbody>
              {sortedMetrics.map((stock, index) => (
                <tr key={stock.symbol} className={`border-b border-border ${index % 2 === 0 ? "bg-muted dark:bg-muted/50" : "bg-background"} hover:bg-muted transition-colors`}>
                  <td className="py-3 px-2">
                    <div className="font-semibold text-foreground">{stock.symbol}</div>
                    <div className="text-xs text-muted-foreground truncate max-w-[120px]">{stock.name}</div>
                  </td>
                  <td className="text-right py-3 px-2 text-foreground">{frac(stock.f1_macro)}</td>
                  <td className="text-right py-3 px-2 text-foreground">{frac(stock.accuracy)}</td>
                  <td className="text-right py-3 px-2 text-foreground">{pct(stock.cumulativeReturn, 1, true)}</td>
                  <td className="text-right py-3 px-2 text-muted-foreground">{pct(stock.bh_return, 1, true)}</td>
                  <td className="text-right py-3 px-2 text-foreground">{num(stock.sharpeRatio, 2, true)}</td>
                  <td className="text-right py-3 px-2 text-red-600 dark:text-red-400">{dd(stock.maxDrawdown)}</td>
                  <td className="text-right py-3 px-2 text-foreground">{pct(stock.winRate, 1)}<div className="text-xs text-muted-foreground">{stock.numberOfTrades ?? 0} op.</div></td>
                  <td className="text-right py-3 px-2 text-foreground whitespace-nowrap text-xs">
                    {pct(stock.signal_buy_pct, 0)} / {pct(stock.signal_hold_pct, 0)} / {pct(stock.signal_sell_pct, 0)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-muted-foreground mt-4">
          C / M / V = porcentaje de señales COMPRAR / MANTENER / VENDER emitidas en el periodo. La estrategia abre
          una posición larga (COMPRAR) o corta (VENDER) al cierre y la cierra al cierre del día siguiente; MANTENER
          no opera. Sin costos de transacción. Las métricas se calculan solo con las señales cuyo resultado ya se conoce;
          el Sharpe se omite (—) cuando hubo menos de 5 días con posición, porque con tan pocas operaciones no es interpretable.
        </p>
      </Card>
    </div>
  );
}

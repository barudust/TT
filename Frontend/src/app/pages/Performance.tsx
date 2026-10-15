import { useState, useEffect } from "react";
import { Link } from "react-router";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { MetricCard } from "../components/MetricCard";
import { InfoLink } from "../components/InfoLink";
import { toast } from "sonner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { Target, Wallet, Table2 } from "lucide-react";
import { API_BASE_URL } from "../../config/api";
import { SIGNAL_CONFIG, dd, fechaLarga, frac, num, pct, usd } from "../format";
import type { StockMetrics } from "../types";

type SortKey = "name" | "f1_macro" | "accuracy" | "cumulativeReturn" | "bh_return" | "sharpeRatio" | "maxDrawdown" | "winRate" | "signal_hold_pct";

const tooltipStyle = {
  backgroundColor: "var(--color-background)",
  border: "1px solid var(--color-border)",
  borderRadius: "8px",
  color: "var(--color-foreground)",
  fontSize: 12,
};
const ejeEstilo = { fontSize: 12, fill: "currentColor", opacity: 0.7 };

// Nombre corto para los ejes (la clave sola no le dice nada a quien no conoce la bolsa)
const NOMBRE_CORTO: Record<string, string> = {
  AAPL: "Apple", MSFT: "Microsoft", GOOGL: "Google", AMZN: "Amazon", TSLA: "Tesla", META: "Meta", NVDA: "NVIDIA",
};

export default function Performance() {
  const [metrics, setMetrics] = useState<StockMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [sortBy, setSortBy] = useState<SortKey>("name");
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
      toast.error("No se pudieron cargar los resultados");
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
        <p className="mt-4 text-muted-foreground">Cargando resultados...</p>
      </div>
    );

  const ref = metrics[0];
  const corto = (m: StockMetrics) => NOMBRE_CORTO[m.symbol] ?? m.symbol;
  const returnData = metrics.map((m) => ({
    empresa: corto(m),
    "Siguiendo las recomendaciones": m.cumulativeReturn ?? 0,
    "Comprar y esperar": m.bh_return ?? 0,
  }));
  const f1Data = metrics.map((m) => ({ empresa: corto(m), "Calificación (F1)": +((m.f1_macro ?? 0) * 100).toFixed(1) }));

  const roiProm = avg((m) => m.cumulativeReturn);
  const bhProm = avg((m) => m.bh_return);
  const aciertosTot = metrics.reduce((s, m) => s + (m.correctPredictions ?? 0), 0);
  const evaluadosTot = metrics.reduce((s, m) => s + (m.evaluatedPredictions ?? 0), 0);
  const ganaron = metrics.filter((m) => (m.return_vs_bh ?? -Infinity) > 0).length;

  const header = (key: SortKey, label: string, unidad: string, help?: string, align = "text-right") => (
    <th className={`${align} py-3 px-2 font-semibold text-foreground align-bottom`}>
      <span className="inline-flex items-start gap-1">
        <button className="cursor-pointer select-none hover:text-blue-500 text-left" onClick={() => handleSort(key)} title="Ordenar">
          {label}
          {sortBy === key ? (sortOrder === "asc" ? " ▲" : " ▼") : ""}
        </button>
        {help && <InfoLink term={help} />}
      </span>
      {unidad && <div className="text-[11px] font-normal text-muted-foreground">{unidad}</div>}
    </th>
  );

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-foreground">¿Qué tan bien le ha ido al modelo?</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Las recomendaciones de cada día comparadas con lo que realmente pasó al día siguiente, en las 7 empresas.
        </p>
      </div>

      <div className="mb-6">
        <div className="text-sm font-semibold text-foreground mb-2 flex items-center gap-1">
          Periodo a analizar <InfoLink term="periodo" />
        </div>
        <div className="flex flex-wrap gap-2">
          {[
            [30, "Últimos 30 días hábiles (≈ 1½ meses)"],
            [60, "60 días (≈ 3 meses)"],
            [90, "90 días (≈ 4 meses)"],
          ].map(([d, label]) => (
            <Button key={d} onClick={() => setDays(d as number)} variant={days === d ? "default" : "outline"} size="sm">
              {label}
            </Button>
          ))}
        </div>
        {ref && (
          <p className="text-xs text-muted-foreground mt-2">
            Del {fechaLarga(ref.periodStart)} al {fechaLarga(ref.periodEnd)}
          </p>
        )}
      </div>

      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold text-foreground mb-1">Resumen de las 7 empresas</h3>
        <p className="text-xs text-muted-foreground mb-4">Promedio de las 7 empresas, con $1,000 invertidos en cada una y sin comisiones.</p>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          <MetricCard
            label="Recomendaciones acertadas"
            help="aciertos"
            value={evaluadosTot ? pct((aciertosTot / evaluadosTot) * 100, 0) : "—"}
            hint={`${aciertosTot} de ${evaluadosTot} días calificados · al azar ≈ 33 %`}
          />
          <MetricCard label="Calificación del modelo (F1)" help="f1" value={frac(avg((m) => m.f1_macro), 0)} hint="De 0 a 100 %. Al azar ≈ 33 %" color="text-[#8b5cf6]" />
          <MetricCard
            label="Empresas en que convino seguir las recomendaciones"
            help="diferencia"
            value={`${ganaron} de ${metrics.length}`}
            hint="Dieron más que comprar y esperar"
          />
          <MetricCard
            label="Rendimiento de la inversión (ROI) promedio"
            help="roi"
            value={pct(roiProm, 1, true)}
            color={roiProm === undefined ? undefined : roiProm >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}
            hint={roiProm !== undefined ? `$1,000 → ${usd(1000 * (1 + roiProm / 100))}` : undefined}
          />
          <MetricCard
            label="Si solo hubieras comprado y esperado"
            help="comprar-y-esperar"
            value={pct(bhProm, 1, true)}
            hint={bhProm !== undefined ? `$1,000 → ${usd(1000 * (1 + bhProm / 100))}` : undefined}
          />
          <MetricCard
            label="Ganancia ajustada al riesgo (Sharpe)"
            help="sharpe"
            value={num(avg((m) => m.sharpeRatio), 2, true)}
            hint={`> 0 gana · > 1 bueno · comprar y esperar: ${num(avg((m) => m.bh_sharpe), 2, true)}`}
            color="text-[#06b6d4]"
          />
          <MetricCard label="Peor caída promedio" help="drawdown" value={dd(avg((m) => m.maxDrawdown))} color="text-red-600 dark:text-red-400" />
          <MetricCard label="Operaciones con ganancia" help="win-rate" value={pct(avg((m) => m.winRate), 0)} hint="50 % sería como lanzar una moneda" />
          <div className="bg-muted p-4 rounded-lg">
            <div className="text-sm text-muted-foreground mb-2 flex items-center gap-1">
              Cuántas veces recomendó cada opción <InfoLink term="frecuencia-recomendaciones" />
            </div>
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
        <div className="flex items-center gap-2 mb-1">
          <Wallet className="w-5 h-5 text-[#06b6d4]" />
          <h3 className="text-lg font-bold text-foreground">¿Cuánto habrías ganado o perdido en cada empresa?</h3>
        </div>
        <p className="text-xs text-muted-foreground mb-4">
          Barra de color: siguiendo las recomendaciones. Barra gris: comprando el primer día y esperando. Arriba de la
          línea del 0 % es ganancia; abajo, pérdida.
        </p>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={returnData} margin={{ top: 10, right: 10, bottom: 30, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis dataKey="empresa" tick={ejeEstilo} interval={0} angle={-35} textAnchor="end" height={55} label={{ value: "Empresa", position: "insideBottom", offset: -20, style: ejeEstilo }} />
              <YAxis
                tick={ejeEstilo}
                unit=" %"
                width={70}
                label={{ value: "Rendimiento de la inversión (%)", angle: -90, position: "insideLeft", style: { ...ejeEstilo, textAnchor: "middle" } }}
              />
              <Tooltip
                contentStyle={tooltipStyle}
                formatter={(v: any, name: any) => [`${Number(v) > 0 ? "+" : ""}${Number(v).toFixed(1)} % ($1,000 → ${usd(1000 * (1 + Number(v) / 100))})`, name]}
              />
              <ReferenceLine y={0} stroke="currentColor" opacity={0.5} />
              <Bar dataKey="Siguiendo las recomendaciones" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Comprar y esperar" fill="#94a3b8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3.5 h-3.5 rounded-sm bg-[#06b6d4]"></div>
            <span className="text-muted-foreground">Siguiendo las recomendaciones</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3.5 h-3.5 rounded-sm bg-[#94a3b8]"></div>
            <span className="text-muted-foreground">Comprar y esperar</span>
          </div>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Target className="w-5 h-5 text-[#8b5cf6]" />
          <h3 className="text-lg font-bold text-foreground">¿Qué tan bien acierta el modelo en cada empresa?</h3>
          <InfoLink term="f1" />
        </div>
        <p className="text-xs text-muted-foreground mb-4">
          Calificación del modelo (F1) de 0 a 100 %. La línea roja punteada es lo que se obtendría escogiendo al azar
          (33 %): las barras por encima de ella son mejores que adivinar.
        </p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={f1Data} margin={{ top: 10, right: 30, bottom: 30, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis dataKey="empresa" tick={ejeEstilo} interval={0} angle={-35} textAnchor="end" height={55} label={{ value: "Empresa", position: "insideBottom", offset: -20, style: ejeEstilo }} />
              <YAxis
                tick={ejeEstilo}
                unit=" %"
                width={70}
                domain={[0, 60]}
                label={{ value: "Calificación F1 (%)", angle: -90, position: "insideLeft", style: { ...ejeEstilo, textAnchor: "middle" } }}
              />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: any) => [`${v} % (al azar ≈ 33 %)`, "Calificación"]} />
              <ReferenceLine y={33.3} stroke="#ef4444" strokeDasharray="4 4" label={{ value: "azar", position: "right", fontSize: 11, fill: "#ef4444" }} />
              <Bar dataKey="Calificación (F1)" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-2 mb-1">
          <Table2 className="w-5 h-5 text-[#3b82f6]" />
          <h3 className="text-lg font-bold text-foreground">Comparación de las 7 empresas</h3>
        </div>
        <p className="text-xs text-muted-foreground mb-4">
          Toca el nombre de una columna para ordenar. Toca una empresa para ver su detalle.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                {header("name", "Empresa", "", undefined, "text-left")}
                {header("accuracy", "Acertó", "% de días (días)", "aciertos")}
                {header("f1_macro", "Calificación", "F1, % (azar 33)", "f1")}
                {header("cumulativeReturn", "Siguiendo recomendaciones", "rendimiento %", "roi")}
                {header("bh_return", "Comprar y esperar", "rendimiento %", "comprar-y-esperar")}
                {header("sharpeRatio", "Ajustada al riesgo", "Sharpe", "sharpe")}
                {header("maxDrawdown", "Peor caída", "%", "drawdown")}
                {header("winRate", "Operaciones con ganancia", "% (días)", "win-rate")}
                {header("signal_hold_pct", "Recomendó", "% COMPRAR / MANTENER / VENDER", "frecuencia-recomendaciones")}
              </tr>
            </thead>
            <tbody>
              {sortedMetrics.map((stock, index) => {
                const ganados = stock.winRate != null && stock.numberOfTrades ? Math.round((stock.winRate * stock.numberOfTrades) / 100) : null;
                return (
                  <tr key={stock.symbol} className={`border-b border-border ${index % 2 === 0 ? "bg-muted dark:bg-muted/50" : "bg-background"} hover:bg-muted transition-colors`}>
                    <td className="py-3 px-2">
                      <Link to={`/stock/${stock.symbol}`} className="font-semibold text-foreground hover:text-blue-500">{stock.name}</Link>
                      <div className="text-xs text-muted-foreground">{stock.symbol}</div>
                    </td>
                    <td className="text-right py-3 px-2 text-foreground">
                      {frac(stock.accuracy, 0)}
                      <div className="text-xs text-muted-foreground">{stock.correctPredictions ?? 0} de {stock.evaluatedPredictions}</div>
                    </td>
                    <td className="text-right py-3 px-2 text-foreground">{frac(stock.f1_macro, 0)}</td>
                    <td className={`text-right py-3 px-2 font-medium ${(stock.cumulativeReturn ?? 0) >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}>
                      {pct(stock.cumulativeReturn, 1, true)}
                      <div className="text-xs text-muted-foreground font-normal">$1,000 → {usd(stock.finalCapital, 0)}</div>
                    </td>
                    <td className="text-right py-3 px-2 text-muted-foreground">{pct(stock.bh_return, 1, true)}</td>
                    <td className="text-right py-3 px-2 text-foreground">{num(stock.sharpeRatio, 2, true)}</td>
                    <td className="text-right py-3 px-2 text-red-600 dark:text-red-400">{dd(stock.maxDrawdown)}</td>
                    <td className="text-right py-3 px-2 text-foreground">
                      {pct(stock.winRate, 0)}
                      <div className="text-xs text-muted-foreground">{ganados !== null ? `${ganados} de ${stock.numberOfTrades}` : "sin operaciones"}</div>
                    </td>
                    <td className="text-right py-3 px-2 text-foreground whitespace-nowrap text-xs">
                      <span className={SIGNAL_CONFIG.buy.color}>{pct(stock.signal_buy_pct, 0)}</span> /{" "}
                      <span className={SIGNAL_CONFIG.hold.color}>{pct(stock.signal_hold_pct, 0)}</span> /{" "}
                      <span className={SIGNAL_CONFIG.sell.color}>{pct(stock.signal_sell_pct, 0)}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-muted-foreground mt-4">
          Simulación: con COMPRAR se compra al cierre y se vende al cierre del día siguiente; con VENDER se vende en corto
          igual; con MANTENER no se hace nada. Sin comisiones. Solo cuentan los días que ya se pueden calificar. La
          ganancia ajustada al riesgo (Sharpe) aparece como «—» cuando hubo menos de 5 días invertidos.
        </p>
      </Card>
    </div>
  );
}

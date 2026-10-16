import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { ArrowLeft, TrendingUp, Calendar, Target, Wallet, PiggyBank } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { MetricCard } from "../components/MetricCard";
import { InfoLink } from "../components/InfoLink";
import { SeguridadBadge } from "../components/SeguridadBadge";
import { toast } from "sonner";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { API_BASE_URL } from "../../config/api";
import { SIGNAL_CONFIG, dd, deTotal, fecha, fechaDia, fechaEje, fechaLarga, frac, num, pct, usd } from "../format";
import type { HistoryRow, Signal, StockDetail as StockDetailType, WindowMetrics } from "../types";

const CAPITAL_INICIAL = 1000;

const tooltipStyle = {
  backgroundColor: "var(--color-background)",
  border: "1px solid var(--color-border)",
  borderRadius: 8,
  color: "var(--color-foreground)",
  fontSize: 12,
};
const ejeEstilo = { fontSize: 12, fill: "currentColor", opacity: 0.7 };

function SignalPill({ signal }: { signal: Signal | null }) {
  if (!signal) return <span className="text-muted-foreground">—</span>;
  const c = SIGNAL_CONFIG[signal];
  return <span className={`px-2 py-1 rounded text-xs font-bold inline-block bg-muted ${c.color}`}>{c.short}</span>;
}

function ProbabilityBar({ probabilities }: { probabilities: StockDetailType["probabilities"] }) {
  if (!probabilities) return null;
  const order: Signal[] = ["buy", "hold", "sell"];
  return (
    <div>
      <div className="flex h-4 w-full overflow-hidden rounded-full">
        {order.map((s) => (
          <div
            key={s}
            style={{ width: `${probabilities[s] * 100}%`, backgroundColor: SIGNAL_CONFIG[s].hex }}
            title={`${SIGNAL_CONFIG[s].short}: ${frac(probabilities[s])}`}
          />
        ))}
      </div>
      <div className="mt-2 grid grid-cols-3 text-xs">
        {order.map((s) => (
          <div key={s} className={`${SIGNAL_CONFIG[s].color} ${s === "hold" ? "text-center" : s === "sell" ? "text-right" : ""}`}>
            <span className="font-semibold">{SIGNAL_CONFIG[s].short}</span> {frac(probabilities[s], 0)}
          </div>
        ))}
      </div>
    </div>
  );
}

/** Capital día a día siguiendo las recomendaciones y comprando y esperando
 *  (misma fórmula que la API: compra +r, venta −r, mantener 0, con r = ln(1+cambio)). */
function curvaCapital(history: HistoryRow[]) {
  let estrategia = CAPITAL_INICIAL;
  let compraEspera = CAPITAL_INICIAL;
  const puntos: Array<{ date: string; estrategia: number; compraEspera: number }> = [];
  for (const row of history) {
    if (row.nextReturn === null) continue;
    const r = Math.log1p(row.nextReturn / 100);
    const pos = row.prediction === "buy" ? 1 : row.prediction === "sell" ? -1 : 0;
    estrategia *= Math.exp(pos * r);
    compraEspera *= Math.exp(r);
    puntos.push({ date: row.date, estrategia: +estrategia.toFixed(2), compraEspera: +compraEspera.toFixed(2) });
  }
  return puntos;
}

export default function StockDetail() {
  const { symbol } = useParams();
  const navigate = useNavigate();

  const [stock, setStock] = useState<StockDetailType | null>(null);
  const [history, setHistory] = useState<HistoryRow[]>([]);
  const [metrics, setMetrics] = useState<WindowMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    fetchStockData();
  }, [symbol, selectedPeriod]);

  const fetchStockData = async () => {
    try {
      setLoading(true);
      const [detailData, historyData, metricsData] = await Promise.all([
        fetch(`${API_BASE_URL}/stocks/${symbol}`).then((r) => r.json()),
        fetch(`${API_BASE_URL}/stocks/${symbol}/history?days=${selectedPeriod}`).then((r) => r.json()),
        fetch(`${API_BASE_URL}/stocks/${symbol}/metrics?days=${selectedPeriod}`).then((r) => r.json()),
      ]);

      if (detailData?.success && historyData?.success && metricsData?.success) {
        setStock(detailData.data);
        setHistory(historyData.data);
        setMetrics(metricsData.data);
      } else {
        throw new Error("Error al cargar datos");
      }
    } catch (error) {
      console.error("Error fetching stock detail:", error);
      toast.error("No pudimos cargar esta empresa. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stock || !metrics) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p className="mt-4 text-muted-foreground">Cargando…</p>
      </div>
    );
  }

  const config = SIGNAL_CONFIG[stock.signal];
  const Icon = config.icon;

  const chartData = history.map((item) => ({
    date: item.date,
    price: item.close,
    prediction: item.prediction,
    correct: item.correct,
    nextReturn: item.nextReturn,
  }));
  const capital = curvaCapital(history);

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (!payload || !payload.prediction) return null;
    const color = SIGNAL_CONFIG[payload.prediction as Signal]?.hex;
    return <circle cx={cx} cy={cy} r={6} fill={color} stroke="white" strokeWidth={1.5} />;
  };

  const evaluadas = stock.recentSignals.filter((s) => s.correct !== null);
  const aciertos = evaluadas.filter((s) => s.correct).length;
  const pendientes = stock.recentSignals.length - evaluadas.length;
  const colorSigno = (v?: number | null) =>
    v === undefined || v === null ? "text-foreground" : v >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400";

  const evaluados = metrics.evaluatedPredictions;
  const diasRecomendo = (s: Signal) => Math.round(((metrics[`signal_${s}_pct` as const] ?? 0) * metrics.totalPredictions) / 100);
  const capitalBH = metrics.bh_return !== undefined ? CAPITAL_INICIAL * (1 + metrics.bh_return / 100) : undefined;
  const diasInvertido = metrics.numberOfTrades ?? 0;
  const diasGanados = metrics.winRate != null ? Math.round((metrics.winRate * diasInvertido) / 100) : null;

  return (
    <div>
      <Button onClick={() => navigate("/")} variant="ghost" size="sm" className="mb-4 gap-2">
        <ArrowLeft className="w-4 h-4" /> Volver
      </Button>

      {/* ── Recomendación de hoy ─────────────────────────────────────────── */}
      <Card className="p-6 mb-6">
        <div className="flex flex-wrap items-start justify-between gap-4 mb-5">
          <div className="flex-1 min-w-[200px]">
            <div className="flex items-baseline gap-2">
              <h1 className="text-3xl font-bold text-foreground">{stock.name}</h1>
              <span className="text-muted-foreground">{stock.symbol}</span>
            </div>
            <div className="text-4xl font-bold text-foreground mt-4">{usd(stock.currentPrice)}</div>
            <div className="text-xs text-muted-foreground">Cierre del {fechaDia(stock.dataDate)}</div>
          </div>
          <div className={`flex flex-col items-center gap-1.5 px-6 py-4 rounded-xl bg-muted border-2 text-center ${config.borderColor}`}>
            {stock.nextTradingDay && <span className="text-xs text-muted-foreground">Para el {fechaDia(stock.nextTradingDay)}</span>}
            <Icon className={`w-8 h-8 ${config.color}`} />
            <span className={`text-lg font-bold uppercase tracking-wide ${config.color}`}>{config.label}</span>
            <span className="text-xs text-muted-foreground">{config.frase}</span>
          </div>
        </div>
        <div className="border-t border-border pt-4 grid gap-5 md:grid-cols-2">
          <div>
            <div className="text-sm font-semibold text-foreground mb-2">¿Qué tan segura es?</div>
            <SeguridadBadge confianza={stock.confidence} variante="completo" conAyuda />
          </div>
          <div>
            <div className="text-sm font-semibold text-foreground mb-2 flex items-center gap-1">
              Cómo se repartió la decisión <InfoLink term="probabilidades" />
            </div>
            <ProbabilityBar probabilities={stock.probabilities} />
            <p className="text-xs text-muted-foreground mt-2">Si las tres andan cerca de 33 %, el modelo está indeciso.</p>
          </div>
        </div>
      </Card>

      {/* ── Periodo ──────────────────────────────────────────────────────── */}
      <div className="mb-4">
        <div className="flex flex-wrap items-center gap-2">
          {[30, 60, 90].map((days) => (
            <Button key={days} onClick={() => setSelectedPeriod(days)} variant={selectedPeriod === days ? "default" : "outline"} size="sm">
              {days} días
            </Button>
          ))}
          <InfoLink term="periodo" />
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Del {fecha(metrics.periodStart)} al {fecha(metrics.periodEnd)}
        </p>
      </div>

      {/* ── Gráfica de precio ────────────────────────────────────────────── */}
      <Card className="p-6 mb-6">
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-xl font-bold text-foreground">Precio y recomendaciones</h2>
        </div>
        <p className="text-xs text-muted-foreground mb-4">Cada punto es lo que el modelo recomendó ese día.</p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, bottom: 25, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis
                dataKey="date"
                tick={ejeEstilo}
                tickFormatter={fechaEje}
                minTickGap={20}
                label={{ value: "Fecha", position: "insideBottom", offset: -15, style: ejeEstilo }}
              />
              <YAxis
                tick={ejeEstilo}
                domain={["auto", "auto"]}
                width={75}
                tickFormatter={(v: number) => `$${v.toFixed(0)}`}
                label={{ value: "Precio (USD)", angle: -90, position: "insideLeft", style: { ...ejeEstilo, textAnchor: "middle" } }}
              />
              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={(v: string) => fechaLarga(v)}
                formatter={(value: any, _name: any, item: any) => {
                  const p = item.payload;
                  const rec = SIGNAL_CONFIG[p.prediction as Signal]?.short.toLowerCase() ?? "—";
                  const res = p.correct === null ? "pendiente" : p.correct ? "acertó" : "falló";
                  return [`${usd(Number(value))} · dijo ${rec} (${res})`, "Cierre"];
                }}
              />
              <Line type="linear" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={<CustomDot />} activeDot={{ r: 8 }} name="Cierre" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex flex-wrap gap-4 text-xs">
          {(["buy", "hold", "sell"] as Signal[]).map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div className="w-3.5 h-3.5 rounded-full" style={{ backgroundColor: SIGNAL_CONFIG[s].hex }}></div>
              <span className="text-muted-foreground">{SIGNAL_CONFIG[s].short}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* ── ¿Qué habría pasado con $1,000? ───────────────────────────────── */}
      {capital.length > 1 && (
        <Card className="p-6 mb-6">
          <div className="flex items-center gap-2 mb-1">
            <PiggyBank className="w-5 h-5 text-[#06b6d4]" />
            <h2 className="text-xl font-bold text-foreground">Si hubieras invertido $1,000</h2>
            <InfoLink term="estrategia" />
          </div>
          <p className="text-xs text-muted-foreground mb-4">Haciéndole caso al modelo contra solo comprar y esperar. Sin comisiones.</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={capital} margin={{ top: 10, right: 10, bottom: 25, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
                <XAxis
                  dataKey="date"
                  tick={ejeEstilo}
                  tickFormatter={fechaEje}
                  minTickGap={20}
                  label={{ value: "Fecha", position: "insideBottom", offset: -15, style: ejeEstilo }}
                />
                <YAxis
                  tick={ejeEstilo}
                  domain={["auto", "auto"]}
                  width={75}
                  tickFormatter={(v: number) => `$${v.toFixed(0)}`}
                  label={{ value: "Dinero (USD)", angle: -90, position: "insideLeft", style: { ...ejeEstilo, textAnchor: "middle" } }}
                />
                <ReferenceLine y={CAPITAL_INICIAL} stroke="currentColor" strokeDasharray="4 4" opacity={0.4} />
                <Tooltip
                  contentStyle={tooltipStyle}
                  labelFormatter={(v: string) => fecha(v)}
                  formatter={(v: any, name: any) => [usd(Number(v)), name]}
                />
                <Line type="linear" dataKey="estrategia" name="Haciéndole caso al modelo" stroke="#06b6d4" strokeWidth={2.5} dot={false} />
                <Line type="linear" dataKey="compraEspera" name="Comprar y esperar" stroke="#94a3b8" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 flex flex-wrap gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-5 h-1 rounded bg-[#06b6d4]"></div>
              <span className="text-muted-foreground">Haciéndole caso al modelo</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-5 h-1 rounded bg-[#94a3b8]"></div>
              <span className="text-muted-foreground">Comprar y esperar</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-5 border-t border-dashed border-muted-foreground"></div>
              <span className="text-muted-foreground">Los $1,000 del inicio</span>
            </div>
          </div>
        </Card>
      )}

      {/* ── Resultados del periodo ───────────────────────────────────────── */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold text-foreground">¿Cómo le fue en estos {metrics.totalPredictions} días?</h3>
        <p className="text-xs text-muted-foreground mb-4">
          {evaluados} ya calificados
          {metrics.pendingPredictions > 0 ? `, ${metrics.pendingPredictions} pendiente${metrics.pendingPredictions > 1 ? "s" : ""}` : ""}
        </p>

        <div className="flex items-center gap-2 mb-3">
          <Target className="w-4 h-4 text-[#8b5cf6]" />
          <h4 className="font-semibold text-foreground">Aciertos</h4>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 mb-4">
          <MetricCard
            label="Acertó"
            help="aciertos"
            value={frac(metrics.accuracy, 0)}
            hint={metrics.correctPredictions !== undefined ? `${metrics.correctPredictions} de ${evaluados} días` : undefined}
          />
          <MetricCard label="Calificación (F1)" help="f1" value={frac(metrics.f1_macro, 0)} hint="Adivinando: 33 %" color="text-[#8b5cf6]" />
          <MetricCard label="Seguridad promedio" help="seguridad" value={<span className="text-base"><SeguridadBadge confianza={metrics.avgConfidence} /></span>} />
        </div>
        <div className="flex flex-wrap items-center gap-2 mb-6 text-xs">
          <span className="text-muted-foreground inline-flex items-center gap-1">
            Qué recomendó <InfoLink term="frecuencia-recomendaciones" />
          </span>
          {(["buy", "hold", "sell"] as Signal[]).map((s) => (
            <span key={s} className="inline-flex items-center gap-1.5 text-white px-2 py-1 rounded" style={{ backgroundColor: SIGNAL_CONFIG[s].hex }}>
              <span className="font-semibold">{SIGNAL_CONFIG[s].short}</span>
              <span>
                {pct(metrics[`signal_${s}_pct` as const], 0)} ({diasRecomendo(s)} {diasRecomendo(s) === 1 ? "día" : "días"})
              </span>
            </span>
          ))}
        </div>

        <div className="flex items-center gap-2 mb-3">
          <Wallet className="w-4 h-4 text-[#06b6d4]" />
          <h4 className="font-semibold text-foreground">Dinero (con $1,000 al inicio)</h4>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 mb-6">
          <MetricCard
            label="Haciéndole caso"
            help="roi"
            value={pct(metrics.cumulativeReturn, 1, true)}
            color={colorSigno(metrics.cumulativeReturn)}
            hint={metrics.finalCapital !== undefined ? `$1,000 → ${usd(metrics.finalCapital)}` : undefined}
          />
          <MetricCard
            label="Comprar y esperar"
            help="comprar-y-esperar"
            value={pct(metrics.bh_return, 1, true)}
            color={colorSigno(metrics.bh_return)}
            hint={capitalBH !== undefined ? `$1,000 → ${usd(capitalBH)}` : undefined}
          />
          <MetricCard
            label="Diferencia"
            help="diferencia"
            value={metrics.return_vs_bh !== undefined ? `${num(metrics.return_vs_bh, 1, true)} pts` : "—"}
            color={colorSigno(metrics.return_vs_bh)}
            hint={metrics.return_vs_bh === undefined ? undefined : metrics.return_vs_bh >= 0 ? "Ganó el modelo" : "Ganó comprar y esperar"}
          />
          <MetricCard
            label="Ganancia vs. riesgo (Sharpe)"
            help="sharpe"
            value={num(metrics.sharpeRatio, 2, true)}
            hint={metrics.sharpeRatio === null ? "Muy pocos días para calcularlo" : `Comprar y esperar: ${num(metrics.bh_sharpe, 2, true)}`}
            color="text-[#06b6d4]"
          />
          <MetricCard label="Peor caída" help="drawdown" value={dd(metrics.maxDrawdown)} color="text-red-600 dark:text-red-400" />
          <MetricCard
            label="Días con ganancia"
            help="win-rate"
            value={pct(metrics.winRate, 0)}
            hint={diasGanados !== null ? `${diasGanados} de ${diasInvertido} días invertidos` : "No invirtió ningún día"}
          />
        </div>

        <p className="text-xs text-muted-foreground">
          Una recomendación acierta si coincide con lo que convenía hacer al día siguiente <InfoLink term="lo-que-convenia" />
        </p>
      </Card>

      {/* ── Últimas recomendaciones ──────────────────────────────────────── */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-1">
          <Calendar className="w-5 h-5 text-[#3b82f6]" />
          <h2 className="text-xl font-bold text-foreground">Últimas 10 recomendaciones</h2>
        </div>
        <p className="text-xs text-muted-foreground mb-4">La más reciente se califica cuando cierre el día siguiente.</p>
        <div className="overflow-x-auto mb-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b-2 border-border bg-muted text-xs">
                <th className="text-left py-2 px-3 font-semibold text-foreground">Fecha</th>
                <th className="text-center py-2 px-3 font-semibold text-foreground">Recomendó</th>
                <th className="text-left py-2 px-3 font-semibold text-foreground">Seguridad</th>
                <th className="text-right py-2 px-3 font-semibold text-foreground">Cierre (USD)</th>
                <th className="text-right py-2 px-3 font-semibold text-foreground">Al día siguiente (%)</th>
                <th className="text-center py-2 px-3 font-semibold text-foreground">Convenía</th>
                <th className="text-center py-2 px-3 font-semibold text-foreground">¿Acertó?</th>
              </tr>
            </thead>
            <tbody>
              {stock.recentSignals.map((signal) => (
                <tr key={signal.date} className="border-b border-border hover:bg-muted">
                  <td className="py-3 px-3 text-foreground whitespace-nowrap">{fecha(signal.date)}</td>
                  <td className="py-3 px-3 text-center"><SignalPill signal={signal.signal} /></td>
                  <td className="py-3 px-3 text-xs whitespace-nowrap"><SeguridadBadge confianza={signal.confidence} /></td>
                  <td className="py-3 px-3 text-right text-foreground">{usd(signal.actualPrice)}</td>
                  <td className={`py-3 px-3 text-right ${colorSigno(signal.nextReturn)}`}>
                    {signal.nextReturn === null ? "—" : pct(signal.nextReturn, 2, true)}
                  </td>
                  <td className="py-3 px-3 text-center"><SignalPill signal={signal.actualSignal} /></td>
                  <td className="py-3 px-3 text-center">
                    {signal.correct === null ? (
                      <span className="text-xs text-muted-foreground">Pendiente</span>
                    ) : signal.correct ? (
                      <span className="text-emerald-600 dark:text-emerald-400 font-semibold text-xs">✓ Sí</span>
                    ) : (
                      <span className="text-red-600 dark:text-red-400 font-semibold text-xs">✗ No</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pt-4 border-t border-border flex flex-wrap gap-x-6 gap-y-1 text-sm">
          <span className="text-emerald-600 dark:text-emerald-400 font-medium">Acertó {deTotal(aciertos, evaluadas.length)}</span>
          <span className="text-red-600 dark:text-red-400 font-medium">Falló {deTotal(evaluadas.length - aciertos, evaluadas.length)}</span>
          {pendientes > 0 && <span className="text-muted-foreground">Pendientes: {pendientes}</span>}
        </div>
      </Card>
    </div>
  );
}

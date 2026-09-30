import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router";
import { ArrowLeft, TrendingUp, Calendar, Target, Wallet } from "lucide-react";
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
import { SIGNAL_CONFIG, dd, fecha, frac, num, pct } from "../format";
import type { HistoryRow, Signal, StockDetail as StockDetailType, WindowMetrics } from "../types";

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
      <div className="flex h-3 w-full overflow-hidden rounded-full">
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
            <span className="font-semibold">{SIGNAL_CONFIG[s].short}</span> {frac(probabilities[s])}
          </div>
        ))}
      </div>
    </div>
  );
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

  const config = SIGNAL_CONFIG[stock.signal];
  const Icon = config.icon;

  const chartData = history.map((item) => ({ date: item.date, price: item.close, prediction: item.prediction }));

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (!payload || !payload.prediction) return null;
    const color = SIGNAL_CONFIG[payload.prediction as Signal]?.hex;
    return <circle cx={cx} cy={cy} r={3} fill={color} stroke="white" strokeWidth={1} />;
  };

  const evaluadas = stock.recentSignals.filter((s) => s.correct !== null);
  const aciertos = evaluadas.filter((s) => s.correct).length;
  const pendientes = stock.recentSignals.length - evaluadas.length;
  const hayEvaluacion = metrics.evaluatedPredictions > 0;
  const colorSigno = (v?: number) => (v === undefined ? "text-foreground" : v >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400");

  return (
    <div>
      <Button onClick={() => navigate("/")} variant="ghost" size="sm" className="mb-4 gap-2">
        <ArrowLeft className="w-4 h-4" /> Volver
      </Button>

      <Card className="p-6 mb-6">
        <div className="flex items-start justify-between gap-4 mb-5">
          <div className="flex-1 min-w-0">
            <h1 className="text-3xl font-bold text-foreground">{stock.symbol}</h1>
            <p className="text-muted-foreground mt-1">{stock.name}</p>
            <div className="text-4xl font-bold text-foreground mt-4">${stock.currentPrice.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground mt-1">Cierre del {fecha(stock.dataDate)}</p>
          </div>
          <div className={`flex flex-col items-center gap-2 px-6 py-4 rounded-xl bg-muted border-2 ${config.borderColor}`}>
            <Icon className={`w-8 h-8 ${config.color}`} />
            <span className={`text-sm font-bold ${config.color}`}>{config.label}</span>
            <span className="text-xs text-muted-foreground">{frac(stock.confidence, 0)} confianza</span>
          </div>
        </div>
        <div className="border-t border-border pt-4">
          <div className="text-sm font-semibold text-foreground mb-2">Probabilidades del modelo para el siguiente día hábil</div>
          <ProbabilityBar probabilities={stock.probabilities} />
          <p className="text-xs text-muted-foreground mt-3">
            El modelo elige la señal con mayor probabilidad. Al azar, cada señal tendría 33 %.
          </p>
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
          <h2 className="text-xl font-bold text-foreground">Precio y señal diaria del modelo</h2>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v: string) => {
                const [, m, d] = v.split("-");
                return `${Number(d)}/${Number(m)}`;
              }} />
              <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
              <Tooltip
                contentStyle={{ backgroundColor: "var(--color-background)", border: "1px solid var(--color-border)", borderRadius: 8, color: "var(--color-foreground)" }}
                labelFormatter={(v: string) => fecha(v)}
                formatter={(value: any, _name: any, item: any) => [
                  `$${Number(value).toFixed(2)} · señal ${SIGNAL_CONFIG[item.payload.prediction as Signal]?.short ?? "—"}`,
                  "Cierre",
                ]}
              />
              <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={<CustomDot />} name="Precio de Cierre" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex flex-wrap gap-4 text-xs">
          {(["buy", "sell", "hold"] as Signal[]).map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: SIGNAL_CONFIG[s].hex }}></div>
              <span className="text-muted-foreground">Señal {SIGNAL_CONFIG[s].short}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <h3 className="text-lg font-bold text-foreground">Desempeño del modelo: últimos {metrics.totalPredictions} días hábiles</h3>
        <p className="text-xs text-muted-foreground mb-4">
          {fecha(metrics.periodStart)} – {fecha(metrics.periodEnd)} · {metrics.evaluatedPredictions} señales con resultado conocido
          {metrics.pendingPredictions > 0 ? `, ${metrics.pendingPredictions} pendiente${metrics.pendingPredictions > 1 ? "s" : ""}` : ""}
        </p>

        <div className="flex items-center gap-2 mb-3">
          <Target className="w-4 h-4 text-[#8b5cf6]" />
          <h4 className="font-semibold text-foreground">Clasificación</h4>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5 mb-6">
          <MetricCard label="F1-macro" value={frac(metrics.f1_macro)} hint="Azar ≈ 33 %" color="text-[#8b5cf6]" />
          <MetricCard label="Aciertos" value={frac(metrics.accuracy)} hint={hayEvaluacion ? `${metrics.correctPredictions} de ${metrics.evaluatedPredictions}` : undefined} />
          <MetricCard label="F1 COMPRAR" value={frac(metrics.f1_buy)} color={SIGNAL_CONFIG.buy.color} />
          <MetricCard label="F1 MANTENER" value={frac(metrics.f1_hold)} color={SIGNAL_CONFIG.hold.color} />
          <MetricCard label="F1 VENDER" value={frac(metrics.f1_sell)} color={SIGNAL_CONFIG.sell.color} />
        </div>

        <div className="flex items-center gap-2 mb-3">
          <Wallet className="w-4 h-4 text-[#06b6d4]" />
          <h4 className="font-semibold text-foreground">Estrategia de la tesis vs. comprar y mantener</h4>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 mb-6">
          <MetricCard label="Retorno estrategia" value={pct(metrics.cumulativeReturn, 1, true)} color={colorSigno(metrics.cumulativeReturn)} />
          <MetricCard label="Retorno buy & hold" value={pct(metrics.bh_return, 1, true)} hint={`Diferencia: ${pct(metrics.return_vs_bh, 1, true)}`} />
          <MetricCard label="Sharpe estrategia" value={num(metrics.sharpeRatio, 2, true)} hint={metrics.sharpeRatio === null ? "Menos de 5 días con posición" : `Buy & hold: ${num(metrics.bh_sharpe, 2, true)}`} color="text-[#06b6d4]" />
          <MetricCard label="Máx. drawdown" value={dd(metrics.maxDrawdown)} color="text-red-600 dark:text-red-400" />
          <MetricCard label="Win rate" value={pct(metrics.winRate, 1)} hint={`${metrics.numberOfTrades ?? 0} días con posición`} />
          <MetricCard label="Profit factor" value={num(metrics.profitFactor, 2)} hint={metrics.profitFactor === null ? "Menos de 5 días con posición o sin pérdidas" : undefined} />
          <MetricCard label="Exposición" value={pct(metrics.exposure, 1)} hint="Días con posición abierta" />
          <MetricCard label="Confianza media" value={frac(metrics.avgConfidence)} />
        </div>

        <div className="bg-muted p-4 rounded-lg mb-4">
          <div className="text-sm text-muted-foreground mb-2">Distribución de señales emitidas</div>
          <div className="flex flex-wrap items-center gap-2">
            {(["buy", "hold", "sell"] as Signal[]).map((s) => (
              <span key={s} className="inline-flex items-center gap-2 text-white px-2 py-0.5 rounded text-xs" style={{ backgroundColor: SIGNAL_CONFIG[s].hex }}>
                <span className="font-semibold">{SIGNAL_CONFIG[s].short}</span>
                <span className="font-medium">{pct(metrics[`signal_${s}_pct` as const], 1)}</span>
              </span>
            ))}
          </div>
        </div>

        <p className="text-xs text-muted-foreground">
          La señal de cada día se compara con lo que pasó del cierre de ese día al cierre del siguiente día hábil,
          usando la misma etiqueta del entrenamiento: COMPRAR si el retorno quedó en el 30 % más alto de los últimos
          252 días, VENDER si quedó en el 30 % más bajo, MANTENER en otro caso. Estrategia: COMPRAR = posición larga,
          VENDER = posición corta, MANTENER = sin posición, durante un día y sin costos de transacción.
        </p>
      </Card>

      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5 text-[#3b82f6]" />
          <h2 className="text-xl font-bold text-foreground">Historial de señales (últimas 10)</h2>
        </div>
        <div className="overflow-x-auto mb-4">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b-2 border-border bg-muted">
                <th className="text-left py-2 px-3 font-semibold text-foreground">Fecha</th>
                <th className="text-center py-2 px-3 font-semibold text-foreground">Señal</th>
                <th className="text-right py-2 px-3 font-semibold text-foreground">Confianza</th>
                <th className="text-right py-2 px-3 font-semibold text-foreground">Día siguiente</th>
                <th className="text-center py-2 px-3 font-semibold text-foreground">Real</th>
                <th className="text-center py-2 px-3 font-semibold text-foreground">Resultado</th>
                <th className="text-right py-2 px-3 font-semibold text-foreground">Cierre</th>
              </tr>
            </thead>
            <tbody>
              {stock.recentSignals.map((signal) => (
                <tr key={signal.date} className="border-b border-border hover:bg-muted">
                  <td className="py-3 px-3 text-foreground whitespace-nowrap">{fecha(signal.date)}</td>
                  <td className="py-3 px-3 text-center"><SignalPill signal={signal.signal} /></td>
                  <td className="py-3 px-3 text-right text-foreground">{frac(signal.confidence, 0)}</td>
                  <td className={`py-3 px-3 text-right ${colorSigno(signal.nextReturn ?? undefined)}`}>
                    {signal.nextReturn === null ? "—" : pct(signal.nextReturn, 2, true)}
                  </td>
                  <td className="py-3 px-3 text-center"><SignalPill signal={signal.actualSignal} /></td>
                  <td className="py-3 px-3 text-center">
                    {signal.correct === null ? (
                      <span className="text-xs text-muted-foreground">Pendiente</span>
                    ) : signal.correct ? (
                      <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center mx-auto border border-[#10b981]"><span className="text-[#10b981] text-sm font-bold">✓</span></div>
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center mx-auto border border-[#ef4444]"><span className="text-[#ef4444] text-sm font-bold">✗</span></div>
                    )}
                  </td>
                  <td className="py-3 px-3 text-right text-foreground font-semibold">${signal.actualPrice.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pt-4 border-t border-border flex flex-wrap gap-4 text-sm">
          <span className="text-muted-foreground">Correctas: {aciertos}/{evaluadas.length}</span>
          <span className="text-muted-foreground">Incorrectas: {evaluadas.length - aciertos}/{evaluadas.length}</span>
          {pendientes > 0 && <span className="text-muted-foreground">Pendientes: {pendientes} (aún sin cierre del día siguiente)</span>}
        </div>
        <div className="mt-4 p-3 bg-muted border border-[#f59e0b] rounded text-xs text-muted-foreground">
          <strong>Nota:</strong> Cada señal se calcula con el cierre de su fecha y se refiere al movimiento hasta el
          cierre del siguiente día hábil. "Real" es la señal que habría sido correcta según ese movimiento.
        </div>
      </Card>
    </div>
  );
}

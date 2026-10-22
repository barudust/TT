import { useEffect, useState } from "react";
import { Link } from "react-router";
import { ArrowRight, RotateCcw, Sunrise, Sunset } from "lucide-react";
import { CartesianGrid, Line, LineChart, ReferenceDot, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { API_BASE_URL } from "../../config/api";
import { SIGNAL_CONFIG, fechaDia, fechaEje, pct, usd } from "../format";
import type { HistoryRow, Signal } from "../types";

const CAPITAL = 1000;

const EMPRESAS = [
  { symbol: "AAPL", name: "Apple" },
  { symbol: "MSFT", name: "Microsoft" },
  { symbol: "GOOGL", name: "Google" },
  { symbol: "AMZN", name: "Amazon" },
  { symbol: "TSLA", name: "Tesla" },
  { symbol: "META", name: "Meta" },
  { symbol: "NVDA", name: "NVIDIA" },
];

/** Qué hace cada decisión con el cambio de precio del día siguiente:
 *  comprar gana lo que sube, vender en corto gana lo que baja, mantener no se mueve. */
const SENTIDO: Record<Signal, number> = { buy: 1, sell: -1, hold: 0 };

const NOMBRE: Record<Signal, string> = {
  buy: "Comprar",
  sell: "Vender en corto",
  hold: "Mantener",
};

const EXPLICA: Record<Signal, string> = {
  buy: "Compras hoy y vendes mañana. Ganas si el precio sube.",
  sell: "Vendes hoy una acción prestada y la recompras mañana. Ganas si el precio baja.",
  hold: "No haces nada. Tu dinero no se mueve.",
};

const colorDinero = (v: number) =>
  v > 0 ? "text-emerald-600 dark:text-emerald-400" : v < 0 ? "text-red-600 dark:text-red-400" : "text-muted-foreground";

const conSigno = (v: number) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${usd(Math.abs(v))}`;

const tooltipStyle = {
  backgroundColor: "var(--color-background)",
  border: "1px solid var(--color-border)",
  borderRadius: 8,
  color: "var(--color-foreground)",
  fontSize: 12,
};
const ejeEstilo = { fontSize: 12, fill: "currentColor", opacity: 0.7 };

// ── 1. Una recomendación dura un día ──────────────────────────────────────
function UnDia() {
  return (
    <Card className="p-5 mb-4">
      <h3 className="font-bold text-foreground text-lg mb-3">Cada recomendación dura un solo día</h3>
      <div className="flex flex-col sm:flex-row items-stretch gap-3 text-sm">
        <div className="flex-1 rounded-lg bg-muted p-3 flex gap-3 items-start">
          <Sunset className="w-6 h-6 text-amber-500 flex-shrink-0" />
          <div>
            <div className="font-semibold text-foreground">Hoy, al cerrar la bolsa</div>
            <div className="text-muted-foreground">El modelo ve cómo cerró y recomienda qué hacer: comprar, vender en corto o mantener.</div>
          </div>
        </div>
        <ArrowRight className="w-6 h-6 text-muted-foreground self-center rotate-90 sm:rotate-0 flex-shrink-0" />
        <div className="flex-1 rounded-lg bg-muted p-3 flex gap-3 items-start">
          <Sunrise className="w-6 h-6 text-blue-500 flex-shrink-0" />
          <div>
            <div className="font-semibold text-foreground">Mañana, al cerrar la bolsa</div>
            <div className="text-muted-foreground">Se cierra la operación y se ve si ganaste o perdiste. Al día siguiente, otra recomendación.</div>
          </div>
        </div>
      </div>
    </Card>
  );
}

// ── 2. ¿Qué pasaría con $1,000? ───────────────────────────────────────────
function Deslizador() {
  const [cambio, setCambio] = useState(2);
  return (
    <Card className="p-5 mb-4">
      <h3 className="font-bold text-foreground text-lg mb-1">¿Qué pasa con $1,000 en cada caso?</h3>
      <p className="text-sm text-muted-foreground mb-4">Mueve la barra: es cuánto cambia el precio de la acción de hoy a mañana.</p>
      <div className="mb-5">
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>Baja 5 %</span>
          <span className={`text-base font-bold ${colorDinero(cambio)}`}>
            {cambio === 0 ? "No cambia" : `${cambio > 0 ? "Sube" : "Baja"} ${pct(Math.abs(cambio), 1)}`}
          </span>
          <span>Sube 5 %</span>
        </div>
        <input
          type="range"
          min={-5}
          max={5}
          step={0.5}
          value={cambio}
          onChange={(e) => setCambio(Number(e.target.value))}
          className="w-full accent-blue-500"
          aria-label="Cambio del precio de hoy a mañana, en porcentaje"
        />
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        {(["buy", "sell", "hold"] as Signal[]).map((s) => {
          const c = SIGNAL_CONFIG[s];
          const Icon = c.icon;
          const ganancia = (CAPITAL * SENTIDO[s] * cambio) / 100;
          return (
            <div key={s} className={`rounded-lg border-2 bg-muted p-3 ${c.borderColor}`}>
              <div className="flex items-center gap-2 mb-1">
                <Icon className={`w-5 h-5 ${c.color}`} />
                <span className={`font-bold ${c.color}`}>{NOMBRE[s]}</span>
              </div>
              <div className="text-xs text-muted-foreground mb-2 min-h-[2.5rem]">{EXPLICA[s]}</div>
              <div className="text-sm text-muted-foreground">$1,000 se vuelven</div>
              <div className="text-2xl font-bold text-foreground">{usd(CAPITAL + ganancia)}</div>
              <div className={`text-sm font-semibold ${colorDinero(ganancia)}`}>
                {ganancia === 0 ? "Ni ganas ni pierdes" : `${ganancia > 0 ? "Ganas" : "Pierdes"} ${usd(Math.abs(ganancia))}`}
              </div>
            </div>
          );
        })}
      </div>
      <p className="text-xs text-muted-foreground mt-3">
        Comprar y vender en corto son espejo: lo que gana uno lo pierde el otro. Mantener es la opción para cuando el modelo
        no ve hacia dónde va el precio.
      </p>
    </Card>
  );
}

// ── 3. La venta en corto, paso a paso ─────────────────────────────────────
function VentaEnCorto() {
  const [manana, setManana] = useState(95);
  const resultado = 100 - manana;
  const pasos = [
    { n: 1, titulo: "Pides prestada una acción", detalle: "Hoy vale $100. Todavía no es tuya: la tienes que devolver." },
    { n: 2, titulo: "La vendes hoy", detalle: "Recibes $100 en efectivo." },
    { n: 3, titulo: "Mañana la vuelves a comprar", detalle: `Ahora cuesta ${usd(manana, 0)}.` },
    { n: 4, titulo: "La devuelves", detalle: `Te quedas con $100 − ${usd(manana, 0)} = ${conSigno(resultado)}.` },
  ];
  return (
    <Card className="p-5 mb-4">
      <h3 className="font-bold text-foreground text-lg mb-1">¿Cómo se gana si el precio baja? La venta en corto</h3>
      <p className="text-sm text-muted-foreground mb-3">Elige qué pasa mañana:</p>
      <div className="flex gap-2 mb-4">
        <Button size="sm" variant={manana === 95 ? "default" : "outline"} onClick={() => setManana(95)}>
          Baja a $95
        </Button>
        <Button size="sm" variant={manana === 105 ? "default" : "outline"} onClick={() => setManana(105)}>
          Sube a $105
        </Button>
      </div>
      <ol className="grid gap-2 sm:grid-cols-4">
        {pasos.map((p) => (
          <li key={p.n} className="rounded-lg bg-muted p-3 text-sm">
            <div className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs font-bold flex items-center justify-center mb-2">{p.n}</div>
            <div className="font-semibold text-foreground">{p.titulo}</div>
            <div className="text-muted-foreground">{p.detalle}</div>
          </li>
        ))}
      </ol>
      <p className={`mt-3 text-sm font-semibold ${colorDinero(resultado)}`}>
        {resultado > 0
          ? `El precio bajó: ganaste ${usd(resultado, 0)} por acción.`
          : `El precio subió: perdiste ${usd(Math.abs(resultado), 0)} por acción.`}
      </p>
    </Card>
  );
}

// ── 4. Pruébalo con precios reales ────────────────────────────────────────
interface Jugada {
  tu: Signal;
  cambio: number;
}

function Juego() {
  const [symbol, setSymbol] = useState("AAPL");
  const [dias, setDias] = useState<HistoryRow[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(false);
  const [i, setI] = useState(0);
  const [jugadas, setJugadas] = useState<Jugada[]>([]);
  const [revelado, setRevelado] = useState(false);

  const cargar = async (s: string) => {
    setCargando(true);
    setError(false);
    try {
      const body = await fetch(`${API_BASE_URL}/stocks/${s}/history?days=30`).then((r) => r.json());
      if (!body?.success) throw new Error("respuesta inválida");
      const filas: HistoryRow[] = (body.data as HistoryRow[]).filter((r) => r.nextReturn !== null);
      setDias(filas);
      setI(0);
      setJugadas([]);
      setRevelado(false);
    } catch (e) {
      console.error("Error cargando historial para Aprende:", e);
      setError(true);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar(symbol);
  }, [symbol]);

  const empresa = EMPRESAS.find((e) => e.symbol === symbol)?.name ?? symbol;
  const hoy = dias[i];
  const terminado = dias.length > 0 && i >= dias.length;

  // Dinero acumulado: tú, el modelo y comprar y esperar, con las mismas reglas
  let tuDinero = CAPITAL;
  let modelo = CAPITAL;
  let espera = CAPITAL;
  jugadas.forEach((j, k) => {
    const c = j.cambio / 100;
    tuDinero *= 1 + SENTIDO[j.tu] * c;
    modelo *= 1 + SENTIDO[dias[k].prediction] * c;
    espera *= 1 + c;
  });

  const elegir = (s: Signal) => {
    if (!hoy || revelado) return;
    setJugadas((js) => [...js, { tu: s, cambio: hoy.nextReturn ?? 0 }]);
    setRevelado(true);
  };
  const siguiente = () => {
    setI((v) => v + 1);
    setRevelado(false);
  };
  const reiniciar = () => {
    setI(0);
    setJugadas([]);
    setRevelado(false);
  };

  const ultima = revelado ? jugadas[jugadas.length - 1] : null;
  const precioManana = hoy && hoy.nextReturn !== null ? hoy.close * (1 + hoy.nextReturn / 100) : null;
  // La gráfica muestra solo lo que ya pasó: hasta hoy, y mañana cuando ya se reveló
  const visibles = dias.slice(0, Math.min(dias.length, i + 1)).map((d) => ({ date: d.date, close: d.close }));
  if (revelado && precioManana !== null && dias[i + 1]) {
    visibles.push({ date: dias[i + 1].date, close: dias[i + 1].close });
  }

  return (
    <Card className="p-5 mb-4">
      <h3 className="font-bold text-foreground text-lg mb-1">Pruébalo con precios reales</h3>
      <p className="text-sm text-muted-foreground mb-3">
        Vas día por día por los últimos 30 días hábiles. Cada día decides qué hacer con tu dinero para el día siguiente, y lo
        comparas con lo que recomendó el modelo. Empiezas con $1,000.
      </p>
      <div className="flex flex-wrap gap-2 mb-4">
        {EMPRESAS.map((e) => (
          <Button key={e.symbol} size="sm" variant={symbol === e.symbol ? "default" : "outline"} onClick={() => setSymbol(e.symbol)}>
            {e.name}
          </Button>
        ))}
      </div>

      {cargando && <p className="text-sm text-muted-foreground">Cargando precios… la primera vez puede tardar hasta un minuto.</p>}
      {error && (
        <div className="text-sm text-muted-foreground">
          No pudimos cargar los precios.{" "}
          <button className="text-blue-600 dark:text-blue-400 underline" onClick={() => cargar(symbol)}>
            Intentar de nuevo
          </button>
        </div>
      )}

      {!cargando && !error && dias.length > 0 && (
        <>
          <div className="grid grid-cols-3 gap-2 mb-4 text-center">
            {[
              ["Tú", tuDinero],
              ["El modelo", modelo],
              ["Comprar y esperar", espera],
            ].map(([n, v]) => (
              <div key={n as string} className="rounded-lg bg-muted p-2">
                <div className="text-xs text-muted-foreground">{n}</div>
                <div className="text-lg font-bold text-foreground">{usd(v as number)}</div>
                <div className={`text-xs font-semibold ${colorDinero((v as number) - CAPITAL)}`}>{conSigno((v as number) - CAPITAL)}</div>
              </div>
            ))}
          </div>

          <div className="h-56 mb-3">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={visibles} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
                <XAxis dataKey="date" tick={ejeEstilo} tickFormatter={fechaEje} minTickGap={20} label={{ value: "Fecha", position: "insideBottom", offset: -10, style: ejeEstilo }} />
                <YAxis tick={ejeEstilo} domain={["auto", "auto"]} width={60} tickFormatter={(v: number) => `$${v.toFixed(0)}`} />
                <Tooltip contentStyle={tooltipStyle} labelFormatter={(v: string) => fechaDia(v)} formatter={(v: any) => [usd(Number(v)), "Cierre"]} />
                <Line type="linear" dataKey="close" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} isAnimationActive={false} />
                {hoy && <ReferenceDot x={hoy.date} y={hoy.close} r={7} fill="#f59e0b" stroke="white" />}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {!terminado && hoy && (
            <div className="rounded-lg border border-border p-4">
              <div className="text-sm text-muted-foreground">
                Día {i + 1} de {dias.length} · {fechaDia(hoy.date)}
              </div>
              <div className="text-foreground mb-3">
                {empresa} cerró en <strong>{usd(hoy.close)}</strong> (punto naranja). ¿Qué haces para mañana?
              </div>
              <div className="flex flex-wrap gap-2">
                {(["buy", "sell", "hold"] as Signal[]).map((s) => {
                  const c = SIGNAL_CONFIG[s];
                  const Icon = c.icon;
                  const elegido = ultima?.tu === s;
                  return (
                    <button
                      key={s}
                      onClick={() => elegir(s)}
                      disabled={revelado}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 bg-muted text-sm font-semibold transition-opacity ${c.borderColor} ${c.color} ${
                        revelado && !elegido ? "opacity-40" : ""
                      }`}
                    >
                      <Icon className="w-4 h-4" /> {NOMBRE[s]}
                    </button>
                  );
                })}
              </div>

              {revelado && ultima && precioManana !== null && (
                <div className="mt-4 space-y-1 text-sm">
                  <div className="text-foreground">
                    Al día siguiente cerró en <strong>{usd(precioManana)}</strong>{" "}
                    <span className={colorDinero(ultima.cambio)}>({pct(ultima.cambio, 2, true)})</span>.
                  </div>
                  {(() => {
                    const antes = jugadas.length > 1 ? jugadas.slice(0, -1).reduce((acc, j) => acc * (1 + (SENTIDO[j.tu] * j.cambio) / 100), CAPITAL) : CAPITAL;
                    const g = antes * ((SENTIDO[ultima.tu] * ultima.cambio) / 100);
                    return (
                      <div className={`font-semibold ${colorDinero(g)}`}>
                        Elegiste {NOMBRE[ultima.tu].toLowerCase()}: {g === 0 ? "tu dinero no se movió" : g > 0 ? `ganaste ${usd(g)}` : `perdiste ${usd(-g)}`}.
                      </div>
                    );
                  })()}
                  <div className="text-muted-foreground">
                    El modelo recomendó <span className={`font-semibold ${SIGNAL_CONFIG[hoy.prediction].color}`}>{NOMBRE[hoy.prediction].toLowerCase()}</span>
                    {hoy.actualSignal && (
                      <>
                        {" "}· lo que convenía: <span className={`font-semibold ${SIGNAL_CONFIG[hoy.actualSignal].color}`}>{NOMBRE[hoy.actualSignal].toLowerCase()}</span>
                      </>
                    )}
                  </div>
                  <Button size="sm" className="mt-2 gap-1" onClick={siguiente}>
                    {i + 1 < dias.length ? "Siguiente día" : "Ver resultado final"} <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </div>
          )}

          {terminado && (
            <div className="rounded-lg border border-border p-4 text-sm space-y-2">
              <div className="font-semibold text-foreground">Terminaste los {dias.length} días con {empresa}.</div>
              <div className="text-muted-foreground">
                Tú terminaste con <strong className="text-foreground">{usd(tuDinero)}</strong>, el modelo con{" "}
                <strong className="text-foreground">{usd(modelo)}</strong> y solo comprar y esperar con{" "}
                <strong className="text-foreground">{usd(espera)}</strong>.
              </div>
              <div className="text-muted-foreground">
                Adivinar el día siguiente es muy difícil: por eso el modelo acierta poco más que el azar.
              </div>
              <Button size="sm" variant="outline" className="gap-1" onClick={reiniciar}>
                <RotateCcw className="w-4 h-4" /> Jugar otra vez
              </Button>
            </div>
          )}

          <p className="text-xs text-muted-foreground mt-3">
            Sin comisiones. La gráfica «Si hubieras invertido $1,000» de cada empresa usa la fórmula de la tesis (rendimientos
            logarítmicos), por eso puede diferir por unos centavos.
          </p>
        </>
      )}
    </Card>
  );
}

export default function Aprende() {
  return (
    <div className="pb-8">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-foreground">Comprar, vender en corto o mantener</h2>
        <p className="text-sm text-muted-foreground mt-1">Qué significa cada recomendación, con ejemplos que puedes mover.</p>
      </div>
      <UnDia />
      <Deslizador />
      <VentaEnCorto />
      <Juego />
      <p className="text-center text-xs text-muted-foreground">
        ¿Dudas con algún término?{" "}
        <Link to="/ayuda?tab=glosario" className="text-blue-600 dark:text-blue-400 hover:underline">
          Ver el glosario
        </Link>
      </p>
    </div>
  );
}

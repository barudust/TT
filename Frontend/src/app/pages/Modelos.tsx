import { useState } from "react";
import { Link } from "react-router";
import { Award } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { InfoLink } from "../components/InfoLink";
import { fecha, num } from "../format";
import datosCrudos from "../data/comparacion_modelos.json";

// ── Datos ────────────────────────────────────────────────────────────────
// Los genera scripts_opt/observaciones_sinodal.py (exportar_web) a partir de
// los resultados guardados de la investigación; la página no calcula nada.

type Modelo = "LR" | "XGBoost" | "LSTM" | "CNN-LSTM" | "CNN";
type Exp = "A" | "B" | "C";

interface Panel {
  modelo: Modelo;
  f1_macro: number;
  exactitud: number;
  exactitud_balanceada: number;
  kappa: number;
  auc_macro: number;
  log_loss: number;
  sharpe_0bp: number;
  sharpe_10bp: number;
  rotacion: number;
  pct_mantener: number;
  val_f1_2025?: number;
  desde?: string;
  hasta?: string;
}

interface Comparacion {
  modelos: Modelo[];
  nombres: Record<Modelo, string>;
  experimentos: Record<Exp, Panel[]>;
  intervalos: { exp: Exp; modelo: Modelo; f1: number; lo: number; hi: number }[];
  anio_por_anio: { config: "v4" | "v5"; anio: number; modelo: Modelo; f1_macro: number; sharpe_10bp: number }[];
  seleccion: {
    modelo: Modelo; config: "v4" | "v5"; f1_prueba_media: number; rango_medio: number;
    anios_ganados: number; sharpe_10bp_medio: number;
  }[];
  eleccion_por_validacion: {
    config: "v4" | "v5"; anio: number; elegido_por_validacion: Modelo; f1_prueba_del_elegido: number;
    mejor_en_prueba: Modelo; f1_prueba_del_mejor: number;
  }[];
  lr_contra_cada_uno_6anios?: { config: string; comparacion: string; dif_f1: number; ic_lo: number; ic_hi: number; significativa: boolean }[];
  ciega2026?: Panel[];
  ciega2026_diferencias?: { comparacion: string; dif_f1: number; ic_lo: number; ic_hi: number; significativa: boolean }[];
  multicolinealidad?: { exp: string; modelo: Modelo; brazo: "todas_61" | "filtro_vif10"; n_variables: number; f1_macro: number }[];
  multicolinealidad_diagnostico?: {
    n_variables: number; "pares_r_mayor_0.9": number; vif_mayor_10: number; vif_max: number;
    variables_tras_filtro_vif10_B: number;
  };
  global_vs_por_accion: { modelo: Modelo; celdas: number; celdas_gana_global_f1: number; p_signo_f1: number }[];
}

const D = datosCrudos as unknown as Comparacion;
const MODELOS: Modelo[] = ["LR", "XGBoost", "LSTM", "CNN-LSTM", "CNN"];
const NOMBRE: Record<Modelo, string> = {
  LR: "Reg. Logística",
  XGBoost: "XGBoost",
  LSTM: "LSTM",
  "CNN-LSTM": "CNN-LSTM",
  CNN: "CNN 1D",
};
const COLOR: Record<Modelo, string> = {
  LR: "#2a78d6",
  XGBoost: "#eb6834",
  LSTM: "#7b8594",
  "CNN-LSTM": "#9aa3ae",
  CNN: "#b8bfc8",
};
const TRAZO: Record<Modelo, string | undefined> = {
  LR: undefined,
  XGBoost: undefined,
  LSTM: "6 4",
  "CNN-LSTM": "2 4",
  CNN: "10 4 2 4",
};

const tooltipStyle = {
  backgroundColor: "var(--color-background)",
  border: "1px solid var(--color-border)",
  borderRadius: 8,
  color: "var(--color-foreground)",
  fontSize: 12,
};
const ejeEstilo = { fontSize: 12, fill: "currentColor", opacity: 0.7 };

const SECCIONES = [
  ["elegido", "El elegido"],
  ["igualdad", "En igualdad"],
  ["prueba", "Prueba 2025"],
  ["anios", "Año por año"],
  ["ciega", "2026"],
  ["dinero", "Dinero"],
  ["global", "Global"],
  ["variables", "Variables"],
] as const;

function Titulo({ id, children, ayuda }: { id: string; children: React.ReactNode; ayuda?: string }) {
  return (
    <h3 id={id} className="text-lg font-bold text-foreground scroll-mt-40 flex items-center gap-2">
      {children}
      {ayuda && <InfoLink term={ayuda} />}
    </h3>
  );
}

function SelectorExp({ exp, setExp }: { exp: Exp; setExp: (e: Exp) => void }) {
  const etiqueta: Record<Exp, string> = { A: "A · 10 años", B: "B · 6 años", C: "C · 4 años" };
  return (
    <div className="flex flex-wrap gap-2">
      {(["A", "B", "C"] as Exp[]).map((e) => (
        <Button key={e} size="sm" variant={exp === e ? "default" : "outline"} onClick={() => setExp(e)}>
          {etiqueta[e]}
        </Button>
      ))}
    </div>
  );
}

/** El mejor valor de una columna (para resaltarlo). */
function mejor(filas: Panel[], campo: keyof Panel, menorEsMejor = false) {
  const vals = filas.map((f) => f[campo] as number);
  return menorEsMejor ? Math.min(...vals) : Math.max(...vals);
}

// ── Secciones ────────────────────────────────────────────────────────────

function Elegido() {
  const b = D.experimentos.B;
  const lr = b.find((f) => f.modelo === "LR")!;
  const ciega = D.ciega2026 ? [...D.ciega2026].sort((x, y) => y.f1_macro - x.f1_macro) : null;
  const lugar2026 = ciega ? ciega.findIndex((f) => f.modelo === "LR") + 1 : null;
  const lr2026 = ciega?.find((f) => f.modelo === "LR");
  return (
    <Card id="elegido" className="p-6 mb-6 border-2 border-[#2a78d6] scroll-mt-40">
      <div className="flex items-start gap-3">
        <Award className="w-8 h-8 text-[#2a78d6] flex-shrink-0" />
        <div className="space-y-3">
          <h3 className="text-xl font-bold text-foreground">Modelo elegido: Regresión Logística</h3>
          <ul className="list-disc list-inside text-sm text-muted-foreground space-y-2">
            <li>
              En la prueba principal (2025) es la mejor de los cinco en <strong>las ocho métricas</strong> y en los tres
              experimentos (en B: F1 {num(lr.f1_macro, 3)}, contra 0.33 del azar).
            </li>
            <li>
              En seis años de prueba <strong>empata con XGBoost</strong> y les gana a las tres redes. Ante el empate
              elegimos la más simple: cambia menos de posición, así que le pesan menos las comisiones, y se puede
              explicar qué variable empuja cada recomendación.
            </li>
            {lr2026 && (
              <li>
                En 2026, con datos que ningún modelo vio, saca el F1 {lugar2026 === 1 ? "más alto" : `lugar ${lugar2026} de 5`} ({num(lr2026.f1_macro, 3)}),
                aunque casi empatado con XGBoost y dos de las redes; en dinero, ese año dos redes salieron mejor.
              </li>
            )}
            <li>
              No la elegimos por un solo resultado: elegir por la validación de un año falla seguido (lo mostramos
              abajo).
            </li>
          </ul>
        </div>
      </div>
    </Card>
  );
}

function Igualdad() {
  const filas: [string, string][] = [
    ["Datos", "Las mismas 7 acciones, los mismos años y las mismas 61 variables"],
    ["Separación", "Por tiempo: entrenamiento, validación (2024) y prueba (2025)"],
    ["Días calificados", "Exactamente los mismos 1,736 días de prueba para los cinco"],
    ["Métricas", "Las mismas ocho, calculadas con el mismo código para todos"],
    ["Ajustes", "Optuna para los cinco, decidiendo solo con 2024"],
    ["Prueba", "2025 se usa una sola vez; además seis años y 2026"],
  ];
  return (
    <Card className="p-6 mb-6">
      <Titulo id="igualdad">Cómo los comparamos: en igualdad de condiciones</Titulo>
      <table className="w-full text-sm mt-3">
        <tbody>
          {filas.map(([a, b]) => (
            <tr key={a} className="border-b border-border">
              <td className="py-2 pr-3 font-semibold text-foreground whitespace-nowrap">{a}</td>
              <td className="py-2 text-muted-foreground">{b}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-muted-foreground mt-3">
        Lo único que no puede ser igual es cómo aprende cada uno por dentro (la Regresión Logística no tiene épocas; las
        redes sí). Pero a todos se les califica con las mismas reglas.
      </p>
    </Card>
  );
}

function PruebaPrincipal() {
  const [exp, setExp] = useState<Exp>("B");
  const filas = MODELOS.map((m) => D.experimentos[exp].find((f) => f.modelo === m)!).filter(Boolean);
  const ic = D.intervalos.filter((x) => x.exp === exp);
  const datos = filas.map((f) => ({ modelo: NOMBRE[f.modelo], f1: f.f1_macro, color: COLOR[f.modelo] }));
  const cols: [keyof Panel, string, boolean, number][] = [
    ["f1_macro", "F1", false, 3],
    ["exactitud", "Exactitud", false, 3],
    ["exactitud_balanceada", "Exact. balanceada", false, 3],
    ["kappa", "Kappa", false, 3],
    ["auc_macro", "AUC", false, 3],
    ["log_loss", "Log-loss ↓", true, 3],
    ["sharpe_0bp", "Sharpe", false, 2],
    ["sharpe_10bp", "Sharpe con comisión", false, 2],
  ];
  return (
    <Card className="p-6 mb-6">
      <Titulo id="prueba" ayuda="f1">Prueba principal: 2025</Titulo>
      <p className="text-sm text-muted-foreground mt-1 mb-3">Elige el experimento: cambia cuántos años se usan para entrenar.</p>
      <SelectorExp exp={exp} setExp={setExp} />
      <div className="h-64 mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={datos} margin={{ top: 10, right: 44, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
            <XAxis dataKey="modelo" tick={ejeEstilo} interval={0} />
            <YAxis tick={ejeEstilo} domain={[0, 0.45]} ticks={[0, 0.1, 0.2, 0.3, 0.4]} width={45} />
            <Tooltip contentStyle={tooltipStyle} formatter={(v: any) => [num(Number(v), 3), "F1-macro"]} />
            <ReferenceLine y={0.333} stroke="currentColor" strokeDasharray="4 4" opacity={0.6} label={{ value: "azar", position: "right", fontSize: 11, fill: "currentColor" }} />
            <Bar dataKey="f1" radius={[4, 4, 0, 0]} isAnimationActive={false}>
              {datos.map((d) => (
                <Cell key={d.modelo} fill={d.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="overflow-x-auto mt-4">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b-2 border-border bg-muted">
              <th className="text-left py-2 px-2 font-semibold text-foreground">Modelo</th>
              {cols.map(([, t]) => (
                <th key={t} className="text-right py-2 px-2 font-semibold text-foreground whitespace-nowrap">{t}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filas.map((f) => (
              <tr key={f.modelo} className="border-b border-border">
                <td className="py-2 px-2 font-semibold whitespace-nowrap" style={{ color: f.modelo === "LR" ? COLOR.LR : undefined }}>
                  {NOMBRE[f.modelo]}
                </td>
                {cols.map(([c, t, menor, dec]) => {
                  const v = f[c] as number;
                  const esMejor = v === mejor(filas, c, menor);
                  return (
                    <td key={t} className={`py-2 px-2 text-right ${esMejor ? "font-bold text-foreground" : "text-muted-foreground"}`}>
                      {num(v, dec, c.startsWith("sharpe"))}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-muted-foreground mt-2">En negritas, el mejor de cada columna. Log-loss: menor es mejor.</p>

      <h4 className="font-semibold text-foreground mt-6 mb-2 flex items-center gap-1">
        ¿Qué tan seguros estamos? <InfoLink term="intervalo" />
      </h4>
      <div className="space-y-2">
        {MODELOS.map((m) => {
          const x = ic.find((i) => i.modelo === m);
          if (!x) return null;
          const pos = (v: number) => `${((v - 0.2) / 0.25) * 100}%`;
          return (
            <div key={m} className="flex items-center gap-2 text-xs">
              <span className="w-24 flex-shrink-0 text-foreground">{NOMBRE[m]}</span>
              <div className="relative flex-1 h-6">
                <div className="absolute top-0 bottom-0 border-l-2 border-dashed border-muted-foreground/60" style={{ left: pos(0.333) }} />
                <div className="absolute top-[11px] h-1 rounded" style={{ left: pos(x.lo), width: `${((x.hi - x.lo) / 0.25) * 100}%`, backgroundColor: COLOR[m] }} />
                <div className="absolute top-[5px] w-3.5 h-3.5 -ml-[7px] rounded-full border-2 border-background" style={{ left: pos(x.f1), backgroundColor: COLOR[m] }} />
              </div>
              <span className="w-32 flex-shrink-0 text-right text-muted-foreground whitespace-nowrap">
                {num(x.f1, 3)} [{num(x.lo, 3)}–{num(x.hi, 3)}]
              </span>
            </div>
          );
        })}
      </div>
      <p className="text-xs text-muted-foreground mt-2">
        Punto: F1. Línea: intervalo de confianza del 95 %. Línea punteada: azar. Comparando par por par, la Regresión
        Logística es significativamente mejor que cada uno de los otros cuatro en A, B y C.
      </p>
    </Card>
  );
}

function AnioPorAnio() {
  const [config, setConfig] = useState<"v4" | "v5">("v4");
  const filas = D.anio_por_anio.filter((x) => x.config === config);
  const anios = [...new Set(filas.map((x) => x.anio))].sort();
  const datos = anios.map((a) => {
    const o: Record<string, number | string> = { anio: String(a) };
    for (const m of MODELOS) {
      const x = filas.find((f) => f.anio === a && f.modelo === m);
      if (x) o[m] = x.f1_macro;
    }
    return o;
  });
  const resumen = MODELOS.map((m) => D.seleccion.find((s) => s.modelo === m && s.config === config)!).filter(Boolean);
  const elec = D.eleccion_por_validacion.filter((x) => x.config === config);
  const mediaElec = elec.reduce((s, x) => s + x.f1_prueba_del_elegido, 0) / Math.max(elec.length, 1);
  const difs = (D.lr_contra_cada_uno_6anios ?? []).filter((x) => x.config === config);
  return (
    <Card className="p-6 mb-6">
      <Titulo id="anios" ayuda="anio-por-anio">¿Y si la prueba no fuera 2025?</Titulo>
      <p className="text-sm text-muted-foreground mt-1 mb-3">
        Cada año de 2020 a 2025 se usa como prueba: se entrena con los 5 años anteriores al de validación.
      </p>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant={config === "v4" ? "default" : "outline"} onClick={() => setConfig("v4")}>
          Ajustes fijos de antemano
        </Button>
        <Button size="sm" variant={config === "v5" ? "default" : "outline"} onClick={() => setConfig("v5")}>
          Ajustes elegidos con 2024
        </Button>
      </div>
      <div className="h-72 mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={datos} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
            <XAxis dataKey="anio" tick={ejeEstilo} />
            <YAxis tick={ejeEstilo} domain={[0.2, 0.42]} ticks={[0.2, 0.25, 0.3, 0.35, 0.4]} width={45} />
            <Tooltip contentStyle={tooltipStyle} formatter={(v: any, n: any) => [num(Number(v), 3), NOMBRE[n as Modelo] ?? n]} />
            <ReferenceLine y={0.333} stroke="currentColor" strokeDasharray="4 4" opacity={0.6} />
            <Legend formatter={(v: string) => NOMBRE[v as Modelo] ?? v} wrapperStyle={{ fontSize: 12 }} />
            {MODELOS.map((m) => (
              <Line key={m} type="linear" dataKey={m} stroke={COLOR[m]} strokeWidth={m === "LR" || m === "XGBoost" ? 3 : 2} strokeDasharray={TRAZO[m]} dot={{ r: 4 }} isAnimationActive={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="overflow-x-auto mt-3">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b-2 border-border bg-muted">
              <th className="text-left py-2 px-2 text-foreground">Modelo</th>
              <th className="text-right py-2 px-2 text-foreground">F1 promedio</th>
              <th className="text-right py-2 px-2 text-foreground">Lugar promedio</th>
              <th className="text-right py-2 px-2 text-foreground">Años ganados</th>
              <th className="text-right py-2 px-2 text-foreground whitespace-nowrap">Sharpe con comisión</th>
            </tr>
          </thead>
          <tbody>
            {resumen.map((r) => (
              <tr key={r.modelo} className="border-b border-border">
                <td className="py-2 px-2 font-semibold whitespace-nowrap">{NOMBRE[r.modelo]}</td>
                <td className="py-2 px-2 text-right">{num(r.f1_prueba_media, 3)}</td>
                <td className="py-2 px-2 text-right">{num(r.rango_medio, 2)}</td>
                <td className="py-2 px-2 text-right">{r.anios_ganados}</td>
                <td className="py-2 px-2 text-right">{num(r.sharpe_10bp_medio, 2, true)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {difs.length > 0 && (
        <p className="text-xs text-muted-foreground mt-2">
          Juntando los seis años: la Regresión Logística{" "}
          {difs.map((d, i) => (
            <span key={d.comparacion}>
              {i > 0 && "; "}
              {d.significativa ? "le gana a" : "empata con"} {NOMBRE[d.comparacion.replace("LR − ", "") as Modelo]}
            </span>
          ))}
          .
        </p>
      )}

      <h4 className="font-semibold text-foreground mt-6 mb-2">¿Y si cada año eligiéramos el que mejor sale en validación?</h4>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b-2 border-border bg-muted">
              <th className="text-left py-2 px-2 text-foreground">Año</th>
              <th className="text-left py-2 px-2 text-foreground">Elegido por validación</th>
              <th className="text-right py-2 px-2 text-foreground">Su F1 en prueba</th>
              <th className="text-left py-2 px-2 text-foreground">El mejor en prueba</th>
            </tr>
          </thead>
          <tbody>
            {elec.map((e) => (
              <tr key={e.anio} className="border-b border-border">
                <td className="py-2 px-2">{e.anio}</td>
                <td className="py-2 px-2">{NOMBRE[e.elegido_por_validacion]}</td>
                <td className="py-2 px-2 text-right">{num(e.f1_prueba_del_elegido, 3)}</td>
                <td className="py-2 px-2">{NOMBRE[e.mejor_en_prueba]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-muted-foreground mt-2">
        Elegir así da un F1 promedio de {num(mediaElec, 3)}: peor que quedarse siempre con un modelo clásico. Con tan poca
        señal, un solo año de validación no basta para escoger; por eso decidimos con varios años y con criterios de costo y
        sencillez.
      </p>
    </Card>
  );
}

function Ciega() {
  if (!D.ciega2026) return null;
  const filas = MODELOS.map((m) => D.ciega2026!.find((f) => f.modelo === m)!).filter(Boolean);
  const datos = filas.map((f) => ({ modelo: NOMBRE[f.modelo], f1: f.f1_macro, color: COLOR[f.modelo] }));
  const difs = D.ciega2026_diferencias ?? [];
  const rango = filas[0]?.desde && filas[0]?.hasta ? `del ${fecha(filas[0].desde)} al ${fecha(filas[0].hasta)}` : "de 2026";
  return (
    <Card className="p-6 mb-6">
      <Titulo id="ciega">Prueba ciega: 2026</Titulo>
      <p className="text-sm text-muted-foreground mt-1 mb-3">
        Los cinco con sus ajustes congelados, entrenados con 2020–2024 y probados con datos {rango} que ninguna decisión
        usó.
      </p>
      <div className="h-60">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={datos} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
            <XAxis dataKey="modelo" tick={ejeEstilo} interval={0} />
            <YAxis tick={ejeEstilo} domain={[0, 0.45]} ticks={[0, 0.1, 0.2, 0.3, 0.4]} width={45} />
            <Tooltip contentStyle={tooltipStyle} formatter={(v: any) => [num(Number(v), 3), "F1-macro 2026"]} />
            <ReferenceLine y={0.333} stroke="currentColor" strokeDasharray="4 4" opacity={0.6} />
            <Bar dataKey="f1" radius={[4, 4, 0, 0]} isAnimationActive={false}>
              {datos.map((d) => (
                <Cell key={d.modelo} fill={d.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="overflow-x-auto mt-3">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b-2 border-border bg-muted">
              <th className="text-left py-2 px-2 text-foreground">Modelo</th>
              <th className="text-right py-2 px-2 text-foreground">Validación 2025</th>
              <th className="text-right py-2 px-2 text-foreground">F1 2026</th>
              <th className="text-right py-2 px-2 text-foreground">Kappa</th>
              <th className="text-right py-2 px-2 text-foreground whitespace-nowrap">Sharpe con comisión</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((f) => (
              <tr key={f.modelo} className="border-b border-border">
                <td className="py-2 px-2 font-semibold whitespace-nowrap">{NOMBRE[f.modelo]}</td>
                <td className="py-2 px-2 text-right">{num(f.val_f1_2025, 3)}</td>
                <td className="py-2 px-2 text-right">{num(f.f1_macro, 3)}</td>
                <td className="py-2 px-2 text-right">{num(f.kappa, 3)}</td>
                <td className="py-2 px-2 text-right">{num(f.sharpe_10bp, 2, true)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {difs.length > 0 && (
        <p className="text-xs text-muted-foreground mt-2">
          Diferencia de la Regresión Logística contra cada uno:{" "}
          {difs.map((d, i) => (
            <span key={d.comparacion}>
              {i > 0 && " · "}
              {NOMBRE[d.comparacion.replace("LR − ", "") as Modelo]} {num(d.dif_f1, 3, true)} ({d.significativa ? "significativa" : "no significativa"})
            </span>
          ))}
          .
        </p>
      )}
      <p className="text-xs text-muted-foreground mt-2">
        En 2026 los cinco quedan casi en el azar. En dinero, las redes salieron mejor este año: la CNN 1D casi nunca dice
        «mantener» y casi no cambia de posición, así que se comporta como una apuesta casi fija. Un Sharpe de diez meses no es
        significativo por sí solo; por eso no elegimos con un solo periodo.
      </p>
    </Card>
  );
}

function Dinero() {
  const [exp, setExp] = useState<Exp>("B");
  const datos = MODELOS.map((m) => {
    const f = D.experimentos[exp].find((x) => x.modelo === m)!;
    return { modelo: NOMBRE[m], sin: f.sharpe_0bp, con: f.sharpe_10bp };
  });
  return (
    <Card className="p-6 mb-6">
      <Titulo id="dinero" ayuda="sharpe">Con dinero: ganancia contra riesgo</Titulo>
      <p className="text-sm text-muted-foreground mt-1 mb-3">Sharpe de seguir las recomendaciones en 2025, sin y con una comisión de 0.1 % por cambio de posición.</p>
      <SelectorExp exp={exp} setExp={setExp} />
      <div className="h-64 mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={datos} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
            <XAxis dataKey="modelo" tick={ejeEstilo} interval={0} />
            <YAxis tick={ejeEstilo} width={45} />
            <Tooltip contentStyle={tooltipStyle} formatter={(v: any, n: any) => [num(Number(v), 2, true), n === "sin" ? "Sin comisión" : "Con comisión"]} />
            <ReferenceLine y={0} stroke="currentColor" opacity={0.6} />
            <Legend formatter={(v: string) => (v === "sin" ? "Sin comisión" : "Con comisión")} wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="sin" fill="#3d4450" radius={[4, 4, 0, 0]} isAnimationActive={false} />
            <Bar dataKey="con" fill="#a9aeb5" radius={[4, 4, 0, 0]} isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-muted-foreground mt-2">Arriba de 0 gana; abajo pierde. Las redes pierden dinero incluso sin comisiones.</p>
    </Card>
  );
}

function GlobalVsAccion() {
  const datos = MODELOS.map((m) => {
    const g = D.global_vs_por_accion.find((x) => x.modelo === m)!;
    return { modelo: NOMBRE[m], gana: g.celdas_gana_global_f1, p: g.p_signo_f1, color: COLOR[m] };
  });
  return (
    <Card className="p-6 mb-6">
      <Titulo id="global">Un modelo para las 7 acciones o uno por acción</Titulo>
      <p className="text-sm text-muted-foreground mt-1 mb-3">
        De 21 comparaciones (7 acciones × 3 experimentos, mismos días), en cuántas ganó el modelo global.
      </p>
      <div className="h-60">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={datos} layout="vertical" margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
            <XAxis type="number" domain={[0, 21]} tick={ejeEstilo} />
            <YAxis type="category" dataKey="modelo" tick={ejeEstilo} width={90} />
            <Tooltip contentStyle={tooltipStyle} formatter={(v: any, _n: any, it: any) => [`${v} de 21 (p = ${num(it.payload.p, 3)})`, "Gana el global"]} />
            <ReferenceLine x={10.5} stroke="currentColor" strokeDasharray="4 4" opacity={0.6} />
            <Bar dataKey="gana" radius={[0, 4, 4, 0]} isAnimationActive={false}>
              {datos.map((d) => (
                <Cell key={d.modelo} fill={d.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-muted-foreground mt-2">
        Línea punteada: empate. El global gana con significancia en Reg. Logística, LSTM y CNN 1D, y empata en XGBoost y
        CNN-LSTM. Ningún modelo es mejor por acción.
      </p>
    </Card>
  );
}

function Variables() {
  const [exp, setExp] = useState<Exp>("B");
  const diag = D.multicolinealidad_diagnostico;
  const mc = D.multicolinealidad;
  const par = (m: Modelo, e: string) => ({
    todas: mc?.find((x) => x.modelo === m && x.exp === e && x.brazo === "todas_61")?.f1_macro,
    filtro: mc?.find((x) => x.modelo === m && x.exp === e && x.brazo === "filtro_vif10")?.f1_macro,
  });
  const datos = mc
    ? MODELOS.map((m) => ({ modelo: NOMBRE[m], ...par(m, exp) })).filter((d) => d.todas !== undefined && d.filtro !== undefined)
    : [];
  const casos = MODELOS.flatMap((m) => (["A", "B", "C"] as Exp[]).map((e) => par(m, e))).filter(
    (c) => c.todas !== undefined && c.filtro !== undefined,
  );
  const ganan61 = casos.filter((c) => (c.todas as number) > (c.filtro as number)).length;
  const nFiltro = mc?.find((x) => x.exp === exp && x.brazo === "filtro_vif10")?.n_variables;
  return (
    <Card className="p-6 mb-6">
      <Titulo id="variables" ayuda="multicolinealidad">¿Por qué no quitamos las variables parecidas?</Titulo>
      <p className="text-sm text-muted-foreground mt-1">
        Muchas de las 61 variables se parecen entre sí (multicolinealidad). Eso complica interpretar cada coeficiente, pero
        no necesariamente empeora las predicciones: la regularización de la Regresión Logística reparte el peso entre
        variables parecidas y los árboles de XGBoost no se ven afectados.
      </p>
      {diag && (
        <div className="grid grid-cols-3 gap-2 my-4 text-center">
          <div className="rounded-lg bg-muted p-2">
            <div className="text-lg font-bold text-foreground">{diag["pares_r_mayor_0.9"]}</div>
            <div className="text-xs text-muted-foreground">pares con correlación mayor a 0.9</div>
          </div>
          <div className="rounded-lg bg-muted p-2">
            <div className="text-lg font-bold text-foreground">{diag.vif_mayor_10}</div>
            <div className="text-xs text-muted-foreground">variables con VIF mayor a 10</div>
          </div>
          <div className="rounded-lg bg-muted p-2">
            <div className="text-lg font-bold text-foreground">{diag.variables_tras_filtro_vif10_B}</div>
            <div className="text-xs text-muted-foreground">quedan si se quitan hasta VIF ≤ 10</div>
          </div>
        </div>
      )}
      {datos.length > 0 && (
        <>
          <p className="text-sm text-muted-foreground mb-2">
            F1 en la prueba 2025 con las 61 variables contra solo las {nFiltro} que quedan tras el filtro:
          </p>
          <SelectorExp exp={exp} setExp={setExp} />
          <div className="h-64 mt-3">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={datos} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.2} />
                <XAxis dataKey="modelo" tick={ejeEstilo} interval={0} />
                <YAxis tick={ejeEstilo} domain={[0, 0.45]} ticks={[0, 0.1, 0.2, 0.3, 0.4]} width={45} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: any, n: any) => [num(Number(v), 3), n === "todas" ? "Las 61" : "Con filtro VIF"]} />
                <ReferenceLine y={0.333} stroke="currentColor" strokeDasharray="4 4" opacity={0.6} />
                <Legend formatter={(v: string) => (v === "todas" ? "Las 61 variables" : "Con filtro VIF ≤ 10")} wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="todas" fill="#2a78d6" radius={[4, 4, 0, 0]} isAnimationActive={false} />
                <Bar dataKey="filtro" fill="#a9aeb5" radius={[4, 4, 0, 0]} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
      {casos.length > 0 && (
        <p className="text-sm text-foreground mt-3">
          Con las 61 variables el resultado es mejor en <strong>{ganan61} de {casos.length}</strong> casos (5 modelos × 3
          experimentos). A las redes, quitar variables las empeora; a los modelos clásicos les da prácticamente igual. Por eso
          se quedan las 61: es además la opción más favorable para las redes, y aun así ganan los clásicos.
        </p>
      )}
      <p className="text-xs text-muted-foreground mt-2">
        El filtro se calcula solo con los datos de entrenamiento. En el TT1 cada modelo usaba un filtro distinto; desde la
        Etapa 3 los cinco usan las mismas 61 para compararlos en igualdad.
      </p>
    </Card>
  );
}

export default function Modelos() {
  return (
    <div className="pb-8">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-foreground">Los cinco modelos, comparados</h2>
        <p className="text-sm text-muted-foreground mt-1">Cómo los comparamos y por qué usamos la Regresión Logística.</p>
      </div>
      <div className="flex flex-wrap gap-2 mb-6">
        {SECCIONES.map(([id, t]) => (
          <a key={id} href={`#${id}`} className="text-xs px-3 py-1.5 rounded-full bg-muted text-foreground hover:bg-card border border-border">
            {t}
          </a>
        ))}
      </div>
      <Elegido />
      <Igualdad />
      <PruebaPrincipal />
      <AnioPorAnio />
      <Ciega />
      <Dinero />
      <GlobalVsAccion />
      <Variables />
      <p className="text-center text-xs text-muted-foreground">
        Las seis etapas del trabajo y todos los detalles están en{" "}
        <Link to="/about" className="text-blue-600 dark:text-blue-400 hover:underline">
          Acerca de
        </Link>
        .
      </p>
    </div>
  );
}

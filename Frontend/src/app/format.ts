import { ArrowDown, ArrowUp, Circle } from "lucide-react";
import type { Signal } from "./types";

export const SIGNAL_CONFIG = {
  buy: {
    icon: ArrowUp,
    label: "Comprar",
    short: "Comprar",
    /** Explicación en pocas palabras para quien no conoce el término. */
    frase: "Podría subir",
    color: "text-emerald-600 dark:text-emerald-400",
    borderColor: "border-emerald-500 dark:border-emerald-400",
    hex: "#10b981",
  },
  sell: {
    icon: ArrowDown,
    label: "Vender",
    short: "Vender",
    frase: "Podría bajar",
    color: "text-red-600 dark:text-red-400",
    borderColor: "border-red-500 dark:border-red-400",
    hex: "#ef4444",
  },
  hold: {
    icon: Circle,
    label: "Mantener",
    short: "Mantener",
    frase: "Mejor esperar",
    color: "text-amber-600 dark:text-amber-400",
    borderColor: "border-amber-500 dark:border-amber-400",
    hex: "#f59e0b",
  },
} as const satisfies Record<Signal, unknown>;

// ── Seguridad de la recomendación ─────────────────────────────────────────
// La "confianza" del modelo (probabilidad de la opción elegida) casi siempre
// está entre 0.33 y 0.45 y no se entiende como porcentaje. Se traduce a tres
// niveles con palabras. Cortes = percentiles 30 y 60 de la confianza del
// modelo actual; `acierto` = % de aciertos de cada nivel en 2019–2025, con
// modelos que no habían visto el año evaluado; `dias` = % de días en cada
// nivel. Fuente: scripts_opt/calibrar_niveles_confianza.py →
// RESULTADOS_OPTIMIZADOS/analisis_hold/9_niveles_seguridad.json.
// No hay un nivel "Segura": ningún tramo acierta ni la mitad de las veces.
export const ACIERTO_AZAR = 33;
export const NIVELES_SEGURIDAD = [
  { desde: 0, nombre: "Nada segura", acierto: 37, dias: 30, descripcion: "El modelo está casi indeciso." },
  { desde: 0.35, nombre: "Poco segura", acierto: 38, dias: 30, descripcion: "Se inclina por una opción, pero por poco." },
  { desde: 0.3664, nombre: "Medianamente segura", acierto: 42, dias: 40, descripcion: "Tiene una preferencia más clara." },
] as const;

export type NivelSeguridad = (typeof NIVELES_SEGURIDAD)[number] & { indice: number };

export function nivelSeguridad(confianza: number | null | undefined): NivelSeguridad | null {
  if (!isNum(confianza)) return null;
  let indice = 0;
  NIVELES_SEGURIDAD.forEach((n, i) => {
    if (confianza >= n.desde) indice = i;
  });
  return { ...NIVELES_SEGURIDAD[indice], indice };
}

// ── Números ───────────────────────────────────────────────────────────────
const isNum = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);

/** Porcentaje ya expresado en % (p. ej. 12.3 -> "12.3 %"). */
export function pct(v: number | null | undefined, decimals = 1, signed = false): string {
  if (!isNum(v)) return "—";
  const s = v.toFixed(decimals).replace("-", "−"); // signo menos tipográfico
  // espacio no separable: "37.4 %" nunca se parte en dos líneas
  return `${signed && v > 0 ? "+" : ""}${s} %`;
}

/** Fracción 0-1 mostrada como % (p. ej. 0.412 -> "41.2 %"). */
export function frac(v: number | null | undefined, decimals = 1): string {
  return isNum(v) ? pct(v * 100, decimals) : "—";
}

export function num(v: number | null | undefined, decimals = 2, signed = false): string {
  if (!isNum(v)) return "—";
  return `${signed && v > 0 ? "+" : ""}${v.toFixed(decimals).replace("-", "−")}`;
}

/** Dinero en dólares: 1052.3 -> "$1,052.30". */
export function usd(v: number | null | undefined, decimals = 2): string {
  if (!isNum(v)) return "—";
  return `${v < 0 ? "−" : ""}$${Math.abs(v).toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

/** "12 de 29 (41 %)". */
export function deTotal(parte: number | null | undefined, total: number | null | undefined): string {
  if (!isNum(parte) || !isNum(total) || total === 0) return "—";
  return `${parte} de ${total} (${pct((parte / total) * 100, 0)})`;
}

/** Drawdown (positivo = caída) como "−4.6 %"; 0 sin signo. */
export function dd(v: number | null | undefined, decimals = 1): string {
  if (!isNum(v)) return "—";
  return Number(v.toFixed(decimals)) > 0 ? `−${pct(v, decimals)}` : pct(0, decimals);
}

// ── Fechas (sin desfase de zona horaria) ──────────────────────────────────
function aFecha(iso: string): Date | null {
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  return y && m && d ? new Date(Date.UTC(y, m - 1, d)) : null;
}

/** "2026-09-29" -> "29 sep 2026". */
export function fecha(iso: string | null | undefined): string {
  if (!iso) return "—";
  const f = aFecha(iso);
  return f ? f.toLocaleDateString("es-MX", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }) : iso;
}

/** "2026-09-29" -> "martes 29 de septiembre de 2026". */
export function fechaLarga(iso: string | null | undefined): string {
  if (!iso) return "—";
  const f = aFecha(iso);
  return f
    ? f
        .toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long", year: "numeric", timeZone: "UTC" })
        .replace(",", "") // "miércoles, 14 de…" -> "miércoles 14 de…"
    : iso;
}

/** "2026-09-29" -> "martes 29 de septiembre" (sin año, para frases cortas). */
export function fechaDia(iso: string | null | undefined): string {
  if (!iso) return "—";
  const f = aFecha(iso);
  return f
    ? f.toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" }).replace(",", "")
    : iso;
}

/** "2026-09-29" -> "mar 29 sep" (para encabezados de tabla). */
export function fechaConDia(iso: string | null | undefined): string {
  if (!iso) return "—";
  const f = aFecha(iso);
  return f ? f.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" }) : iso;
}

/** "2026-09-29" -> "29 sep" (para ejes de gráficas). */
export function fechaEje(iso: string): string {
  const f = aFecha(iso);
  return f ? f.toLocaleDateString("es-MX", { day: "numeric", month: "short", timeZone: "UTC" }) : iso;
}

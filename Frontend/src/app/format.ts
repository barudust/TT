import { ArrowDown, ArrowUp, Circle } from "lucide-react";
import type { Signal } from "./types";

export const SIGNAL_CONFIG = {
  buy: {
    icon: ArrowUp,
    label: "COMPRAR (LARGO)",
    short: "COMPRAR",
    color: "text-emerald-600 dark:text-emerald-400",
    borderColor: "border-emerald-500 dark:border-emerald-400",
    hex: "#10b981",
  },
  sell: {
    icon: ArrowDown,
    label: "VENDER (CORTO)",
    short: "VENDER",
    color: "text-red-600 dark:text-red-400",
    borderColor: "border-red-500 dark:border-red-400",
    hex: "#ef4444",
  },
  hold: {
    icon: Circle,
    label: "MANTENER",
    short: "MANTENER",
    color: "text-amber-600 dark:text-amber-400",
    borderColor: "border-amber-500 dark:border-amber-400",
    hex: "#f59e0b",
  },
} as const satisfies Record<Signal, unknown>;

const isNum = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);

/** Porcentaje ya expresado en % (p. ej. 12.3 -> "12.3 %"). */
export function pct(v: number | null | undefined, decimals = 1, signed = false): string {
  if (!isNum(v)) return "—";
  const s = v.toFixed(decimals);
  // espacio no separable: "37.4 %" nunca se parte en dos líneas
  return `${signed && v > 0 ? "+" : ""}${s} %`;
}

/** Fracción 0-1 mostrada como % (p. ej. 0.412 -> "41.2 %"). */
export function frac(v: number | null | undefined, decimals = 1): string {
  return isNum(v) ? pct(v * 100, decimals) : "—";
}

export function num(v: number | null | undefined, decimals = 2, signed = false): string {
  if (!isNum(v)) return "—";
  return `${signed && v > 0 ? "+" : ""}${v.toFixed(decimals)}`;
}

/** "2026-09-29" -> "29 sep 2026" sin desfase de zona horaria. */
export function fecha(iso: string | null | undefined): string {
  if (!iso) return "—";
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  if (!y || !m || !d) return iso;
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString("es-MX", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

/** Drawdown (positivo = caída) como "−4.6 %"; 0 sin signo. */
export function dd(v: number | null | undefined, decimals = 1): string {
  if (!isNum(v)) return "—";
  return Number(v.toFixed(decimals)) > 0 ? `−${pct(v, decimals)}` : pct(0, decimals);
}

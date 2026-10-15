import type { ReactNode } from "react";
import { InfoLink } from "./InfoLink";

interface MetricCardProps {
  label: string;
  value: ReactNode;
  /** Texto pequeño bajo el valor: cómo leerlo o con qué compararlo. */
  hint?: ReactNode;
  color?: string;
  /** id del término en el glosario (muestra un "?" junto al nombre). */
  help?: string;
}

export function MetricCard({ label, value, hint, color = "text-foreground", help }: MetricCardProps) {
  return (
    <div className="bg-muted p-4 rounded-lg">
      <div className="text-sm text-muted-foreground mb-1 flex items-start gap-1">
        <span>{label}</span>
        {help && <InfoLink term={help} />}
      </div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      {hint && <div className="text-xs text-muted-foreground mt-1">{hint}</div>}
    </div>
  );
}

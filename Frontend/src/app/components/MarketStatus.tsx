import { Clock, CalendarDays } from "lucide-react";
import { fecha } from "../format";

interface MarketStatusProps {
  isOpen?: boolean | null; // null/undefined = estado desconocido (API sin responder)
  lastUpdate?: string;
  dataDate?: string;
}

function tiempoDesde(iso?: string): string | null {
  if (!iso) return null;
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return null;
  const minutos = Math.floor((Date.now() - t) / 60000);
  if (minutos < 1) return "hace unos momentos";
  if (minutos < 60) return `hace ${minutos} min`;
  const horas = Math.floor(minutos / 60);
  if (horas < 48) return `hace ${horas} hora${horas > 1 ? "s" : ""}`;
  const dias = Math.floor(horas / 24);
  return `hace ${dias} días`;
}

export function MarketStatus({ isOpen, lastUpdate, dataDate }: MarketStatusProps) {
  const actualizado = tiempoDesde(lastUpdate);

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs">
      {isOpen !== null && isOpen !== undefined && (
        <div className="flex items-center gap-1.5">
          <div className={`w-2 h-2 rounded-full ${isOpen ? "bg-[#10b981] animate-pulse" : "bg-muted-foreground/40"}`} />
          <span className="text-muted-foreground font-medium">
            {isOpen ? "Mercado abierto (NYSE)" : "Mercado cerrado (NYSE)"}
          </span>
        </div>
      )}
      {dataDate && (
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <CalendarDays className="w-3.5 h-3.5" />
          <span>Señales con el cierre del {fecha(dataDate)}</span>
        </div>
      )}
      {actualizado && (
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <Clock className="w-3.5 h-3.5" />
          <span>Recalculadas {actualizado}</span>
        </div>
      )}
    </div>
  );
}

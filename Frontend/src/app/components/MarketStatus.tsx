import { Clock, CalendarDays, CalendarClock } from "lucide-react";
import { fechaLarga } from "../format";
import { InfoLink } from "./InfoLink";

interface MarketStatusProps {
  isOpen?: boolean | null; // null/undefined = estado desconocido (API sin responder)
  lastUpdate?: string;
  dataDate?: string;
  nextTradingDay?: string;
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

export function MarketStatus({ isOpen, lastUpdate, dataDate, nextTradingDay }: MarketStatusProps) {
  const actualizado = tiempoDesde(lastUpdate);

  return (
    <div className="space-y-1.5 text-xs">
      {nextTradingDay && (
        <div className="flex items-center gap-1.5 text-foreground">
          <CalendarClock className="w-4 h-4 text-blue-500" />
          <span>
            Recomendaciones para la sesión del <strong>{fechaLarga(nextTradingDay)}</strong>
          </span>
        </div>
      )}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
        {dataDate && (
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <CalendarDays className="w-3.5 h-3.5" />
            <span>Calculadas con los precios de cierre del {fechaLarga(dataDate)}</span>
          </div>
        )}
        {isOpen !== null && isOpen !== undefined && (
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full ${isOpen ? "bg-[#10b981] animate-pulse" : "bg-muted-foreground/40"}`} />
            <span className="text-muted-foreground font-medium">
              {isOpen ? "Bolsa de Nueva York abierta ahora" : "Bolsa de Nueva York cerrada ahora"}
            </span>
            <InfoLink term="mercado" />
          </div>
        )}
        {actualizado && (
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <Clock className="w-3.5 h-3.5" />
            <span>Actualizadas {actualizado}</span>
          </div>
        )}
      </div>
    </div>
  );
}

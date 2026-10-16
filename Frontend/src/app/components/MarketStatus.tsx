import { CalendarClock } from "lucide-react";
import { fechaDia } from "../format";

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
  if (minutos < 1) return "hace un momento";
  if (minutos < 60) return `hace ${minutos} min`;
  const horas = Math.floor(minutos / 60);
  if (horas < 48) return `hace ${horas} h`;
  const dias = Math.floor(horas / 24);
  return `hace ${dias} días`;
}

export function MarketStatus({ isOpen, lastUpdate, dataDate, nextTradingDay }: MarketStatusProps) {
  const actualizado = tiempoDesde(lastUpdate);
  const detalles = [
    dataDate && `Con los precios del ${fechaDia(dataDate)}`,
    isOpen !== null && isOpen !== undefined && (isOpen ? "Bolsa abierta ahora" : "Bolsa cerrada"),
    actualizado && `Actualizado ${actualizado}`,
  ].filter(Boolean);

  return (
    <div className="space-y-1">
      {nextTradingDay && (
        <div className="flex items-center gap-1.5 text-sm text-foreground">
          <CalendarClock className="w-4 h-4 text-blue-500" />
          <span>
            Para el <strong>{fechaDia(nextTradingDay)}</strong>
          </span>
        </div>
      )}
      {detalles.length > 0 && (
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          {isOpen && <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse" />}
          <span>{detalles.join(" · ")}</span>
        </div>
      )}
    </div>
  );
}

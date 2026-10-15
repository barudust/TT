import { Link } from "react-router";
import { ChevronRight } from "lucide-react";
import { SIGNAL_CONFIG, usd } from "../format";
import { SeguridadBadge } from "./SeguridadBadge";
import type { Stock } from "../types";

export type { Stock };

interface StockCardProps {
  stock: Stock;
}

export function StockCard({ stock }: StockCardProps) {
  const config = SIGNAL_CONFIG[stock.signal];
  const Icon = config.icon;

  return (
    <Link to={`/stock/${stock.symbol}`} aria-label={`Ver detalle de ${stock.name}`}>
      <div className="bg-card rounded-xl shadow-sm border border-border p-4 hover:shadow-md transition-all hover:border-border/80 cursor-pointer">
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-bold text-foreground leading-tight">{stock.name}</h3>
            <div className="text-xs text-muted-foreground mb-2">Clave en bolsa: {stock.symbol}</div>
            <div className="text-xs text-muted-foreground">Precio al cierre</div>
            <div className="text-2xl font-bold text-foreground mb-2">{usd(stock.currentPrice)}</div>
            <div className="text-xs text-muted-foreground mb-0.5">Seguridad de la recomendación</div>
            <div className="text-sm">
              <SeguridadBadge confianza={stock.confidence} />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className={`flex flex-col items-center gap-1 px-3 py-3 rounded-lg bg-muted border w-32 text-center ${config.borderColor}`}>
              <Icon className={`w-6 h-6 ${config.color}`} />
              <span className={`text-sm font-bold ${config.color}`}>{config.label}</span>
              <span className="text-[11px] leading-tight text-muted-foreground">{config.frase}</span>
            </div>
            <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
          </div>
        </div>
      </div>
    </Link>
  );
}

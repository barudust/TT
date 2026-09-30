import { Link } from "react-router";
import { SIGNAL_CONFIG, frac } from "../format";
import type { Stock } from "../types";

export type { Stock };

interface StockCardProps {
  stock: Stock;
}

export function StockCard({ stock }: StockCardProps) {
  const config = SIGNAL_CONFIG[stock.signal];
  const Icon = config.icon;

  return (
    <Link to={`/stock/${stock.symbol}`}>
      <div className="bg-card rounded-xl shadow-sm border border-border p-4 hover:shadow-md transition-all hover:border-border/80 cursor-pointer">
        <div className="flex items-center justify-between gap-3">
          {/* Stock Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-baseline gap-2 mb-1">
              <h3 className="text-lg font-bold text-foreground">{stock.symbol}</h3>
              <span className="text-xs text-muted-foreground truncate max-w-[180px]">
                {stock.name}
              </span>
            </div>
            <div className="text-2xl font-bold text-foreground mb-2">
              ${stock.currentPrice.toFixed(2)}
            </div>
            <div className="text-xs text-muted-foreground">
              Confianza del modelo: {frac(stock.confidence, 0)}
            </div>
          </div>

          {/* Signal Badge */}
          <div
            className={`flex flex-col items-center gap-1 px-4 py-3 rounded-lg bg-muted border ${config.borderColor}`}
          >
            <Icon className={`w-6 h-6 ${config.color}`} />
            <span className={`text-xs font-bold ${config.color}`}>
              {config.label}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}

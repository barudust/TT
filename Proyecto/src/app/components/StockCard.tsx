import { ArrowUp, ArrowDown, Circle } from "lucide-react";
import { Link } from "react-router";

export interface Stock {
  symbol: string;
  name: string;
  currentPrice: number;
  signal: "buy" | "sell" | "hold";
  confidence: number;
  lastUpdate: string;
}

interface StockCardProps {
  stock: Stock;
}

export function StockCard({ stock }: StockCardProps) {
  const signalConfig = {
    buy: {
      icon: ArrowUp,
      label: "COMPRAR (LARGO)",
      color: "text-emerald-600 dark:text-emerald-400",
      bgColor: "bg-muted",
      borderColor: "border-emerald-500 dark:border-emerald-400",
    },
    sell: {
      icon: ArrowDown,
      label: "VENDER (CORTO)",
      color: "text-red-600 dark:text-red-400",
      bgColor: "bg-muted",
      borderColor: "border-red-500 dark:border-red-400",
    },
    hold: {
      icon: Circle,
      label: "MANTENER",
      color: "text-amber-600 dark:text-amber-400",
      bgColor: "bg-muted",
      borderColor: "border-amber-500 dark:border-amber-400",
    },
  };

  const config = signalConfig[stock.signal];
  const Icon = config.icon;

  return (
    <Link to={`/stock/${stock.symbol}`}>
      <div className="bg-card rounded-xl shadow-sm border border-border p-4 hover:shadow-md transition-all hover:border-border/80 cursor-pointer">
        <div className="flex items-center justify-between">
          {/* Stock Info */}
          <div className="flex-1">
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
              Confianza: {(stock.confidence * 100).toFixed(0)}%
            </div>
          </div>

          {/* Signal Badge */}
          <div
            className={`flex flex-col items-center gap-1 px-4 py-3 rounded-lg ${config.bgColor} border ${config.borderColor}`}
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

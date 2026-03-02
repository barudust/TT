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
      label: "BUY LONG",
      color: "text-green-600",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
    },
    sell: {
      icon: ArrowDown,
      label: "SELL SHORT",
      color: "text-red-600",
      bgColor: "bg-red-50",
      borderColor: "border-red-200",
    },
    hold: {
      icon: Circle,
      label: "HOLD",
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
      borderColor: "border-yellow-200",
    },
  };

  const config = signalConfig[stock.signal];
  const Icon = config.icon;

  return (
    <Link to={`/stock/${stock.symbol}`}>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 hover:shadow-md transition-all hover:border-gray-300 cursor-pointer">
        <div className="flex items-center justify-between">
          {/* Stock Info */}
          <div className="flex-1">
            <div className="flex items-baseline gap-2 mb-1">
              <h3 className="text-lg font-bold text-gray-900">{stock.symbol}</h3>
              <span className="text-xs text-gray-500 truncate max-w-[180px]">
                {stock.name}
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-2">
              ${stock.currentPrice.toFixed(2)}
            </div>
            <div className="text-xs text-gray-500">
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

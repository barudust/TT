import { Clock, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MarketStatusProps {
  isOpen?: boolean;
  lastUpdate?: string;
}

export function MarketStatus({ isOpen = false, lastUpdate }: MarketStatusProps) {
  const now = new Date();
  const updateTime = lastUpdate ? new Date(lastUpdate) : now;
  
  // Calcular tiempo desde última actualización
  const minutesSinceUpdate = Math.floor((now.getTime() - updateTime.getTime()) / 60000);
  
  let updateText = "Hace unos momentos";
  if (minutesSinceUpdate > 60) {
    const hours = Math.floor(minutesSinceUpdate / 60);
    updateText = `Hace ${hours} hora${hours > 1 ? "s" : ""}`;
  } else if (minutesSinceUpdate > 0) {
    updateText = `Hace ${minutesSinceUpdate} min`;
  }

  return (
    <div className="flex items-center gap-3 text-xs">
      <div className="flex items-center gap-1.5">
        <div className={`w-2 h-2 rounded-full ${isOpen ? "bg-[#10b981] animate-pulse" : "bg-muted"}`} />
        <span className="text-muted-foreground font-medium">
          {isOpen ? "Mercado abierto" : "Mercado cerrado"}
        </span>
      </div>
      <div className="flex items-center gap-1.5 text-muted-foreground">
        <Clock className="w-3.5 h-3.5" />
        <span>{updateText}</span>
      </div>
    </div>
  );
}

interface SignalBadgeProps {
  signal: "buy" | "sell" | "hold";
  size?: "sm" | "md" | "lg";
}

export function SignalBadge({ signal, size = "md" }: SignalBadgeProps) {
  const configs = {
    buy: {
      icon: TrendingUp,
      label: "BUY",
      colors: "bg-slate-800 text-[#10b981] border-[#10b981]",
    },
    sell: {
      icon: TrendingDown,
      label: "SELL",
      colors: "bg-slate-800 text-[#ef4444] border-[#ef4444]",
    },
    hold: {
      icon: Minus,
      label: "HOLD",
      colors: "bg-slate-800 text-[#f59e0b] border-[#f59e0b]",
    },
  };

  const sizes = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
    lg: "px-3 py-1.5 text-sm",
  };

  const iconSizes = {
    sm: "w-3 h-3",
    md: "w-3.5 h-3.5",
    lg: "w-4 h-4",
  };

  const config = configs[signal];
  const Icon = config.icon;

  return (
    <div className={`inline-flex items-center gap-1 rounded-full border font-bold ${config.colors} ${sizes[size]}`}>
      <Icon className={iconSizes[size]} />
      {config.label}
    </div>
  );
}

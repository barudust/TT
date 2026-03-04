import { Outlet, Link, useLocation } from "react-router";
import { TrendingUp, BarChart3, Info, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export default function Root() {
  const location = useLocation();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"];
  const navItems = [
    { path: "/", icon: TrendingUp, label: "Stocks" },
    { path: "/performance", icon: BarChart3, label: "Performance" },
    { path: "/about", icon: Info, label: "About" },
  ];

  return (
    <div className="min-h-screen bg-background pb-20">
      <header className="bg-background border-b border-border sticky top-0 z-50 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-2 rounded-xl">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">TradingSignals AI</h1>
                <p className="text-xs text-muted-foreground">Deep Learning Stock Prediction</p>
              </div>
            </div>
            {mounted && (
              <button
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="p-2 rounded-lg hover:bg-muted transition-colors"
                title="Cambiar tema"
              >
                {theme === "dark" ? (
                  <Sun className="w-5 h-5 text-amber-400" />
                ) : (
                  <Moon className="w-5 h-5 text-blue-400" />
                )}
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="bg-background border-b border-border sticky top-16 z-40">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="overflow-x-auto">
            <div className="flex gap-2 min-w-max">
              {stocks.map((symbol) => {
                const isActive = location.pathname === `/stock/${symbol}`;
                return (
                  <Link
                    key={symbol}
                    to={`/stock/${symbol}`}
                    className={`px-4 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition-all ${
                      isActive
                        ? "bg-blue-500 text-white shadow-md"
                        : "bg-muted text-foreground hover:bg-card"
                    }`}
                  >
                    {symbol}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <main className="max-w-4xl mx-auto px-4 py-6">
        <Outlet />
      </main>

      <nav className="fixed bottom-0 left-0 right-0 bg-background border-t border-border shadow-lg z-50">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex justify-around items-center h-16">
            {navItems.map((item) => {
              const isActive = item.path === "/"
                ? location.pathname === "/"
                : location.pathname.startsWith(item.path);
              const Icon = item.icon;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex flex-col items-center justify-center gap-1 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? "text-blue-500"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Icon className={`w-6 h-6 ${isActive ? "fill-blue-100 dark:fill-blue-900" : ""}`} />
                  <span className="text-xs font-medium">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>
    </div>
  );
}


import { Outlet, Link, useLocation } from "react-router";
import { TrendingUp, BarChart3, Info } from "lucide-react";

export default function Root() {
  const location = useLocation();
  const stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM"];
  const navItems = [
    { path: "/", icon: TrendingUp, label: "Stocks" },
    { path: "/performance", icon: BarChart3, label: "Performance" },
    { path: "/about", icon: Info, label: "About" },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-2 rounded-xl">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">TradingSignals AI</h1>
              <p className="text-xs text-gray-500">Deep Learning Stock Prediction</p>
            </div>
          </div>
        </div>
      </header>

      <div className="bg-white border-b border-gray-200 sticky top-16 z-40">
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
                        ? "bg-blue-600 text-white shadow-md"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
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

      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
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
                      ? "text-blue-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  <Icon className={`w-6 h-6 ${isActive ? "fill-blue-100" : ""}`} />
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


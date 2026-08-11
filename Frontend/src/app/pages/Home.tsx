import { useState, useEffect } from "react";
import { StockCard, Stock } from "../components/StockCard";
import { LoadingSpinner, StockCardSkeleton } from "../components/LoadingStates";
import { MarketStatus } from "../components/MarketStatus";
import { RefreshCw } from "lucide-react";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import { API_BASE_URL } from "../../config/api";

export default function Home() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  const fetchStocks = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      let response = await fetch(`${API_BASE_URL}/stocks`);

      if (!response.ok) {
        throw new Error("Error al obtener datos de acciones");
      }

      let data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Error desconocido");
      }

      // Cold start conocido del plan free de Render: la API puede responder
      // "sana" (health check ok) pero con el catálogo vacío si Yahoo
      // Finance falló transitoriamente al arrancar (ver
      // docs/DEPLOY_RENDER.md). Antes este botón solo releía esa misma
      // caché vacía sin arreglar nada. Si detectamos el catálogo vacío,
      // forzamos /admin/refresh (recalcula todo desde cero, ~30-40s) y
      // reintentamos una sola vez antes de rendirnos.
      if (data.data.length === 0) {
        toast.info("El servidor no tenía datos cargados. Repoblando… puede tardar ~30s.");
        await fetch(`${API_BASE_URL}/admin/refresh`, { method: "POST" }).catch((e) => {
          console.error("Error triggering /admin/refresh:", e);
        });

        response = await fetch(`${API_BASE_URL}/stocks`);
        if (response.ok) {
          data = await response.json();
        }
      }

      if (data.success) {
        setStocks(data.data);
        if (data.data.length > 0) {
          setLastUpdate(data.data[0].lastUpdate);
        }
        if (isRefresh) {
          toast.success("Datos actualizados correctamente");
        }
      } else {
        throw new Error(data.error || "Error desconocido");
      }
    } catch (error) {
      console.error("Error fetching stocks:", error);
      toast.error("No se pudieron cargar los datos. Intenta nuevamente.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStocks();
  }, []);

  if (loading) {
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-foreground">Señales del Día</h2>
          <p className="text-sm text-muted-foreground mt-1">Cargando predicciones...</p>
        </div>
        <div className="space-y-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <StockCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Señales del Día</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Predicciones generadas al cierre del mercado
            </p>
          </div>
          <Button
            onClick={() => fetchStocks(true)}
            disabled={refreshing}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            {refreshing ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
        {lastUpdate && (
          <div className="mt-3">
            <MarketStatus isOpen={false} lastUpdate={lastUpdate} />
          </div>
        )}
      </div>
      <div className="space-y-3">
        {stocks.map((stock) => (
          <StockCard key={stock.symbol} stock={stock} />
        ))}
      </div>
      <div className="mt-8 bg-muted border border-border rounded-lg p-4">
        <p className="text-sm text-muted-foreground">
          <span className="font-semibold">💡 Nota:</span> Las señales son generadas
          por un modelo de Machine Learning (Regresión Logística elasticnet)
          entrenado con datos históricos. No constituyen asesoramiento financiero.
        </p>
      </div>
    </div>
  );
}

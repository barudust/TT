import { useState, useEffect } from "react";
import { StockCard } from "../components/StockCard";
import { StockCardSkeleton } from "../components/LoadingStates";
import { MarketStatus } from "../components/MarketStatus";
import { RefreshCw, HelpCircle } from "lucide-react";
import { Link } from "react-router";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import { API_BASE_URL } from "../../config/api";
import type { MarketStatusInfo, Stock } from "../types";

export default function Home() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [market, setMarket] = useState<MarketStatusInfo | null>(null);

  const fetchMarketStatus = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/market-status`);
      const body = await res.json();
      if (body?.success) setMarket(body.data);
    } catch (e) {
      console.error("Error fetching market status:", e);
      setMarket(null);
    }
  };

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
      // docs/DEPLOY_RENDER.md). Si detectamos el catálogo vacío, forzamos
      // /admin/refresh (recalcula todo desde cero, ~30-40s) y reintentamos
      // una sola vez antes de rendirnos.
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
    fetchMarketStatus();
  }, []);

  const refresh = () => {
    fetchStocks(true);
    fetchMarketStatus();
  };

  if (loading) {
    return (
      <div>
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-foreground">¿Qué hacer hoy con cada acción?</h2>
          <p className="text-sm text-muted-foreground mt-1">Cargando recomendaciones… (la primera carga puede tardar hasta 1 minuto)</p>
        </div>
        <div className="space-y-3">
          {Array.from({ length: 7 }).map((_, i) => (
            <StockCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  const ref = stocks[0];

  return (
    <div>
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-2xl font-bold text-foreground">¿Qué hacer hoy con cada acción?</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Recomendación diaria del modelo para cada una de las 7 empresas. Toca una tarjeta para ver su detalle.
            </p>
          </div>
          <Button
            onClick={refresh}
            disabled={refreshing}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            {refreshing ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
        <div className="mt-3">
          <MarketStatus isOpen={market?.isOpen} lastUpdate={ref?.lastUpdate} dataDate={ref?.dataDate} nextTradingDay={ref?.nextTradingDay} />
        </div>
      </div>
      <div className="space-y-3">
        {stocks.map((stock) => (
          <StockCard key={stock.symbol} stock={stock} />
        ))}
      </div>
      <div className="mt-8 bg-muted border border-border rounded-lg p-4 space-y-2 text-sm text-muted-foreground">
        <p>
          <span className="font-semibold text-foreground">Cómo leer cada tarjeta:</span> a la derecha está la
          recomendación (COMPRAR, VENDER o MANTENER) para la próxima sesión de la bolsa; abajo del precio, qué tan
          segura es, según qué tan seguido acertó el modelo en el pasado en situaciones parecidas.
        </p>
        <p>
          Las recomendaciones las genera un modelo de Regresión Logística entrenado con datos de 2018 a 2025
          {ref?.modelVersion ? ` (versión ${ref.modelVersion})` : ""}. Se actualizan una vez al día, después del
          cierre de la bolsa. <strong>Son un ejercicio académico, no asesoría financiera.</strong>
        </p>
        <Link to="/ayuda" className="inline-flex items-center gap-1.5 text-blue-600 dark:text-blue-400 font-medium hover:underline">
          <HelpCircle className="w-4 h-4" /> Guía de uso y glosario de términos
        </Link>
      </div>
    </div>
  );
}

import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./ui/button";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      <div className="bg-red-50 p-4 rounded-full mb-4">
        <AlertCircle className="w-12 h-12 text-red-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Error al cargar datos
      </h3>
      <p className="text-sm text-gray-600 text-center max-w-md mb-6">
        {message || "No se pudieron cargar los datos. Por favor, intenta nuevamente."}
      </p>
      {onRetry && (
        <Button onClick={onRetry} className="gap-2">
          <RefreshCw className="w-4 h-4" />
          Reintentar
        </Button>
      )}
    </div>
  );
}

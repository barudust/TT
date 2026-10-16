import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./ui/button";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      <div className="bg-muted p-4 rounded-full mb-4">
        <AlertCircle className="w-12 h-12 text-[#ef4444]" />
      </div>
      <h3 className="text-lg font-semibold text-foreground mb-2">
        Algo salió mal
      </h3>
      <p className="text-sm text-muted-foreground text-center max-w-md mb-6">
        {message || "No pudimos cargar los datos. Intenta de nuevo en un momento."}
      </p>
      {onRetry && (
        <Button onClick={onRetry} className="gap-2">
          <RefreshCw className="w-4 h-4" />
          Volver a intentar
        </Button>
      )}
    </div>
  );
}

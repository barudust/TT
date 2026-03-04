export function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="relative">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-[#3b82f6]"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-8 w-8 bg-muted rounded-full"></div>
        </div>
      </div>
      <p className="mt-6 text-muted-foreground font-medium">Cargando datos...</p>
    </div>
  );
}

export function StockCardSkeleton() {
  return (
    <div className="bg-card rounded-xl shadow-sm border border-border p-4 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="h-5 bg-muted rounded w-16 mb-2"></div>
          <div className="h-3 bg-muted rounded w-32 mb-3"></div>
          <div className="h-8 bg-muted rounded w-24 mb-2"></div>
          <div className="h-3 bg-muted rounded w-20"></div>
        </div>
        <div className="w-20 h-20 bg-muted rounded-lg"></div>
      </div>
    </div>
  );
}

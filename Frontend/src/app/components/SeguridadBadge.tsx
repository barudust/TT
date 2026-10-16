import { ACIERTO_AZAR, NIVELES_SEGURIDAD, nivelSeguridad } from "../format";
import { InfoLink } from "./InfoLink";

interface SeguridadBadgeProps {
  confianza: number | null | undefined;
  /** "completo" agrega qué significa el nivel y cuánto acertó en el pasado. */
  variante?: "corto" | "completo";
  conAyuda?: boolean;
}

/** Nivel de seguridad con palabras y barras (en lugar de un porcentaje).
 *  Las barras son azules para no confundirse con los colores de comprar,
 *  vender y mantener. */
export function SeguridadBadge({ confianza, variante = "corto", conAyuda = false }: SeguridadBadgeProps) {
  const nivel = nivelSeguridad(confianza);
  if (!nivel) return <span className="text-muted-foreground">—</span>;
  return (
    <span className="inline-flex flex-col gap-1">
      <span className="inline-flex items-center gap-2">
        <span className="inline-flex items-end gap-0.5" aria-hidden="true">
          {NIVELES_SEGURIDAD.map((_, i) => (
            <span
              key={i}
              className={`w-1.5 rounded-sm ${i <= nivel.indice ? "bg-blue-500" : "bg-border"}`}
              style={{ height: `${7 + i * 4}px` }}
            />
          ))}
        </span>
        <span className="font-semibold text-foreground">{nivel.nombre}</span>
        {conAyuda && <InfoLink term="seguridad" />}
      </span>
      {variante === "completo" && (
        <span className="text-xs text-muted-foreground">
          {nivel.descripcion} Con este nivel ha acertado {nivel.acierto} de cada 100 veces (adivinando, {ACIERTO_AZAR}).
        </span>
      )}
    </span>
  );
}

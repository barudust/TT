import { Link } from "react-router";
import { HelpCircle } from "lucide-react";
import { GLOSARIO } from "../glosario";

/** Ícono "?" que lleva a la definición del término en el glosario de Ayuda. */
export function InfoLink({ term }: { term: string }) {
  const entrada = GLOSARIO.find((t) => t.id === term);
  return (
    <Link
      to={`/ayuda?tab=glosario#${term}`}
      title={entrada ? `¿Qué es «${entrada.termino}»?` : "Ver en el glosario"}
      aria-label={entrada ? `¿Qué es ${entrada.termino}?` : "Ver en el glosario"}
      className="inline-flex align-middle text-muted-foreground hover:text-blue-500 transition-colors"
      onClick={(e) => e.stopPropagation()}
    >
      <HelpCircle className="w-3.5 h-3.5" />
    </Link>
  );
}

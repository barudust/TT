import { useEffect, useState } from "react";
import { useLocation, useSearchParams } from "react-router";
import { BookOpen, ListChecks, Search, AlertTriangle } from "lucide-react";
import { Card } from "../components/ui/card";
import { CATEGORIAS_GLOSARIO, GLOSARIO } from "../glosario";
import { NIVELES_SEGURIDAD, SIGNAL_CONFIG } from "../format";
import { SeguridadBadge } from "../components/SeguridadBadge";
import type { Signal } from "../types";

type Pestana = "guia" | "glosario";

function Seccion({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <Card className="p-5 mb-4">
      <h3 className="font-bold text-foreground text-lg mb-3">{titulo}</h3>
      <div className="text-sm text-muted-foreground space-y-2 leading-relaxed">{children}</div>
    </Card>
  );
}

function Guia() {
  return (
    <div>
      <Seccion titulo="¿Qué es esto?">
        <p>
          Todos los días, cuando cierra la Bolsa de Nueva York, un modelo revisa cómo se movieron 7 empresas tecnológicas
          y sugiere qué hacer con cada una al día siguiente: comprar, vender o mantener.
        </p>
        <p>También te enseña qué tanto ha atinado y cuánto habrías ganado o perdido haciéndole caso.</p>
      </Seccion>

      <Seccion titulo="Las tarjetas de «Hoy»">
        <p>Cada tarjeta trae el precio de la empresa al cierre, qué tan segura es la recomendación y, a la derecha, la recomendación:</p>
        <div className="grid gap-2 sm:grid-cols-3 my-2">
          {(["buy", "hold", "sell"] as Signal[]).map((s) => {
            const c = SIGNAL_CONFIG[s];
            const Icon = c.icon;
            return (
              <div key={s} className={`flex items-center gap-2 p-2 rounded-lg bg-muted border ${c.borderColor}`}>
                <Icon className={`w-5 h-5 ${c.color}`} />
                <div>
                  <div className={`font-bold uppercase tracking-wide ${c.color}`}>{c.label}</div>
                  <div className="text-xs">{c.frase}</div>
                </div>
              </div>
            );
          })}
        </div>
        <p>Toca una tarjeta para ver la historia de esa empresa.</p>
      </Seccion>

      <Seccion titulo="Dentro de cada empresa">
        <ul className="list-disc list-inside space-y-1">
          <li>La recomendación de hoy y cómo se repartió la decisión del modelo.</li>
          <li>El precio de los últimos 30, 60 o 90 días, con un punto de color por cada recomendación.</li>
          <li>Qué habría pasado con $1,000 haciéndole caso, contra solo comprar y esperar.</li>
          <li>Las últimas 10 recomendaciones y si le atinó o no.</li>
        </ul>
        <p>Si un dato no te queda claro, toca el «?» que tiene al lado.</p>
      </Seccion>

      <Seccion titulo="«Resultados»">
        <p>Junta las 7 empresas para ver cómo le va al modelo en general y en cuáles le ha ido mejor.</p>
      </Seccion>

      <Seccion titulo="¿Qué tan segura es una recomendación?">
        <p>
          Adivinar si una acción sube o baja mañana es muy difícil, así que el modelo nunca está muy seguro. En vez de un
          porcentaje, usamos tres niveles según qué tanto ha atinado antes:
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm my-2">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-2 text-foreground">Nivel</th>
                <th className="text-right py-2 px-2 text-foreground">Ha acertado</th>
                <th className="text-right py-2 pl-2 text-foreground">Aparece</th>
              </tr>
            </thead>
            <tbody>
              {NIVELES_SEGURIDAD.map((n, i) => (
                <tr key={n.nombre} className="border-b border-border">
                  <td className="py-2 pr-2">
                    <SeguridadBadge confianza={n.desde + (i === 0 ? 0.34 : 0.0001)} />
                    <div className="text-xs text-muted-foreground">{n.descripcion}</div>
                  </td>
                  <td className="text-right py-2 px-2 text-foreground">{n.acierto} de cada 100</td>
                  <td className="text-right py-2 pl-2">{n.dias} % de los días</td>
                </tr>
              ))}
              <tr>
                <td className="py-2 pr-2 italic">Adivinando</td>
                <td className="text-right py-2 px-2">33 de cada 100</td>
                <td />
              </tr>
            </tbody>
          </table>
        </div>
        <p>Incluso en el mejor nivel se equivoca más de la mitad de las veces. Tómalo como una opinión más, no como una garantía.</p>
      </Seccion>

      <Seccion titulo="¿Cuándo se actualiza?">
        <p>
          Una vez al día, a las 16:30 de Nueva York (entre 14:30 y 15:30 en el centro de México). Fines de semana y días
          festivos no hay recomendaciones nuevas.
        </p>
        <p>Si tarda en abrir, dale hasta un minuto: el servidor es gratuito y se duerme cuando nadie lo usa.</p>
      </Seccion>

      <Card className="p-5 mb-4 border-2 border-[#ef4444]">
        <div className="flex gap-3">
          <AlertTriangle className="w-6 h-6 text-[#ef4444] flex-shrink-0" />
          <p className="text-sm text-muted-foreground">
            Es un proyecto escolar (ESCOM-IPN), no una asesoría financiera. Invertir siempre implica el riesgo de perder dinero.
          </p>
        </div>
      </Card>
    </div>
  );
}

function Glosario() {
  const [buscar, setBuscar] = useState("");
  const q = buscar.trim().toLowerCase();
  const visibles = GLOSARIO.filter(
    (t) => !q || [t.termino, t.tambien ?? "", t.definicion].some((x) => x.toLowerCase().includes(q)),
  );

  return (
    <div>
      <div className="relative mb-4">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input
          value={buscar}
          onChange={(e) => setBuscar(e.target.value)}
          placeholder="Busca un término (por ejemplo: Sharpe, ganancia, mantener)"
          className="w-full pl-9 pr-3 py-2 rounded-lg border border-border bg-background text-sm text-foreground"
        />
      </div>
      {CATEGORIAS_GLOSARIO.map((cat) => {
        const terminos = visibles.filter((t) => t.categoria === cat);
        if (terminos.length === 0) return null;
        return (
          <div key={cat} className="mb-6">
            <h3 className="text-sm font-bold uppercase tracking-wide text-muted-foreground mb-2">{cat}</h3>
            <div className="space-y-3">
              {terminos.map((t) => (
                <Card key={t.id} id={t.id} className="p-4 scroll-mt-40 target:ring-2 target:ring-blue-500">
                  <div className="font-bold text-foreground">{t.termino}</div>
                  {t.tambien && <div className="text-xs text-muted-foreground mb-1">También: {t.tambien}</div>}
                  <p className="text-sm text-muted-foreground leading-relaxed">{t.definicion}</p>
                  {t.ejemplo && <p className="text-sm text-muted-foreground mt-1"><span className="font-semibold text-foreground">Ejemplo:</span> {t.ejemplo}</p>}
                </Card>
              ))}
            </div>
          </div>
        );
      })}
      {visibles.length === 0 && <p className="text-sm text-muted-foreground">No encontramos ese término.</p>}
    </div>
  );
}

export default function Help() {
  const [params, setParams] = useSearchParams();
  const location = useLocation();
  const pestana: Pestana = params.get("tab") === "glosario" ? "glosario" : "guia";

  // Al llegar desde un ícono "?" (/ayuda?tab=glosario#sharpe), llevar al término.
  useEffect(() => {
    if (!location.hash) return;
    const el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      el.classList.add("ring-2", "ring-blue-500");
      const t = setTimeout(() => el.classList.remove("ring-2", "ring-blue-500"), 2500);
      return () => clearTimeout(t);
    }
  }, [location.hash, pestana]);

  const tab = (id: Pestana, label: string, Icon: typeof BookOpen) => (
    <button
      onClick={() => setParams(id === "guia" ? {} : { tab: id })}
      className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-md text-sm font-semibold transition-colors ${
        pestana === id ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
      }`}
    >
      <Icon className="w-4 h-4" /> {label}
    </button>
  );

  return (
    <div className="pb-8">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-foreground">Ayuda</h2>
        <p className="text-sm text-muted-foreground mt-1">Cómo leer la página y qué significa cada cosa.</p>
      </div>
      <div className="flex gap-1 p-1 bg-muted rounded-lg mb-6">
        {tab("guia", "Guía rápida", ListChecks)}
        {tab("glosario", "Glosario", BookOpen)}
      </div>
      {pestana === "guia" ? <Guia /> : <Glosario />}
    </div>
  );
}

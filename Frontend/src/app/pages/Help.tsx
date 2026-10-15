import { useEffect, useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router";
import { BookOpen, ListChecks, Search, Smartphone, AlertTriangle } from "lucide-react";
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

function Termino({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <Link to={`/ayuda?tab=glosario#${id}`} className="text-blue-600 dark:text-blue-400 hover:underline">
      {children}
    </Link>
  );
}

function Guia() {
  return (
    <div>
      <Seccion titulo="¿Qué hace esta aplicación?">
        <p>
          Cada día hábil, después de que cierra la Bolsa de Nueva York, un modelo revisa los precios de 7 empresas
          tecnológicas (Apple, Microsoft, Google, Amazon, Tesla, Meta y NVIDIA) y recomienda qué hacer con cada una en
          la siguiente sesión: <strong>COMPRAR</strong>, <strong>VENDER</strong> o <strong>MANTENER</strong>.
        </p>
        <p>
          También muestra, con datos reales, qué tan seguido ha acertado y cuánto habría ganado o perdido alguien que
          siguiera sus recomendaciones.
        </p>
      </Seccion>

      <Seccion titulo="1. Pantalla «Hoy»: la recomendación de cada empresa">
        <p>Cada tarjeta muestra:</p>
        <ul className="list-disc list-inside space-y-1">
          <li><strong>Nombre de la empresa</strong> y su <Termino id="accion">clave en bolsa</Termino> (por ejemplo, AAPL).</li>
          <li><strong>Precio al cierre</strong> del último día hábil, en dólares.</li>
          <li><strong>La recomendación</strong> a la derecha, con una frase que la explica:</li>
        </ul>
        <div className="grid gap-2 sm:grid-cols-3 my-2 list-none">
          {(["buy", "hold", "sell"] as Signal[]).map((s) => {
            const c = SIGNAL_CONFIG[s];
            const Icon = c.icon;
            return (
              <div key={s} className={`flex items-center gap-2 p-2 rounded-lg bg-muted border ${c.borderColor}`}>
                <Icon className={`w-5 h-5 ${c.color}`} />
                <div>
                  <div className={`font-bold ${c.color}`}>{c.label}</div>
                  <div className="text-xs">{c.frase}</div>
                </div>
              </div>
            );
          })}
        </div>
        <ul className="list-disc list-inside space-y-1">
          <li><strong>La seguridad</strong> de la recomendación, en palabras (ver la sección 4).</li>
        </ul>
        <p>Arriba se indica para qué día es la recomendación y con qué precios se calculó.</p>
      </Seccion>

      <Seccion titulo="2. Detalle de una empresa">
        <p>Toca una tarjeta o el nombre de la empresa en la barra superior. Verás, de arriba hacia abajo:</p>
        <ol className="list-decimal list-inside space-y-1">
          <li><strong>La recomendación de hoy</strong> y cómo repartió el modelo su opinión entre las tres opciones (<Termino id="probabilidades">probabilidades</Termino>).</li>
          <li><strong>El periodo</strong>: elige 30, 60 o 90 días hábiles hacia atrás; todo lo de abajo se recalcula.</li>
          <li>
            <strong>Gráfica de precio:</strong> eje horizontal = fecha; eje vertical = precio de cierre en dólares. Cada
            punto de color es la recomendación que dio el modelo ese día (verde COMPRAR, amarillo MANTENER, rojo VENDER).
          </li>
          <li>
            <strong>Gráfica «¿Qué habría pasado con $1,000?»:</strong> eje horizontal = fecha; eje vertical = dinero. La
            línea de color sigue las recomendaciones; la gris compra la acción y la deja quieta.
          </li>
          <li><strong>Qué tan bien acertó</strong> y <strong>cuánto habría ganado o perdido</strong> en el periodo. Cada dato tiene un ícono «?» con su explicación.</li>
          <li><strong>Las últimas 10 recomendaciones</strong>, qué pasó al día siguiente y si acertó.</li>
        </ol>
      </Seccion>

      <Seccion titulo="3. Pantalla «Resultados»: las 7 empresas juntas">
        <p>
          Promedia los resultados de las 7 empresas y las compara entre sí: cuánto habrías ganado en cada una siguiendo
          las recomendaciones contra solo comprar y esperar, y la calificación del modelo en cada una contra lo que se
          obtendría al azar. La tabla del final se puede ordenar tocando el nombre de cada columna.
        </p>
      </Seccion>

      <Seccion titulo="4. ¿Qué tan segura es una recomendación?">
        <p>
          El modelo nunca está muy seguro: predecir si una acción subirá o bajará mañana es muy difícil. Por eso, en lugar
          de un porcentaje, la aplicación usa tres niveles basados en <strong>qué tan seguido acertó el modelo en el
          pasado</strong> cuando estaba igual de seguro (pruebas con datos de 2019 a 2025 que el modelo no había visto):
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm my-2">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 pr-2 text-foreground">Nivel</th>
                <th className="text-right py-2 px-2 text-foreground">Aciertos en el pasado</th>
                <th className="text-right py-2 pl-2 text-foreground">Qué tan seguido aparece</th>
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
                  <td className="text-right py-2 pl-2">{n.dias} de cada 100 días</td>
                </tr>
              ))}
              <tr>
                <td className="py-2 pr-2 italic">Escoger al azar</td>
                <td className="text-right py-2 px-2">33 de cada 100</td>
                <td />
              </tr>
            </tbody>
          </table>
        </div>
        <p>
          Aun en el nivel más alto, el modelo se equivoca más de la mitad de las veces. Úsalo como una opinión adicional,
          nunca como una garantía.
        </p>
      </Seccion>

      <Seccion titulo="5. ¿Cuándo se actualiza?">
        <p>
          Una vez por día hábil, a las 16:30 hora de Nueva York (alrededor de las 14:30 o 15:30 hora del centro de México,
          según el horario de verano de EE. UU.). Fines de semana y feriados de la bolsa no hay recomendaciones nuevas.
          La recomendación más reciente aparece como <Termino id="pendiente">«Pendiente»</Termino> hasta que cierra el día siguiente.
        </p>
        <p>
          Si la aplicación tarda en cargar la primera vez, espera hasta un minuto: el servidor gratuito se "duerme" cuando
          nadie lo usa.
        </p>
      </Seccion>

      <Seccion titulo="6. Instalarla en el celular">
        <div className="flex gap-3">
          <Smartphone className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p><strong>Android (Chrome):</strong> menú ⋮ → «Agregar a la pantalla principal» o «Instalar aplicación».</p>
            <p><strong>iPhone (Safari):</strong> botón Compartir → «Agregar a inicio».</p>
          </div>
        </div>
      </Seccion>

      <Card className="p-5 mb-4 border-2 border-[#ef4444]">
        <div className="flex gap-3">
          <AlertTriangle className="w-6 h-6 text-[#ef4444] flex-shrink-0" />
          <p className="text-sm text-muted-foreground">
            <strong className="text-foreground">Importante:</strong> esta aplicación es parte de un trabajo académico
            (ESCOM-IPN). Las recomendaciones no son asesoría financiera; invertir implica riesgo de perder dinero.
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
          placeholder="Buscar un término (por ejemplo: Sharpe, rendimiento, MANTENER)"
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
                  {t.tambien && <div className="text-xs text-muted-foreground mb-1">También llamado: {t.tambien}</div>}
                  <p className="text-sm text-muted-foreground leading-relaxed">{t.definicion}</p>
                  {t.ejemplo && <p className="text-sm text-muted-foreground mt-1"><span className="font-semibold text-foreground">Ejemplo:</span> {t.ejemplo}</p>}
                </Card>
              ))}
            </div>
          </div>
        );
      })}
      {visibles.length === 0 && <p className="text-sm text-muted-foreground">No se encontró ningún término.</p>}
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
        <p className="text-sm text-muted-foreground mt-1">Cómo usar la aplicación y qué significa cada término</p>
      </div>
      <div className="flex gap-1 p-1 bg-muted rounded-lg mb-6">
        {tab("guia", "Guía de uso", ListChecks)}
        {tab("glosario", "Glosario", BookOpen)}
      </div>
      {pestana === "guia" ? <Guia /> : <Glosario />}
    </div>
  );
}

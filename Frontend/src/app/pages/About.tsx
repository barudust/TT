import { useEffect, useState } from "react";
import { Card } from "../components/ui/card";
import { Link } from "react-router";
import { AlertTriangle, BookOpen, Code, Cpu, TrendingUp, Users } from "lucide-react";
import { API_BASE_URL } from "../../config/api";
import type { ModelInfo } from "../types";

export default function About() {
  const [model, setModel] = useState<ModelInfo | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/model`)
      .then((r) => r.json())
      .then((body) => body?.success && setModel(body.data))
      .catch((e) => console.error("Error fetching model info:", e));
  }, []);

  const stocks = [
    { symbol: "AAPL", name: "Apple Inc.", sector: "Tecnología" },
    { symbol: "MSFT", name: "Microsoft Corporation", sector: "Tecnología" },
    { symbol: "GOOGL", name: "Alphabet Inc.", sector: "Tecnología / Internet" },
    { symbol: "AMZN", name: "Amazon.com Inc.", sector: "Consumo / E-commerce" },
    { symbol: "TSLA", name: "Tesla Inc.", sector: "Automotriz / Energía" },
    { symbol: "META", name: "Meta Platforms Inc.", sector: "Redes Sociales" },
    { symbol: "NVDA", name: "NVIDIA Corporation", sector: "Semiconductores / IA" },
  ];

  const technologies = [
    "Python",
    "scikit-learn",
    "XGBoost",
    "PyTorch",
    "Optuna",
    "Flask",
    "SQLite",
    "React",
    "TypeScript",
    "Yahoo Finance",
  ];

  const ficha: Array<[string, string]> = model
    ? [
        ["Algoritmo", `Regresión Logística multinomial (${model.algorithm})`],
        ["Regularización", `${model.penalty?.toUpperCase() ?? "—"}, C = ${model.C?.toExponential(2) ?? "—"}, pesos de clase ${model.classWeight ?? "—"}`],
        ["Variables", `${model.nFeatures} (${model.nFeaturesBase} indicadores técnicos y de mercado + ${model.nInteractions} interacciones)`],
        ["Escalado", model.scaler],
        ["Estrategia", model.strategy],
        ["Datos de entrenamiento", `${model.trainRange ?? "—"}${model.nTrainSamples ? ` · ${model.nTrainSamples.toLocaleString("es-MX")} días-acción` : ""}`],
        ["Etiqueta", `Retorno a ${model.target.horizonDays} día; comprar ≥ percentil ${model.target.percentileBuy}, vender ≤ percentil ${model.target.percentileSell} de los últimos ${model.target.rollingWindowDays} días`],
        ["Versión", model.version],
      ]
    : [];

  return (
    <div className="pb-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Acerca del proyecto</h2>
        <p className="text-sm text-muted-foreground mt-1">Trabajo Terminal 2026-B164 · ESCOM-IPN</p>
      </div>

      <Card className="p-6 mb-6 border-2 border-[#ef4444] bg-muted">
        <div className="flex gap-4">
          <AlertTriangle className="w-8 h-8 text-[#ef4444] flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-[#ef4444] text-lg mb-2">Antes de usarla</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Es un proyecto escolar con fines educativos, <strong>no una asesoría financiera</strong>. Invertir implica
              el riesgo de perder dinero; si vas a hacerlo, consulta a un asesor certificado.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="bg-muted p-3 rounded-lg flex-shrink-0">
            <BookOpen className="w-6 h-6 text-[#3b82f6]" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-foreground text-lg mb-3">De qué trata</h3>
            <p className="text-muted-foreground leading-relaxed">
              Comparamos varias técnicas de aprendizaje automático para decidir qué hacer al día siguiente (comprar,
              mantener o vender) con 7 acciones grandes de tecnología, usando solo datos gratuitos de Yahoo Finance.
              Las recomendaciones que ves aquí son del modelo que mejor salió.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="bg-muted p-3 rounded-lg flex-shrink-0">
            <Code className="w-6 h-6 text-[#8b5cf6]" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-foreground text-lg mb-3">Cómo lo hicimos</h3>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-foreground mb-2">Modelos que comparamos</h4>
                <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                  <li><strong>Regresión Logística</strong>: la ganadora, es la que se usa aquí.</li>
                  <li><strong>XGBoost</strong>: muchos árboles de decisión combinados.</li>
                  <li><strong>LSTM</strong>: red neuronal que lee los días anteriores en orden.</li>
                  <li><strong>CNN 1D</strong>: red neuronal que busca patrones cortos en esos días.</li>
                  <li><strong>CNN-LSTM</strong>: una mezcla de las dos anteriores.</li>
                </ul>
                <p className="text-sm text-muted-foreground mt-2">
                  Probamos cada uno con las 7 acciones juntas y con cada acción por separado, y ajustamos sus parámetros con
                  Optuna. Un solo modelo para las 7 salió igual o mejor que uno por acción.
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-foreground mb-2">Paso a paso</h4>
                <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                  <li>Bajamos los precios diarios de Yahoo Finance, junto con el S&P 500 y el VIX para tener el contexto del mercado.</li>
                  <li>Con esos precios calculamos indicadores técnicos: tendencias, volatilidad, RSI, MACD, volumen y otros.</li>
                  <li>Marcamos cada día como comprar, mantener o vender según qué tanto se movió la acción al día siguiente, comparado con su último año.</li>
                  <li>Calificamos los modelos por qué tanto atinan (F1) y por cuánto habrían ganado.</li>
                  <li>Todos los días, al cerrar la bolsa, el servidor baja los datos nuevos y el modelo da la recomendación del día siguiente.</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="bg-muted p-3 rounded-lg flex-shrink-0">
            <Cpu className="w-6 h-6 text-[#06b6d4]" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-foreground text-lg mb-1">Modelo elegido: Regresión Logística</h3>
            <p className="text-sm text-muted-foreground mb-3">
              Por qué este y no los otros cuatro:{" "}
              <Link to="/modelos" className="text-blue-600 dark:text-blue-400 hover:underline">comparación completa en «Modelos»</Link>.
            </p>
            {model ? (
              <dl className="text-sm grid grid-cols-1 sm:grid-cols-[max-content_1fr] gap-x-4 gap-y-2">
                {ficha.map(([k, v]) => (
                  <div key={k} className="contents">
                    <dt className="font-semibold text-foreground">{k}</dt>
                    <dd className="text-muted-foreground break-words">{v}</dd>
                  </div>
                ))}
              </dl>
            ) : (
              <p className="text-sm text-muted-foreground">No se pudo consultar la información del modelo en la API.</p>
            )}
          </div>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="bg-muted p-3 rounded-lg flex-shrink-0">
            <TrendingUp className="w-6 h-6 text-[#10b981]" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-foreground text-lg mb-3">Las 7 empresas</h3>
            <p className="text-muted-foreground mb-4">
              Siete de las tecnológicas más grandes de EE. UU., con mucho movimiento en la bolsa y más de diez años de
              historia:
            </p>
            <div className="grid gap-2">
              {stocks.map((stock) => (
                <div
                  key={stock.symbol}
                  className="flex justify-between items-center p-3 bg-muted dark:bg-muted rounded-lg hover:bg-card transition-colors"
                >
                  <div>
                    <div className="font-semibold text-foreground">{stock.symbol}</div>
                    <div className="text-sm text-muted-foreground">{stock.name}</div>
                  </div>
                  <div className="text-xs text-muted-foreground bg-muted dark:bg-muted/50 px-2 py-1 rounded">
                    {stock.sector}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="bg-muted p-3 rounded-lg flex-shrink-0">
            <Users className="w-6 h-6 text-[#f59e0b]" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-foreground text-lg mb-4">Créditos</h3>

            <div className="space-y-4 text-sm text-muted-foreground">
              <div>
                <div className="font-semibold text-foreground mb-2">Institución</div>
                <p className="text-muted-foreground">
                  Escuela Superior de Cómputo (ESCOM)
                  <br />
                  Instituto Politécnico Nacional (IPN)
                </p>
              </div>

              <div>
                <div className="font-semibold text-foreground mb-2">Trabajo Terminal</div>
                <p className="text-muted-foreground">TT 2026-B164</p>
              </div>

              <div>
                <div className="font-semibold text-foreground mb-2">Desarrolladores</div>
                <ul className="text-muted-foreground list-disc list-inside space-y-1">
                  <li>Reyes Ramos David</li>
                  <li>Polvo Cuatianquiz Jesús Baruc</li>
                </ul>
              </div>

              <div>
                <div className="font-semibold text-foreground mb-2">Directores</div>
                <p className="text-muted-foreground">Abdiel Reyes Vera</p>
                <p className="text-muted-foreground">Emmanuel Juárez Carbajal</p>
              </div>

              <div>
                <div className="font-semibold text-foreground mb-2">Tecnologías</div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {technologies.map((tech) => (
                    <span
                      key={tech}
                      className="px-3 py-1 bg-muted text-[#3b82f6] border border-[#3b82f6] rounded-full text-xs font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

    </div>
  );
}

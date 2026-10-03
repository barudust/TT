import { useEffect, useState } from "react";
import { Card } from "../components/ui/card";
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
        ["Etiqueta", `Retorno a ${model.target.horizonDays} día; COMPRAR ≥ percentil ${model.target.percentileBuy}, VENDER ≤ percentil ${model.target.percentileSell} de los últimos ${model.target.rollingWindowDays} días`],
        ["Versión", model.version],
      ]
    : [];

  return (
    <div className="pb-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground">Acerca del Proyecto</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Trabajo Terminal 2026-B164 - ESCOM IPN
        </p>
      </div>

      <Card className="p-6 mb-6 border-2 border-[#ef4444] bg-muted">
        <div className="flex gap-4">
          <AlertTriangle className="w-8 h-8 text-[#ef4444] flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-[#ef4444] text-lg mb-2">
              Aviso Legal Importante
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Las señales de trading generadas por esta aplicación son{" "}
              <strong>exclusivamente con fines educativos y de investigación</strong>. Este
              proyecto forma parte de un trabajo de tesis académico en la Escuela Superior de
              Cómputo del Instituto Politécnico Nacional (ESCOM-IPN) y{" "}
              <strong>no constituye asesoramiento financiero profesional</strong>. Invertir en
              los mercados financieros implica riesgos significativos y puede resultar en
              pérdida de capital. Se recomienda encarecidamente consultar con un asesor
              financiero certificado antes de tomar cualquier decisión de inversión.
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
            <h3 className="font-bold text-foreground text-lg mb-3">
              Descripción del Proyecto
            </h3>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Esta aplicación es el resultado del Trabajo Terminal <strong>TT 2026-B164</strong>, que
              compara técnicas de Machine Learning y Deep Learning para clasificar la señal de
              trading del día siguiente en acciones de alta capitalización, usando únicamente
              datos históricos gratuitos de Yahoo Finance. Las señales que se muestran las genera
              el modelo ganador de esa comparación.
            </p>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>
                <strong>COMPRAR:</strong> el modelo espera que el retorno del día siguiente quede
                entre los más altos de su último año (posición larga).
              </p>
              <p>
                <strong>VENDER (en corto):</strong> el modelo espera que quede entre los más bajos
                (posición corta).
              </p>
              <p>
                <strong>MANTENER:</strong> el modelo no distingue una dirección clara; no se abre
                posición. Es más frecuente en periodos de baja volatilidad.
              </p>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="bg-muted p-3 rounded-lg flex-shrink-0">
            <Code className="w-6 h-6 text-[#8b5cf6]" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-foreground text-lg mb-3">Metodología</h3>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-foreground mb-2">Modelos comparados</h4>
                <ul className="text-sm text-muted-foreground space-y-2 list-disc list-inside">
                  <li><strong>Regresión Logística</strong> con regularización (modelo ganador, en producción).</li>
                  <li><strong>XGBoost</strong>: ensamble de árboles de decisión con gradient boosting.</li>
                  <li><strong>LSTM</strong>: red neuronal recurrente que lee la secuencia de días previos.</li>
                  <li><strong>CNN 1D</strong>: red convolucional que detecta patrones locales en la secuencia.</li>
                  <li><strong>CNN-LSTM</strong>: híbrido convolucional + recurrente.</li>
                </ul>
                <p className="text-sm text-muted-foreground mt-2">
                  Cada modelo se entrenó de forma global (un modelo para las 7 acciones) y por acción,
                  en tres ventanas de entrenamiento con el mismo año de prueba (2025), con búsqueda de
                  hiperparámetros con Optuna. La Regresión Logística obtuvo el mejor F1-macro y el mejor
                  Sharpe; la versión global resultó igual o mejor que entrenar un modelo por acción.
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-foreground mb-2">
                  Proceso
                </h4>
                <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
                  <li><strong>Datos:</strong> precios diarios OHLCV de Yahoo Finance, más el S&P 500 (SPY) y el VIX como contexto de mercado.</li>
                  <li><strong>Variables:</strong> indicadores técnicos (retornos, medias móviles, volatilidad, RSI, MACD, volumen, velas, estacionalidad y mercado).</li>
                  <li><strong>Etiquetado:</strong> COMPRAR / MANTENER / VENDER según el percentil del retorno del día siguiente respecto a los 252 días previos del mismo activo.</li>
                  <li><strong>Evaluación:</strong> F1-macro para la clasificación y un backtest de un día (Sharpe, drawdown, win rate) para el valor económico.</li>
                  <li><strong>Operación diaria:</strong> después del cierre de NYSE la API descarga los datos, recalcula las variables y el modelo emite la señal del siguiente día hábil.</li>
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
            <h3 className="font-bold text-foreground text-lg mb-3">Modelo en producción</h3>
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
            <h3 className="font-bold text-foreground text-lg mb-3">
              Acciones Seleccionadas
            </h3>
            <p className="text-muted-foreground mb-4">
              Se eligieron 7 acciones de alta capitalización del sector tecnológico de EE. UU.,
              con alta liquidez y más de diez años de historial disponible:
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
                <div className="font-semibold text-foreground mb-2">Tecnologías Utilizadas</div>
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

      <div className="mt-6 text-center text-sm text-muted-foreground">
        <p>Desarrollado con fines académicos</p>
      </div>
    </div>
  );
}

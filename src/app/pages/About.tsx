import { Card } from "../components/ui/card";
import { AlertTriangle, BookOpen, GraduationCap, Code, TrendingUp, Users } from "lucide-react";

export default function About() {
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
    "TensorFlow",
    "LSTM",
    "CNN-LSTM",
    "React",
    "TypeScript",
    "Flask",
    "Yahoo Finance",
  ];

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
              Esta aplicación es el resultado del Trabajo Terminal{" "}
              <strong>TT 2026-B164</strong>, cuyo objetivo es demostrar la aplicación de
              técnicas de Deep Learning para la clasificación de tendencias en el mercado
              bursátil. A través de modelos de redes neuronales (LSTM y CNN-LSTM),
              entrenados con datos históricos de precios obtenidos de Yahoo Finance, generamos
              señales de trading diarias para una selección de acciones de alta capitalización.
            </p>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>
                <strong>BUY (Comprar):</strong> Se espera que el precio suba en el corto
                plazo.
              </p>
              <p>
                <strong>SELL (Vender en corto):</strong> Se espera que el precio baje.
              </p>
              <p>
                <strong>HOLD (Mantener):</strong> No hay una dirección clara o se recomienda
                esperar.
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
                <h4 className="font-semibold text-foreground mb-2">Modelos Utilizados</h4>
                <ul className="text-sm text-muted-foreground space-y-2 list-disc list-inside">
                  <li>
                    <strong>LSTM (Long Short-Term Memory):</strong> Redes neuronales
                    recurrentes diseñadas para capturar dependencias temporales en series de
                    datos, ideales para el análisis de precios históricos.
                  </li>
                  <li>
                    <strong>CNN-LSTM:</strong> Arquitectura híbrida que combina capas
                    convolucionales para extraer patrones locales relevantes y capas LSTM
                    para modelar las relaciones temporales de largo plazo.
                  </li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-foreground mb-2">
                  Proceso de Entrenamiento
                </h4>
                <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
                  <li>
                    <strong>Recolección de datos:</strong> Descarga de precios históricos
                    desde Yahoo Finance
                  </li>
                  <li>
                    <strong>Preprocesamiento:</strong> Cálculo de indicadores técnicos y
                    normalización
                  </li>
                  <li>
                    <strong>Etiquetado:</strong> Generación de señales BUY/SELL/HOLD basadas
                    en volatilidad
                  </li>
                  <li>
                    <strong>División de datos:</strong> Conjuntos de entrenamiento,
                    validación y prueba
                  </li>
                  <li>
                    <strong>Entrenamiento y evaluación:</strong> Optimización con métricas
                    como accuracy, precision, recall y F1-score
                  </li>
                </ol>
              </div>
            </div>
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
              Se eligieron 7 acciones de alta capitalización que representan diversos
              sectores del mercado, garantizando liquidez y disponibilidad de datos
              históricos:
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
                <div className="font-semibold text-foreground mb-2">Director</div>
                <p className="text-muted-foreground">Abdiel Reyes Vega</p>
                <p className="text-muted-foreground">Emmanuel Juarez Carvajal</p>
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
        <p>Versión 1.0.0 - Marzo 2026</p>
        <p className="mt-1">Desarrollado con fines académicos</p>
      </div>
    </div>
  );
}

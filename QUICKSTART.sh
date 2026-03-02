#!/bin/bash
# ============================================================================
# QUICKSTART - Ejecutar TradingSignals AI Local (3 pasos)
# ============================================================================

echo "🚀 TradingSignals AI - Quick Start"
echo "=================================="
echo ""

# PASO 1: Instalar dependencias
echo "📦 PASO 1: Instalando dependencias Python..."
echo "================================================"
cd api
pip install -r requirements.txt
echo ""
echo "✅ Dependencias instaladas"
echo ""

# PASO 2: Terminal 1 - API
echo "🔧 PASO 2: Iniciando API..."
echo "================================================"
echo ""
echo "Ejecuta esto en TERMINAL 1:"
echo "  cd api"
echo "  python main.py"
echo ""
echo "⏳ Espera a que veas:"
echo "  'Uvicorn running on http://0.0.0.0:8000'"
echo ""

# PASO 3: Terminal 2 - Frontend
echo "💻 PASO 3: Iniciando Frontend..."
echo "================================================"
echo ""
echo "Ejecuta esto en TERMINAL 2:"
echo "  npm run dev"
echo ""
echo "⏳ Espera a que veas:"
echo "  'Local: http://localhost:5173'"
echo ""

# PASO 4: Abrir navegador
echo "🌐 PASO 4: Abre en tu navegador:"
echo "================================================"
echo "  http://localhost:5173"
echo ""

# PASO 5: Enviar datos (Opcional)
echo "📤 PASO 5 (Opcional): Enviar datos simulados..."
echo "================================================"
echo "  Ejecuta en TERMINAL 3:"
echo "  cd api"
echo "  python send_data.py"
echo ""

echo "✅ ¡LISTO!"
echo "=================================="

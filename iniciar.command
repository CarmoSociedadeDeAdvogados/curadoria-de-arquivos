#!/bin/bash
cd "$(dirname "$0")"
echo "Iniciando Curadoria de Arquivos..."
echo "Acesse no Safari: http://127.0.0.1:5000"
echo ""
echo "NÃO feche esta janela enquanto estiver usando o app."
echo "Para parar o servidor, feche esta janela ou pressione Control+C."
echo ""
python3 app.py

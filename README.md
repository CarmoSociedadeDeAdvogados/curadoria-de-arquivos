# Curadoria de Arquivos

Aplicação web para comparar e limpar arquivos `.CR3` (RAW Canon) que não possuem um `.JPG` correspondente.

## Uso

1. Instalar dependências:
```bash
pip3 install flask send2trash
```

2. Iniciar o servidor:
```bash
python3 app.py
```

3. Abrir no Safari: `http://localhost:5000`

4. Configurar o caminho da pasta SG 2026 no iCloud Drive

5. Selecionar mês e cliente, analisar e excluir os .CR3 órfãos

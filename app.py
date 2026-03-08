import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from send2trash import send2trash

app = Flask(__name__)
CONFIG_FILE = Path(__file__).parent / "config.json"


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"base_path": ""}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())


@app.route("/api/config", methods=["POST"])
def set_config():
    data = request.get_json()
    base_path = data.get("base_path", "").strip()
    if not base_path:
        return jsonify({"error": "Caminho não pode ser vazio"}), 400
    expanded = os.path.expanduser(base_path)
    if not os.path.isdir(expanded):
        return jsonify({"error": f"Pasta não encontrada: {expanded}"}), 400
    config = {"base_path": expanded}
    save_config(config)
    return jsonify(config)


@app.route("/api/meses")
def listar_meses():
    config = load_config()
    base = config.get("base_path", "")
    if not base or not os.path.isdir(base):
        return jsonify({"error": "Caminho base não configurado"}), 400
    meses = sorted(
        d for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d)) and not d.startswith(".")
    )
    return jsonify(meses)


@app.route("/api/clientes/<mes>")
def listar_clientes(mes):
    config = load_config()
    base = config.get("base_path", "")
    mes_path = os.path.join(base, mes)
    if not os.path.isdir(mes_path):
        return jsonify({"error": f"Pasta do mês não encontrada: {mes}"}), 400
    clientes = sorted(
        d for d in os.listdir(mes_path)
        if os.path.isdir(os.path.join(mes_path, d)) and not d.startswith(".")
    )
    return jsonify(clientes)


@app.route("/api/analisar/<mes>/<cliente>")
def analisar(mes, cliente):
    config = load_config()
    base = config.get("base_path", "")
    cliente_path = os.path.join(base, mes, cliente)
    if not os.path.isdir(cliente_path):
        return jsonify({"error": "Pasta da cliente não encontrada"}), 400

    jpgs = {}
    cr3s = {}

    for root, _, files in os.walk(cliente_path):
        for f in files:
            name_lower = f.lower()
            base_name = os.path.splitext(f)[0].upper()
            full_path = os.path.join(root, f)
            if name_lower.endswith(".jpg") or name_lower.endswith(".jpeg"):
                jpgs[base_name] = full_path
            elif name_lower.endswith(".cr3"):
                cr3s[base_name] = full_path

    orfaos = []
    for base_name, path in sorted(cr3s.items()):
        if base_name not in jpgs:
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            orfaos.append({
                "nome": os.path.basename(path),
                "caminho": path,
                "tamanho": size,
            })

    return jsonify({
        "total_jpg": len(jpgs),
        "total_cr3": len(cr3s),
        "total_orfaos": len(orfaos),
        "orfaos": orfaos,
    })


@app.route("/api/excluir", methods=["POST"])
def excluir():
    data = request.get_json()
    arquivos = data.get("arquivos", [])
    if not arquivos:
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    excluidos = []
    erros = []
    for caminho in arquivos:
        if not os.path.isfile(caminho):
            erros.append(f"Arquivo não encontrado: {caminho}")
            continue
        if not caminho.lower().endswith(".cr3"):
            erros.append(f"Arquivo não é .CR3: {caminho}")
            continue
        try:
            send2trash(caminho)
            excluidos.append(caminho)
        except Exception as e:
            erros.append(f"Erro ao excluir {caminho}: {e}")

    return jsonify({
        "excluidos": len(excluidos),
        "erros": erros,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)

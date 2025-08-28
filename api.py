from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
from pathlib import Path
from etl import ETLClima
import os

app = Flask(__name__)
CORS(app)

ARQUIVO = Path("clima.csv")

API_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.environ.get("API_KEY", "9990c81e5c84b63299f7503255f90592")
etl = ETLClima(API_URL, API_KEY)

def obter_cidades():
    if ARQUIVO.exists():
        df = pd.read_csv(ARQUIVO)
        return df["cidade"].dropna().unique().tolist()
    return []

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>API de Clima</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f4f8;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 50px;
        }
        h1 {
            color: #1e90ff;
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        input[type="text"] {
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #ccc;
            margin-right: 10px;
        }
        button {
            padding: 8px 15px;
            border-radius: 5px;
            border: none;
            background-color: #1e90ff;
            color: #fff;
            cursor: pointer;
        }
        button:hover {
            background-color: #0b6fc2;
        }
        #resultado {
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: 300px;
        }
        li {
            margin-bottom: 5px;
        }
        p {
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>🌤 API de Clima</h1>
    <form id="formClima">
        <label for="cidade">Digite o nome da cidade:</label>
        <input type="text" id="cidade" name="cidade" required>
        <button type="submit">Consultar</button>
    </form>
    <div id="resultado"></div>

    <script>
    document.getElementById("formClima").addEventListener("submit", async function(e) {
        e.preventDefault();
        const cidade = document.getElementById("cidade").value;
        const resposta = await fetch(`/clima?cidade=${cidade}`);
        const dados = await resposta.json();
        let html = "";
        if(dados.erro){
            html = `<p style="color:red">${dados.erro}</p>`;
        } else {
            html = `
                <h2>Clima em ${dados.cidade}</h2>
                <ul>
                    <li>Temperatura: ${dados.temperatura}°C</li>
                    <li>Umidade: ${dados.umidade}%</li>
                    <li>Coleta em: ${dados.data_coleta}</li>
                </ul>
            `;
        }
        document.getElementById("resultado").innerHTML = html;
    });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/clima", methods=["GET"])
def clima():
    cidade = request.args.get("cidade")
    if not cidade:
        return jsonify({"erro": "Passe ?cidade=NomeDaCidade"}), 400

    dados_json = etl.extrair(cidade)
    dados = etl.transformar(dados_json)

    if not dados:
        return jsonify({"erro": "Não foi possível obter dados dessa cidade"}), 404

    etl.carregar(dados)
    return jsonify(dados)

@app.route("/historico", methods=["GET"])
def historico():
    cidade = request.args.get("cidade")
    if not cidade:
        return jsonify({"erro": "Passe ?cidade=NomeDaCidade"}), 400
    if not ARQUIVO.exists():
        return jsonify({"erro": "Nenhum dado coletado ainda."}), 404

    df = pd.read_csv(ARQUIVO)
    dados = df[df["cidade"].str.lower() == cidade.lower()].tail(10)

    if dados.empty:
        return jsonify({"erro": "Cidade não encontrada"}), 404
    return jsonify(dados.to_dict(orient="records"))

@app.route("/buscar", methods=["GET"])
def buscar():
    cidade = request.args.get("cidade")
    if not cidade:
        return jsonify({"erro": "Passe ?cidade=NomeDaCidade"}), 400

    dados_json = etl.extrair(cidade)
    dados = etl.transformar(dados_json)

    if not dados:
        return jsonify({"erro": f"Não foi possível obter dados para {cidade}"}), 404

    etl.carregar(dados)
    return jsonify(dados)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

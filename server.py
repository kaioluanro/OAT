from flask import Flask, request, jsonify
import pandas as pd
import threading
import json
from utils import salve_olhc

app = Flask(__name__)
@app.route('/nojson', methods=['POST'])
def receber_dados():
    data = request.get_json()  # Recebe JSON
    print(data)  # Exibe os dados no servidor
    return None

@app.route("/", methods=["POST"])
def get_dados():
    try:
        # Carrega o arquivo JSON
        with open('dadostoESP32.json', 'r', encoding='utf-8') as file:
            dados = json.load(file)
        
        # Resposta com o JSON carregado
        return jsonify({
            "status": "success",
            "mensagem":"OK!",
            "data": dados
        }), 200  # Código HTTP 200 (OK)

    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": "Arquivo JSON nao encontrado!"
        }), 404  # Código HTTP 404 (Not Found)

    except json.JSONDecodeError:
        return jsonify({
            "status": "error",
            "message": "Erro na leitura do JSON!"
        }), 500  # Código HTTP 500 (Internal Server Error)


if __name__ == "__main__":
    threading.Thread(target=salve_olhc, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
    
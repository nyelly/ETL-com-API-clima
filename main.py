import os
import schedule
import time
from threading import Thread
from datetime import datetime
from api import app, etl
from flask_cors import CORS

CORS(app)

def obter_cidades():
    return etl.listar_cidades()

def coletar_dados():
    cidades = obter_cidades()

    if not cidades:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Nenhuma cidade encontrada para atualizar.")
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Coletando dados de {len(cidades)} cidades...")

    for cidade in cidades:
        etl.executar(cidade)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Coleta concluída.\n")

def iniciar_agendador():
    schedule.every(5).minutes.do(coletar_dados)

    coletar_dados()

    while True:
        schedule.run_pending()
        time.sleep(3)

if __name__ == "__main__":
    Thread(target=iniciar_agendador, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

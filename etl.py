import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import pytz
import locale

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
except:
    locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")

class ETLClima:
    def __init__(self, api_url, api_key, arquivo="clima.csv"):
        self.api_url = api_url
        self.api_key = api_key
        self.arquivo = Path(arquivo)

    def extrair(self, cidade):
        url = f"{self.api_url}?q={cidade},BR&appid={self.api_key}&units=metric&lang=pt_br"
        resposta = requests.get(url)
        if resposta.status_code != 200:
            print(f"Erro ao coletar {cidade}: {resposta.text}")
            return None
        return resposta.json()

    def formatar_data_coleta(self):
        """Formata a data da coleta para português com fuso horário do Brasil"""
        fuso_brasil = pytz.timezone("America/Sao_Paulo")
        agora = datetime.now(fuso_brasil)
        return agora.strftime("%A, %d de %B de %Y %H:%M:%S").capitalize()

    def transformar(self, dados_json):
        if not dados_json or "main" not in dados_json:
            return None
        return {
            "cidade": dados_json.get("name", "Desconhecida"),
            "temperatura": dados_json["main"].get("temp"),
            "umidade": dados_json["main"].get("humidity"),
            "data_coleta": self.formatar_data_coleta()
        }

    def carregar(self, dados):
        df_novo = pd.DataFrame([dados])
        if self.arquivo.exists():
            df_antigo = pd.read_csv(self.arquivo)
            df = pd.concat([df_antigo, df_novo], ignore_index=True)
        else:
            df = df_novo
        df.to_csv(self.arquivo, index=False)
        print(f"Dados salvos em {self.arquivo}")

    def listar_cidades(self):
        """Lê o arquivo clima.csv e retorna a lista de cidades salvas"""
        if self.arquivo.exists():
            df = pd.read_csv(self.arquivo)
            return df["cidade"].dropna().unique().tolist()
        return []

    def executar(self, cidade):
        dados_json = self.extrair(cidade)
        dados = self.transformar(dados_json)
        if dados:
            self.carregar(dados)

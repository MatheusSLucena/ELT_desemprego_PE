import requests
import json
import os
import subprocess
from dotenv import load_dotenv
from src.extract import Extract
from src.load import Load
from src.transform import Transform

load_dotenv()
url_neon = os.getenv("URL_NEON")
tem_neon = bool(url_neon and url_neon.strip())

transformer = Transform()
extractor = Extract()
loader = Load()
 
print("\n--- Etapa 1: Extraindo dados do IBGE ---")
response = extractor.extract_pnadc()
data = response.json()

print("\n--- Etapa 2: Salvando dados em JSON ---")
loader.load_json("dados_desemprego", data)

print("\n--- Etapa 3: Transformando dados ---")
with open("dados_desemprego.json", 'r', encoding='UTF-8') as f:
    data = json.load(f)
clean_data = transformer.transform_pnadc(data)
print("Dados transformados com sucesso!")

print("\n--- Etapa 4: Salvando dados no Banco de Dados ---")
loader.load_sqlite(clean_data, "desemprego_PE")

if tem_neon:
    loader.load_neon(clean_data, "desemprego_PE")
    print("\n--- Etapa 5: Extraindo dados do Neon para visualização ---")
    df = extractor.extract_collection_from_neon("desemprego_PE")
    print(df.dtypes)
else:
    print("Aviso: 'URL_NEON' não encontrada no .env. Usando apenas o SQLite (IBGE.db).")

print("\n--- Etapa 6: Iniciando o Dashboard Streamlit ---")
subprocess.run(["streamlit", "run", "src/app.py"])
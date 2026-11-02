import requests
import time
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd


load_dotenv()
# Tira dados de algum lugar
class Extract():

    def __init__(self):
        self.access_neon = os.getenv("URL_NEON")
        if self.access_neon and self.access_neon.strip():
            self.neon_engine = create_engine(self.access_neon, echo=False, pool_size=5, pool_pre_ping=True)
        else:
            self.neon_engine = None

    def extract_pnadc(self):
        "Extrai os dados sobre desemprego da API do IBGE"

        url = "https://servicodados.ibge.gov.br/api/v3/agregados/4093/periodos/201201|201202|201203|201204|201301|201302|201303|201304|201401|201402|201403|201404|201501|201502|201503|201504|201601|201602|201603|201604|201701|201702|201703|201704|201801|201802|201803|201804|201901|201902|201903|201904|202001|202002|202003|202004|202101|202102|202103|202104|202201|202202|202203|202204|202301|202302|202303|202304|202401|202402|202403|202404|202501|202502|202503|202504|202601|202602/variaveis/1641|4088|4090|4092|4094|4096|4097|4098|4099|12466|4723?localidades=N3[26]&classificacao=2[6794]"
        max_retries = 5
        wait = 2
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url, timeout=10)
        
                if response.status_code == 200:
                    return response
        
                print(f"Attempt {attempt}: got {response.status_code}")
        
            except requests.exceptions.RequestException as e:
                # Network errors, timeouts, connection refused, etc.
                print(f"Attempt {attempt}: {e}")
        
            time.sleep(wait * attempt)  # waits 2s, 4s, 6s... (simple backoff)
        
        raise RuntimeError(f"Failed after {max_retries} attempts: {url}")
    


    def extract_collection_from_neon(self, collection_name):
        df = pd.read_sql(f'SELECT * FROM "{collection_name}" ORDER BY periodo',con=self.neon_engine,parse_dates=['periodo'])
        #df["periodo"] = df["periodo"].dt.to_period("Q-DEC")
        self.neon_engine.dispose()
        return df
        


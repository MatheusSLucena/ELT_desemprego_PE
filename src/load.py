import json
from dotenv import load_dotenv
from sqlalchemy import create_engine,types
import os
import pandas as pd
import sqlite3


load_dotenv()

# Coloca dados em algum lugar
class Load():
    def __init__(self):
        self.access_neon = os.getenv("URL_NEON")
        self.neon_engine = create_engine(self.access_neon,echo=False,pool_size=5,pool_pre_ping=True)

    def load_json(self, nome_doc ,data):
        with open(f"{nome_doc}.json",'w',encoding='utf-8') as file:
            json.dump(data,file,indent=2)
        print(f"Dados salvos no SQLite com sucesso em JSON com o nome '{nome_doc}'")
        
    def load_sqlite(self, data: pd.DataFrame, nome_tabela: str):
        for col in data.columns:
            if isinstance(data[col].dtype, pd.PeriodDtype):
                data[col] = data[col].astype(str)
        connect = sqlite3.connect("IBGE.db")
        try:
            data.to_sql(nome_tabela, con=connect, if_exists="replace", index=False)
            print(f"Dados salvos no SQLite com sucesso na tabela '{nome_tabela}'")
        finally:
            connect.close()

    def load_neon(self,df:pd.DataFrame,nome_tabela):
        # O Postgres não aceita periodo como trimestre, então vamos formatar a coluna como DATE
        if isinstance(df["periodo"].dtype, pd.PeriodDtype):
            df["periodo"] = df["periodo"].dt.to_timestamp()
        else:  # se ainda estiver como texto "2012Q1"
            df["periodo"] = pd.PeriodIndex(df["periodo"], freq="Q-DEC").to_timestamp()

        df.to_sql(
            f'{nome_tabela}',
            con=self.neon_engine,
            if_exists="replace",
            index=False,
            dtype={"periodo": types.Date()},   # cria a coluna como DATE no Postgres
        )

        self.neon_engine.dispose()
        print(f"Dados salvos no Neon com sucesso na tabela '{nome_tabela}'!")
    
import pandas as pd

#Pega algum tipo de dado e transforma em outro
class Transform:    

    def __init__(self):
        pass

    def transform_pnadc(self,data):
        # Navega pela resposta Json e separa os difentes dados extraidos.
        total = data[0]["resultados"][0]["series"][0]["serie"]
        forca = data[1]["resultados"][0]["series"][0]["serie"]
        ocupadas = data[2]["resultados"][0]["series"][0]["serie"]
        desocupadas = data[3]["resultados"][0]["series"][0]["serie"]
        fora_da_forca = data[4]["resultados"][0]["series"][0]["serie"]
        forca_taxa_participacao = data[5]["resultados"][0]["series"][0]["serie"]
        nivel_de_ocupacao = data[6]["resultados"][0]["series"][0]["serie"]
        nivel_de_desocupacao = data[7]["resultados"][0]["series"][0]["serie"]
        taxa_de_desocupacao = data[8]["resultados"][0]["series"][0]["serie"]
        taxa_de_informalidade = data[9]["resultados"][0]["series"][0]["serie"]
        ocupadas_em_informalidade = data[10]["resultados"][0]["series"][0]["serie"]

        #Transforma as datas para organizar todos os dados pelos períodos
        df_total = self.JSON_to_df(total,"total")
        df_forca = self.JSON_to_df(forca,"forca")
        df_ocupadas = self.JSON_to_df(ocupadas,"ocupadas")
        df_desocupadas = self.JSON_to_df(desocupadas,"desocupadas")
        df_fora_da_forca = self.JSON_to_df(fora_da_forca,"fora_da_forca")
        df_forca_taxa_participacao = self.JSON_to_df(forca_taxa_participacao,"forca_taxa_participacao")
        df_nivel_de_ocupacao = self.JSON_to_df(nivel_de_ocupacao,"nivel_de_ocupacao")
        df_nivel_de_desocupacao = self.JSON_to_df(nivel_de_desocupacao,"nivel_de_desocupacao")
        df_taxa_de_desocupacao = self.JSON_to_df(taxa_de_desocupacao,"taxa_de_desocupacao")
        df_taxa_de_informalidade = self.JSON_to_df(taxa_de_informalidade,"taxa_de_informalidade")
        df_ocupadas_em_informalidade = self.JSON_to_df(ocupadas_em_informalidade,"ocupadas_em_informalidade")


        #Combina todas as DataFrames em uma só
        df = df_total.merge(df_forca,on="periodo",how="left")
        df = df.merge(df_ocupadas,on="periodo",how="left")
        df = df.merge(df_desocupadas,on="periodo",how="left")
        df = df.merge(df_fora_da_forca,on="periodo",how="left")
        df = df.merge(df_forca_taxa_participacao,on="periodo",how="left")
        df = df.merge(df_nivel_de_ocupacao,on="periodo",how="left")
        df = df.merge(df_nivel_de_desocupacao,on="periodo",how="left")
        df = df.merge(df_taxa_de_desocupacao,on="periodo",how="left")
        df  = df.merge(df_taxa_de_informalidade,on="periodo",how="left")
        df = df.merge(df_ocupadas_em_informalidade,on="periodo",how="left")

        df = df.rename(columns={'forca' : 'forca_de_trabalho'})

        #Lista colunas que precisam trocar de tipo de dado
        taxas = ['forca_taxa_participacao', 'nivel_de_ocupacao',
            'nivel_de_desocupacao', 'taxa_de_desocupacao', 'taxa_de_informalidade']
        inteiros = ['total', 'forca_de_trabalho', 'ocupadas', 'desocupadas',
            'fora_da_forca', 'ocupadas_em_informalidade']

        #Concerta o tipo de dado das colunas
        for col in taxas:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        for col in inteiros:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        return df

    @staticmethod
    def JSON_to_df(series,series_name):
        df = pd.DataFrame.from_dict(data=series,orient='index',columns=[series_name])
        df.index.name = 'periodo'
        df = df.reset_index()
        df['ano'] = df['periodo'].str[:4]
        df['tri'] = df['periodo'].str[-1:]
        df['periodo'] = pd.PeriodIndex(df['ano']+'Q'+df['tri'], freq='Q')
        df = df.drop(labels=['ano','tri'],axis='columns')
        return df
    
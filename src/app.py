import os
import sqlite3
from dotenv import load_dotenv
import streamlit as st
import plotly.express as px
import pandas as pd
from extract import Extract

load_dotenv()

st.set_page_config(page_title="Dashboard IBGE - PE", layout="wide")
st.title("Estrutura do Desemprego em Pernambuco (2022 - Atual)")

@st.cache_data
def load_data():
    url_neon = os.getenv("URL_NEON")
    
    if url_neon and url_neon.strip():
        extractor = Extract()
        df = extractor.extract_collection_from_neon("desemprego_PE")
    else:
        # Fallback para o banco local SQLite (IBGE.db)
        conn = sqlite3.connect("IBGE.db")
        try:
            df = pd.read_sql('SELECT * FROM "desemprego_PE" ORDER BY periodo', con=conn)
        finally:
            conn.close()
        
        # Formata a coluna periodo exatamente como no retorno do Neon (Period[Q-DEC])
        df["periodo"] = pd.PeriodIndex(df["periodo"], freq="Q-DEC")
    
    # Filtra a partir de 2022Q1 considerando o tipo Period[Q-DEC]
    df = df[df['periodo'] >= '2022Q1'].copy()
    
    # Cria coluna como string (ex: "2022Q1") para renderização limpa no Plotly
    df['periodo_str'] = df['periodo'].astype(str)
    return df

def plot_1_composicao_pia(df: pd.DataFrame):
    """1. Composição da População em Idade de Trabalhar (Barras Agrupadas)"""
    fig = px.bar(
        df,
        x='periodo_str',
        y=['ocupadas', 'desocupadas', 'fora_da_forca'],
        barmode='group',
        title="1. Composição da População de 14 Anos ou Mais (PIA)",
        labels={
            'periodo_str': 'Trimestre',
            'value': 'Quantidade (Mil Pessoas)',
            'variable': 'Condição'
        },
        color_discrete_map={
            'ocupadas': '#00CC96',       # Verde vibrante
            'desocupadas': '#FF3366',    # Vermelho/Rosa intenso
            'fora_da_forca': '#636EFA'   # Azul/Roxo
        }
    )
    return fig

def plot_2_raiox_proporcional_pia(df: pd.DataFrame):
    """2. Raio-X Proporcional da População de 14 Anos ou Mais (Área 100% Empilhada)"""
    df_prop = df.dropna(subset=['ocupadas', 'ocupadas_em_informalidade', 'desocupadas', 'fora_da_forca']).copy()
    
    # Deriva o volume de ocupados formais para fechar os 100% da PIA sem sobreposição
    df_prop['ocupadas_formais'] = df_prop['ocupadas'] - df_prop['ocupadas_em_informalidade']

    fig = px.area(
        df_prop,
        x='periodo_str',
        y=['ocupadas_formais', 'ocupadas_em_informalidade', 'desocupadas', 'fora_da_forca'],
        groupnorm='percent',
        title="2. Raio-X Proporcional da População de 14 Anos ou Mais (100% Empilhado)",
        labels={
            'periodo_str': 'Trimestre',
            'value': 'Participação na PIA (%)',
            'variable': 'Grupo Populacional'
        },
        color_discrete_map={
            'ocupadas_formais': '#00CC96',          # Verde (Emprego Formal)
            'ocupadas_em_informalidade': '#FFA15A', # Laranja (Emprego Informal)
            'desocupadas': '#FF3366',               # Vermelho (Desempregados)
            'fora_da_forca': '#636EFA'              # Roxo/Azul (Fora da Força)
        }
    )
    fig.update_yaxes(ticksuffix="%")
    return fig

def plot_3_volume_ocupados_informais(df: pd.DataFrame):
    """3. Volume de Ocupados vs. Emprego na Informalidade (Barras Agrupadas)"""
    fig = px.bar(
        df,
        x='periodo_str',
        y=['ocupadas', 'ocupadas_em_informalidade'],
        barmode='group',
        title="3. Volume de Ocupados vs. Emprego na Informalidade",
        labels={
            'periodo_str': 'Trimestre',
            'value': 'Pessoas (Mil)',
            'variable': 'Categoria'
        },
        color_discrete_map={
            'ocupadas': '#00C3FF',                 # Azul elétrico
            'ocupadas_em_informalidade': '#FF3366' # Rosa/Vermelho intenso
        }
    )
    return fig

def plot_4_taxa_informalidade(df: pd.DataFrame):
    """4. Evolução da Taxa de Informalidade (%)"""
    fig = px.line(
        df,
        x='periodo_str',
        y='taxa_de_informalidade',
        markers=True,
        title="4. Evolução da Taxa de Informalidade (%)",
        labels={
            'periodo_str': 'Trimestre',
            'taxa_de_informalidade': 'Taxa de Informalidade (%)'
        }
    )
    fig.update_traces(
        line=dict(color='#FFD700', width=3),
        marker=dict(size=8)
    )
    return fig

def plot_5_dimensao_desemprego(df: pd.DataFrame):
    """5. Dimensão Real do Desemprego: Taxa na Força vs. Nível na População"""
    df_melted = df.melt(
        id_vars=['periodo_str', 'forca_de_trabalho', 'total'],
        value_vars=['taxa_de_desocupacao', 'nivel_de_desocupacao'],
        var_name='Indicador',
        value_name='Percentual'
    )

    fig = px.line(
        df_melted,
        x='periodo_str',
        y='Percentual',
        color="Indicador",
        markers=True,
        hover_data=['forca_de_trabalho', 'total'],
        title="5. Taxa de Desocupação (na Força) vs. Nível de Desocupação (na PIA)",
        labels={
            'periodo_str': 'Trimestre',
            'Percentual': 'Taxa (%)',
            'forca_de_trabalho': 'Força de Trabalho (Mil)',
            'total': 'População 14+ (Mil)'
        },
        color_discrete_map={
            'taxa_de_desocupacao': '#FF5733',
            'nivel_de_desocupacao': '#33C1FF'
        }
    )
    return fig

def plot_6_saldo_liquido_trimestral(df: pd.DataFrame):
    """6. Saldo Líquido Trimestral de Vagas e Desemprego (Barras Divergentes)"""
    df_calc = df.dropna(subset=['ocupadas', 'desocupadas']).copy()
    df_calc['saldo_ocupadas'] = df_calc['ocupadas'].diff()
    df_calc['saldo_desocupadas'] = df_calc['desocupadas'].diff()
    df_calc = df_calc.dropna(subset=['saldo_ocupadas', 'saldo_desocupadas'])

    fig = px.bar(
        df_calc,
        x='periodo_str',
        y=['saldo_ocupadas', 'saldo_desocupadas'],
        barmode='group',
        title="6. Saldo Líquido Trimestral: Variação de Ocupados vs. Desocupados",
        labels={
            'periodo_str': 'Trimestre',
            'value': 'Variação no Trimestre (Mil Pessoas)',
            'variable': 'Indicador'
        },
        color_discrete_map={
            'saldo_ocupadas': '#00CC96',    # Verde para variação de ocupados
            'saldo_desocupadas': '#FF3366'  # Vermelho para variação de desocupados
        }
    )
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.6)
    return fig

# --- Execução do Layout Principal ---
df = load_data()

# Linha 1: Gráficos 1 e 2 (Composição Absoluta e Proporcional da PIA) lado a lado
st.markdown("""
    ### Composição da população em relação à força de trabalho.
    Começamos nossa análise explorando a relação da nossa força de trabalho com a população total. 
    Vemos que a nossa força de trabalho se mantém em um equilíbrio em relação a população fora da força, que representa pessoas como
    adolescentes estudantes, idosos, pessoas em situação de rua e etc. A nossa força de trabalho é a força motríz do nosso paíz, e esse equilíbrio mantém 
    nossa balança comercial balanceada tanto quanto nossa indústria.
""")
col_pia1, col_pia2 = st.columns(2)
with col_pia1:
    st.plotly_chart(plot_1_composicao_pia(df), width='stretch')

with col_pia2:
    st.plotly_chart(plot_2_raiox_proporcional_pia(df), width='stretch')

# Linha 2: Gráficos 3 e 4 (Decomposição da Informalidade) lado a lado
st.markdown(""" 
    ### Emprego formal vs informal
    Quantas pessoas das pessoas empregadas estão trabalhando em emprego informal? Essa é uma pergunta que reflete a saúde dos empregos no Brasil,
    quanto mais caro fica para contratar, mais pessoas tendem a adotar empregos informais para sobreviver. Mas vemos que esse equilíbrio
    se mantém estável. Variando somente 4% ao longo dos últimos 4 anos.
""")
col_inf1, col_inf2 = st.columns(2)
with col_inf1:
    st.plotly_chart(plot_3_volume_ocupados_informais(df), width='stretch')

with col_inf2:
    st.plotly_chart(plot_4_taxa_informalidade(df), width='stretch')

# Linha 3: Gráfico 5 (Dimensão Real do Desemprego) em largura total
st.markdown("""
    ### Composição da população desempregada.
    Comparação entre **pessoas na força de trabalho procurando emprego e não encontram** (taxa_de_desocupação), e **pessoas desocupadas que são capazes de trabalhar** (nível de desocupação).
    A correlação positiva da variação das duas séries mostra que as pessoas que deixam de ser desocupadas não estão
    desistindo de trabalhar, e sim encontrando ocupação.
""")
st.plotly_chart(plot_5_dimensao_desemprego(df), width='stretch')

# Linha 4: Gráfico 6 (Saldo Líquido Trimestral) em largura total
st.markdown("""
    ### Diferença semestral entre criação de empregos e novos desempregados.
    Quais trimestres registraram os maiores choques de destruição ou criação líquida de postos de trabalho e de novos desempregados em relação ao trimestre imediatamente anterior? 
    Respondendo essa pergunta conseguimos olhar ao longo do tempo a evolução entre pessoas encontrando emprego e pessoas sendo demitidas.
""")
st.plotly_chart(plot_6_saldo_liquido_trimestral(df), width='stretch')

# Conclusões

st.markdown(""" ### Conclusões
    Com as comparações realizadas podemos ver que o mercado de trabalho em pernambuco se manteve estável nos últimos 4 anos, 
    mostrando até um leve avanço contra o desemprego. Tivemos uma queda total de 7,6% no desemprego formal. E a nossa comparação entre a taxa de desocupação e 
    nível de desocupação mostra que essa queda foi saudável, essas pessoas estão se integrando na força de trabalho.
 """)
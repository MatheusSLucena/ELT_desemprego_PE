# Pipeline ETL e Dashboard Analítico: Estrutura do Desemprego em Pernambuco (IBGE / PNAD Contínua)

## 1. Descrição do Projeto
Este projeto de Engenharia e Ciência de Dados realiza a extração, transformação e carregamento (ETL) de dados históricos da Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua - Agregado 4093), disponibilizados pela API de Serviço de Dados do IBGE, com foco no estado de Pernambuco (código UF 26). 

Após o processamento e armazenamento em banco de dados relacional, o pipeline inicia automaticamente uma aplicação web interativa construída com Streamlit e Plotly. O dashboard apresenta análises visuais sobre a dinâmica do mercado de trabalho pernambucano pós-pandemia (a partir de 2022), investigando a composição da População em Idade de Trabalhar (PIA), a relação entre emprego formal e informal, o comportamento da desocupação e o saldo líquido trimestral de vagas.

---

## 2. Arquitetura do Pipeline ETL e Estrutura de Arquivos

A estrutura modular do projeto está dividida da seguinte forma:

Desemprego_pernambuco/
│
├── main.py                              # Orquestrador do pipeline ETL e inicializador do Streamlit
├── IBGE.db                              # Banco de dados relacional local (SQLite)
├── dados_desemprego.json                # Backup local dos dados brutos extraídos da API
├── variaveis_ibge_pnad_pernambuco.xlsx  # Dicionário de variáveis do projeto
├── .env                                 # (Opcional) Variáveis de ambiente com a string URL_NEON
└── src/
    ├── extract.py                       # Classe Extract: requisições à API do IBGE e leitura do banco
    ├── transform.py                     # Classe Transform: limpeza, tipagem e modelagem com Pandas
    ├── load.py                          # Classe Load: persistência em JSON, SQLite e PostgreSQL (Neon)
    └── app.py                           # Aplicação web e visualizações de dados (Streamlit + Plotly)

### Etapas do Pipeline (`main.py`):
1. **Extract (`src/extract.py`)**: Realiza requisições HTTP GET na API v3 de Agregados do IBGE com política de *retry* e *backoff* exponencial para garantir resiliência contra instabilidades de rede. Extrai 11 variáveis trimestrais relativas a pessoas de 14 anos ou mais em Pernambuco.
2. **Backup Bruto (`src/load.py`)**: Salva o payload original da API no arquivo `dados_desemprego.json`.
3. **Transform (`src/transform.py`)**: Desaninha a estrutura JSON, converte os identificadores de período para objetos trimestrais (`PeriodIndex` do Pandas), unifica as 11 séries temporais em um único DataFrame e aplica a tipagem estrita (`Int64` para contagens populacionais em milhares e `float` para taxas percentuais).
4. **Load (`src/load.py`)**: Carrega a tabela tratada `desemprego_PE` no banco local SQLite (`IBGE.db`) e, caso configurada, também no banco em nuvem PostgreSQL (NeonDB), convertendo os períodos trimestrais para o tipo `DATE`.
5. **Visualização (`src/app.py`)**: Inicia automaticamente o servidor do Streamlit ao final do script principal.

---

## 3. O Dashboard Analítico (`src/app.py`)

O site gerado ao final da execução apresenta um estudo visual guiado com 6 gráficos interativos:
* **Gráfico 1 - Composição da População de 14 Anos ou Mais (Barras Agrupadas)**: Compara o volume absoluto de pessoas ocupadas, desocupadas e fora da força de trabalho.
* **Gráfico 2 - Raio-X Proporcional da PIA (Área 100% Empilhada)**: Demonstra a participação percentual exata de ocupados formais, ocupados informais, desocupados e inativos dentro da população total em idade ativa.
* **Gráfico 3 - Volume de Ocupados vs. Emprego na Informalidade (Barras Agrupadas)**: Confronta o total de trabalhadores empregados com a parcela que atua na informalidade.
* **Gráfico 4 - Evolução da Taxa de Informalidade (Linha)**: Acompanha a estabilidade e as oscilações percentuais da informalidade ao longo dos trimestres.
* **Gráfico 5 - Taxa de Desocupação vs. Nível de Desocupação (Múltiplas Linhas)**: Analisa se a redução do desemprego decorre da efetiva absorção pelo mercado de trabalho ou da saída de pessoas da força de trabalho.
* **Gráfico 6 - Saldo Líquido Trimestral (Barras Divergentes)**: Exibe a criação ou destruição líquida de vagas e o fluxo de novos desempregados em relação ao trimestre imediatamente anterior.

---

## 4. Bibliotecas e Tecnologias Utilizadas

* **Python 3.10+**
* **Requests**: Consumo da API REST do IBGE.
* **Pandas**: Manipulação, limpeza, tipagem e agregação de séries temporais.
* **SQLAlchemy & Psycopg2**: ORM e driver para conexão e persistência no PostgreSQL (NeonDB).
* **SQLite3**: Persistência relacional local nativa.
* **Python-dotenv**: Gerenciamento de variáveis de ambiente e credenciais seguras.
* **Streamlit**: Construção do web app e servidor de dados interativo.
* **Plotly Express**: Geração de gráficos interativos e responsivos.

---

## 5. Configuração do Banco de Dados (Funcionamento Híbrido: SQLite vs. NeonDB)

O projeto conta com um mecanismo automático de detecção de ambiente para facilitar o uso tanto localmente (por recrutadores ou desenvolvedores que clonarem o repositório) quanto conectado à nuvem:

* **Modo Local Padrão (Sem `.env`)**: Se nenhum arquivo `.env` for configurado (ou se a variável `URL_NEON` estiver vazia), o pipeline salvará os dados transformados exclusivamente no banco local SQLite (`IBGE.db`), e o dashboard em Streamlit consumirá os dados diretamente desse arquivo local.
* **Modo Nuvem PostgreSQL (Com `.env` e `URL_NEON`)**: Se você criar um arquivo `.env` na raiz do projeto contendo uma string de conexão válida para o NeonDB (PostgreSQL), o `main.py` ativará automaticamente o upload dos dados para o banco na nuvem, e a função `load_data()` do `src/app.py` passará a extrair os dados diretamente do NeonDB para alimentar os gráficos do site.

Exemplo de configuração do arquivo `.env` na raiz do projeto:
```env
URL_NEON="postgresql+psycopg2://usuario:senha@ep-exemplo.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

---

## 6. Como Executar o Projeto

### Passo 1: Clonar o repositório
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd Desemprego_pernambuco
```

### Passo 2: Criar um ambiente virtual e instalar as dependências
```bash
python -m venv .venv

# Ativar no Windows:
.venv\Scripts\activate

# Ativar no Linux/macOS:
source .venv/bin/activate

# Instalar pacotes necessários:
pip install requests pandas sqlalchemy psycopg2-binary python-dotenv streamlit plotly
```

### Passo 3: (Opcional) Configurar o NeonDB
Caso deseje utilizar o PostgreSQL no Neon, crie o arquivo `.env` na raiz do projeto com a sua variável `URL_NEON`. Caso contrário, pule para o Passo 4 para rodar via SQLite.

### Passo 4: Executar o Pipeline e Abrir o Site
Execute o arquivo principal:
```bash
python main.py
```
O script executará todas as etapas da ETL no terminal e, ao finalizar, abrirá automaticamente uma aba no seu navegador padrão (geralmente em `http://localhost:8501`) exibindo o dashboard interativo.

Caso queira abrir apenas o dashboard posteriormente sem rodar a extração da API novamente, execute:
```bash
streamlit run src/app.py
```
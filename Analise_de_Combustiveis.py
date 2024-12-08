import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread 
import matplotlib.pyplot as plt

def tratar_coluna_numerica(df, coluna):

    df[coluna] = df[coluna].str.replace('.', '')

    df[coluna] = df[coluna].str.replace(',', '.')

    df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

    return df

def puxar_aba_simples(id_gsheet, nome_aba, nome_df):

    nome_credencial = st.secrets["CREDENCIAL_SHEETS"]
    credentials = service_account.Credentials.from_service_account_info(nome_credencial)
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = credentials.with_scopes(scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(id_gsheet)
    
    sheet = spreadsheet.worksheet(nome_aba)

    sheet_data = sheet.get_all_values()

    st.session_state[nome_df] = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])

    st.session_state[nome_df][['Veículo', 'Despesa', 'Item']] = st.session_state[nome_df][['Veículo', 'Despesa', 'Item']].astype(str)

    for index in range(len(st.session_state[nome_df])):

        if st.session_state[nome_df].at[index, 'Veículo']!='':

            veiculo = st.session_state[nome_df].at[index, 'Veículo']

        else:

            st.session_state[nome_df].at[index, 'Veículo'] = veiculo

    st.session_state[nome_df]['Data'] = pd.to_datetime(st.session_state[nome_df]['Data'], format='%d/%m/%Y %H:%M:%S')

    st.session_state[nome_df] = st.session_state[nome_df][st.session_state[nome_df]['Veículo']!='Total'].reset_index(drop=True)

    st.session_state[nome_df]['mes'] = st.session_state[nome_df]['Data'].dt.month

    st.session_state[nome_df]['ano'] = st.session_state[nome_df]['Data'].dt.year

    st.session_state[nome_df]['Veículo'] = st.session_state[nome_df]['Veículo'].replace('WL61(DESATIVADO)', 'WL61')

    st.session_state[nome_df]['Item'] = st.session_state[nome_df]['Item'].replace({'DIESEL S-10': 'DIESEL', 'Diesel comum': 'DIESEL', 'Diesel S10': 'DIESEL', 
                                                                                                    'Gasolina aditivada': 'GASOLINA', 'Gasolina comum': 'GASOLINA'})

    st.session_state.dict_tipos_veiculos = {'UTILITARIO': ['SN70', 'SN71', 'SN72', 'SN73', 'SN74', 'SN75', 'SN77', 'SN78', 'SN79'], 
                                            'BUGGY': ['BUGGY LUCK 01', 'BUGGY RYAN'],
                                            'JP': ['JP40', 'JP41', 'JP42'],
                                            'MM': ['MAMULENGO 1', 'MAMULENGO 2'],
                                            'VAN': ['I21', 'I80', 'I81', 'I82', 'I85', 'MA53', 'MA55', 'MA56', 'MA86', 'MA87', 'MA88', 'SP51', 'SP54', 'SP83', 'SP84'], 
                                            'SENIOR': ['S25', 'S26', 'S27', 'S28', 'S29', 'S30'], 
                                            'WL': ['WL60', 'WL61', 'WL62', 'WL63', 'WL64', 'WL65', 'WL66', 'WL67', 'WL68', 'WL69'],
                                            'LU': ['LU09', 'LU10', 'LU11', 'LU15', 'LU16', 'LU17'],
                                            'TA': ['TA04', 'TA09', 'TA10', 'TA11', 'TA12', 'TA13', 'TA14']}

    st.session_state[nome_df]['Tipo de Veículo'] = st.session_state[nome_df]['Veículo'].apply(mapear_tipo_veiculo)

    st.session_state[nome_df] = tratar_coluna_numerica(st.session_state[nome_df], 'Distância de abastecimento')

    st.session_state[nome_df] = tratar_coluna_numerica(st.session_state[nome_df], 'Quantidade')

def mapear_tipo_veiculo(item):

    for tipo, veiculos in st.session_state.dict_tipos_veiculos.items():

        if item in veiculos:

            return tipo
        
    return 'Desconhecido'

def filtro_excluir(df_abastecimentos, veiculos_excluir, coluna):

    if len(veiculos_excluir)>0:

        df_abastecimentos = df_abastecimentos[~df_abastecimentos[coluna].isin(veiculos_excluir)].reset_index(drop=True)

    return df_abastecimentos

def filtro_incluir(df_abastecimentos, veiculos_excluir, coluna):

    if len(veiculos_excluir)>0:

        df_abastecimentos = df_abastecimentos[df_abastecimentos[coluna].isin(veiculos_excluir)].reset_index(drop=True)

    return df_abastecimentos

def grafico_duas_linhas_numero(referencia, eixo_x, eixo_y_1, ref_1_label, eixo_y_2, ref_2_label, titulo):
    
    fig, ax = plt.subplots(figsize=(15, 8))
    
    plt.plot(referencia[eixo_x], referencia[eixo_y_1], label = ref_1_label, linewidth = 0.5, color = 'black')
    ax.plot(referencia[eixo_x], referencia[eixo_y_2], label = ref_2_label, linewidth = 0.5, color = 'blue')
    
    for i in range(len(referencia[eixo_x])):
        texto = str(int(referencia[eixo_y_1][i]))
        plt.text(referencia[eixo_x][i], referencia[eixo_y_1][i], texto, ha='center', va='bottom')
    for i in range(len(referencia[eixo_x])):
        texto = str(int(referencia[eixo_y_2][i]))
        plt.text(referencia[eixo_x][i], referencia[eixo_y_2][i], texto, ha='center', va='bottom')

    plt.title(titulo, fontsize=30)
    plt.xlabel('Ano/Mês')
    ax.legend(loc='lower right', bbox_to_anchor=(1.2, 1))
    st.pyplot(fig)
    plt.close(fig)

st.set_page_config(layout='wide')

st.title('Orçamento Luck JPA - 2025')

st.subheader('Análise de Combustíveis')

st.divider()

if not 'df_abastecimentos' in st.session_state:

    puxar_aba_simples('1K_2XjbklqLbchLoszdEo1H4iH14lUORmLOcSUcL3jpk', 'BD - Abastecimentos', 'df_abastecimentos')

ler_planilha = st.button('Puxar Dados Google Drive')

if ler_planilha:

    puxar_aba_simples('1K_2XjbklqLbchLoszdEo1H4iH14lUORmLOcSUcL3jpk', 'BD - Abastecimentos', 'df_abastecimentos')

df_abastecimentos = st.session_state.df_abastecimentos.groupby(['ano', 'mes', 'Veículo', 'Tipo de Veículo', 'Item'])[['Distância de abastecimento', 'Quantidade']].sum().reset_index()

row1 = st.columns(2)

with row1[0]:

    veiculos_excluir = st.multiselect('Excluir Veículos', sorted(df_abastecimentos['Veículo'].unique().tolist()), 
                                      default=['AMAROK', 'BALANÇO ALMOXARIFADO', 'BUGGY ALEXANDRE', 'GARAGEM', 'KOMBI KUARA', 'KOMBI MOVEL', 'MOTO ADM (BRANCA)', 'MOTO GARAGEM (VERMELHA)', 
                                               'NOVA SAVEIRO', 'RENEGADE', 'JARDINEIRA - V32'])

df_abastecimentos = filtro_excluir(df_abastecimentos, veiculos_excluir, 'Veículo')

with row1[1]:

    combustiveis = st.multiselect('Filtrar Combustíveis', sorted(df_abastecimentos['Item'].unique().tolist()), default=None)

df_abastecimentos = filtro_incluir(df_abastecimentos, combustiveis, 'Item')

with row1[0]:

    tipos_de_veiculos = st.multiselect('Filtrar Tipos de Veículos', sorted(df_abastecimentos['Tipo de Veículo'].unique().tolist()), default=None)

df_abastecimentos = filtro_incluir(df_abastecimentos, tipos_de_veiculos, 'Tipo de Veículo')

with row1[0]:

    veiculos = st.multiselect('Filtrar Veículos', sorted(df_abastecimentos['Veículo'].unique().tolist()), default=None)

df_abastecimentos = filtro_incluir(df_abastecimentos, veiculos, 'Veículo')

with row1[1]:

    excluir_anos = st.multiselect('Excluir Anos', [2019, 2020, 2021, 2022, 2023, 2024], default=None)

df_abastecimentos = filtro_excluir(df_abastecimentos, excluir_anos, 'ano')

with row1[1]:

    filtrar_anos = st.multiselect('Filtrar Anos', [2019, 2020, 2021, 2022, 2023, 2024], default=None)

df_abastecimentos = filtro_incluir(df_abastecimentos, filtrar_anos, 'ano')

with row1[1]:

    filtrar_meses = st.multiselect('Filtrar Meses', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], default=None)

df_abastecimentos = filtro_incluir(df_abastecimentos, filtrar_meses, 'mes')

df_abastecimentos_mensal = df_abastecimentos.groupby(['ano', 'mes'])[['Distância de abastecimento', 'Quantidade']].sum().reset_index()

df_abastecimentos_mensal['mes_ano'] = df_abastecimentos_mensal['mes'].astype(str) + '/' + df_abastecimentos_mensal['ano'].astype(str).str[-2:]

st.divider()

grafico_duas_linhas_numero(df_abastecimentos_mensal, 'mes_ano', 'Distância de abastecimento', 'Km Rodado', 'Quantidade', 'Litros Combustível', 'Km Rodado x Litros Consumidos')

st.divider()

st.subheader('Tabela p/ Download')

st.dataframe(df_abastecimentos_mensal, hide_index=True)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Carregando o DataFrame
df = pd.read_csv(r'C:\Users\andre\Documents\GitHub\painel_farmacia\André\treinofarmaciagithubrepositorio\vendas.csv')

# Convertendo a coluna de data
df['mês/ano'] = pd.to_datetime(df['mês/ano'], format='%m/%Y')

# Cabeçalho da aplicação
st.header("Análise de Vendas")
st.write("---")  

# Criando as abas
aba_gerencial, aba_filiais, aba_vendedores = st.tabs(["Gerencial", "Filiais", "Vendedores"])

with aba_gerencial:
    # Seleção de mês para filtrar os dados
    meses = sorted(df['mês/ano'].dt.strftime('%m/%Y').unique())
    mes_selecionado = st.selectbox('Selecione o mês', meses)
    df_mes = df[df['mês/ano'].dt.strftime('%m/%Y') == mes_selecionado]  # Filtrando pelo mês selecionado

    # Seleção de filial e coluna para agrupar
    filial = st.selectbox('Selecione a filial', df_mes['filial2'].unique())
    coluna = st.selectbox('Selecione a coluna', ['grupo', 'desc_modo_pgto', 'convenio'])

    # Tipo de exibição
    display_type = st.selectbox('Exibir como:', ['Percentual', 'Número bruto'])

    # Filtrando o DataFrame pela filial e agrupando pela coluna escolhida
    df_filtrado = df_mes[df_mes['filial2'] == filial].groupby(coluna)['lct_preco_item'].sum().reset_index()

    # Ordenando o DataFrame em ordem decrescente
    df_filtrado = df_filtrado.sort_values(by='lct_preco_item', ascending=False)

    # Configuração do formato de exibição no gráfico de pizza
    if display_type == 'Percentual':
        autopct_format = '%1.1f%%'  # Exibe como percentual
    else:
        autopct_format = lambda p: f'{p * sum(df_filtrado["lct_preco_item"]) / 100:.0f}'

    # Gráfico de pizza
    fig, ax = plt.subplots()
    ax.pie(df_filtrado['lct_preco_item'], labels=df_filtrado[coluna], autopct=autopct_format)
    ax.set_title(f"Distribuição de Vendas por {coluna.capitalize()}")
    st.pyplot(fig)

    # Tabela filtrada
    st.dataframe(df_filtrado)

    # Total de vendas por grupo
    st.write("### Total Vendido por Grupo")
    total_por_grupo = df_mes.groupby('grupo')['lct_preco_item'].sum().reset_index().sort_values(by='lct_preco_item', ascending=False)
    st.dataframe(total_por_grupo)

    # Total de vendas
    total_sales = df_filtrado['lct_preco_item'].sum()
    st.metric("Total de Vendas", f"R$ {total_sales:.2f}")

    # Gráfico de barras horizontal de Comparação de Vendas
    st.write("### Comparação de Vendas")
    bar_fig, bar_ax = plt.subplots()
    bar_ax.barh(df_filtrado[coluna], df_filtrado['lct_preco_item'], color='skyblue')
    bar_ax.set_ylabel(coluna.capitalize())
    bar_ax.set_xlabel('Total de Vendas')
    bar_ax.set_title('Comparação de Vendas')
    st.pyplot(bar_fig)

    # Filtro de grupo para o gráfico de CMV por filial
    st.write("### Gráfico de CMV por Filial")
    grupos_selecionados = st.multiselect('Selecione os grupos', df_mes['grupo'].unique(), default=df_mes['grupo'].unique())

    # Filtrando o DataFrame pelos grupos selecionados
    df_cmv = df_mes[df_mes['grupo'].isin(grupos_selecionados)]

    # Calculando o CMV por filial com base nos grupos selecionados
    cmv_por_filial = df_cmv.groupby('filial2').apply(lambda x: x['lct_cmv'].sum() / x['lct_preco_item'].sum()).reset_index()
    cmv_por_filial.columns = ['filial2', 'cmv']
    
    # Ordenando o CMV em ordem decrescente
    cmv_por_filial = cmv_por_filial.sort_values(by='cmv', ascending=False)

    # Calculando a média geral do CMV
    media_cmv_geral = cmv_por_filial['cmv'].mean()

    # Gráfico de barras vertical do CMV com eixo y em porcentagem
    cmv_fig, cmv_ax = plt.subplots()
    cmv_ax.bar(cmv_por_filial['filial2'], cmv_por_filial['cmv'], color='orange')
    cmv_ax.axhline(media_cmv_geral, color='red', linestyle='--', label=f'Média Geral: {media_cmv_geral:.2%}')
    cmv_ax.set_xlabel('Filial')
    cmv_ax.set_ylabel('% CMV')
    cmv_ax.set_title('% CMV por Filial')
    cmv_ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))  # Formatação em porcentagem
    cmv_ax.set_xticklabels(cmv_por_filial['filial2'], rotation=45)
    cmv_ax.legend()
    st.pyplot(cmv_fig)

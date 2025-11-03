import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io 

st.set_page_config(
    page_title="Dashboard de Análise de Inventário (PI_IV)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛍️ Análise Estratégica de Inventário")
st.markdown("Este dashboard transforma seus dados de inventário em insights acionáveis de Análise ABC (Pareto) e Desempenho de Categoria.")
st.divider()

csv_data = """ID_Item,Categoria,Marca,Tamanho,Data_Entrada,Data_Venda,Custo_Aquisicao,Preco_Venda,Status
IT001,Caderno,Tilibra,A4,2025-08-01,2025-08-15,15.00,40.00,Vendido
IT002,Quebra-Cabeca,Grow,1000 Pecas,2025-08-01,,45.00,120.00,Disponível
IT003,Caneta,Bic,UN,2025-08-02,2025-08-10,1.50,5.00,Vendido
IT004,Carrinho,Hot Wheels,P,2025-08-03,,8.00,25.00,Disponível
IT005,Mochila,Xeryus,G,2025-08-05,2025-09-01,50.00,150.00,Vendido
IT006,Boneca,Mattel,M,2025-08-05,2025-08-20,30.00,90.00,Vendido
IT007,Pincel,Acrilex,Kit,2025-08-10,,12.00,35.00,Disponível
IT008,Bloco Notas,Post-it,76x76mm,2025-08-11,2025-08-14,5.00,15.00,Vendido
IT009,Jogo Tabuleiro,Estrela,UN,2025-08-12,,70.00,180.00,Disponível
IT010,Giz de Cera,Crayola,12 Cores,2025-08-15,2025-09-10,10.00,30.00,Vendido
"""

@st.cache_data
def carregar_e_preparar_dados(data):
    """Carrega e limpa os dados brutos."""
   
    df = pd.read_csv(io.StringIO(data), parse_dates=['Data_Entrada', 'Data_Venda'])
    df['Preco_Venda'] = pd.to_numeric(df['Preco_Venda'], errors='coerce')
    df['Custo_Aquisicao'] = pd.to_numeric(df['Custo_Aquisicao'], errors='coerce')
    return df

df = carregar_e_preparar_dados(csv_data)

st.sidebar.header("Filtros")
status_selecionado = st.sidebar.multiselect(
    "Filtrar por Status:",
    options=df['Status'].unique(),
    default=df['Status'].unique()
)

df_filtrado = df[df['Status'].isin(status_selecionado)]

# Exibição dados brutos
with st.expander("Ver Dados Brutos"):
    st.dataframe(df_filtrado)

def perform_abc_analysis(df_input):
    """Realiza a Análise de Pareto (ABC) por Faturamento."""
    df_vendidos = df_input[df_input['Status'] == 'Vendido'].copy()
    if df_vendidos.empty:
        return pd.DataFrame(), None

    faturamento_categoria = df_vendidos.groupby('Categoria')['Preco_Venda'].sum().sort_values(ascending=False)
    df_abc = faturamento_categoria.reset_index()
    df_abc.rename(columns={'Preco_Venda': 'Faturamento (R$)'}, inplace=True)

    df_abc['Participacao (%)'] = (df_abc['Faturamento (R$)'] / df_abc['Faturamento (R$)'].sum()) * 100
    df_abc['Acumulado (%)'] = df_abc['Participacao (%)'].cumsum()

    def classificar_categoria(percentual_acumulado):
        if percentual_acumulado <= 80:
            return 'A'
        elif percentual_acumulado <= 95:
            return 'B'
        else:
            return 'C'

    df_abc['Classe'] = df_abc['Acumulado (%)'].apply(classificar_categoria)

    # Gera o gráfico de Pareto
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(df_abc['Categoria'], df_abc['Faturamento (R$)'], color='skyblue', label='Faturamento')
    ax1.set_ylabel('Faturamento (R$)')
    ax1.tick_params(axis='x', rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(df_abc['Categoria'], df_abc['Acumulado (%)'], color='red', marker='o', linestyle='--', label='Acumulado %')
    ax2.set_ylabel('Percentual Acumulado (%)')
    ax2.set_ylim(0, 105)
    
    ax2.axhline(80, color='gray', linestyle=':', label='80% (Classe A)')
    
    fig.suptitle('Análise de Pareto (ABC) por Categoria de Produtos', fontsize=16)
    plt.style.use('seaborn-v0_8-whitegrid')
    fig.tight_layout()
    
    return df_abc, fig

def perform_performance_matrix(df_input):
    """Realiza a análise de Giro, Margem e gera a Matriz de Desempenho."""
    df_vendidos = df_input[df_input['Status'] == 'Vendido'].copy()
    
    if df_vendidos.empty:
        return pd.DataFrame(), None

    df_vendidos['Tempo_Permanencia'] = (df_vendidos['Data_Venda'] - df_vendidos['Data_Entrada']).dt.days
    df_vendidos['Lucro'] = df_vendidos['Preco_Venda'] - df_vendidos['Custo_Aquisicao']
    df_vendidos['Margem_%'] = np.where(df_vendidos['Preco_Venda'] > 0, 
                                     (df_vendidos['Lucro'] / df_vendidos['Preco_Venda']) * 100, 
                                     0)

    giro_categoria = df_vendidos.groupby('Categoria')['Tempo_Permanencia'].mean().round(0).reset_index(name='Giro_Medio_Dias')
    margem_categoria = df_vendidos.groupby('Categoria')['Margem_%'].mean().round(1).reset_index(name='Margem_Media_%')

    estoque_atual = df_input[df_input['Status'] == 'Disponível']['Categoria'].value_counts().reset_index(name='Pecas_Estoque')
    total_vendido = df_vendidos['Categoria'].value_counts().reset_index(name='Pecas_Vendidas')

    df_desempenho = pd.merge(giro_categoria, margem_categoria, on='Categoria', how='outer')
    df_desempenho = pd.merge(df_desempenho, estoque_atual, on='Categoria', how='outer')
    df_desempenho = pd.merge(df_desempenho, total_vendido, on='Categoria', how='outer')
    df_desempenho.fillna(0, inplace=True)
    
    def gerar_insight(row):
        giro = row['Giro_Medio_Dias']
        estoque = row['Pecas_Estoque']
        margem = row['Margem_Media_%']

        if giro <= 15 and estoque < 2:
            return "🔥 REPOR IMEDIATAMENTE"
        if giro > 30 and estoque > 3:
            return "❄️ PROMOÇÃO / REAVALIAÇÃO"
        if margem > 50 and giro <= 20:
            return "⭐ ALTA PERFORMANCE"
        return "OK"
    
    df_desempenho['Insight Estratégico'] = df_desempenho.apply(gerar_insight, axis=1)

    df_desempenho = df_desempenho[['Categoria', 'Pecas_Estoque', 'Pecas_Vendidas', 
                                   'Giro_Medio_Dias', 'Margem_Media_%', 'Insight Estratégico']]

    fig, ax = plt.subplots(figsize=(12, 8))

    scatter = ax.scatter(
        df_desempenho['Giro_Medio_Dias'],
        df_desempenho['Pecas_Vendidas'],
        s=df_desempenho['Margem_Media_%'] * 10,
        c=df_desempenho['Margem_Media_%'],
        cmap='viridis',
        alpha=0.7
    )

  
    for i, row in df_desempenho.iterrows():
        ax.text(row['Giro_Medio_Dias'] + 0.5, row['Pecas_Vendidas'], row['Categoria'], 
                fontsize=10, weight='bold')

   
    media_giro = df_desempenho['Giro_Medio_Dias'].mean()
    media_vendas = df_desempenho['Pecas_Vendidas'].mean()
    ax.axvline(media_giro, color='red', linestyle='--', linewidth=0.8)
    ax.axhline(media_vendas, color='blue', linestyle='--', linewidth=0.8)

   
    ax.set_title('Matriz de Desempenho de Categorias (Giro vs Vendas)', fontsize=18, weight='bold')
    ax.set_xlabel('Giro Médio (Dias) <-- Rápido | Lento -->')
    ax.set_ylabel('Total de Peças Vendidas')
    fig.colorbar(scatter, label='Margem de Lucro Média (%)')

    ax.text(media_giro / 2, media_vendas * 1.05, 'Estrelas (Giro Rápido / Alta Venda)', color='darkgreen', ha='center', fontsize=10)
    ax.text(media_giro * 1.2, media_vendas * 0.95, 'Abacaxis (Giro Lento / Baixa Venda)', color='darkred', ha='center', fontsize=10)

    plt.style.use('seaborn-v0_8-whitegrid')
    fig.tight_layout()
    
    return df_desempenho, fig


# Análise ABC (Pareto)
st.header("1. Análise ABC (Pareto)")
st.info("Identifica as categorias que geram 80% do seu faturamento, classificando-as como A, B ou C.")

df_abc_result, fig_abc = perform_abc_analysis(df_filtrado)

if df_abc_result.empty:
    st.warning("Não há itens 'Vendidos' nos dados para realizar a Análise ABC.")
else:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(df_abc_result.style.format({
            'Faturamento (R$)': "R$ {:,.2f}",
            'Participacao (%)': "{:.1f}%",
            'Acumulado (%)': "{:.1f}%"
        }))

    with col2:
        st.pyplot(fig_abc)

st.divider()

# Matriz de Desempenho
st.header("2. Matriz de Desempenho e Insights")
st.info("Compara a velocidade de venda (Giro) com o volume (Vendas) e a rentabilidade (Margem).")

df_desempenho_result, fig_desempenho = perform_performance_matrix(df_filtrado)

if df_desempenho_result.empty:
    st.warning("Não há itens 'Vendidos' nos dados para calcular o Desempenho.")
else:
    st.dataframe(df_desempenho_result.style.format({
        'Margem_Media_%': "{:.1f}%",
        'Giro_Medio_Dias': "{:.0f} dias"
    }))
    
    st.pyplot(fig_desempenho)

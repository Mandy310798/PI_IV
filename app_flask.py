from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import io

# --- 1. Configuração do Flask ---
app = Flask(__name__)

# --- 2. Dados de Entrada (Seu CSV) ---
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

def carregar_e_preparar_dados(data):
    """Carrega e limpa os dados brutos."""
    df = pd.read_csv(io.StringIO(data), parse_dates=['Data_Entrada', 'Data_Venda'])
    return df

df = carregar_e_preparar_dados(csv_data)

# --- 3. Funções de Análise e Geração de Gráficos Plotly ---

def gerar_grafico_abc(df_input):
    """Realiza a Análise ABC e gera o gráfico Plotly."""
    df_vendidos = df_input[df_input['Status'] == 'Vendido'].copy()
    if df_vendidos.empty:
        return None, "Não há dados de vendas."

    faturamento_categoria = df_vendidos.groupby('Categoria')['Preco_Venda'].sum().sort_values(ascending=False)
    df_abc = faturamento_categoria.reset_index(name='Faturamento')
    
    df_abc['Participacao (%)'] = (df_abc['Faturamento'] / df_abc['Faturamento'].sum()) * 100
    df_abc['Acumulado (%)'] = df_abc['Participacao (%)'].cumsum()

    # Cria a figura com dois eixos Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Gráfico de Barras (Faturamento)
    fig.add_trace(
        go.Bar(
            x=df_abc['Categoria'], 
            y=df_abc['Faturamento'], 
            name='Faturamento (R$)', 
            marker_color='#4682B4'
        ),
        secondary_y=False,
    )

    # Gráfico de Linha (Acumulado %)
    fig.add_trace(
        go.Scatter(
            x=df_abc['Categoria'], 
            y=df_abc['Acumulado (%)'], 
            name='Acumulado (%)', 
            mode='lines+markers', 
            line=dict(color='red', dash='dash')
        ),
        secondary_y=True,
    )

    # Linha de 80% (Para classificação A)
    fig.add_hline(y=80, line_dash="dot", annotation_text="80% (Classe A)", 
                  secondary_y=True, annotation_position="top left", line_color="grey")

    fig.update_layout(
        title_text="Análise de Pareto (ABC) por Categoria",
        title_font_size=20,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Categoria",
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255, 255, 255, 0)'),
        height=500
    )
    fig.update_yaxes(title_text="Faturamento (R$)", secondary_y=False)
    fig.update_yaxes(title_text="Percentual Acumulado (%)", secondary_y=True, range=[0, 105])

    # Retorna o gráfico Plotly como JSON
    return fig.to_json(), df_abc.to_html(classes='table table-striped table-hover', index=False)


def gerar_grafico_desempenho(df_input):
    """Gera a Matriz de Desempenho (Bubble Chart) com Plotly Express."""
    df_vendidos = df_input[df_input['Status'] == 'Vendido'].copy()
    
    if df_vendidos.empty:
        return None

    # Seus cálculos de Margem e Giro
    df_vendidos['Tempo_Permanencia'] = (df_vendidos['Data_Venda'] - df_vendidos['Data_Entrada']).dt.days
    df_vendidos['Lucro'] = df_vendidos['Preco_Venda'] - df_vendidos['Custo_Aquisicao']
    df_vendidos['Margem_%'] = np.where(df_vendidos['Preco_Venda'] > 0, 
                                     (df_vendidos['Lucro'] / df_vendidos['Preco_Venda']) * 100, 
                                     0)
    giro_categoria = df_vendidos.groupby('Categoria')['Tempo_Permanencia'].mean().round(0).reset_index(name='Giro_Medio_Dias')
    margem_categoria = df_vendidos.groupby('Categoria')['Margem_%'].mean().round(1).reset_index(name='Margem_Media_%')
    total_vendido = df_vendidos['Categoria'].value_counts().reset_index(name='Pecas_Vendidas')
    
    df_desempenho = pd.merge(giro_categoria, margem_categoria, on='Categoria', how='outer')
    df_desempenho = pd.merge(df_desempenho, total_vendido, on='Categoria', how='outer')
    df_desempenho.fillna(0, inplace=True)
    
    # Geração do Bubble Chart com Plotly Express
    fig = px.scatter(
        df_desempenho,
        x='Giro_Medio_Dias',
        y='Pecas_Vendidas',
        size='Margem_Media_%', # O tamanho da bolha é a margem
        color='Margem_Media_%', # A cor também é a margem
        hover_name='Categoria',
        text='Categoria', # Adiciona o rótulo da categoria na bolha
        title='Matriz de Desempenho de Categorias (Giro vs Vendas)',
        labels={
            'Giro_Medio_Dias': 'Giro Médio (Dias) <-- Rápido | Lento -->',
            'Pecas_Vendidas': 'Total de Peças Vendidas',
            'Margem_Media_%': 'Margem Média (%)'
        }
    )
    
    # Adicionar as linhas de média
    media_giro = df_desempenho['Giro_Medio_Dias'].mean()
    media_vendas = df_desempenho['Pecas_Vendidas'].mean()
    
    fig.add_vline(x=media_giro, line_dash="dash", line_color="red", annotation_text="Giro Médio")
    fig.add_hline(y=media_vendas, line_dash="dash", line_color="blue", annotation_text="Média de Vendas")
    
    fig.update_traces(textposition='top center')
    fig.update_layout(height=500)
    
    return fig.to_json()


# --- 4. Rota principal do Flask ---

@app.route('/')
def index():
    # 1. Gera os gráficos Plotly em formato JSON
    graph_abc_json, table_abc_html = gerar_grafico_abc(df)
    graph_desempenho_json = gerar_grafico_desempenho(df)
    
    # 2. Renderiza o template HTML e passa os dados JSON
    return render_template(
        'index.html',
        graph_abc_json=graph_abc_json,
        table_abc_html=table_abc_html,
        graph_desempenho_json=graph_desempenho_json
    )

if __name__ == '__main__':
    # Quando em produção, mude debug=False
    app.run(debug=True)
import plotly.graph_objects as go
import numpy as np

def _ensure_serializable(fig):
    """Converte numpy arrays em listas dentro dos traces (text, marker.size, etc.)."""
    for trace in fig.data:
        try:
            if getattr(trace, 'text', None) is not None:
                if not isinstance(trace.text, (list, str, int, float)):
                    trace.text = list(trace.text)
        except Exception:
            pass

        try:
            if getattr(trace, 'marker', None) is not None and getattr(trace.marker, 'size', None) is not None:
                size = trace.marker.size
                if not isinstance(size, list):
                    try:
                        trace.marker.size = list(size)
                    except Exception:
                        pass
        except Exception:
            pass

    return fig

def make_pareto_fig(df_abc):
    x = df_abc['categoria'].tolist()
    fatur = df_abc['faturamento'].tolist()
    acumulado = df_abc['acumulado_pct'].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=fatur, name='Faturamento (R$)',
                         hovertemplate='%{x}<br>R$ %{y:.2f}<extra></extra>'))
    fig.add_trace(go.Scatter(x=x, y=acumulado, name='Acumulado (%)', yaxis='y2',
                             mode='lines+markers', hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'))

    fig.update_layout(
        title='Análise de Pareto (ABC)',
        xaxis=dict(title='Categoria', tickangle=-30),
        yaxis=dict(title='Faturamento (R$)'),
        yaxis2=dict(title='Percentual Acumulado (%)', overlaying='y', side='right', range=[0,110]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        template='plotly_white', margin=dict(l=60, r=60, t=60, b=120)
    )

    fig.add_hline(y=80, line=dict(dash='dash', color='gray'), yref='y2')

    for xi, yi in zip(x, fatur):
        fig.add_annotation(x=xi, y=yi, text=f'R$ {yi:.0f}', showarrow=False, yshift=5)

    return _ensure_serializable(fig)

def make_matrix_fig(df):
    x = df['giro_medio']
    y = df['vendas']
    size = (df['faturamento'] / df['faturamento'].max()) * 60 + 10
    color = df['margem']
    names = df['categoria']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, text=names, mode='markers+text', textposition='top center',
        marker=dict(size=size, color=color, colorscale='Viridis', showscale=True, colorbar=dict(title='Margem')),
        hovertemplate='<b>%{text}</b><br>Giro Médio: %{x:.1f} dias<br>Vendas: %{y}<extra></extra>'
    ))

    mean_x = float(np.mean(x))
    mean_y = float(np.mean(y))

    fig.add_vline(x=mean_x, line=dict(color='red', dash='dash'), annotation_text='Giro Médio', annotation_position='top left')
    fig.add_hline(y=mean_y, line=dict(color='blue', dash='dash'), annotation_text='Média de Vendas', annotation_position='bottom right')

    fig.update_layout(title='Matriz de Desempenho (Giro x Vendas)', xaxis=dict(title='Giro Médio (Dias)'), yaxis=dict(title='Total de Vendas'), template='plotly_white', margin=dict(l=60, r=60, t=60, b=60))

    return _ensure_serializable(fig)

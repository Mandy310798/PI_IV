import pandas as pd

def load_sample_data():
    data = {
        'categoria': ['Mochila', 'Boneca', 'Caderno', 'Giz de Cera', 'Bloco Notas', 'Caneta'],
        'faturamento': [150.0, 90.0, 40.0, 30.0, 15.0, 5.0],
        'vendas': [10, 6, 3, 2, 1, 1],
        'margem': [0.25, 0.22, 0.18, 0.20, 0.12, 0.10],
        'giro_medio': [14.5, 16.0, 15.2, 15.0, 16.5, 16.2]
    }
    return pd.DataFrame(data)

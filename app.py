
from flask import Flask, render_template, jsonify
import traceback
import logging
import json
from plotly.utils import PlotlyJSONEncoder


try:
    from data import load_sample_data
except Exception as e:
    load_sample_data = None
    print("AVISO: não foi possível importar load_sample_data:", e)

try:
    from plots import make_pareto_fig, make_matrix_fig
except Exception as e:
    make_pareto_fig = None
    make_matrix_fig = None
    print("AVISO: não foi possível importar funções de plots:", e)

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)


@app.route('/dashboard')
def dashboard():
    error_info = None
    tabela_html = None
    pareto_json = None
    matrix_json = None
    df_info = None

    try:
        if load_sample_data is None:
            raise ImportError("Função 'load_sample_data' não importada. Verifique data.py")

        df = load_sample_data()

        df_info = {
            'columns': list(df.columns),
            'dtypes': {c: str(t) for c, t in df.dtypes.items()},
            'head': df.head(10).to_dict(orient='records')
        }

        required_for_abc = {'categoria', 'faturamento'}
        required_for_matrix = {'categoria', 'vendas', 'giro_medio', 'faturamento', 'margem'}

        missing_abc = required_for_abc - set(df.columns)
        missing_matrix = required_for_matrix - set(df.columns)

        if missing_abc:
            raise KeyError(f"Colunas faltando para ABC: {missing_abc}")
        if missing_matrix:
            raise KeyError(f"Colunas faltando para Matriz: {missing_matrix}")

        df_abc = (
            df.groupby('categoria', as_index=False)['faturamento']
              .sum()
              .sort_values('faturamento', ascending=False)
        )

        total = df_abc['faturamento'].sum()
        if total == 0:
            df_abc['participacao_pct'] = 0
        else:
            df_abc['participacao_pct'] = df_abc['faturamento'] / total * 100

        df_abc['acumulado_pct'] = df_abc['participacao_pct'].cumsum()

        if make_pareto_fig is None or make_matrix_fig is None:
            raise ImportError("Funções de plot não foram importadas (ver plots.py)")

        pareto_fig = make_pareto_fig(df_abc)
        matrix_fig = make_matrix_fig(df)

        pareto_obj = pareto_fig.to_plotly_json()
        matrix_obj = matrix_fig.to_plotly_json()


        tabela_html = df_abc.to_html(classes='table table-striped table-sm', index=False, float_format='%.2f')

        return render_template('dashboard.html',
                            pareto_obj=pareto_obj,
                            matrix_obj=matrix_obj,
                            tabela_html=tabela_html,
                            error_info=None,
                            df_info=df_info)

    except Exception as e:
        tb = traceback.format_exc()
        app.logger.exception("Erro ao gerar gráficos: %s", e)
        error_info = {'error_message': str(e), 'traceback': tb}

        # tentar recuperar info do df
        try:
            if load_sample_data is not None:
                df = load_sample_data()
                df_info = {
                    'columns': list(df.columns),
                    'dtypes': {c: str(t) for c, t in df.dtypes.items()},
                    'head': df.head(10).to_dict(orient='records')
                }
        except Exception:
            df_info = None

        return render_template('dashboard.html',
                                pareto_obj=None,
                                matrix_obj=None,
                                tabela_html="<p>Erro ao gerar tabela.</p>",
                                error_info=error_info,
                                df_info=df_info)


@app.route('/')
def home():
    return dashboard()


@app.route('/debug/pareto')
def debug_pareto():
    try:
        if load_sample_data is None or make_pareto_fig is None:
            raise ImportError("Debug: falta load_sample_data ou make_pareto_fig")
        df = load_sample_data()
        df_abc = df.groupby('categoria', as_index=False)['faturamento'].sum().sort_values('faturamento', ascending=False)
        total = df_abc['faturamento'].sum()
        df_abc['participacao_pct'] = 0 if total == 0 else df_abc['faturamento'] / total * 100
        df_abc['acumulado_pct'] = df_abc['participacao_pct'].cumsum()
        fig = make_pareto_fig(df_abc)
        return jsonify(fig.to_plotly_json())
    except Exception as e:
        return jsonify({'error': str(e), 'type': type(e).__name__, 'trace': traceback.format_exc()}), 500


@app.route('/debug/matrix')
def debug_matrix():
    try:
        if load_sample_data is None or make_matrix_fig is None:
            raise ImportError("Debug: falta load_sample_data ou make_matrix_fig")
        df = load_sample_data()
        fig = make_matrix_fig(df)
        return jsonify(fig.to_plotly_json())
    except Exception as e:
        return jsonify({'error': str(e), 'type': type(e).__name__, 'trace': traceback.format_exc()}), 500


if __name__ == '__main__':
    app.run(debug=True)

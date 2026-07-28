"""
Rotas para Análise de Distribuição por Linha e Coluna
"""

from flask import Blueprint, render_template, jsonify
from services.analise_distribuicao_linha_coluna_service import AnaliseDistribuicaoLinhaColuna

distribuicao_lc_bp = Blueprint('distribuicao_linha_coluna', __name__)


@distribuicao_lc_bp.route('/analise/distribuicao-linha-coluna')
def pagina_distribuicao_linha_coluna():
    """Página principal da análise de distribuição"""
    return render_template('analise_distribuicao_linha_coluna.html')


@distribuicao_lc_bp.route('/analise/volante')
def pagina_analise_volante():
    """Página de análise do volante"""
    return render_template('analise_volante.html')


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/completa')
def api_analise_completa():
    """API que retorna análise completa (todas as seções)"""
    try:
        dados = AnaliseDistribuicaoLinhaColuna.obter_analise_completa()
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/historica/<tipo>')
def api_distribuicao_historica(tipo):
    """API para distribuição histórica (linha ou coluna)"""
    try:
        if tipo not in ['linha', 'coluna']:
            return jsonify({'erro': 'Tipo inválido. Use "linha" ou "coluna"'}), 400

        dados = AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica(tipo)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/top3/<tipo>')
def api_top3(tipo):
    """API para TOP 3 (linha ou coluna)"""
    try:
        if tipo not in ['linha', 'coluna']:
            return jsonify({'erro': 'Tipo inválido'}), 400

        dados = AnaliseDistribuicaoLinhaColuna.obter_top3(tipo)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/insight/<tipo>')
def api_insight(tipo):
    """API para insight por período"""
    try:
        if tipo not in ['linha', 'coluna']:
            return jsonify({'erro': 'Tipo inválido'}), 400

        dados = AnaliseDistribuicaoLinhaColuna.calcular_insight_por_periodo(tipo)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/regioes-quentes/<tipo>')
def api_regioes_quentes(tipo):
    """API para regiões quentes"""
    try:
        if tipo not in ['linha', 'coluna']:
            return jsonify({'erro': 'Tipo inválido'}), 400

        dados = AnaliseDistribuicaoLinhaColuna.identificar_regioes_quentes(tipo)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/mapa-calor/<tipo>')
def api_mapa_calor(tipo):
    """API para dados do mapa de calor"""
    try:
        if tipo not in ['linha', 'coluna']:
            return jsonify({'erro': 'Tipo inválido'}), 400

        dados = AnaliseDistribuicaoLinhaColuna.gerar_mapa_calor(tipo)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/comparativa')
def api_comparativa():
    """API para análise comparativa Linha x Coluna"""
    try:
        dados = AnaliseDistribuicaoLinhaColuna.analise_comparativa()
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/desvio/<tipo>')
def api_desvio(tipo):
    """API para análise de desvio padrão"""
    try:
        if tipo not in ['linha', 'coluna']:
            return jsonify({'erro': 'Tipo inválido'}), 400

        dados = AnaliseDistribuicaoLinhaColuna.analise_desvio_padrao(tipo)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/clusters')
def api_clusters():
    """API para clusterização de padrões"""
    try:
        dados = AnaliseDistribuicaoLinhaColuna.clusterizar_padroes()
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/probabilidade/<tipo>')
def api_probabilidade(tipo):
    """API para probabilidade da próxima composição"""
    try:
        if tipo not in ['linha', 'coluna']:
            return jsonify({'erro': 'Tipo inválido'}), 400

        dados = AnaliseDistribuicaoLinhaColuna.calcular_probabilidade_proxima(tipo)
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/alertas')
def api_alertas():
    """API para alertas de anomalias"""
    try:
        dados = AnaliseDistribuicaoLinhaColuna.gerar_alertas_anomalias()
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/distribuicao-linha-coluna/recomendacao')
def api_recomendacao():
    """API para recomendação final"""
    try:
        dados = AnaliseDistribuicaoLinhaColuna.gerar_recomendacao_final()
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@distribuicao_lc_bp.route('/api/analise/volante', methods=['POST'])
def api_analise_volante():
    """
    API para análise do volante com filtros personalizados

    Body JSON esperado:
    {
        "modo": "linha" ou "coluna",
        "filtro_tipo": "todos", "unico", "intervalo", "multiplos",
        "concurso_unico": 1139 (opcional),
        "intervalo_inicio": 1 (opcional),
        "intervalo_fim": 100 (opcional),
        "concursos_ids": [1, 5, 10] (opcional)
    }
    """
    from flask import request

    try:
        dados_request = request.get_json()
        modo = dados_request.get('modo', 'coluna')
        filtro_tipo = dados_request.get('filtro_tipo', 'todos')

        # Validações
        if modo not in ['linha', 'coluna']:
            return jsonify({'erro': 'Modo inválido. Use "linha" ou "coluna"'}), 400

        # Por enquanto, vamos usar a análise completa existente e adaptar
        # TODO: Implementar filtros de concursos no service
        dados = AnaliseDistribuicaoLinhaColuna.obter_analise_volante(
            modo=modo,
            filtro_tipo=filtro_tipo,
            concurso_unico=dados_request.get('concurso_unico'),
            intervalo_inicio=dados_request.get('intervalo_inicio'),
            intervalo_fim=dados_request.get('intervalo_fim'),
            concursos_ids=dados_request.get('concursos_ids')
        )

        return jsonify(dados), 200

    except AttributeError:
        # Fallback: se o método não existir no service, usar distribuição histórica
        try:
            dados = AnaliseDistribuicaoLinhaColuna.calcular_distribuicao_historica(modo)
            # Adaptar formato para o esperado pelo frontend
            resultado = {
                'modo': modo,
                'total_sorteios_analisados': dados.get('total_sorteios', 0),
                'primeiro_concurso': dados.get('primeiro_concurso', '-'),
                'ultimo_concurso': dados.get('ultimo_concurso', '-'),
                'volante_visual': gerar_volante_visual(dados, modo),
                'volante_frequencias': dados.get('frequencias', {}),
                'top3_posicoes': dados.get('top3', []),
                'mais_destacada': dados.get('mais_frequente', {}),
                'menos_destacada': dados.get('menos_frequente', {}),
                'insights': gerar_insights(dados, modo)
            }
            return jsonify(resultado), 200
        except Exception as e_fallback:
            return jsonify({'erro': f'Método de análise não implementado: {str(e_fallback)}'}), 500
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


def gerar_volante_visual(dados, modo):
    """Gera estrutura visual do volante 3x10"""
    volante = []
    for linha_idx in range(3):
        linha = []
        for col_idx in range(10):
            numero = linha_idx * 10 + col_idx + 1
            if numero > 31:
                linha.append({'numero': None, 'frequencia': 0})
            else:
                freq = dados.get('frequencias', {}).get(str(numero), 0)
                linha.append({'numero': numero, 'frequencia': freq})
        volante.append(linha)
    return volante


def gerar_insights(dados, modo):
    """Gera insights automáticos baseados nos dados"""
    insights = []
    tipo = 'linhas' if modo == 'linha' else 'colunas'

    # Insight básico
    insights.append(f"Análise baseada em {dados.get('total_sorteios', 0)} sorteios históricos.")

    if dados.get('top3'):
        top1 = dados['top3'][0]
        insights.append(f"A {tipo[:-1]} {top1.get('posicao')} é a mais frequente com {top1.get('percentual')}% de aparições.")

    return insights

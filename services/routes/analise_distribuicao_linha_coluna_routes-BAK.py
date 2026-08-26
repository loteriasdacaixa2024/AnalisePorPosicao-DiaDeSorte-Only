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

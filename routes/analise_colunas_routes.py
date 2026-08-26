"""
ROUTES: Análise de Colunas - VERSÃO SIMPLIFICADA
Destino: routes/analise_colunas_routes.py

IMPORTANTE: Apenas 3 rotas essenciais!
"""

from flask import Blueprint, render_template, jsonify
from services.analise_colunas_service import AnaliseColunasService

colunas_bp = Blueprint('analise_colunas', __name__, url_prefix='/analise-colunas')


@colunas_bp.route('/dashboard')
def dashboard():
    """Página principal do dashboard"""
    return render_template('dashboard_colunas.html')


@colunas_bp.route('/api/importar', methods=['POST'])
def api_importar():
    """API: Importar histórico completo"""
    resultado = AnaliseColunasService.importar_historico()
    status = 200 if resultado['sucesso'] else 500
    return jsonify(resultado), status


@colunas_bp.route('/api/ranking')
def api_ranking():
    """API: Obter ranking das colunas"""
    dados = AnaliseColunasService.obter_ranking()
    return jsonify(dados), 200


@colunas_bp.route('/api/coocorrencias')
def api_coocorrencias():
    """API: Obter co-ocorrências"""
    dados = AnaliseColunasService.obter_coocorrencias(top_n=20)
    return jsonify(dados), 200


@colunas_bp.route('/api/verificar-atualizacao')
def api_verificar_atualizacao():
    """API: Verifica se precisa atualizar os dados"""
    resultado = AnaliseColunasService.verificar_atualizacao_necessaria()
    return jsonify(resultado), 200


@colunas_bp.route('/api/status')
def api_status():
    """API: Retorna status atual da análise"""
    status = AnaliseColunasService.obter_status()
    return jsonify(status), 200

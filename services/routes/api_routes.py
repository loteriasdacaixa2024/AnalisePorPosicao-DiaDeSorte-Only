# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify
from services.caixa_service import CaixaService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/sincronizar/novos', methods=['POST'])
def sincronizar_novos():
    """
    Sincroniza apenas NOVOS sorteios (do último no banco até o último na API)
    """
    try:
        resultado = CaixaService.sincronizar_novos()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': f'Erro: {str(e)}'}), 500

@api_bp.route('/status', methods=['GET'])
def status_sincronizacao():
    """
    Status da sincronização
    """
    try:
        status = CaixaService.obter_status_sincronizacao()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'erro': f'Erro: {str(e)}'}), 500

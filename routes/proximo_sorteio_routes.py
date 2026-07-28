"""
Routes para informações do próximo sorteio

Fornece endpoint para buscar informações do próximo sorteio
diretamente do banco de dados.
"""

from flask import Blueprint, jsonify
from services.proximo_sorteio_service import ProximoSorteioService

proximo_sorteio_bp = Blueprint('proximo_sorteio', __name__)


@proximo_sorteio_bp.route('/api/proximo-sorteio')
def api_proximo_sorteio():
    """
    API que retorna informações do próximo sorteio do banco de dados

    GET /api/proximo-sorteio

    Returns:
        JSON com informações do próximo sorteio
    """
    try:
        resultado = ProximoSorteioService.obter_info_proximo_sorteio()
        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            'erro': str(e),
            'disponivel': False
        }), 500

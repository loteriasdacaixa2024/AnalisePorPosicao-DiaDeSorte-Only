from flask import Blueprint, jsonify, request
from services.concentracao_estrategica_service import ConcentracaoEstrategicaService

concentracao_estrategica_bp = Blueprint('concentracao_estrategica', __name__)


@concentracao_estrategica_bp.route('/api/concentracao/score-uniao', methods=['GET'])
def api_score_uniao():
    limite = request.args.get('limite', 250, type=int)
    resultado = ConcentracaoEstrategicaService.calcular_score_uniao(limite)
    return jsonify(resultado)

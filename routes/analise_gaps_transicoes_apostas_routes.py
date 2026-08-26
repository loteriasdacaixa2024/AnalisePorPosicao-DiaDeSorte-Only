from flask import Blueprint, jsonify, request
from services.analise_gaps_transicoes_apostas_service import AnaliseGapsTransicoesApostasService

analise_gaps_transicoes_apostas_bp = Blueprint('analise_gaps_transicoes_apostas', __name__)


@analise_gaps_transicoes_apostas_bp.route('/api/analise/gaps-transicoes-apostas', methods=['POST'])
def analisar_gaps_transicoes():
    try:
        data = request.get_json(force=True, silent=True) or {}
        anterior = data.get('dezenas_anterior') or data.get('resultado_anterior')
        apostas = data.get('apostas')
        if anterior is None or apostas is None:
            return jsonify({'error': 'Campos dezenas_anterior e apostas sao obrigatorios'}), 400

        resultado = AnaliseGapsTransicoesApostasService.analisar_gaps_transicoes(anterior, apostas)
        return jsonify(resultado), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Falha ao processar gaps/transicoes: {e}'}), 500

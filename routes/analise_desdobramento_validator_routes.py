from flask import Blueprint, jsonify, request
from services.analise_desdobramento_validator_service import AnaliseDesdobramentoValidatorService

analise_desdobramento_validator_bp = Blueprint('analise_desdobramento_validator', __name__)


@analise_desdobramento_validator_bp.route('/api/analise/valida-desdobramento', methods=['POST'])
def validar_desdobramento():
    try:
        data = request.get_json(force=True, silent=True) or {}
        anterior = data.get('dezenas_anterior') or data.get('resultado_anterior')
        apostas = data.get('apostas')
        if anterior is None or apostas is None:
            return jsonify({'error': 'Campos dezenas_anterior e apostas sao obrigatorios'}), 400

        resultado = AnaliseDesdobramentoValidatorService.validar_desdobramento(anterior, apostas)
        return jsonify(resultado), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Falha ao validar desdobramento: {e}'}), 500

from flask import Blueprint, jsonify, request
from services.analise_simulacao_reversa_service import AnaliseSimulacaoReversaService

analise_simulacao_reversa_bp = Blueprint('analise_simulacao_reversa', __name__)


@analise_simulacao_reversa_bp.route('/api/analise/simulacao-reversa', methods=['GET'])
def analisar_simulacao_reversa():
    try:
        limite = request.args.get('limite') or request.args.get('historico')
        limite_int = int(limite) if limite else 20
        resultado = AnaliseSimulacaoReversaService.analisar_simulacao_reversa(limite_int)
        status_code = 200 if 'error' not in resultado else 400
        return jsonify(resultado), status_code
    except ValueError:
        return jsonify({'error': 'Parametro limite deve ser inteiro'}), 400
    except Exception as e:
        return jsonify({'error': f'Falha ao executar simulacao reversa: {e}'}), 500

from flask import Blueprint, jsonify, request
from services.analise_frequencia_interna_apostas_service import AnaliseFrequenciaInternaApostasService

analise_freq_interna_apostas_bp = Blueprint('analise_freq_interna_apostas', __name__)


@analise_freq_interna_apostas_bp.route('/api/analise/freq-interna-apostas', methods=['POST'])
def analisar_freq_interna():
    try:
        data = request.get_json(force=True, silent=True) or {}
        apostas = data.get('apostas')
        if apostas is None:
            return jsonify({'error': 'Campo apostas obrigatorio'}), 400

        resultado = AnaliseFrequenciaInternaApostasService.calcular_frequencia_interna(apostas)
        return jsonify(resultado), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Falha ao processar frequencia interna: {e}'}), 500

from flask import Blueprint, jsonify, request, render_template
from services.analise_quentes_frios_service import AnaliseQuentesFriosService

analise_quentes_frios_bp = Blueprint('analise_quentes_frios', __name__)


@analise_quentes_frios_bp.route('/analise/quentes-frios')
def pagina_quentes_frios():
    return render_template('analise_quentes_frios.html')


@analise_quentes_frios_bp.route('/api/analise/quentes-frios', methods=['GET'])
def obter_quentes_frios():
    try:
        top = request.args.get('top', 15, type=int)
        resultado = AnaliseQuentesFriosService.obter_numeros_quentes_frios(top)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@analise_quentes_frios_bp.route('/api/analise/quentes-frios/completo', methods=['GET'])
def obter_estatisticas_completas():
    try:
        resultado = AnaliseQuentesFriosService.obter_estatisticas_completas()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

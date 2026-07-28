from flask import Blueprint, jsonify, render_template
from services.analise_frequencia_premios_service import AnaliseFrequenciaPremiosService

analise_frequencia_premios_bp = Blueprint('analise_frequencia_premios', __name__)


@analise_frequencia_premios_bp.route('/analise/frequencia-premios')
def pagina_analise_frequencia_premios():
    return render_template('analise_frequencia_premios.html')


@analise_frequencia_premios_bp.route('/api/analise/frequencia-premios')
def api_analise_frequencia_premios():
    try:
        resultado = AnaliseFrequenciaPremiosService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

from flask import Blueprint, jsonify, render_template
from services.analise_acumulos_mes_service import AnaliseAcumulosMesService

analise_acumulos_mes_bp = Blueprint('analise_acumulos_mes', __name__)


@analise_acumulos_mes_bp.route('/analise/acumulos-mes')
def pagina_analise_acumulos_mes():
    return render_template('analise_acumulos_mes.html')


@analise_acumulos_mes_bp.route('/api/analise/acumulos-mes')
def api_analise_acumulos_mes():
    try:
        resultado = AnaliseAcumulosMesService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

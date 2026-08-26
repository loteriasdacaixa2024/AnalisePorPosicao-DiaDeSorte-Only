from flask import Blueprint, jsonify, render_template
from services.analise_ciclos_intervalos_service import AnaliseCiclosIntervalosService

analise_ciclos_intervalos_bp = Blueprint('analise_ciclos_intervalos', __name__)


@analise_ciclos_intervalos_bp.route('/analise/ciclos-intervalos')
def pagina_analise_ciclos_intervalos():
    return render_template('analise_ciclos_intervalos.html')


@analise_ciclos_intervalos_bp.route('/api/analise/ciclos-intervalos')
def api_analise_ciclos_intervalos():
    try:
        resultado = AnaliseCiclosIntervalosService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

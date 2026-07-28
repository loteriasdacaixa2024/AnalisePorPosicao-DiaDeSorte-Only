from flask import Blueprint, jsonify, render_template
from services.analise_tubular_service import AnaliseTubularService

analise_tubular_bp = Blueprint('analise_tubular', __name__)


@analise_tubular_bp.route('/analise/tubular')
def pagina_analise_tubular():
    return render_template('analise_tubular.html')


@analise_tubular_bp.route('/api/analise/tubular')
def api_analise_tubular():
    try:
        resultado = AnaliseTubularService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

from flask import Blueprint, jsonify, render_template
from services.analise_sazonal_service import AnaliseSazonalService

analise_sazonal_bp = Blueprint('analise_sazonal', __name__)


@analise_sazonal_bp.route('/analise/sazonal')
def pagina_analise_sazonal():
    return render_template('analise_sazonal.html')


@analise_sazonal_bp.route('/api/analise/sazonal')
def api_analise_sazonal():
    try:
        resultado = AnaliseSazonalService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

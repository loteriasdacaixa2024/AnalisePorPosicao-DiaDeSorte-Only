from flask import Blueprint, jsonify, render_template
from services.analise_padroes_sequencias_service import AnalisePadroesSequenciasService

analise_padroes_sequencias_bp = Blueprint('analise_padroes_sequencias', __name__)


@analise_padroes_sequencias_bp.route('/analise/padroes-sequencias')
def pagina_analise_padroes_sequencias():
    return render_template('analise_padroes_sequencias.html')


@analise_padroes_sequencias_bp.route('/api/analise/padroes-sequencias')
def api_analise_padroes_sequencias():
    try:
        resultado = AnalisePadroesSequenciasService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

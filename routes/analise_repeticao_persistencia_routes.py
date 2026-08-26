from flask import Blueprint, jsonify, render_template
from services.analise_repeticao_persistencia_service import AnaliseRepeticaoPersistenciaService

analise_repeticao_persistencia_bp = Blueprint('analise_repeticao_persistencia', __name__)


@analise_repeticao_persistencia_bp.route('/analise/repeticao-persistencia')
def pagina_analise_repeticao_persistencia():
    return render_template('analise_repeticao_persistencia.html')


@analise_repeticao_persistencia_bp.route('/api/analise/repeticao-persistencia')
def api_analise_repeticao_persistencia():
    try:
        resultado = AnaliseRepeticaoPersistenciaService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

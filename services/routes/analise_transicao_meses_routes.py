from flask import Blueprint, jsonify, render_template
from services.analise_transicao_meses_service import AnaliseTransicaoMesesService

analise_transicao_meses_bp = Blueprint('analise_transicao_meses', __name__)


@analise_transicao_meses_bp.route('/analise/transicao-meses')
def pagina_analise_transicao_meses():
    return render_template('analise_transicao_meses.html')


@analise_transicao_meses_bp.route('/api/analise/transicao-meses')
def api_analise_transicao_meses():
    try:
        resultado = AnaliseTransicaoMesesService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

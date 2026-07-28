from flask import Blueprint, jsonify, render_template
from services.analise_correlacao_mes_dezenas_service import AnaliseCorrelacaoMesDezenaService

analise_correlacao_mes_dezenas_bp = Blueprint('analise_correlacao_mes_dezenas', __name__)


@analise_correlacao_mes_dezenas_bp.route('/analise/correlacao-mes-dezenas')
def pagina_analise_correlacao_mes_dezenas():
    return render_template('analise_correlacao_mes_dezenas.html')


@analise_correlacao_mes_dezenas_bp.route('/api/analise/correlacao-mes-dezenas')
def api_analise_correlacao_mes_dezenas():
    try:
        resultado = AnaliseCorrelacaoMesDezenaService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

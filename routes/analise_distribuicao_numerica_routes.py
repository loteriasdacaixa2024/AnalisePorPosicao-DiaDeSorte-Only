from flask import Blueprint, jsonify, render_template
from services.analise_distribuicao_numerica_service import AnaliseDistribuicaoNumericaService

analise_distribuicao_numerica_bp = Blueprint('analise_distribuicao_numerica', __name__)


@analise_distribuicao_numerica_bp.route('/analise/distribuicao-numerica')
def pagina_analise_distribuicao_numerica():
    return render_template('analise_distribuicao_numerica.html')


@analise_distribuicao_numerica_bp.route('/api/analise/distribuicao-numerica')
def api_analise_distribuicao_numerica():
    try:
        resultado = AnaliseDistribuicaoNumericaService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

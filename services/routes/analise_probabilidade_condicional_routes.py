from flask import Blueprint, jsonify, render_template
from services.analise_probabilidade_condicional_service import AnaliseProbabilidadeCondicionalService

analise_probabilidade_condicional_bp = Blueprint('analise_probabilidade_condicional', __name__)


@analise_probabilidade_condicional_bp.route('/analise/probabilidade-condicional')
def pagina_analise_probabilidade_condicional():
    return render_template('analise_probabilidade_condicional.html')


@analise_probabilidade_condicional_bp.route('/api/analise/probabilidade-condicional')
def api_analise_probabilidade_condicional():
    try:
        resultado = AnaliseProbabilidadeCondicionalService.obter_analise_completa()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

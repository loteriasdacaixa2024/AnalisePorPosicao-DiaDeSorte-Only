from flask import Blueprint, jsonify, render_template
from services.analise_dezenas_service import AnaliseDezenasFaixasService

analise_dezenas_bp = Blueprint('analise_dezenas', __name__)

@analise_dezenas_bp.route('/analise/dezenas-faixas')
def pagina_dezenas_faixas():
    return render_template('analise_dezenas.html')

@analise_dezenas_bp.route('/api/analise/dezenas-faixas', methods=['GET'])
def obter_dezenas_faixas():
    resultado = AnaliseDezenasFaixasService.obter_distribuicao_faixas()
    return jsonify(resultado)
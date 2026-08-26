from flask import Blueprint, jsonify, render_template
from services.analise_finais_iguais_service import AnaliseFinaisIguaisService

analise_finais_iguais_bp = Blueprint('analise_finais_iguais', __name__)


@analise_finais_iguais_bp.route('/analises/finais-iguais')
def pagina_finais_iguais():
    """Página HTML de visualização da análise"""
    return render_template('analise_finais_iguais.html')


@analise_finais_iguais_bp.route('/api/analises/finais-iguais', methods=['GET'])
def api_finais_iguais():
    """
    API JSON para análise de finais iguais
    Retorna Top 3, insights e recomendações
    """
    resultado = AnaliseFinaisIguaisService.analisar_finais_iguais()
    return jsonify(resultado), 200

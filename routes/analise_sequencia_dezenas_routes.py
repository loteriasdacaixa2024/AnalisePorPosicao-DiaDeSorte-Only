from flask import Blueprint, jsonify, render_template
from services.analise_sequencia_dezenas_service import AnaliseSequenciaDezenasService

analise_sequencia_dezenas_bp = Blueprint('analise_sequencia_dezenas', __name__)


@analise_sequencia_dezenas_bp.route('/analises/sequencias-dezenas')
def pagina_sequencias():
    """Página HTML de visualização da análise"""
    return render_template('analise_sequencia_dezenas.html')


@analise_sequencia_dezenas_bp.route('/api/analises/sequencias-dezenas', methods=['GET'])
def api_sequencias():
    """
    API JSON para análise de sequências de dezenas
    Retorna Top 3, insights e recomendações
    """
    resultado = AnaliseSequenciaDezenasService.analisar_sequencias()
    return jsonify(resultado), 200

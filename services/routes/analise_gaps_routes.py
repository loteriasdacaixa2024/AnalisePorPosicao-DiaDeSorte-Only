from flask import Blueprint, jsonify, render_template
from services.analise_gaps_service import AnaliseGapsService

analise_gaps_bp = Blueprint('analise_gaps', __name__)

@analise_gaps_bp.route('/analise/gaps-distancias')
def pagina_gaps():
    """Página de análise de gaps (distâncias entre números)"""
    return render_template('analise_gaps.html')

@analise_gaps_bp.route('/api/analise/gaps-distancias', methods=['GET'])
def obter_gaps():
    """API para obter análise completa de gaps"""
    resultado = AnaliseGapsService.analisar_gaps()
    return jsonify(resultado)

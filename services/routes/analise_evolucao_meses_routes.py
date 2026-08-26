from flask import Blueprint, jsonify, render_template
from services.analise_evolucao_meses_service import AnaliseEvolucaoMesesService

analise_evolucao_meses_bp = Blueprint('analise_evolucao_meses', __name__)

@analise_evolucao_meses_bp.route('/analise/evolucao-meses')
def pagina_evolucao_meses():
    return render_template('analise_evolucao_meses.html')

@analise_evolucao_meses_bp.route('/api/analise/evolucao-meses', methods=['GET'])
def obter_evolucao_meses():
    resultado = AnaliseEvolucaoMesesService.analisar_evolucao_meses()
    return jsonify(resultado)
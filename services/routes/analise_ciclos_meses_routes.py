from flask import Blueprint, jsonify, render_template, request
from services.analise_ciclos_meses_service import AnaliseCiclosMesesService

analise_ciclos_meses_bp = Blueprint('analise_ciclos_meses', __name__)

@analise_ciclos_meses_bp.route('/analise/ciclos-meses')
def pagina_ciclos_meses():
    return render_template('analise_ciclos_meses.html')

@analise_ciclos_meses_bp.route('/api/analise/ciclos-meses', methods=['GET'])
def obter_ciclos_meses():
    resultado = AnaliseCiclosMesesService.analisar_ciclos()
    return jsonify(resultado)
from flask import Blueprint, jsonify, render_template, request
from services.analise_numeros_devidos_service import AnaliseNumerosDevidosService

analise_numeros_devidos_bp = Blueprint('analise_numeros_devidos', __name__)

@analise_numeros_devidos_bp.route('/analise/numeros-devidos')
def pagina_numeros_devidos():
    return render_template('analise_numeros_devidos.html')

@analise_numeros_devidos_bp.route('/api/analise/numeros-devidos', methods=['GET'])
def obter_numeros_devidos():
    resultado = AnaliseNumerosDevidosService.analisar_devidos()
    return jsonify(resultado)
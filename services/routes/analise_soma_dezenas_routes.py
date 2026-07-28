from flask import Blueprint, jsonify, render_template, request
from services.analise_soma_dezenas_service import AnaliseSomaDezenasService

analise_soma_dezenas_bp = Blueprint('analise_soma_dezenas', __name__)

@analise_soma_dezenas_bp.route('/analise/soma-dezenas')
def pagina_soma_dezenas():
    return render_template('analise_soma_dezenas.html')

@analise_soma_dezenas_bp.route('/api/analise/soma-dezenas', methods=['GET'])
def obter_soma_dezenas():
    resultado = AnaliseSomaDezenasService.analisar_somas()
    return jsonify(resultado)

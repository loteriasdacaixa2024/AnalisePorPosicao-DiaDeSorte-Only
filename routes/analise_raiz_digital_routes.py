from flask import Blueprint, jsonify, render_template
from services.analise_raiz_digital_service import AnaliseRaizDigitalService

analise_raiz_digital_bp = Blueprint('analise_raiz_digital', __name__)

@analise_raiz_digital_bp.route('/analise/raiz-digital')
def pagina_raiz_digital():
    return render_template('analise_raiz_digital.html')

@analise_raiz_digital_bp.route('/api/analise/raiz-digital', methods=['GET'])
def obter_raiz_digital():
    resultado = AnaliseRaizDigitalService.analisar_raiz_digital()
    return jsonify(resultado)
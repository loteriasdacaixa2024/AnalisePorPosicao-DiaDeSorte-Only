from flask import Blueprint, jsonify, render_template
from services.analise_digitos_unicos_service import AnaliseDigitosUnicosService

analise_digitos_unicos_bp = Blueprint('analise_digitos_unicos', __name__)

@analise_digitos_unicos_bp.route('/analise/digitos-unicos')
def pagina_digitos_unicos():
    return render_template('analise_digitos_unicos.html')

@analise_digitos_unicos_bp.route('/api/analise/digitos-unicos', methods=['GET'])
def obter_digitos_unicos():
    resultado = AnaliseDigitosUnicosService.analisar_digitos_unicos()
    return jsonify(resultado)
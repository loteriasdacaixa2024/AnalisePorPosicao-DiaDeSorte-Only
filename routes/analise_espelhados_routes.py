from flask import Blueprint, jsonify, render_template
from services.analise_espelhados_service import AnaliseEspelhadosService

analise_espelhados_bp = Blueprint('analise_espelhados', __name__)

@analise_espelhados_bp.route('/analise/numeros-espelhados')
def pagina_espelhados():
    return render_template('analise_espelhados.html')

@analise_espelhados_bp.route('/api/analise/numeros-espelhados', methods=['GET'])
def obter_espelhados():
    resultado = AnaliseEspelhadosService.analisar_espelhados()
    return jsonify(resultado)
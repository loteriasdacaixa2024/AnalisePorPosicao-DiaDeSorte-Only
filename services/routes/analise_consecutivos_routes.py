from flask import Blueprint, jsonify, render_template
from services.analise_consecutivos_service import AnaliseConsecutivosService

analise_consecutivos_bp = Blueprint('analise_consecutivos', __name__)

@analise_consecutivos_bp.route('/analise/numeros-consecutivos')
def pagina_consecutivos():
    return render_template('analise_consecutivos.html')

@analise_consecutivos_bp.route('/api/analise/numeros-consecutivos', methods=['GET'])
def obter_consecutivos():
    resultado = AnaliseConsecutivosService.analisar_consecutivos()
    return jsonify(resultado)
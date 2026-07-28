from flask import Blueprint, jsonify, render_template
from services.analise_repeticoes_service import AnaliseRepeticoesService

analise_repeticoes_bp = Blueprint('analise_repeticoes', __name__)

@analise_repeticoes_bp.route('/analise/numeros-repetem')
def pagina_numeros_repetem():
    return render_template('analise_repeticoes.html')

@analise_repeticoes_bp.route('/api/analise/numeros-repetem', methods=['GET'])
def obter_numeros_repetem():
    resultado = AnaliseRepeticoesService.obter_numeros_que_repetem()
    return jsonify(resultado)
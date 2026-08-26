from flask import Blueprint, jsonify, render_template
from services.analise_primos_compostos_service import AnalisePrimosCompostosService

analise_primos_compostos_bp = Blueprint('analise_primos_compostos', __name__)

@analise_primos_compostos_bp.route('/analise/primos-compostos')
def pagina_primos_compostos():
    return render_template('analise_primos_compostos.html')

@analise_primos_compostos_bp.route('/api/analise/primos-compostos', methods=['GET'])
def obter_primos_compostos():
    resultado = AnalisePrimosCompostosService.analisar_primos_compostos()
    return jsonify(resultado)

from flask import Blueprint, jsonify, render_template, request
from services.analise_matriz_probabilidade_service import AnaliseProbabilidadePosicaoService

analise_matriz_probabilidade_bp = Blueprint('analise_matriz_probabilidade', __name__)

@analise_matriz_probabilidade_bp.route('/analise/matriz-probabilidade')
def pagina_matriz_probabilidade():
    return render_template('analise_matriz_probabilidade.html')

@analise_matriz_probabilidade_bp.route('/api/analise/matriz-probabilidade', methods=['GET'])
def obter_matriz_probabilidade():
    resultado = AnaliseProbabilidadePosicaoService.calcular_matriz()
    return jsonify(resultado)
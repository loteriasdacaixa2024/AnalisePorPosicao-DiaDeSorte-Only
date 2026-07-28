from flask import Blueprint, jsonify, render_template, request
from services.analise_calculadora_probabilidade_service import AnaliseCalculadoraProbabilidadeService

analise_calculadora_probabilidade_bp = Blueprint('analise_calculadora_probabilidade', __name__)

@analise_calculadora_probabilidade_bp.route('/analise/calculadora-probabilidade')
def pagina_calculadora_probabilidade():
    return render_template('analise_calculadora_probabilidade.html')

@analise_calculadora_probabilidade_bp.route('/api/analise/calculadora-probabilidade', methods=['POST'])
def calcular_probabilidade():
    data = request.get_json()
    
    numero = data.get('numero')
    posicao = data.get('posicao')
    num_concursos = data.get('concursos')
    
    if numero is None or posicao is None or num_concursos is None:
        return jsonify({'error': 'Parâmetros obrigatórios: numero, posicao, concursos'}), 400
    
    try:
        numero = int(numero)
        posicao = int(posicao)
        num_concursos = int(num_concursos)
    except ValueError:
        return jsonify({'error': 'Parâmetros devem ser números inteiros'}), 400
    
    resultado = AnaliseCalculadoraProbabilidadeService.calcular_probabilidade(
        numero, posicao, num_concursos
    )
    
    if 'error' in resultado:
        return jsonify(resultado), 400
    
    return jsonify(resultado)
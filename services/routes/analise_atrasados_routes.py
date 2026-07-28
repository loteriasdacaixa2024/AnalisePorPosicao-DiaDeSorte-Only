from flask import Blueprint, jsonify, request, render_template
from services.analise_atrasados_service import AnaliseAtrasadosService

analise_atrasados_bp = Blueprint('analise_atrasados', __name__)

@analise_atrasados_bp.route('/api/analise/atrasados/posicao/<int:posicao>', methods=['GET'])
def obter_atrasados_por_posicao(posicao):
    top = request.args.get('top', 10, type=int)
    resultado = AnaliseAtrasadosService.obter_frequencia_por_posicao(posicao)
    
    if 'erro' in resultado:
        return jsonify(resultado), 400
    
    resultado['numeros'] = resultado['numeros'][:top]
    
    return jsonify(resultado)

@analise_atrasados_bp.route('/api/analise/atrasados/probabilidade/<int:concursos>', methods=['GET'])
def calcular_probabilidade(concursos):
    prob = AnaliseAtrasadosService.calcular_probabilidade(concursos)
    return jsonify({
        'concursos': concursos,
        'probabilidade': prob
    })

@analise_atrasados_bp.route('/analise/numeros-atrasados')
def pagina_numeros_atrasados():
    return render_template('analise_atrasados.html')
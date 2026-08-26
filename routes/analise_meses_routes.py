from flask import Blueprint, jsonify, request, render_template
from services.analise_meses_service import AnaliseMesesService

analise_meses_bp = Blueprint('analise_meses', __name__)

@analise_meses_bp.route('/api/analise/meses', methods=['GET'])
def obter_meses():
    resultado = AnaliseMesesService.obter_estatisticas_meses()
    return jsonify(resultado)

@analise_meses_bp.route('/api/analise/meses/estatisticas', methods=['GET'])
def obter_estatisticas_meses():
    resultado = AnaliseMesesService.obter_estatisticas_meses()
    return jsonify(resultado)

@analise_meses_bp.route('/api/analise/meses/probabilidade', methods=['GET'])
def calcular_probabilidade():
    concursos = request.args.get('concursos', 10, type=int)
    qtd_meses = request.args.get('qtd_meses', 1, type=int)
    prob = AnaliseMesesService.calcular_probabilidade(concursos, qtd_meses)
    return jsonify({
        'concursos': concursos,
        'qtd_meses': qtd_meses,
        'probabilidade': prob
    })

@analise_meses_bp.route('/analise/meses-atrasados')
def pagina_meses_atrasados():
    return render_template('analise_meses.html')
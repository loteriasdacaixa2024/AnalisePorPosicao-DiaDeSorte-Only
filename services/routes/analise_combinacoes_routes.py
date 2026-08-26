from flask import Blueprint, jsonify, request, render_template
from services.analise_combinacoes_service import AnaliseCombinacoesService

analise_combinacoes_bp = Blueprint('analise_combinacoes', __name__)

@analise_combinacoes_bp.route('/api/analise/combinacoes/top', methods=['GET'])
def obter_top_combinacoes():
    top = request.args.get('top', 20, type=int)
    resultado = AnaliseCombinacoesService.numeros_que_saem_juntos(top)
    return jsonify(resultado)

@analise_combinacoes_bp.route('/api/analise/combinacoes/com-numero/<int:numero>', methods=['GET'])
def obter_combinacoes_com_numero(numero):
    top = request.args.get('top', 10, type=int)
    resultado = AnaliseCombinacoesService.buscar_combinacoes_com_numero(numero, top)
    return jsonify(resultado)

@analise_combinacoes_bp.route('/analise/numeros-juntos')
def pagina_numeros_juntos():
    return render_template('analise_combinacoes.html')
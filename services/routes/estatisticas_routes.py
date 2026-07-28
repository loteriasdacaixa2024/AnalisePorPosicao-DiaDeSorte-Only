# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify, render_template
from services import EstatisticaService

estatisticas_bp = Blueprint('estatisticas', __name__)

@estatisticas_bp.route('/estatisticas')
def pagina_estatisticas():
    return render_template('estatisticas.html')

@estatisticas_bp.route('/api/estatisticas/frequencia-geral', methods=['GET'])
def frequencia_geral():
    return jsonify(EstatisticaService.frequencia_geral())

@estatisticas_bp.route('/api/estatisticas/frequencia-posicao/<int:posicao>', methods=['GET'])
def frequencia_posicao(posicao):
    return jsonify(EstatisticaService.frequencia_por_posicao(posicao))

@estatisticas_bp.route('/api/estatisticas/atrasados', methods=['GET'])
def atrasados():
    return jsonify(EstatisticaService.numeros_atrasados())

@estatisticas_bp.route('/api/estatisticas/mes-sorte', methods=['GET'])
def mes_sorte():
    return jsonify(EstatisticaService.estatisticas_mes_sorte())
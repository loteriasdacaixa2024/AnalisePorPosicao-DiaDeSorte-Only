# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify, request, render_template
from services import PalpiteService

palpites_bp = Blueprint('palpites', __name__)

@palpites_bp.route('/palpites')
def pagina_palpites():
    return render_template('palpites.html')

@palpites_bp.route('/api/palpites/gerar', methods=['GET'])
def gerar():
    tipo = request.args.get('tipo', 'inteligente')
    quantidade = int(request.args.get('quantidade', 5))
    return jsonify(PalpiteService.gerar_multiplos_palpites(quantidade, tipo))
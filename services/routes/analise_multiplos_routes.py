from flask import Blueprint, jsonify, render_template
from services.analise_multiplos_service import AnaliseMultiplosService

analise_multiplos_bp = Blueprint('analise_multiplos', __name__)

@analise_multiplos_bp.route('/analise/multiplos')
def pagina_multiplos():
    return render_template('analise_multiplos.html')

@analise_multiplos_bp.route('/api/analise/multiplos', methods=['GET'])
def obter_multiplos():
    resultado = AnaliseMultiplosService.analisar_multiplos()
    return jsonify(resultado)
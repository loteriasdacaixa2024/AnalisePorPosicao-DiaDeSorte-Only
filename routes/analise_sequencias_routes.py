from flask import Blueprint, jsonify, render_template
from services.analise_sequencias_service import AnaliseSequenciasService

analise_sequencias_bp = Blueprint('analise_sequencias', __name__)

@analise_sequencias_bp.route('/analise/sequencias')
def pagina_sequencias():
    return render_template('analise_sequencias.html')

@analise_sequencias_bp.route('/api/analise/sequencias', methods=['GET'])
def obter_sequencias():
    resultado = AnaliseSequenciasService.obter_analise_sequencias()
    return jsonify(resultado)
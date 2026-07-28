from flask import Blueprint, jsonify, render_template
from services.analise_quadrantes_service import AnaliseQuadrantesService

analise_quadrantes_bp = Blueprint('analise_quadrantes', __name__)

@analise_quadrantes_bp.route('/analise/quadrantes-volante')
def pagina_quadrantes():
    return render_template('analise_quadrantes.html')

@analise_quadrantes_bp.route('/api/analise/quadrantes-volante', methods=['GET'])
def obter_quadrantes():
    resultado = AnaliseQuadrantesService.analisar_quadrantes()
    return jsonify(resultado)
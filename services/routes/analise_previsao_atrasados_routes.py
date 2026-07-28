from flask import Blueprint, jsonify, render_template
from services.analise_previsao_atrasados_service import AnalisePrevisaoAtrasadosService

analise_previsao_atrasados_bp = Blueprint('analise_previsao_atrasados', __name__)

@analise_previsao_atrasados_bp.route('/analise/previsao-atrasados')
def pagina_previsao_atrasados():
    return render_template('analise_previsao_atrasados.html')

@analise_previsao_atrasados_bp.route('/api/analise/previsao-atrasados', methods=['GET'])
def obter_previsao_atrasados():
    resultado = AnalisePrevisaoAtrasadosService.obter_previsao_atrasados()
    return jsonify(resultado)
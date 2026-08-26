from flask import Blueprint, jsonify, render_template
from services.analise_digito_padrao_inicial_final_service import AnaliseDigitoPadraoInicialFinalService

analise_digito_padrao_inicial_final_bp = Blueprint('analise_digito_padrao_inicial_final', __name__)

@analise_digito_padrao_inicial_final_bp.route('/analise/digito-padrao-inicial-final')
def pagina_digito_padrao():
    return render_template('analise_digito_padrao_inicial_final.html')

@analise_digito_padrao_inicial_final_bp.route('/api/analise/digito-padrao-inicial-final', methods=['GET'])
def obter_digito_padrao():
    resultado = AnaliseDigitoPadraoInicialFinalService.analisar_padroes()
    return jsonify(resultado)
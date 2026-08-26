from flask import Blueprint, jsonify, render_template, request
from services.analise_defasagem_service import AnaliseDefasagemService

analise_defasagem_bp = Blueprint('analise_defasagem', __name__)

@analise_defasagem_bp.route('/analise/defasagem')
def pagina_defasagem():
    return render_template('analise_defasagem.html')

@analise_defasagem_bp.route('/api/analise/defasagem', methods=['GET'])
def obter_defasagem():
    resultado = AnaliseDefasagemService.analisar_defasagem()
    return jsonify(resultado)

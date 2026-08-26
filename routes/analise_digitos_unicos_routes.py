from flask import Blueprint, jsonify, render_template
from services.analise_digitos_unicos_service import AnaliseDigitosUnicosService

analise_digitos_unicos_bp = Blueprint('analise_digitos_unicos', __name__)

@analise_digitos_unicos_bp.route('/analise/digitos-unicos')
def pagina_digitos_unicos():
    return render_template('analise_digitos_unicos.html')

@analise_digitos_unicos_bp.route('/api/analise/digitos-unicos', methods=['GET'])
def obter_digitos_unicos():
    resultado = AnaliseDigitosUnicosService.analisar_digitos_unicos()
    return jsonify(resultado)

@analise_digitos_unicos_bp.route('/api/analise/matriz-elite', methods=['POST'])
def obter_matriz_elite():
    from flask import request
    dados = request.get_json()
    if not dados or 'relacoes' not in dados:
        return jsonify({'erro': 'Deve enviar a lista de relacoes_alvo(ex: ["7/104"]).'}), 400
    
    matriz = AnaliseDigitosUnicosService.gerar_matriz_elite(dados['relacoes'])
    return jsonify(matriz)
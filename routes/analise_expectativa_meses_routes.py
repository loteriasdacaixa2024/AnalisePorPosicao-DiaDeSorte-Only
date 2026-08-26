from flask import Blueprint, jsonify, render_template, request
from services.analise_expectativa_meses_service import AnaliseExpectativaMesesService

analise_expectativa_meses_bp = Blueprint('analise_expectativa_meses', __name__)

@analise_expectativa_meses_bp.route('/analise/expectativa-meses')
def pagina_expectativa_meses():
    return render_template('analise_expectativa_meses.html')

@analise_expectativa_meses_bp.route('/api/analise/expectativa-meses', methods=['GET'])
def obter_expectativa_meses():
    resultado = AnaliseExpectativaMesesService.obter_expectativa_meses()
    return jsonify(resultado)

@analise_expectativa_meses_bp.route('/api/analise/expectativa-meses/calcular', methods=['POST'])
def calcular_customizado():
    data = request.get_json()
    meses_selecionados = data.get('meses', [])
    num_concursos = data.get('concursos', 10)
    
    if not meses_selecionados:
        return jsonify({'error': 'Selecione pelo menos um mês'}), 400
    
    resultado = AnaliseExpectativaMesesService.calcular_probabilidade_customizada(
        meses_selecionados, 
        num_concursos
    )
    return jsonify(resultado)
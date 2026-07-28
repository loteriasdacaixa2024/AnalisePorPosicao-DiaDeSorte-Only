from flask import Blueprint, jsonify, request
from services.analise_simulador_filtros_service import AnaliseSimuladorFiltrosService

analise_simulador_filtros_bp = Blueprint('analise_simulador_filtros', __name__)

@analise_simulador_filtros_bp.route('/api/analise/simulador-filtros', methods=['POST'])
def simular_apostas_filtros():
    data = request.json
    jogos = data.get('jogos', [])
    filtro_digitos_unicos = data.get('filtro_digitos_unicos')
    
    if not jogos:
        return jsonify({'error': 'Nenhum jogo fornecido para simulação'}), 400
        
    resultado = AnaliseSimuladorFiltrosService.simular_jogos(jogos, filtro_digitos_unicos)
    
    if 'error' in resultado:
        return jsonify({'error': resultado['error']}), 400
        
    return jsonify(resultado)

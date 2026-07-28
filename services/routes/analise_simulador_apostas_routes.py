from flask import Blueprint, jsonify, render_template, request
from services.analise_simulador_apostas_service import AnaliseSimuladorApostasService

analise_simulador_apostas_bp = Blueprint('analise_simulador_apostas', __name__)

@analise_simulador_apostas_bp.route('/analise/simulador-apostas')
def pagina_simulador_apostas():
    return render_template('analise_simulador_apostas.html')

@analise_simulador_apostas_bp.route('/api/analise/simulador-apostas', methods=['POST'])
def simular_apostas():
    data = request.get_json()
    numeros = data.get('numeros', [])
    mes = data.get('mes', 1)
    concursos_limite = data.get('concursos_limite')

    resultado = AnaliseSimuladorApostasService.simular_aposta(numeros, mes, concursos_limite)
    return jsonify(resultado)
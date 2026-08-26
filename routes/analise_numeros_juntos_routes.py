from flask import Blueprint, jsonify, render_template, request
from services.analise_numeros_juntos_service import AnaliseNumerosJuntosService

analise_numeros_juntos_bp = Blueprint('analise_numeros_juntos', __name__)

@analise_numeros_juntos_bp.route('/analise/numeros-juntos')
def pagina_numeros_juntos():
    """Página de análise de números que aparecem juntos"""
    return render_template('analise_numeros_juntos.html')

@analise_numeros_juntos_bp.route('/api/analise/numeros-juntos', methods=['GET'])
def obter_numeros_juntos():
    """API para obter análise completa de números juntos"""
    resultado = AnaliseNumerosJuntosService.analisar_numeros_juntos()
    return jsonify(resultado)

@analise_numeros_juntos_bp.route('/api/analise/numeros-juntos/par', methods=['GET'])
def buscar_par():
    """API para buscar um par específico de números"""
    numero1 = request.args.get('numero1', type=int)
    numero2 = request.args.get('numero2', type=int)

    if not numero1 or not numero2:
        return jsonify({'error': 'Informe numero1 e numero2'}), 400

    if numero1 == numero2:
        return jsonify({'error': 'Os números devem ser diferentes'}), 400

    if numero1 < 1 or numero1 > 31 or numero2 < 1 or numero2 > 31:
        return jsonify({'error': 'Números devem estar entre 1 e 31'}), 400

    resultado = AnaliseNumerosJuntosService.buscar_par_especifico(numero1, numero2)
    return jsonify(resultado)

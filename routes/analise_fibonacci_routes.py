from flask import Blueprint, jsonify, render_template
from services.analise_fibonacci_service import AnaliseFibonacciService

analise_fibonacci_bp = Blueprint('analise_fibonacci', __name__)

@analise_fibonacci_bp.route('/analise/fibonacci')
def pagina_fibonacci():
    return render_template('analise_fibonacci.html')

@analise_fibonacci_bp.route('/api/analise/fibonacci', methods=['GET'])
def obter_fibonacci():
    resultado = AnaliseFibonacciService.analisar_fibonacci()
    return jsonify(resultado)
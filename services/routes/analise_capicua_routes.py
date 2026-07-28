from flask import Blueprint, jsonify, render_template
from services.analise_capicua_service import AnaliseCapicuaService

analise_capicua_bp = Blueprint('analise_capicua', __name__)

@analise_capicua_bp.route('/analise/numeros-capicua')
def pagina_capicua():
    return render_template('analise_capicua.html')

@analise_capicua_bp.route('/api/analise/numeros-capicua', methods=['GET'])
def obter_capicua():
    resultado = AnaliseCapicuaService.analisar_capicua()
    return jsonify(resultado)
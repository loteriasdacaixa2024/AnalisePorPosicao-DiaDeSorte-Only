from flask import Blueprint, jsonify, request, render_template
from services.analise_pares_impares_service import AnaliseParesImparesService

analise_pares_impares_bp = Blueprint('analise_pares_impares', __name__)


@analise_pares_impares_bp.route('/analise/pares-impares')
def pagina_pares_impares():
    return render_template('analise_pares_impares.html')


@analise_pares_impares_bp.route('/api/analise/pares-impares', methods=['GET'])
def obter_pares_impares():
    try:
        resultado = AnaliseParesImparesService.obter_distribuicao_pares_impares()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@analise_pares_impares_bp.route('/api/analise/pares-impares/historico', methods=['GET'])
def obter_historico():
    try:
        limite = request.args.get('limite', 50, type=int)
        resultado = AnaliseParesImparesService.obter_historico_recente(limite)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@analise_pares_impares_bp.route('/api/analise/pares-impares/extremos', methods=['GET'])
def obter_padroes_extremos():
    """
    Retorna os padrões extremos e quase-extremos:
    - 0P + 7I, 7P + 0I, 1P + 6I, 6P + 1I
    Com lista completa de concursos e números sorteados.
    """
    try:
        resultado = AnaliseParesImparesService.obter_padroes_extremos()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

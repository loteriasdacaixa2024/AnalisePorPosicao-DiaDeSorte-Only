from flask import Blueprint, jsonify, render_template, request
from services.gerar_fechamento_tubular_service import GerarFechamentoTubularService

gerar_fechamento_tubular_bp = Blueprint('gerar_fechamento_tubular', __name__)


@gerar_fechamento_tubular_bp.route('/ferramentas/gerar-fechamento-tubular')
def pagina_gerar_fechamento_tubular():
    return render_template('gerar_fechamento_tubular.html')


@gerar_fechamento_tubular_bp.route('/api/ferramentas/opcoes-fechamento-tubular')
def api_opcoes_fechamento():
    try:
        opcoes = GerarFechamentoTubularService.obter_opcoes_para_fechamento()
        return jsonify(opcoes), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@gerar_fechamento_tubular_bp.route('/api/ferramentas/gerar-jogos-tubular', methods=['POST'])
def api_gerar_jogos():
    try:
        parametros = request.get_json()
        resultado = GerarFechamentoTubularService.gerar_jogos(parametros)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

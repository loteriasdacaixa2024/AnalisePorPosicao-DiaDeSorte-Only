"""
Routes para Descoberta de Técnicas
"""

from flask import Blueprint, render_template, request, jsonify
from services.descobrir_tecnicas_service import descobrir_tecnicas

# Criar Blueprint
descobrir_tecnicas_bp = Blueprint('descobrir_tecnicas', __name__)


@descobrir_tecnicas_bp.route('/descobrir-tecnicas/', methods=['GET'])
def index():
    """Página principal de descoberta de técnicas"""
    return render_template('descobrir_tecnicas.html')


@descobrir_tecnicas_bp.route('/descobrir-tecnicas/analisar', methods=['POST'])
def analisar_concursos():
    """
    Endpoint para analisar concursos e descobrir técnicas

    Request JSON:
        {
            "concursoInicial": 1134,
            "concursoFinal": 1136  # opcional
        }

    Response JSON:
        {
            "sucesso": true,
            "total_concursos_analisados": 3,
            "total_tecnicas_descobertas": 15,
            "tecnicas": [...]
        }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum dado foi enviado'
            }), 400

        concurso_inicial = dados.get('concursoInicial')
        concurso_final = dados.get('concursoFinal')

        if not concurso_inicial:
            return jsonify({
                'sucesso': False,
                'erro': 'Concurso inicial é obrigatório'
            }), 400

        # Converter para inteiro
        try:
            concurso_inicial = int(concurso_inicial)
            if concurso_final:
                concurso_final = int(concurso_final)
        except ValueError:
            return jsonify({
                'sucesso': False,
                'erro': 'Números de concurso inválidos'
            }), 400

        # Validar intervalo
        if concurso_final and concurso_final < concurso_inicial:
            return jsonify({
                'sucesso': False,
                'erro': 'Concurso final deve ser maior ou igual ao inicial'
            }), 400

        # Limitar análise a no máximo 50 concursos
        if concurso_final and (concurso_final - concurso_inicial) > 50:
            return jsonify({
                'sucesso': False,
                'erro': 'Análise limitada a no máximo 50 concursos por vez'
            }), 400

        # Executar descoberta
        resultado = descobrir_tecnicas(concurso_inicial, concurso_final)

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao analisar concursos: {str(e)}'
        }), 500


@descobrir_tecnicas_bp.route('/descobrir-tecnicas/exportar-tecnicas', methods=['POST'])
def exportar_tecnicas():
    """
    Endpoint para exportar técnicas descobertas em formato JSON

    Request JSON:
        {
            "tecnicas": [...]  # Array de técnicas a exportar
        }

    Response:
        Arquivo JSON para download
    """
    try:
        dados = request.get_json()

        if not dados or 'tecnicas' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhuma técnica foi enviada para exportação'
            }), 400

        tecnicas = dados['tecnicas']

        # Criar estrutura de exportação
        exportacao = {
            'versao': '1.0',
            'data_exportacao': datetime.now().isoformat(),
            'total_tecnicas': len(tecnicas),
            'tecnicas': tecnicas
        }

        return jsonify(exportacao), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao exportar técnicas: {str(e)}'
        }), 500

from flask import Blueprint, jsonify, request
from services.atualizar_premiacao_service import AtualizarPremiacaoService

atualizar_premiacao_bp = Blueprint('atualizar_premiacao', __name__)


@atualizar_premiacao_bp.route('/api/atualizar-premiacao/ultimo', methods=['POST'])
def atualizar_ultimo():
    """
    API para atualizar o último concurso com dados de premiação
    """
    try:
        resultado = AtualizarPremiacaoService.atualizar_ultimo_concurso()

        if resultado['sucesso']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao atualizar último concurso: {str(e)}'
        }), 500


@atualizar_premiacao_bp.route('/api/atualizar-premiacao/concurso/<int:numero_concurso>', methods=['POST'])
def atualizar_concurso_especifico(numero_concurso):
    """
    API para atualizar um concurso específico

    Parâmetro:
        numero_concurso: Número do concurso
    """
    try:
        resultado = AtualizarPremiacaoService.atualizar_concurso(numero_concurso)

        if resultado['sucesso']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao atualizar concurso: {str(e)}'
        }), 500


@atualizar_premiacao_bp.route('/api/atualizar-premiacao/lote', methods=['POST'])
def atualizar_lote():
    """
    API para atualizar múltiplos concursos em lote

    Body JSON:
    {
        "concurso_inicial": 1,
        "concurso_final": 100
    }
    """
    try:
        dados = request.get_json()

        if not dados or 'concurso_inicial' not in dados or 'concurso_final' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campos "concurso_inicial" e "concurso_final" são obrigatórios'
            }), 400

        inicial = int(dados['concurso_inicial'])
        final = int(dados['concurso_final'])

        if inicial > final:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Concurso inicial deve ser menor ou igual ao final'
            }), 400

        if (final - inicial) > 500:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Limite de 500 concursos por requisição'
            }), 400

        resultado = AtualizarPremiacaoService.atualizar_multiplos_concursos(inicial, final)

        return jsonify(resultado), 200

    except ValueError:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Valores inválidos'
        }), 400
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao atualizar lote: {str(e)}'
        }), 500


@atualizar_premiacao_bp.route('/api/atualizar-premiacao/todos-sem-dados', methods=['POST'])
def atualizar_todos_sem_premiacao():
    """
    API para atualizar todos os concursos que não têm dados de premiação
    """
    try:
        resultado = AtualizarPremiacaoService.atualizar_todos_sem_premiacao()

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao atualizar concursos: {str(e)}'
        }), 500

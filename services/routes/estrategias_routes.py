"""
Routes para gerenciamento de estratégias dinâmicas de apostas
"""

from flask import Blueprint, jsonify, request, render_template
from services.estrategias_service import EstrategiasService

estrategias_bp = Blueprint('estrategias', __name__)


@estrategias_bp.route('/estrategias-dinamicas')
def pagina_estrategias():
    """Página de gerenciamento de estratégias"""
    return render_template('estrategias_dinamicas.html')


@estrategias_bp.route('/api/estrategias', methods=['GET'])
def listar_estrategias():
    """
    Lista todas as estratégias

    GET /api/estrategias

    Returns:
        JSON com lista de estratégias
    """
    try:
        estrategias = EstrategiasService.listar_todas()
        return jsonify(estrategias), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@estrategias_bp.route('/api/estrategias/<estrategia_id>', methods=['GET'])
def buscar_estrategia(estrategia_id):
    """
    Busca estratégia por ID

    GET /api/estrategias/:id

    Returns:
        JSON com estratégia ou erro 404
    """
    try:
        estrategia = EstrategiasService.buscar_por_id(estrategia_id)

        if not estrategia:
            return jsonify({'erro': 'Estratégia não encontrada'}), 404

        return jsonify(estrategia), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@estrategias_bp.route('/api/estrategias', methods=['POST'])
def adicionar_estrategia():
    """
    Adiciona nova estratégia

    POST /api/estrategias
    Body: {id, nome, descricao, parametros}

    Returns:
        JSON com estratégia criada ou erro
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        campos_obrigatorios = ['id', 'nome', 'descricao', 'parametros']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({'erro': f'Campo obrigatório: {campo}'}), 400

        resultado = EstrategiasService.adicionar(dados)

        if 'erro' in resultado:
            return jsonify(resultado), 400

        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@estrategias_bp.route('/api/estrategias/<estrategia_id>', methods=['PUT'])
def atualizar_estrategia(estrategia_id):
    """
    Atualiza estratégia existente

    PUT /api/estrategias/:id
    Body: {nome, descricao, parametros}

    Returns:
        JSON com estratégia atualizada ou erro
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        resultado = EstrategiasService.atualizar(estrategia_id, dados)

        if 'erro' in resultado:
            return jsonify(resultado), 404

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@estrategias_bp.route('/api/estrategias/<estrategia_id>', methods=['DELETE'])
def excluir_estrategia(estrategia_id):
    """
    Exclui estratégia

    DELETE /api/estrategias/:id

    Returns:
        JSON com sucesso ou erro
    """
    try:
        resultado = EstrategiasService.excluir(estrategia_id)

        if 'erro' in resultado:
            return jsonify(resultado), 404

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@estrategias_bp.route('/api/estrategias/<estrategia_id>/validar', methods=['POST'])
def validar_jogo_com_estrategia(estrategia_id):
    """
    Valida se um jogo atende aos critérios de uma estratégia

    POST /api/estrategias/:id/validar
    Body: {numeros: [1, 5, 10, 15, 20, 25, 30]}

    Returns:
        JSON com resultado da validação
    """
    try:
        dados = request.get_json()

        if not dados or 'numeros' not in dados:
            return jsonify({'erro': 'Campo "numeros" é obrigatório'}), 400

        numeros = dados['numeros']

        if not isinstance(numeros, list) or len(numeros) != 7:
            return jsonify({'erro': 'O campo "numeros" deve ser uma lista com 7 números'}), 400

        resultado = EstrategiasService.validar_jogo_com_estrategia(numeros, estrategia_id)

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

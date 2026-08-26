"""
Routes para a Central de Garantias
Unifica as funcionalidades de Estratégias Dinâmicas e Apostas com Garantia
"""

from flask import Blueprint, jsonify, request, render_template
from services.estrategias_service import EstrategiasService
from services.garantias_service import GarantiasService

central_garantias_bp = Blueprint('central_garantias', __name__)


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@central_garantias_bp.route('/central-garantias')
def pagina_central_garantias():
    """
    Página unificada da Central de Garantias
    Combina Estratégias Dinâmicas e Tabela de Garantias
    """
    return render_template('central_garantias.html')


# ============================================================
# API - ESTRATÉGIAS DINÂMICAS
# ============================================================

@central_garantias_bp.route('/api/estrategias', methods=['GET'])
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


@central_garantias_bp.route('/api/estrategias/<estrategia_id>', methods=['GET'])
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


@central_garantias_bp.route('/api/estrategias', methods=['POST'])
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


@central_garantias_bp.route('/api/estrategias/<estrategia_id>', methods=['PUT'])
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


@central_garantias_bp.route('/api/estrategias/<estrategia_id>', methods=['DELETE'])
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


@central_garantias_bp.route('/api/estrategias/<estrategia_id>/validar', methods=['POST'])
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


# ============================================================
# API - GARANTIAS DE APOSTAS
# ============================================================

@central_garantias_bp.route('/api/garantias', methods=['GET'])
def listar_garantias():
    """
    Lista todas as garantias

    GET /api/garantias

    Returns:
        JSON com lista de garantias
    """
    try:
        garantias = GarantiasService.listar_todas()
        return jsonify(garantias), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_garantias_bp.route('/api/garantias/<int:garantia_id>', methods=['GET'])
def buscar_garantia(garantia_id):
    """
    Busca garantia por ID

    GET /api/garantias/:id

    Returns:
        JSON com garantia ou erro 404
    """
    try:
        garantia = GarantiasService.buscar_por_id(garantia_id)

        if not garantia:
            return jsonify({'erro': 'Garantia não encontrada'}), 404

        return jsonify(garantia), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_garantias_bp.route('/api/garantias', methods=['POST'])
def adicionar_garantia():
    """
    Adiciona nova garantia

    POST /api/garantias
    Body: {dezenas, apostas, garantia, observacao}

    Returns:
        JSON com garantia criada ou erro
    """
    try:
        dados = request.get_json()

        # Validações
        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        if 'dezenas' not in dados or 'apostas' not in dados or 'garantia' not in dados:
            return jsonify({'erro': 'Campos obrigatórios: dezenas, apostas, garantia'}), 400

        resultado = GarantiasService.adicionar(dados)

        if 'erro' in resultado:
            return jsonify(resultado), 400

        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_garantias_bp.route('/api/garantias/<int:garantia_id>', methods=['PUT'])
def atualizar_garantia(garantia_id):
    """
    Atualiza garantia existente

    PUT /api/garantias/:id
    Body: {dezenas, apostas, garantia, observacao}

    Returns:
        JSON com garantia atualizada ou erro
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        resultado = GarantiasService.atualizar(garantia_id, dados)

        if 'erro' in resultado:
            return jsonify(resultado), 404

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_garantias_bp.route('/api/garantias/<int:garantia_id>', methods=['DELETE'])
def excluir_garantia(garantia_id):
    """
    Exclui garantia

    DELETE /api/garantias/:id

    Returns:
        JSON com sucesso ou erro
    """
    try:
        resultado = GarantiasService.excluir(garantia_id)

        if 'erro' in resultado:
            return jsonify(resultado), 404

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_garantias_bp.route('/api/garantias/calcular-custo', methods=['POST'])
def calcular_custo():
    """
    Calcula custo total baseado no número de dezenas

    POST /api/garantias/calcular-custo
    Body: {dezenas, valor_aposta}

    Returns:
        JSON com informações de custo
    """
    try:
        dados = request.get_json()

        if not dados or 'dezenas' not in dados:
            return jsonify({'erro': 'Campo "dezenas" é obrigatório'}), 400

        num_dezenas = dados['dezenas']
        valor_aposta = dados.get('valor_aposta', 2.50)

        resultado = GarantiasService.calcular_custo(num_dezenas, valor_aposta)

        if 'erro' in resultado:
            return jsonify(resultado), 404

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

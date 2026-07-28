"""
Routes para gerenciamento de garantias de apostas
"""

from flask import Blueprint, jsonify, request, render_template
from services.garantias_service import GarantiasService

garantias_bp = Blueprint('garantias', __name__)


@garantias_bp.route('/apostas-com-garantia')
def pagina_garantias():
    """Página de gerenciamento de garantias"""
    return render_template('apostas_com_garantia.html')


@garantias_bp.route('/api/garantias', methods=['GET'])
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


@garantias_bp.route('/api/garantias/<int:garantia_id>', methods=['GET'])
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


@garantias_bp.route('/api/garantias', methods=['POST'])
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


@garantias_bp.route('/api/garantias/<int:garantia_id>', methods=['PUT'])
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


@garantias_bp.route('/api/garantias/<int:garantia_id>', methods=['DELETE'])
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


@garantias_bp.route('/api/garantias/calcular-custo', methods=['POST'])
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

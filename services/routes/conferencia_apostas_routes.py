"""
Routes para conferência de apostas pós-sorteio
"""

from flask import Blueprint, jsonify, request, render_template
from services.conferencia_apostas_service import ConferenciaApostasService

conferencia_apostas_bp = Blueprint('conferencia_apostas', __name__)


@conferencia_apostas_bp.route('/conferencia-pos-apostas')
def pagina_conferencia():
    """Página de conferência de apostas"""
    return render_template('conferencia_pos_apostas.html')


@conferencia_apostas_bp.route('/api/conferencia/colunas', methods=['GET'])
def listar_colunas():
    """Lista colunas adicionais"""
    try:
        colunas = ConferenciaApostasService.listar_colunas_adicionais()
        return jsonify(colunas), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@conferencia_apostas_bp.route('/api/conferencia/colunas', methods=['POST'])
def adicionar_coluna():
    """Adiciona nova coluna adicional"""
    try:
        dados = request.get_json()

        if not dados or 'nome' not in dados:
            return jsonify({'erro': 'Campo "nome" é obrigatório'}), 400

        nova_coluna = ConferenciaApostasService.adicionar_coluna(
            dados['nome'],
            dados.get('tipo', 'text'),
            dados.get('descricao', '')
        )

        return jsonify(nova_coluna), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@conferencia_apostas_bp.route('/api/conferencia/colunas/<coluna_id>', methods=['DELETE'])
def remover_coluna(coluna_id):
    """Remove coluna adicional"""
    try:
        resultado = ConferenciaApostasService.remover_coluna(coluna_id)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@conferencia_apostas_bp.route('/api/conferencia/normalizar', methods=['POST'])
def normalizar_jogo():
    """Normaliza entrada de jogo com vários formatos"""
    try:
        dados = request.get_json()

        if not dados or 'texto' not in dados:
            return jsonify({'erro': 'Campo "texto" é obrigatório'}), 400

        resultado = ConferenciaApostasService.normalizar_combinacao(dados['texto'])

        if not resultado:
            return jsonify({'erro': 'Formato inválido'}), 400

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@conferencia_apostas_bp.route('/api/conferencia/validar-jogo', methods=['POST'])
def validar_jogo():
    """Valida um jogo"""
    try:
        dados = request.get_json()

        if not dados or 'numeros' not in dados:
            return jsonify({'erro': 'Campo "numeros" é obrigatório'}), 400

        resultado = ConferenciaApostasService.validar_jogo(
            dados['numeros'],
            dados.get('mes')
        )
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@conferencia_apostas_bp.route('/api/conferencia/analisar-jogo', methods=['POST'])
def analisar_jogo():
    """Analisa características de um jogo"""
    try:
        dados = request.get_json()

        if not dados or 'numeros' not in dados:
            return jsonify({'erro': 'Campo "numeros" é obrigatório'}), 400

        validacao = ConferenciaApostasService.validar_jogo(
            dados['numeros'],
            dados.get('mes')
        )
        if not validacao['valido']:
            return jsonify(validacao), 400

        analise = ConferenciaApostasService.analisar_jogo(
            dados['numeros'],
            dados.get('mes'),
            dados.get('concurso_numero')
        )
        return jsonify(analise), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@conferencia_apostas_bp.route('/api/conferencia/conferir', methods=['POST'])
def conferir_jogos():
    """
    Confere jogos com resultado de um concurso

    POST /api/conferencia/conferir
    Body: {
        jogos: [
            {numeros: [1,2,3,4,5,6,7], mes: 1},
            {numeros: [8,9,10,11,12,13,14], mes: 2},
            ...
        ],
        concurso: 1133,
        valor_aposta: 2.50
    }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        if 'jogos' not in dados or 'concurso' not in dados:
            return jsonify({'erro': 'Campos "jogos" e "concurso" são obrigatórios'}), 400

        jogos = dados['jogos']
        concurso = dados['concurso']
        valor_aposta = dados.get('valor_aposta', 2.50)

        for idx, jogo in enumerate(jogos):
            numeros = jogo.get('numeros', jogo) if isinstance(jogo, dict) else jogo
            mes = jogo.get('mes') if isinstance(jogo, dict) else None

            validacao = ConferenciaApostasService.validar_jogo(numeros, mes)
            if not validacao['valido']:
                return jsonify({
                    'erro': f"Jogo {idx + 1}: {validacao['erro']}"
                }), 400

        resultado = ConferenciaApostasService.conferir_multiplos_jogos(
            jogos,
            concurso,
            valor_aposta
        )

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@conferencia_apostas_bp.route('/api/conferencia/concursos', methods=['GET'])
def listar_concursos():
    """Lista concursos disponíveis para conferência (TODOS do primeiro ao último)"""
    try:
        concursos = ConferenciaApostasService.listar_concursos_disponiveis()
        return jsonify(concursos), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

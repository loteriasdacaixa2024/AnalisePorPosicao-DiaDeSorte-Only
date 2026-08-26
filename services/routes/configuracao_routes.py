# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify, render_template, request
from services.configuracao_service import ConfiguracaoService

configuracao_bp = Blueprint('configuracao', __name__)


@configuracao_bp.route('/sistema/configuracoes')
def pagina_configuracoes():
    """Página de configurações do sistema"""
    return render_template('configuracoes.html')


@configuracao_bp.route('/api/configuracoes/listar', methods=['GET'])
def listar_configuracoes():
    """
    API para listar todas as configurações

    Returns:
        JSON com lista de configurações
    """
    try:
        configuracoes = ConfiguracaoService.listar_todas()

        return jsonify({
            'sucesso': True,
            'configuracoes': configuracoes
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao listar configurações: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/obter/<chave>', methods=['GET'])
def obter_configuracao(chave):
    """
    API para obter uma configuração específica

    Args:
        chave: Chave da configuração

    Returns:
        JSON com a configuração
    """
    try:
        valor = ConfiguracaoService.obter_configuracao(chave)

        if valor is None:
            return jsonify({
                'sucesso': False,
                'mensagem': f'Configuração "{chave}" não encontrada'
            }), 404

        return jsonify({
            'sucesso': True,
            'chave': chave,
            'valor': valor
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter configuração: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/valor-aposta', methods=['GET'])
def obter_valor_aposta():
    """
    API para obter o valor da aposta mínima

    Returns:
        JSON com o valor da aposta
    """
    try:
        valor = ConfiguracaoService.obter_valor_aposta()

        return jsonify({
            'sucesso': True,
            'valor_aposta': valor
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter valor da aposta: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/salvar', methods=['POST'])
def salvar_configuracao():
    """
    API para salvar ou atualizar uma configuração

    Body JSON:
    {
        "chave": "nome_da_configuracao",
        "valor": "valor",
        "tipo": "string",  // opcional: string, float, int, boolean
        "descricao": "Descrição da configuração"  // opcional
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados or 'chave' not in dados or 'valor' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campos "chave" e "valor" são obrigatórios'
            }), 400

        chave = dados['chave']
        valor = dados['valor']
        tipo = dados.get('tipo', 'string')
        descricao = dados.get('descricao')

        resultado = ConfiguracaoService.salvar_configuracao(chave, valor, tipo, descricao)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar configuração: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/salvar-valor-aposta', methods=['POST'])
def salvar_valor_aposta():
    """
    API para salvar o valor da aposta mínima

    Body JSON:
    {
        "valor": 2.50
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados or 'valor' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campo "valor" é obrigatório'
            }), 400

        valor = dados['valor']

        resultado = ConfiguracaoService.salvar_valor_aposta(valor)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar valor da aposta: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/excluir/<chave>', methods=['DELETE'])
def excluir_configuracao(chave):
    """
    API para excluir uma configuração

    Args:
        chave: Chave da configuração a ser excluída

    Returns:
        JSON com resultado da operação
    """
    try:
        resultado = ConfiguracaoService.excluir_configuracao(chave)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao excluir configuração: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/cores-meses', methods=['GET'])
def obter_cores_meses():
    """
    API para obter as cores configuradas dos 12 meses
    NÃO retorna fallback - as cores devem estar configuradas no banco

    Returns:
        JSON com cores dos meses (1-12) ou vazio se não configuradas
    """
    try:
        cores = {}
        for mes in range(1, 13):
            chave = f'cor_mes_{mes}'
            cor = ConfiguracaoService.obter_configuracao(chave)
            if cor:
                cores[str(mes)] = cor

        # Retorna cores do banco (pode estar vazio se não configuradas)
        return jsonify({
            'sucesso': True,
            'cores_meses': cores
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter cores dos meses: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/premios-fixos', methods=['GET'])
def obter_premios_fixos():
    """
    API para obter os valores dos prêmios fixos

    Returns:
        JSON com valores dos prêmios fixos (4, 5 acertos e mês da sorte)
    """
    try:
        premios = ConfiguracaoService.obter_premios_fixos()

        return jsonify({
            'sucesso': True,
            'premios_fixos': premios
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter prêmios fixos: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/salvar-premios', methods=['POST'])
def salvar_premios():
    """
    API para salvar os valores dos prêmios fixos

    Body JSON:
    {
        "premio_4_acertos": 5.00,
        "premio_5_acertos": 25.00,
        "premio_mes_sorte": 2.50
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum dado fornecido'
            }), 400

        premio_4 = dados.get('premio_4_acertos', 5.00)
        premio_5 = dados.get('premio_5_acertos', 25.00)
        premio_mes = dados.get('premio_mes_sorte', 2.50)

        resultado = ConfiguracaoService.salvar_premios_fixos(premio_4, premio_5, premio_mes)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar prêmios fixos: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/inicializar', methods=['POST'])
def inicializar_configuracoes():
    """
    API para inicializar configurações padrão do sistema

    Returns:
        JSON com resultado da operação
    """
    try:
        sucesso = ConfiguracaoService.inicializar_configuracoes()

        if sucesso:
            return jsonify({
                'sucesso': True,
                'mensagem': 'Configurações padrão inicializadas com sucesso'
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Erro ao inicializar configurações padrão'
            }), 500

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao inicializar configurações: {str(e)}'
        }), 500


# ========================================================================
# ANÁLISES CONFIGURATION ENDPOINTS
# ========================================================================

@configuracao_bp.route('/api/configuracoes/analises', methods=['GET'])
def obter_analises():
    """
    API para obter o status de todas as análises

    Returns:
        JSON com dicionário de análises ativas/inativas
    """
    try:
        analises = ConfiguracaoService.obter_analises_ativas()

        return jsonify({
            'sucesso': True,
            'analises': analises
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter análises: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/analises/salvar', methods=['POST'])
def salvar_analises():
    """
    API para salvar múltiplas configurações de análises

    Body JSON:
    {
        "analise_gaps": true,
        "analise_atrasados": false,
        ...
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum dado fornecido'
            }), 400

        resultado = ConfiguracaoService.salvar_analises(dados)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar análises: {str(e)}'
        }), 500


# ========================================================================
# DATABASE UPDATE ENDPOINTS
# ========================================================================

@configuracao_bp.route('/api/configuracoes/status-banco', methods=['GET'])
def obter_status_banco():
    """
    API para obter o status atual do banco de dados

    Returns:
        JSON com informações do banco (último concurso, data, total, etc)
    """
    try:
        status = ConfiguracaoService.obter_status_banco()

        if status['sucesso']:
            return jsonify(status)
        else:
            return jsonify(status), 500

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter status do banco: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/atualizar-banco', methods=['POST'])
def atualizar_banco():
    """
    API para atualizar o banco de dados com informações da API Caixa

    Body JSON:
    {
        "tipo": "ultimo" | "especifico" | "range" | "todos",
        "numero": 1098,  // para tipo "especifico"
        "inicio": 1000,  // para tipo "range"
        "fim": 1133      // para tipo "range"
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados or 'tipo' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campo "tipo" é obrigatório'
            }), 400

        tipo = dados['tipo']

        # Valida o tipo
        if tipo not in ['ultimo', 'especifico', 'range', 'todos']:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Tipo inválido. Use: ultimo, especifico, range ou todos'
            }), 400

        # Processa conforme o tipo
        if tipo == 'ultimo':
            resultado = ConfiguracaoService.atualizar_ultimo_concurso()

        elif tipo == 'especifico':
            if 'numero' not in dados:
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Campo "numero" é obrigatório para tipo "especifico"'
                }), 400
            resultado = ConfiguracaoService.atualizar_concurso_especifico(dados['numero'])

        elif tipo == 'range':
            if 'inicio' not in dados or 'fim' not in dados:
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Campos "inicio" e "fim" são obrigatórios para tipo "range"'
                }), 400
            resultado = ConfiguracaoService.atualizar_range_concursos(dados['inicio'], dados['fim'])

        elif tipo == 'todos':
            resultado = ConfiguracaoService.atualizar_todos_concursos()

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 500

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao atualizar banco: {str(e)}'
        }), 500

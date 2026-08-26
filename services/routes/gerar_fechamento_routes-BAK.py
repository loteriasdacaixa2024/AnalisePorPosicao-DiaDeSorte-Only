# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify, render_template, request
from services.gerar_fechamento_service import GerarFechamentoService
from services.configuracao_service import ConfiguracaoService

gerar_fechamento_bp = Blueprint('gerar_fechamento', __name__)


@gerar_fechamento_bp.route('/ferramentas/gerar-fechamento')
def pagina_gerar_fechamento():
    """Página do gerador de fechamento"""
    return render_template('gerar_fechamento_v2.html')


@gerar_fechamento_bp.route('/api/gerar-fechamento/ultimo-sorteio', methods=['GET'])
def obter_ultimo_sorteio():
    """
    API para obter dados do último sorteio

    Returns:
        JSON com dados do último sorteio
    """
    try:
        ultimo = GerarFechamentoService.obter_ultimo_sorteio()

        if ultimo:
            return jsonify({
                'sucesso': True,
                'sorteio': ultimo
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum sorteio encontrado'
            }), 404

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter último sorteio: {str(e)}'
        }), 500


@gerar_fechamento_bp.route('/api/gerar-fechamento/valor-aposta', methods=['GET'])
def obter_valor_aposta():
    """
    API para obter o valor da aposta configurado no sistema

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


@gerar_fechamento_bp.route('/api/gerar-fechamento/gerar', methods=['POST'])
def gerar_fechamentos():
    """
    API para gerar jogos com fechamento

    Body JSON:
    {
        "numeros_minimalistas": [1, 5, 7, 10, 12, 15, 18, 20, 23, 25, 28, 31],
        "quantidade": 15,
        "dezenas_por_jogo": 7,
        "mes": "Janeiro",  // ou "atrasado" ou "aleatorio"
        "min_finais_iguais": 2,
        "min_sequencias": 2,
        "min_repetidos": 2,
        "digitos_unicos_soma": 7
    }

    Returns:
        JSON com jogos gerados
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Dados inválidos'
            }), 400

        # Validações básicas
        if 'numeros_minimalistas' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campo "numeros_minimalistas" é obrigatório'
            }), 400

        numeros_minimalistas = dados['numeros_minimalistas']
        quantidade = int(dados.get('quantidade', 15))
        dezenas_por_jogo = int(dados.get('dezenas_por_jogo', 7))

        # Configuração dos filtros (valores padrão)
        configuracao = {
            'min_finais_iguais': int(dados.get('min_finais_iguais', 2)),
            'min_sequencias': int(dados.get('min_sequencias', 2)),
            'min_repetidos': int(dados.get('min_repetidos', 2)),
            'digitos_unicos_soma': int(dados.get('digitos_unicos_soma', 7))
        }

        # Gera os jogos
        resultado = GerarFechamentoService.gerar_multiplos_jogos(
            numeros_minimalistas,
            quantidade,
            dezenas_por_jogo,
            configuracao
        )

        # Busca o valor da aposta do banco de dados
        valor_aposta = ConfiguracaoService.obter_valor_aposta()

        # Adiciona informações financeiras
        resultado['custo_unitario'] = valor_aposta
        resultado['custo_total'] = len(resultado['jogos']) * valor_aposta

        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })

    except ValueError as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Valor inválido: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao gerar jogos: {str(e)}'
        }), 500

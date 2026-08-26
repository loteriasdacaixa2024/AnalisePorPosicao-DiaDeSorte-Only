from flask import Blueprint, jsonify, render_template, request
from services.valores_probabilidades_service import ValoresProbabilidadesService

valores_probabilidades_bp = Blueprint('valores_probabilidades', __name__)


@valores_probabilidades_bp.route('/analise/valores-probabilidades')
def pagina_valores_probabilidades():
    """Página de valores e probabilidades"""
    return render_template('valores_probabilidades.html')


@valores_probabilidades_bp.route('/api/valores-probabilidades/calcular', methods=['POST'])
def calcular_valores():
    """
    API para calcular valores de apostas baseado no valor base

    Body JSON:
    {
        "valor_base": 2.50
    }
    """
    try:
        dados = request.get_json()

        if not dados or 'valor_base' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campo "valor_base" é obrigatório'
            }), 400

        valor_base = float(dados['valor_base'])

        if valor_base <= 0:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Valor base deve ser maior que zero'
            }), 400

        resultado = ValoresProbabilidadesService.calcular_valores_apostas(valor_base)

        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })

    except ValueError:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Valor base inválido'
        }), 400
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao calcular valores: {str(e)}'
        }), 500


@valores_probabilidades_bp.route('/api/valores-probabilidades/probabilidades', methods=['GET'])
def obter_probabilidades():
    """API para obter todas as probabilidades"""
    try:
        probabilidades = ValoresProbabilidadesService.obter_probabilidades()

        return jsonify({
            'sucesso': True,
            'probabilidades': probabilidades
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter probabilidades: {str(e)}'
        }), 500


@valores_probabilidades_bp.route('/api/valores-probabilidades/premios-fixos', methods=['GET'])
def obter_premios_fixos():
    """API para obter valores dos prêmios fixos"""
    try:
        premios = ValoresProbabilidadesService.obter_premios_fixos()

        return jsonify({
            'sucesso': True,
            'premios_fixos': premios
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter prêmios fixos: {str(e)}'
        }), 500


@valores_probabilidades_bp.route('/api/valores-probabilidades/quantidade-premios/<int:quantidade_numeros>', methods=['GET'])
def obter_quantidade_premios(quantidade_numeros):
    """
    API para obter quantidade de prêmios por faixa

    Parâmetro:
        quantidade_numeros: 7-15
    """
    try:
        if quantidade_numeros < 7 or quantidade_numeros > 15:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Quantidade de números deve estar entre 7 e 15'
            }), 400

        premios = ValoresProbabilidadesService.calcular_quantidade_premios(quantidade_numeros)

        return jsonify({
            'sucesso': True,
            'quantidade_numeros': quantidade_numeros,
            'premios': premios
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter quantidade de prêmios: {str(e)}'
        }), 500


@valores_probabilidades_bp.route('/api/valores-probabilidades/tabela-completa', methods=['POST'])
def obter_tabela_completa():
    """
    API para obter tabela completa com valores, probabilidades e prêmios

    Body JSON (opcional):
    {
        "valor_base": 2.50
    }
    """
    try:
        dados = request.get_json() or {}
        valor_base = float(dados.get('valor_base', 2.50))

        if valor_base <= 0:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Valor base deve ser maior que zero'
            }), 400

        tabela = ValoresProbabilidadesService.obter_tabela_completa(valor_base)

        return jsonify({
            'sucesso': True,
            'tabela': tabela
        })

    except ValueError:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Valor base inválido'
        }), 400
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter tabela completa: {str(e)}'
        }), 500


@valores_probabilidades_bp.route('/api/valores-probabilidades/estimar-premio', methods=['POST'])
def estimar_premio():
    """
    API para estimar valor de prêmio baseado na arrecadação

    Body JSON:
    {
        "quantidade_acertos": 7,
        "quantidade_numeros": 7,
        "valor_arrecadado": 5000000.00
    }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Dados inválidos'
            }), 400

        quantidade_acertos = int(dados.get('quantidade_acertos', 0))
        quantidade_numeros = int(dados.get('quantidade_numeros', 7))
        valor_arrecadado = float(dados.get('valor_arrecadado', 0))

        if quantidade_acertos not in [4, 5, 6, 7]:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Quantidade de acertos deve ser 4, 5, 6 ou 7'
            }), 400

        if quantidade_numeros < 7 or quantidade_numeros > 15:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Quantidade de números deve estar entre 7 e 15'
            }), 400

        estimativa = ValoresProbabilidadesService.calcular_valor_estimado_premio(
            quantidade_acertos,
            quantidade_numeros,
            valor_arrecadado
        )

        return jsonify({
            'sucesso': True,
            'estimativa': estimativa
        })

    except ValueError:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Valores inválidos'
        }), 400
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao estimar prêmio: {str(e)}'
        }), 500

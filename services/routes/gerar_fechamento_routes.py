# -*- coding: utf-8 -*-
"""
Rotas para a funcionalidade de Gerar Fechamento
"""

from flask import Blueprint, jsonify, render_template, request
from services.gerar_fechamento_service import GerarFechamentoService

gerar_fechamento_bp = Blueprint('gerar_fechamento', __name__)


@gerar_fechamento_bp.route('/ferramentas/gerar-fechamento')
def pagina_gerar_fechamento():
    """Página principal de geração de fechamentos"""
    return render_template('gerar_fechamento_v2.html')


@gerar_fechamento_bp.route('/api/ferramentas/calcular-valor-aposta', methods=['POST'])
def api_calcular_valor_aposta():
    """
    Calcula o valor da aposta baseado na quantidade de dezenas

    Body JSON esperado:
    {
        "quantidade_dezenas": 7
    }

    Resposta JSON:
    {
        "quantidade_dezenas": 7,
        "valor_unitario": 2.50,
        "numero_combinacoes": 1
    }
    """
    try:
        dados = request.get_json()
        quantidade_dezenas = dados.get('quantidade_dezenas', 7)

        # Valida quantidade
        if not isinstance(quantidade_dezenas, int) or quantidade_dezenas < 7 or quantidade_dezenas > 15:
            return jsonify({
                'erro': 'Quantidade de dezenas inválida. Deve ser entre 7 e 15.'
            }), 400

        # Calcula valor
        valor_unitario = GerarFechamentoService.calcular_valor_aposta(quantidade_dezenas)

        # Obtém número de combinações
        from services.valores_probabilidades_service import ValoresProbabilidadesService
        from services.configuracao_service import ConfiguracaoService

        valor_base = ConfiguracaoService.obter_valor_aposta()
        dados_valores = ValoresProbabilidadesService.calcular_valores_apostas(valor_base)

        return jsonify({
            'quantidade_dezenas': quantidade_dezenas,
            'valor_unitario': valor_unitario,
            'valor_base': valor_base,
            'numero_combinacoes': dados_valores['combinacoes'][quantidade_dezenas]
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@gerar_fechamento_bp.route('/api/ferramentas/gerar-jogos', methods=['POST'])
def api_gerar_jogos():
    """
    Gera múltiplos jogos baseado nos parâmetros fornecidos

    Body JSON esperado:
    {
        "quantidade": 10,
        "dezenas_por_jogo": 7,
        "config": {
            "min_finais_iguais": 2,
            "min_sequencias": 2,
            "min_repeticoes_anterior": 2,
            "min_digitos_unicos": 7,
            "max_digitos_unicos": 7
        }
    }

    Resposta JSON:
    {
        "sucesso": true,
        "jogos": [...],
        "total": 10,
        "dezenas_por_jogo": 7,
        "valor_unitario": 2.50,
        "valor_total": 25.00,
        "configuracao": {...},
        "ultimo_sorteio": {...}
    }
    """
    try:
        parametros = request.get_json()

        quantidade = parametros.get('quantidade', 1)
        dezenas_por_jogo = parametros.get('dezenas_por_jogo', 7)
        config = parametros.get('config', None)

        # Valida parâmetros
        if not isinstance(quantidade, int) or quantidade < 1 or quantidade > 100:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Quantidade inválida. Deve ser entre 1 e 100.'
            }), 400

        if not isinstance(dezenas_por_jogo, int) or dezenas_por_jogo < 7 or dezenas_por_jogo > 15:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Quantidade de dezenas por jogo inválida. Deve ser entre 7 e 15.'
            }), 400

        # Gera jogos
        resultado = GerarFechamentoService.gerar_multiplos_jogos(
            quantidade=quantidade,
            config=config,
            dezenas_por_jogo=dezenas_por_jogo
        )

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao gerar jogos: {str(e)}'
        }), 500

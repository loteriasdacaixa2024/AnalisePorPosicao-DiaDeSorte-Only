# -*- coding: utf-8 -*-
"""
Rotas UNIFICADAS para Fechamentos do Dia de Sorte
Combina: Palpites Inteligentes + Fechamento Tubular
"""

from flask import Blueprint, jsonify, render_template, request, send_file
from services.gerar_fechamento_service import GerarFechamentoService
from services.gerar_fechamento_tubular_service import GerarFechamentoTubularService
import io
from datetime import datetime

fechamentos_bp = Blueprint('fechamentos', __name__)


# ========================================================================
# ROTA PRINCIPAL - Página Unificada com Abas
# ========================================================================

@fechamentos_bp.route('/ferramentas/fechamentos')
def pagina_fechamentos():
    """Página principal de fechamentos com abas"""
    aba_ativa = request.args.get('aba', 'inteligente')
    return render_template('fechamentos_unificado.html', aba_ativa=aba_ativa)

@fechamentos_bp.route('/ferramentas/gerar-fechamento')
def pagina_gerar_fechamento_legado():
    """Página legada do gerador de fechamentos isolado V2 solicitada pelo usuário"""
    return render_template('gerar_fechamento_v2.html')


# ========================================================================
# APIs DO FECHAMENTO INTELIGENTE (Palpites Inteligentes / Minimalista)
# ========================================================================

@fechamentos_bp.route('/api/ferramentas/calcular-valor-aposta', methods=['POST'])
def api_calcular_valor_aposta():
    """Calcula o valor da aposta baseado na quantidade de dezenas"""
    try:
        dados = request.get_json()
        quantidade_dezenas = dados.get('quantidade_dezenas', 7)

        if not isinstance(quantidade_dezenas, int) or quantidade_dezenas < 7 or quantidade_dezenas > 15:
            return jsonify({
                'erro': 'Quantidade de dezenas inválida. Deve ser entre 7 e 15.'
            }), 400

        valor_unitario = GerarFechamentoService.calcular_valor_aposta(quantidade_dezenas)

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


@fechamentos_bp.route('/api/ferramentas/gerar-jogos', methods=['POST'])
def api_gerar_jogos():
    """Gera múltiplos jogos baseado nos parâmetros fornecidos"""
    try:
        parametros = request.get_json()

        quantidade = parametros.get('quantidade', 1)
        dezenas_por_jogo = parametros.get('dezenas_por_jogo', 7)
        config = parametros.get('config', None)
        distribuicao_dezenas = parametros.get('distribuicao_dezenas', None)
        padrao_analise = parametros.get('padrao_analise', None)

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

        if distribuicao_dezenas:
            total_distribuicao = (distribuicao_dezenas.get('baixas', 0) +
                                distribuicao_dezenas.get('medias', 0) +
                                distribuicao_dezenas.get('altas', 0))

            if total_distribuicao > dezenas_por_jogo:
                return jsonify({
                    'sucesso': False,
                    'mensagem': f'Distribuição total ({total_distribuicao}) excede dezenas por jogo ({dezenas_por_jogo}).'
                }), 400

        resultado = GerarFechamentoService.gerar_multiplos_jogos(
            quantidade=quantidade,
            config=config,
            dezenas_por_jogo=dezenas_por_jogo,
            distribuicao_dezenas=distribuicao_dezenas,
            padrao_analise=padrao_analise
        )

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao gerar jogos: {str(e)}'
        }), 500


@fechamentos_bp.route('/api/ferramentas/opcoes-analise', methods=['GET'])
def api_opcoes_analise():
    """Retorna as opções de análises pré-calculadas disponíveis"""
    try:
        from services.analise_digito_padrao_inicial_final_service import AnaliseDigitoPadraoInicialFinalService

        try:
            analise_dados = AnaliseDigitoPadraoInicialFinalService.analisar_padroes()
            tem_dados = bool(analise_dados and not analise_dados.get('error'))
        except:
            tem_dados = False

        opcoes = []

        if tem_dados:
            opcoes.append({
                'valor': 'top3_iniciais',
                'label': '🥇 Top 3 Padrões Iniciais Mais Frequentes',
                'descricao': 'Baseado na análise histórica dos dígitos iniciais dos números sorteados',
                'total_padroes': len(analise_dados.get('top_padroes_iniciais', []))
            })

        return jsonify({
            'sucesso': True,
            'opcoes': opcoes,
            'dados_disponiveis': tem_dados
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao carregar opções de análise: {str(e)}'
        }), 500


@fechamentos_bp.route('/api/gerar-fechamento/valor-aposta', methods=['GET'])
def api_obter_valor_aposta():
    """Retorna o valor atual da aposta"""
    try:
        from services.configuracao_service import ConfiguracaoService

        valor_aposta = ConfiguracaoService.obter_valor_aposta()

        return jsonify({
            'sucesso': True,
            'valor_aposta': valor_aposta
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'valor_aposta': 2.50
        }), 200


# ========================================================================
# APIs DO FECHAMENTO TUBULAR
# ========================================================================

@fechamentos_bp.route('/api/ferramentas/opcoes-fechamento-tubular')
def api_opcoes_fechamento_tubular():
    """Retorna opções de fechamento (TOP 3, recomendações, etc)"""
    try:
        opcoes = GerarFechamentoTubularService.obter_opcoes_para_fechamento()
        return jsonify(opcoes), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@fechamentos_bp.route('/api/ferramentas/gerar-jogos-tubular', methods=['POST'])
def api_gerar_jogos_tubular():
    """Gera jogos usando a lógica tubular"""
    try:
        parametros = request.get_json()
        resultado = GerarFechamentoTubularService.gerar_jogos(parametros)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500


@fechamentos_bp.route('/api/fechamento/teste', methods=['GET'])
def api_teste_fechamento():
    """Endpoint de teste para validar filtros e geração"""
    try:
        parametros_teste = {
            'quantidade': 5,
            'sequencia': 'Sequência de 2',
            'par_impar': '3P/4I',
            'mes': 'Março',
            'excluir_numero': [11, 13],
            'fixar_numero': [7]
        }

        resultado = GerarFechamentoTubularService.gerar_jogos(parametros_teste)

        preview = []
        for jogo in resultado['jogos']:
            numeros_str = ' '.join([f"{n:02d}" for n in jogo['numeros']])
            mes_abrev = GerarFechamentoTubularService.MESES_ABREV[jogo['mes_sorte']]
            preview.append(f"{numeros_str} {mes_abrev}")

        return jsonify({
            'status': True,
            'filtros_ativos': resultado['filtros'],
            'qtd_apostas': resultado['total'],
            'preview': preview,
            'jogos_completos': resultado['jogos']
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'erro': str(e)
        }), 500


@fechamentos_bp.route('/api/fechamento/exportar/txt', methods=['POST'])
def api_exportar_txt():
    """Exporta palpites em formato TXT"""
    try:
        dados = request.get_json()
        jogos_data = dados.get('jogos_data')

        if not jogos_data:
            return jsonify({'erro': 'Dados de jogos não fornecidos'}), 400

        conteudo_txt = GerarFechamentoTubularService.exportar_txt(jogos_data)

        output = io.BytesIO()
        output.write(conteudo_txt.encode('utf-8'))
        output.seek(0)

        filename = f"palpites_tubular_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        return send_file(
            output,
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@fechamentos_bp.route('/api/fechamento/exportar/xls', methods=['POST'])
def api_exportar_xls():
    """Exporta palpites em formato Excel (.xlsx)"""
    try:
        dados = request.get_json()
        jogos_data = dados.get('jogos_data')

        if not jogos_data:
            return jsonify({'erro': 'Dados de jogos não fornecidos'}), 400

        excel_bytes = GerarFechamentoTubularService.exportar_xls(jogos_data)

        output = io.BytesIO(excel_bytes)
        output.seek(0)

        filename = f"palpites_tubular_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@fechamentos_bp.route('/api/fechamento/exportar/html', methods=['POST'])
def api_exportar_html():
    """Exporta palpites em formato HTML completo"""
    try:
        dados = request.get_json()
        jogos_data = dados.get('jogos_data')
        parametros = dados.get('parametros', {})

        if not jogos_data:
            return jsonify({'erro': 'Dados de jogos não fornecidos'}), 400

        html_conteudo = GerarFechamentoTubularService.exportar_html(jogos_data, parametros)

        output = io.BytesIO()
        output.write(html_conteudo.encode('utf-8'))
        output.seek(0)

        filename = f"palpites_tubular_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        return send_file(
            output,
            mimetype='text/html',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@fechamentos_bp.route('/api/fechamento/validar-filtros', methods=['POST'])
def api_validar_filtros():
    """Valida se os filtros são compatíveis entre si"""
    try:
        filtros = request.get_json()

        avisos = []
        erros = []

        fixos = set(filtros.get('fixar_numero', []))
        excluidos = set(filtros.get('excluir_numero', []))

        conflito = fixos.intersection(excluidos)
        if conflito:
            erros.append(f"Números {list(conflito)} estão tanto em FIXOS quanto em EXCLUÍDOS")

        faixa_min = filtros.get('faixa_min', 1)
        faixa_max = filtros.get('faixa_max', 31)

        for num in fixos:
            if num < faixa_min or num > faixa_max:
                erros.append(f"Número fixo {num} está fora da faixa {faixa_min}-{faixa_max}")

        pool_disponivel = set(range(faixa_min, faixa_max + 1)) - excluidos

        if len(pool_disponivel) < 7:
            erros.append(f"Apenas {len(pool_disponivel)} números disponíveis. Necessário pelo menos 7.")

        par_impar = filtros.get('par_impar')
        if par_impar:
            pares_necessarios = int(par_impar.split('P')[0])
            impares_necessarios = 7 - pares_necessarios

            pares_fixos = sum(1 for n in fixos if n % 2 == 0)
            impares_fixos = sum(1 for n in fixos if n % 2 != 0)

            if pares_fixos > pares_necessarios:
                avisos.append(f"Há {pares_fixos} pares fixos mas padrão exige apenas {pares_necessarios}")

            if impares_fixos > impares_necessarios:
                avisos.append(f"Há {impares_fixos} ímpares fixos mas padrão exige apenas {impares_necessarios}")

        return jsonify({
            'valido': len(erros) == 0,
            'avisos': avisos,
            'erros': erros
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@fechamentos_bp.route('/api/fechamento/estatisticas', methods=['POST'])
def api_estatisticas_jogos():
    """Retorna estatísticas dos jogos gerados"""
    try:
        dados = request.get_json()
        jogos = dados.get('jogos', [])

        if not jogos:
            return jsonify({'erro': 'Nenhum jogo fornecido'}), 400

        somas = [jogo['analise']['soma'] for jogo in jogos]
        pares = [jogo['analise']['pares'] for jogo in jogos]
        com_sequencia = sum(1 for jogo in jogos if jogo['analise']['tem_sequencia'])

        return jsonify({
            'total_jogos': len(jogos),
            'soma_media': sum(somas) / len(somas),
            'soma_min': min(somas),
            'soma_max': max(somas),
            'pares_medio': sum(pares) / len(pares),
            'jogos_com_sequencia': com_sequencia,
            'percentual_com_sequencia': (com_sequencia / len(jogos)) * 100
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

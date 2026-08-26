"""
Rotas para Análise de Posição Mínima e Máxima
Sistema Dia de Sorte - Gerador Inteligente de Palpites
"""

from flask import Blueprint, render_template, jsonify, request, Response
from services.posicao_minima_maxima_service import PosicaoMinimaMaximaService
from services.analise_tubular_service import AnaliseTubularService
from services.analise_soma_dezenas_service import AnaliseSomaDezenasService
from services.analise_digitos_unicos_service import AnaliseDigitosUnicosService
from services.analise_digito_padrao_inicial_final_service import AnaliseDigitoPadraoInicialFinalService

posicao_min_max_bp = Blueprint('posicao_minima_maxima', __name__)


@posicao_min_max_bp.route('/posicao-minima-maxima')
def pagina_posicao_minima_maxima():
    """Página principal da análise"""
    return render_template('posicao_minima_maxima.html')


@posicao_min_max_bp.route('/api/posicao-minima-maxima/analise')
def api_analise():
    """Retorna análise completa de posições"""
    try:
        dados = PosicaoMinimaMaximaService.analisar_posicoes()
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@posicao_min_max_bp.route('/api/posicao-minima-maxima/ultimo-sorteio')
def api_ultimo_sorteio():
    """Retorna último sorteio para opção de repetição"""
    try:
        dados = PosicaoMinimaMaximaService.obter_ultimo_sorteio()
        if dados is None:
            return jsonify({'error': 'Nenhum sorteio encontrado'}), 404
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@posicao_min_max_bp.route('/api/posicao-minima-maxima/top3-analises')
def api_top3_analises():
    """
    Retorna TOP 3 de cada análise para popular checkboxes dinâmicos
    """
    try:
        resultado = {}

        # 1. Grupos de Finais Iguais (OPÇÕES FIXAS - NÃO VEM DE API)
        # O usuário escolhe se quer ter grupos de finais iguais nos palpites
        resultado['grupos_finais'] = [
            {'descricao': '1 grupo de 2 dezenas', 'valor': '1:2', 'exemplo': 'Ex: 01 e 21'},
            {'descricao': '2 grupos de 2 dezenas', 'valor': '2:2', 'exemplo': 'Ex: 01+11 e 03+13'},
            {'descricao': '1 grupo de 3 dezenas', 'valor': '1:3', 'exemplo': 'Ex: 01, 11 e 21'}
        ]

        # 2. Sequências (do analise_tubular_service)
        try:
            tubular = AnaliseTubularService.obter_analise_completa()
            if 'sequencias' in tubular and 'padroes' in tubular['sequencias']:
                resultado['sequencias'] = tubular['sequencias']['padroes'][:3]
        except Exception as e:
            print(f"Erro ao buscar sequências: {e}")
            resultado['sequencias'] = []

        # 3. Padrões de Dígito INICIAL (do analise_digito_padrao_inicial_final_service)
        try:
            digito_padrao = AnaliseDigitoPadraoInicialFinalService.analisar_padroes()
            if 'top_padroes_iniciais' in digito_padrao:
                resultado['padroes_digito_inicial'] = digito_padrao['top_padroes_iniciais'][:3]
        except Exception as e:
            print(f"Erro ao buscar padrões iniciais: {e}")
            resultado['padroes_digito_inicial'] = []

        # 4. Faixas de Soma (do analise_soma_dezenas_service)
        try:
            soma = AnaliseSomaDezenasService.analisar_somas()
            if 'top_10_frequentes' in soma:
                # Agrupar por faixas
                faixas_soma = []
                faixas_definidas = [
                    (70, 90, '70-90'),
                    (91, 110, '91-110'),
                    (111, 130, '111-130'),
                    (131, 150, '131-150')
                ]

                for min_val, max_val, label in faixas_definidas:
                    freq_total = sum(1 for s in soma['ranking_somas']
                                    if min_val <= s['soma'] <= max_val)
                    if freq_total > 0:
                        perc = round((freq_total / soma['total_concursos']) * 100, 2)
                        faixas_soma.append({
                            'descricao': f'Soma {label}',
                            'faixa': label,
                            'frequencia': freq_total,
                            'percentual': perc
                        })

                faixas_soma.sort(key=lambda x: x['frequencia'], reverse=True)
                resultado['soma_faixas'] = faixas_soma[:3]
        except Exception as e:
            print(f"Erro ao buscar faixas de soma: {e}")
            resultado['soma_faixas'] = []

        # 5. Dígitos Únicos (do analise_digitos_unicos_service)
        try:
            digitos = AnaliseDigitosUnicosService.analisar_digitos_unicos()
            if 'analise_por_quantidade' in digitos:
                # Filtrar apenas 6, 7 e 8 dígitos únicos
                digitos_filtrados = [d for d in digitos['analise_por_quantidade']
                                    if d['quantidade'] in [6, 7, 8]]
                digitos_filtrados.sort(key=lambda x: x['frequencia'], reverse=True)
                resultado['digitos_unicos'] = digitos_filtrados[:3]
        except Exception as e:
            print(f"Erro ao buscar dígitos únicos: {e}")
            resultado['digitos_unicos'] = []

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@posicao_min_max_bp.route('/api/posicao-minima-maxima/gerar-palpites', methods=['POST'])
def api_gerar_palpites():
    """
    Gera palpites inteligentes com base nas regras selecionadas
    """
    try:
        dados = request.get_json()

        quantidade_jogos = int(dados.get('quantidade_jogos', 10))
        quantidade_dezenas = int(dados.get('quantidade_dezenas', 7))
        regras = dados.get('regras', {})

        # Validações
        if quantidade_jogos < 1 or quantidade_jogos > 100:
            return jsonify({'error': 'Quantidade de jogos deve estar entre 1 e 100'}), 400

        if quantidade_dezenas < 7 or quantidade_dezenas > 15:
            return jsonify({'error': 'Quantidade de dezenas deve estar entre 7 e 15'}), 400

        # Gerar palpites
        resultado = PosicaoMinimaMaximaService.gerar_palpites_inteligentes(
            quantidade_jogos,
            quantidade_dezenas,
            regras
        )

        if 'error' in resultado:
            if resultado.get('tipo') == 'conflito_regras':
                return jsonify(resultado), 409  # Conflict
            elif resultado.get('tipo') == 'impossivel':
                return jsonify(resultado), 422  # Unprocessable Entity
            else:
                return jsonify(resultado), 400

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@posicao_min_max_bp.route('/api/posicao-minima-maxima/download/<tipo>')
def api_download(tipo):
    """
    Download de arquivos em diferentes formatos
    """
    try:
        # Obter análise
        analise_data = PosicaoMinimaMaximaService.analisar_posicoes()
        if 'error' in analise_data:
            return jsonify(analise_data), 404

        analise_posicoes = analise_data['analise_posicoes']

        # Verificar se há palpites na sessão (simplificado - pode usar cache/db)
        # Por enquanto, apenas análise
        palpites = None

        if tipo == 'txt':
            if palpites is None:
                return jsonify({'error': 'Nenhum palpite gerado'}), 400

            conteudo = PosicaoMinimaMaximaService.exportar_txt(palpites)
            return Response(
                conteudo,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': 'attachment; filename=palpites_dia_sorte.txt'
                }
            )

        elif tipo == 'html':
            conteudo = PosicaoMinimaMaximaService.exportar_html(analise_posicoes, palpites)
            return Response(
                conteudo,
                mimetype='text/html',
                headers={
                    'Content-Disposition': 'attachment; filename=analise_posicao_min_max.html'
                }
            )

        elif tipo == 'xls':
            conteudo = PosicaoMinimaMaximaService.exportar_xls(analise_posicoes, palpites)
            return Response(
                conteudo,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename=analise_posicao_min_max.csv'
                }
            )

        else:
            return jsonify({'error': 'Tipo de download inválido'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@posicao_min_max_bp.route('/api/posicao-minima-maxima/download-palpites/<tipo>', methods=['POST'])
def api_download_palpites(tipo):
    """
    Download de palpites gerados
    """
    try:
        dados = request.get_json()
        palpites = dados.get('palpites', [])

        if not palpites:
            return jsonify({'error': 'Nenhum palpite fornecido'}), 400

        analise_data = PosicaoMinimaMaximaService.analisar_posicoes()
        analise_posicoes = analise_data.get('analise_posicoes', [])

        if tipo == 'txt':
            conteudo = PosicaoMinimaMaximaService.exportar_txt(palpites)
            return Response(
                conteudo,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': 'attachment; filename=palpites_inteligentes.txt'
                }
            )

        elif tipo == 'html':
            conteudo = PosicaoMinimaMaximaService.exportar_html(analise_posicoes, palpites)
            return Response(
                conteudo,
                mimetype='text/html',
                headers={
                    'Content-Disposition': 'attachment; filename=palpites_inteligentes.html'
                }
            )

        elif tipo == 'xls':
            conteudo = PosicaoMinimaMaximaService.exportar_xls(analise_posicoes, palpites)
            return Response(
                conteudo,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': 'attachment; filename=palpites_inteligentes.csv'
                }
            )

        else:
            return jsonify({'error': 'Tipo de download inválido'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

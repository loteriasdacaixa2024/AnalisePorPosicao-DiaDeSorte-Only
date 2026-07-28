# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Rotas: Gerador Inteligente de Apostas

from flask import Blueprint, render_template, request, jsonify
from services.gerador_combinacoes_service import GeradorCombinacoesService
from services.filtro_inteligente_service import FiltroInteligenteService

gerador_inteligente_bp = Blueprint('gerador_inteligente', __name__, url_prefix='/gerador-inteligente')


# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================

@gerador_inteligente_bp.route('/')
def index():
    """
    Página principal do gerador inteligente
    """
    # Verificar status do cache
    info_cache = GeradorCombinacoesService.verificar_cache_existente()
    stats = GeradorCombinacoesService.obter_estatisticas()

    return render_template(
        'gerador_inteligente.html',
        cache=info_cache,
        stats=stats
    )


# ============================================================================
# API: STATUS DO CACHE
# ============================================================================

@gerador_inteligente_bp.route('/api/status-cache')
def api_status_cache():
    """
    Retorna status atual do cache
    """
    try:
        info = GeradorCombinacoesService.verificar_cache_existente()
        stats = GeradorCombinacoesService.obter_estatisticas()

        return jsonify({
            'sucesso': True,
            'cache': info,
            'estatisticas': stats
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: GERAR CACHE (1ª VEZ)
# ============================================================================

@gerador_inteligente_bp.route('/api/gerar-cache', methods=['POST'])
def api_gerar_cache():
    """
    Inicia processo de geração de todas as combinações

    ⚠️  ATENÇÃO: Processo demorado (30-60 segundos)
    """
    try:
        resultado = GeradorCombinacoesService.gerar_todas_combinacoes()

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: SINCRONIZAR COM HISTÓRICO
# ============================================================================

@gerador_inteligente_bp.route('/api/sincronizar-historico', methods=['POST'])
def api_sincronizar_historico():
    """
    Sincroniza combinações com histórico de sorteios
    Marca combinações que já foram sorteadas
    """
    try:
        resultado = GeradorCombinacoesService.sincronizar_com_historico()

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: APLICAR FILTROS
# ============================================================================

@gerador_inteligente_bp.route('/api/aplicar-filtros', methods=['POST'])
def api_aplicar_filtros():
    """
    Aplica filtros sobre as combinações geradas

    Body (JSON):
    {
        "excluir_ja_sorteadas": true,
        "score_minimo": 0,
        "pares": [3, 4],
        "soma_min": 70,
        "soma_max": 110,
        "pagina": 1,
        "por_pagina": 100,
        "ordenacao": "score_desc"
    }
    """
    try:
        dados = request.get_json()

        filtros = {
            'excluir_ja_sorteadas': dados.get('excluir_ja_sorteadas', True),
            'score_minimo': dados.get('score_minimo', 0)
        }

        pagina = dados.get('pagina', 1)
        por_pagina = dados.get('por_pagina', 100)
        ordenacao = dados.get('ordenacao', 'score_desc')

        resultado = FiltroInteligenteService.aplicar_filtros(
            filtros=filtros,
            pagina=pagina,
            por_pagina=por_pagina,
            ordenacao=ordenacao
        )

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: FILTROS AVANÇADOS (COM ANÁLISES)
# ============================================================================

@gerador_inteligente_bp.route('/api/filtros-avancados', methods=['POST'])
def api_filtros_avancados():
    """
    Aplica filtros baseados em análises específicas

    Body (JSON):
    {
        "excluir_ja_sorteadas": true,
        "pares": [3, 4],
        "soma_min": 70,
        "soma_max": 110,
        "sequencias_max": 1,
        "pagina": 1,
        "por_pagina": 100
    }
    """
    try:
        dados = request.get_json()

        pagina = dados.get('pagina', 1)
        por_pagina = dados.get('por_pagina', 100)

        resultado = FiltroInteligenteService.filtrar_por_analises(
            filtros_analises=dados,
            pagina=pagina,
            por_pagina=por_pagina
        )

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: TOP COMBINAÇÕES
# ============================================================================

@gerador_inteligente_bp.route('/api/top-combinacoes')
def api_top_combinacoes():
    """
    Retorna as TOP combinações por score

    Query params:
    - limite: quantidade (padrão: 10)
    - excluir_sorteadas: true/false (padrão: true)
    """
    try:
        limite = request.args.get('limite', 10, type=int)
        excluir_sorteadas = request.args.get('excluir_sorteadas', 'true').lower() == 'true'

        resultado = FiltroInteligenteService.obter_top_combinacoes(
            limite=limite,
            excluir_sorteadas=excluir_sorteadas
        )

        return jsonify({
            'sucesso': True,
            'combinacoes': resultado
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: BUSCAR COMBINAÇÃO ESPECÍFICA
# ============================================================================

@gerador_inteligente_bp.route('/api/buscar-combinacao', methods=['POST'])
def api_buscar_combinacao():
    """
    🔍 BUSCA INTELIGENTE: Verifica se combinação foi sorteada e traz informações completas

    Body (JSON):
    {
        "numeros": [1, 5, 11, 13, 23, 24, 26]
    }

    Response:
    {
        "sucesso": true,
        "informacoes": {
            "ja_sorteada": true/false,
            "numeros_ordenados": [1, 5, 11, 13, 23, 24, 26],
            "concurso": 123,
            "data_sorteio": "15/03/2024",
            "mes_sorte_nome": "Março",
            "ganhadores_7_acertos": 2,
            "valor_premio_7_acertos": "R$ 50.000,00",
            "ganhadores_6_acertos": 150,
            "valor_premio_6_acertos": "R$ 1.500,00"
        }
    }
    """
    try:
        from models.sorteio import Sorteio

        dados = request.get_json()
        numeros = dados.get('numeros', [])

        # Validar
        if len(numeros) != 7:
            return jsonify({
                'sucesso': False,
                'erro': 'Deve conter exatamente 7 números'
            }), 400

        # Validar range
        if any(n < 1 or n > 31 for n in numeros):
            return jsonify({
                'sucesso': False,
                'erro': 'Números devem estar entre 1 e 31'
            }), 400

        # Validar duplicados
        if len(set(numeros)) != 7:
            return jsonify({
                'sucesso': False,
                'erro': 'Números não podem se repetir'
            }), 400

        # Ordenar números
        numeros_ordenados = sorted(numeros)

        # Buscar no histórico de sorteios
        sorteio = Sorteio.query.filter(
            Sorteio.posicao_1.in_(numeros_ordenados),
            Sorteio.posicao_2.in_(numeros_ordenados),
            Sorteio.posicao_3.in_(numeros_ordenados),
            Sorteio.posicao_4.in_(numeros_ordenados),
            Sorteio.posicao_5.in_(numeros_ordenados),
            Sorteio.posicao_6.in_(numeros_ordenados),
            Sorteio.posicao_7.in_(numeros_ordenados)
        ).first()

        # Verificar se todos os números correspondem
        if sorteio:
            nums_sorteio = sorted([
                sorteio.posicao_1,
                sorteio.posicao_2,
                sorteio.posicao_3,
                sorteio.posicao_4,
                sorteio.posicao_5,
                sorteio.posicao_6,
                sorteio.posicao_7
            ])

            if nums_sorteio == numeros_ordenados:
                # COMBINAÇÃO JÁ FOI SORTEADA!
                meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

                return jsonify({
                    'sucesso': True,
                    'informacoes': {
                        'ja_sorteada': True,
                        'numeros_ordenados': numeros_ordenados,
                        'concurso': sorteio.concurso,
                        'data_sorteio': sorteio.data_sorteio.strftime('%d/%m/%Y'),
                        'mes_sorte': sorteio.mes_sorte,
                        'mes_sorte_nome': meses[sorteio.mes_sorte] if sorteio.mes_sorte <= 12 else 'Desconhecido',
                        'ganhadores_7_acertos': sorteio.ganhadores_7_acertos,
                        'valor_premio_7_acertos': f"R$ {sorteio.valor_premio_7_acertos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        'ganhadores_6_acertos': sorteio.ganhadores_6_acertos,
                        'valor_premio_6_acertos': f"R$ {sorteio.valor_premio_6_acertos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        'ganhadores_5_acertos': sorteio.ganhadores_5_acertos,
                        'valor_premio_5_acertos': f"R$ {sorteio.valor_premio_5_acertos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        'ganhadores_4_acertos': sorteio.ganhadores_4_acertos,
                        'valor_premio_4_acertos': f"R$ {sorteio.valor_premio_4_acertos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    }
                })

        # COMBINAÇÃO DISPONÍVEL (nunca foi sorteada)
        return jsonify({
            'sucesso': True,
            'informacoes': {
                'ja_sorteada': False,
                'numeros_ordenados': numeros_ordenados
            }
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: EXPORTAR RESULTADOS
# ============================================================================

@gerador_inteligente_bp.route('/api/exportar', methods=['POST'])
def api_exportar():
    """
    Exporta resultados filtrados para TXT/JSON/Excel

    Body (JSON):
    {
        "formato": "txt",  # txt, json, excel
        "filtros": {...},
        "incluir_mes": true,
        "modo_mes": "aleatorio"  # aleatorio, fixo, distribuido
    }
    """
    try:
        dados = request.get_json()
        formato = dados.get('formato', 'txt')

        # TODO: Implementar exportação
        # Por enquanto retorna sucesso

        return jsonify({
            'sucesso': True,
            'mensagem': f'Exportação em {formato} implementada em breve',
            'arquivo': f'apostas_{formato}'
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: LIMPAR CACHE
# ============================================================================

@gerador_inteligente_bp.route('/api/limpar-cache', methods=['POST'])
def api_limpar_cache():
    """
    Limpa TODAS as combinações do cache

    ⚠️  USE COM CUIDADO!
    """
    try:
        resultado = GeradorCombinacoesService.limpar_cache()

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: ESTATÍSTICAS GERAIS
# ============================================================================

@gerador_inteligente_bp.route('/api/estatisticas')
def api_estatisticas():
    """
    Retorna estatísticas gerais do cache
    """
    try:
        stats = GeradorCombinacoesService.obter_estatisticas()

        return jsonify({
            'sucesso': True,
            'estatisticas': stats
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: OBTER TOP PADRÕES DÍGITO INICIAL/FINAL
# ============================================================================

@gerador_inteligente_bp.route('/api/obter-top-padroes-digito')
def api_obter_top_padroes_digito():
    """
    🔢 NOVO: Obtém os TOP 3 padrões de dígito inicial mais frequentes

    Busca diretamente do banco de dados e calcula os padrões mais frequentes

    Response:
    {
        "sucesso": true,
        "top_padroes": [
            {
                "padrao": "2-2-2-1",
                "padrao_formatado": "0:2 | 1:2 | 2:2 | 3:1",
                "frequencia": 92,
                "porcentagem": 8.04
            },
            ...
        ]
    }
    """
    try:
        from models.sorteio import Sorteio
        from collections import defaultdict

        # Buscar todos os sorteios
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum sorteio encontrado'
            }), 404

        total_concursos = len(sorteios)
        padroes_frequencia = defaultdict(int)

        # Calcular padrão de cada sorteio
        for sorteio in sorteios:
            digitos_iniciais = defaultdict(int)

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    digito_inicial = numero // 10  # 01->0, 15->1, 28->2
                    digitos_iniciais[digito_inicial] += 1

            # Criar padrão "2-2-2-1"
            padrao = '-'.join([str(digitos_iniciais.get(d, 0)) for d in range(4)])
            padroes_frequencia[padrao] += 1

        # Pegar TOP 3
        top_padroes_raw = sorted(
            padroes_frequencia.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # Formatar resposta
        top_padroes = []
        for padrao_simples, freq in top_padroes_raw:
            # Converter "2-2-2-1" para "0:2 | 1:2 | 2:2 | 3:1"
            partes = padrao_simples.split('-')
            padrao_formatado = f"0:{partes[0]} | 1:{partes[1]} | 2:{partes[2]} | 3:{partes[3]}"
            percentual = round((freq / total_concursos * 100), 2)

            top_padroes.append({
                'padrao': padrao_simples,
                'padrao_formatado': padrao_formatado,
                'frequencia': freq,
                'porcentagem': percentual
            })

        return jsonify({
            'sucesso': True,
            'top_padroes': top_padroes
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: FILTRAR POR PADRÃO DÍGITO INICIAL
# ============================================================================

@gerador_inteligente_bp.route('/api/filtrar-por-padrao-digito', methods=['POST'])
def api_filtrar_por_padrao_digito():
    """
    🔢 NOVO: Filtra combinações por padrão de dígito inicial

    Body (JSON):
    {
        "padrao": "2-2-2-1",
        "excluir_sorteadas": true,
        "pagina": 1,
        "por_pagina": 100
    }

    Response:
    {
        "sucesso": true,
        "total_encontradas": 45678,
        "total_disponiveis": 44234,
        "resultados": [...],
        "paginacao": {...}
    }
    """
    try:
        from models.sorteio import Sorteio
        import os

        dados = request.get_json()
        padrao_solicitado = dados.get('padrao', '')  # "2-2-2-1"
        excluir_sorteadas = dados.get('excluir_sorteadas', True)
        pagina = dados.get('pagina', 1)
        por_pagina = dados.get('por_pagina', 100)

        if not padrao_solicitado:
            return jsonify({
                'sucesso': False,
                'erro': 'Padrão não especificado'
            }), 400

        # Converter padrão "2-2-2-1" para array [2, 2, 2, 1]
        try:
            padrao_array = [int(x) for x in padrao_solicitado.split('-')]
            if len(padrao_array) != 4:
                raise ValueError("Padrão deve ter 4 dígitos")
        except:
            return jsonify({
                'sucesso': False,
                'erro': 'Padrão inválido. Use formato 2-2-2-1'
            }), 400

        # Ler combinações sorteadas (se necessário)
        sorteadas_set = set()
        if excluir_sorteadas:
            sorteios = Sorteio.query.all()
            for sorteio in sorteios:
                nums = sorted([
                    sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                    sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                    sorteio.posicao_7
                ])
                combo_str = '-'.join(f"{n:02d}" for n in nums)
                sorteadas_set.add(combo_str)

        # Ler arquivo de combinações
        CACHE_FILE = os.path.join('data', 'combinacoes_cache.txt')

        if not os.path.exists(CACHE_FILE):
            return jsonify({
                'sucesso': False,
                'erro': 'Arquivo de cache não existe. Gere primeiro!'
            }), 404

        # Filtrar combinações por padrão
        combinacoes_filtradas = []
        total_lidas = 0

        with open(CACHE_FILE, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()

                # Pular comentários
                if linha.startswith('#') or not linha:
                    continue

                total_lidas += 1

                # Verificar se já foi sorteada
                if excluir_sorteadas and linha in sorteadas_set:
                    continue

                # Calcular padrão desta combinação
                numeros = [int(n) for n in linha.split('-')]
                padrao_combo = GeradorCombinacoesService.calcular_padrao_digito_inicial(numeros)

                # Comparar padrões
                if padrao_combo == padrao_array:
                    combinacoes_filtradas.append(linha)

        # Estatísticas
        total_encontradas = len(combinacoes_filtradas)

        # Descobrir mês mais atrasado
        mes_atrasado = GeradorCombinacoesService.descobrir_mes_mais_atrasado()

        # Paginação
        inicio = (pagina - 1) * por_pagina
        fim = inicio + por_pagina
        pagina_atual = combinacoes_filtradas[inicio:fim]

        total_paginas = (total_encontradas + por_pagina - 1) // por_pagina

        # Converter para formato de saída
        resultados = []
        for idx, combo_str in enumerate(pagina_atual, start=inicio + 1):
            numeros = [int(n) for n in combo_str.split('-')]

            resultados.append({
                'id': idx,
                'numeros_crescente': numeros,
                'numeros_original': numeros,
                'numeros_crescente_str': combo_str,
                'numeros_original_str': combo_str,
                'padrao': padrao_solicitado,
                'score': 0,
                'ja_sorteada': False,
                'analises': {},
                'resumo_analises': f'Padrão: {padrao_solicitado}'
            })

        return jsonify({
            'sucesso': True,
            'padrao': padrao_solicitado,
            'total_encontradas': total_encontradas,
            'mes_atrasado': mes_atrasado,
            'resultados': resultados,
            'paginacao': {
                'pagina_atual': pagina,
                'por_pagina': por_pagina,
                'total_registros': total_encontradas,
                'total_paginas': total_paginas,
                'tem_anterior': pagina > 1,
                'tem_proximo': pagina < total_paginas,
                'pagina_anterior': pagina - 1 if pagina > 1 else None,
                'pagina_proxima': pagina + 1 if pagina < total_paginas else None
            }
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: EXPORTAR PADRÃO PARA TXT
# ============================================================================

@gerador_inteligente_bp.route('/api/exportar-padrao-txt', methods=['POST'])
def api_exportar_padrao_txt():
    """
    💾 NOVO: Exporta combinações filtradas por padrão para TXT

    Formato: 01 02 03 04 05 06 07 Fev
    (Mês = o mais atrasado do histórico)

    Body (JSON):
    {
        "padrao": "2-2-2-1",
        "excluir_sorteadas": true
    }

    Response:
    {
        "sucesso": true,
        "arquivo_conteudo": "01 02 03 04 05 06 07 Fev\n...",
        "total_linhas": 45678,
        "mes_atrasado": "Fevereiro"
    }
    """
    try:
        from models.sorteio import Sorteio
        from collections import Counter
        import os

        dados = request.get_json()
        padrao_solicitado = dados.get('padrao', '')
        excluir_sorteadas = dados.get('excluir_sorteadas', True)

        if not padrao_solicitado:
            return jsonify({
                'sucesso': False,
                'erro': 'Padrão não especificado'
            }), 400

        # Converter padrão
        try:
            padrao_array = [int(x) for x in padrao_solicitado.split('-')]
            if len(padrao_array) != 4:
                raise ValueError("Padrão deve ter 4 dígitos")
        except:
            return jsonify({
                'sucesso': False,
                'erro': 'Padrão inválido'
            }), 400

        # Descobrir mês mais atrasado
        mes_atrasado_nome = GeradorCombinacoesService.descobrir_mes_mais_atrasado()

        # Ler combinações sorteadas
        sorteadas_set = set()
        if excluir_sorteadas:
            sorteios = Sorteio.query.all()
            for sorteio in sorteios:
                nums = sorted([
                    sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                    sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                    sorteio.posicao_7
                ])
                combo_str = '-'.join(f"{n:02d}" for n in nums)
                sorteadas_set.add(combo_str)

        # Ler arquivo
        CACHE_FILE = os.path.join('data', 'combinacoes_cache.txt')

        if not os.path.exists(CACHE_FILE):
            return jsonify({
                'sucesso': False,
                'erro': 'Arquivo de cache não existe'
            }), 404

        # Filtrar e gerar TXT
        linhas_txt = []

        with open(CACHE_FILE, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()

                if linha.startswith('#') or not linha:
                    continue

                # Excluir sorteadas
                if excluir_sorteadas and linha in sorteadas_set:
                    continue

                # Verificar padrão
                numeros = [int(n) for n in linha.split('-')]
                padrao_combo = GeradorCombinacoesService.calcular_padrao_digito_inicial(numeros)

                if padrao_combo == padrao_array:
                    # Formatar: "01 02 03 04 05 06 07 Fev"
                    nums_formatados = ' '.join(f"{n:02d}" for n in numeros)
                    linha_txt = f"{nums_formatados} {mes_atrasado_nome}\n"
                    linhas_txt.append(linha_txt)

        # Gerar conteúdo final
        arquivo_conteudo = ''.join(linhas_txt)

        return jsonify({
            'sucesso': True,
            'arquivo_conteudo': arquivo_conteudo,
            'total_linhas': len(linhas_txt),
            'mes_atrasado': mes_atrasado_nome,
            'padrao': padrao_solicitado
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


# ============================================================================
# API: EXPORTAR RESULTADOS COMPLETOS (TXT) - STREAMING OTMIZADO
# ============================================================================

@gerador_inteligente_bp.route('/api/exportar-completo', methods=['POST'])
def api_exportar_completo():
    """
    Exporta TODAS as milhares/milhões de combinações via Streaming,
    evitando travamentos no navegador ou estouro de memória no servidor.
    Dessa forma, suporta +2.6 milhões de linhas em ~40MB instantaneamente.
    """
    try:
        from models.sorteio import Sorteio
        from flask import Response, stream_with_context
        import os
        from services.gerador_combinacoes_service import GeradorCombinacoesService

        # No form submit normal via POST, pegamos pelo request.form em vez de get_json()
        excluir_sorteadas = request.form.get('excluir_sorteadas', 'true') == 'true'

        mes_atrasado_nome = GeradorCombinacoesService.descobrir_mes_mais_atrasado()

        sorteadas_set = set()
        if excluir_sorteadas:
            sorteios = Sorteio.query.all()
            for sorteio in sorteios:
                nums = sorted([
                    sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                    sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                    sorteio.posicao_7
                ])
                combo_str = '-'.join(f"{n:02d}" for n in nums)
                sorteadas_set.add(combo_str)

        CACHE_FILE = os.path.join('data', 'combinacoes_cache.txt')
        if not os.path.exists(CACHE_FILE):
            return "Erro: Arquivo de cache não localizado. Limpe e gere o cache novamente.", 404

        def generate_file():
            yield f"# Gerador Inteligente - Exportacao Completa\n"
            yield f"# Mes sugerido: {mes_atrasado_nome}\n"
            yield f"# Filtro: Excluir sorteadas = {'Sim' if excluir_sorteadas else 'Nao'}\n\n"
            
            with open(CACHE_FILE, 'r', encoding='utf-8') as arquivo:
                for linha in arquivo:
                    linha = linha.strip()
                    if not linha or linha.startswith('#'):
                        continue
                    
                    if excluir_sorteadas and linha in sorteadas_set:
                        continue
                    
                    nums = linha.split('-')
                    linha_txt = ' '.join(nums) + f" {mes_atrasado_nome}\n"
                    yield linha_txt

        response = Response(stream_with_context(generate_file()), mimetype='text/plain')
        response.headers['Content-Disposition'] = 'attachment; filename=extracao_completa_gerador_inteligente.txt'
        return response

    except Exception as e:
        return f"Erro ao exportar arquivo completo: {str(e)}", 500

# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Service: Gerador DEFINITIVO (Arquivo + Banco)

from models import db
from models.combinacao_gerada import CombinacaoGerada, CacheGeracao
from models.sorteio import Sorteio
from itertools import combinations
from datetime import datetime
import os
import time


class GeradorCombinacoesService:
    """
    Gerador DEFINITIVO - Usa arquivo TXT como cache principal
    """

    # Caminho do arquivo de cache
    CACHE_FILE = os.path.join('data', 'combinacoes_cache.txt')

    @staticmethod
    def _criar_diretorio_data():
        """Cria diretório data/ se não existir"""
        os.makedirs('data', exist_ok=True)

    @staticmethod
    def verificar_cache_existente():
        """Verifica cache (arquivo + banco)"""
        GeradorCombinacoesService._criar_diretorio_data()

        cache = CacheGeracao.obter_ou_criar()

        # Verificar se arquivo existe
        arquivo_existe = os.path.exists(GeradorCombinacoesService.CACHE_FILE)

        # Verificar tamanho do arquivo
        tamanho_mb = 0
        if arquivo_existe:
            tamanho_bytes = os.path.getsize(GeradorCombinacoesService.CACHE_FILE)
            tamanho_mb = tamanho_bytes / (1024 * 1024)

        return {
            'existe': arquivo_existe or cache.total_geradas > 0,
            'arquivo_existe': arquivo_existe,
            'tamanho_arquivo_mb': round(tamanho_mb, 2),
            'total_geradas': cache.total_geradas,
            'total_sorteadas': cache.total_sorteadas,
            'total_disponiveis': cache.total_disponiveis,
            'data_geracao': cache.data_geracao.strftime('%d/%m/%Y %H:%M:%S') if cache.data_geracao else None,
            'ultimo_concurso_sincronizado': cache.ultimo_concurso_sincronizado,
            'status': cache.status,
            'precisa_gerar': not arquivo_existe,
            'progresso': {
                'atual': cache.progresso_atual,
                'total': cache.progresso_total,
                'percentual': cache.progresso_percentual,
                'mensagem': cache.mensagem_progresso
            }
        }

    @staticmethod
    def gerar_arquivo_cache():
        """
        PASSO 1: Gera arquivo TXT com todas as combinações
        MUITO RÁPIDO: ~10-15 segundos!
        """
        try:
            GeradorCombinacoesService._criar_diretorio_data()

            cache = CacheGeracao.obter_ou_criar()
            cache.status = 'gerando'
            cache.data_geracao = datetime.utcnow()
            cache.progresso_atual = 0
            cache.progresso_total = 2629575
            db.session.commit()

            print("=" * 70)
            print("🚀 GERADOR DE COMBINAÇÕES - MÉTODO ARQUIVO")
            print("=" * 70)
            print(f"📁 Arquivo: {GeradorCombinacoesService.CACHE_FILE}")
            print("⏱️  Tempo estimado: 10-15 segundos")
            print()

            numeros = range(1, 32)
            total = 2629575
            contador = 0
            inicio = time.time()

            with open(GeradorCombinacoesService.CACHE_FILE, 'w', encoding='utf-8') as arquivo:
                # Cabeçalho
                arquivo.write("# CACHE DE COMBINAÇÕES - DIA DE SORTE\n")
                arquivo.write(f"# Total: 2.629.575 combinações\n")
                arquivo.write(f"# Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                arquivo.write("#\n")

                # Gerar e escrever combinações
                for combo in combinations(numeros, 7):
                    contador += 1

                    # Formatar: 01-05-11-13-23-24-26
                    linha = '-'.join(f"{n:02d}" for n in combo) + '\n'
                    arquivo.write(linha)

                    # Atualizar progresso a cada 250k
                    if contador % 250000 == 0:
                        percentual = (contador / total) * 100
                        tempo_decorrido = time.time() - inicio

                        cache.atualizar_progresso(
                            contador,
                            total,
                            f'Gerando arquivo: {contador:,}/{total:,}'
                        )

                        print(f"✅ {contador:,}/{total:,} ({percentual:.1f}%) - {tempo_decorrido:.1f}s")

            tempo_total = time.time() - inicio
            tamanho_mb = os.path.getsize(GeradorCombinacoesService.CACHE_FILE) / (1024 * 1024)

            # Atualizar cache
            cache.total_geradas = contador
            cache.total_disponiveis = contador
            cache.status = 'completo'
            cache.progresso_percentual = 100.0
            cache.mensagem_progresso = 'Arquivo gerado!'
            db.session.commit()

            print()
            print("=" * 70)
            print("🎉 ARQUIVO GERADO COM SUCESSO!")
            print("=" * 70)
            print(f"📊 Total: {contador:,} combinações")
            print(f"⏱️  Tempo: {tempo_total:.1f} segundos")
            print(f"📁 Tamanho: {tamanho_mb:.2f} MB")
            print("=" * 70)
            print()

            return {
                'sucesso': True,
                'total_geradas': contador,
                'tempo_segundos': tempo_total,
                'tamanho_mb': tamanho_mb,
                'mensagem': f'{contador:,} combinações geradas em {tempo_total:.1f}s'
            }

        except Exception as e:
            cache.status = 'erro'
            cache.mensagem_progresso = f'Erro: {str(e)}'
            db.session.commit()

            print(f"❌ Erro: {str(e)}")

            return {
                'sucesso': False,
                'erro': str(e)
            }

    @staticmethod
    def carregar_combinacoes_do_arquivo(pagina=1, por_pagina=100, excluir_sorteadas=True):
        """
        PASSO 2: Carrega combinações do arquivo (com paginação)
        """
        try:
            if not os.path.exists(GeradorCombinacoesService.CACHE_FILE):
                return {
                    'sucesso': False,
                    'erro': 'Arquivo de cache não existe. Gere primeiro!'
                }

            # Ler histórico de sorteadas (se necessário)
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

            # Ler arquivo e filtrar
            combinacoes = []
            total_lidas = 0
            total_filtradas = 0

            with open(GeradorCombinacoesService.CACHE_FILE, 'r', encoding='utf-8') as arquivo:
                for linha in arquivo:
                    linha = linha.strip()

                    # Pular comentários
                    if linha.startswith('#') or not linha:
                        continue

                    total_lidas += 1

                    # Filtrar sorteadas
                    if excluir_sorteadas and linha in sorteadas_set:
                        continue

                    combinacoes.append(linha)
                    total_filtradas += 1

            # Paginação
            inicio = (pagina - 1) * por_pagina
            fim = inicio + por_pagina
            pagina_atual = combinacoes[inicio:fim]

            total_paginas = (total_filtradas + por_pagina - 1) // por_pagina

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
                    'score': 0,
                    'ja_sorteada': False,
                    'analises': {},
                    'resumo_analises': 'Sem análise'
                })

            return {
                'sucesso': True,
                'resultados': resultados,
                'paginacao': {
                    'pagina_atual': pagina,
                    'por_pagina': por_pagina,
                    'total_registros': total_filtradas,
                    'total_paginas': total_paginas,
                    'tem_anterior': pagina > 1,
                    'tem_proximo': pagina < total_paginas,
                    'pagina_anterior': pagina - 1 if pagina > 1 else None,
                    'pagina_proxima': pagina + 1 if pagina < total_paginas else None
                },
                'filtros_aplicados': {
                    'excluir_ja_sorteadas': excluir_sorteadas,
                    'total_lidas': total_lidas,
                    'total_sorteadas_excluidas': total_lidas - total_filtradas
                }
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }

    @staticmethod
    def sincronizar_com_historico():
        """Atualiza estatísticas de sorteadas"""
        try:
            cache = CacheGeracao.obter_ou_criar()

            sorteios = Sorteio.query.order_by(Sorteio.concurso).all()

            if not sorteios:
                return {
                    'sucesso': True,
                    'total_marcados': 0,
                    'mensagem': 'Nenhum sorteio encontrado'
                }

            total_sorteadas = len(sorteios)
            ultimo_concurso = sorteios[-1].concurso if sorteios else 0

            # Atualizar cache
            cache.total_sorteadas = total_sorteadas
            cache.total_disponiveis = cache.total_geradas - total_sorteadas
            cache.ultimo_concurso_sincronizado = ultimo_concurso
            cache.data_ultima_sincronizacao = datetime.utcnow()
            db.session.commit()

            return {
                'sucesso': True,
                'total_marcados': total_sorteadas,
                'total_sorteadas': total_sorteadas,
                'total_disponiveis': cache.total_disponiveis,
                'ultimo_concurso': ultimo_concurso,
                'mensagem': f'{total_sorteadas} combinações já sorteadas'
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }

    @staticmethod
    def limpar_cache():
        """Remove arquivo e reseta cache"""
        try:
            total = 0

            # Remover arquivo
            if os.path.exists(GeradorCombinacoesService.CACHE_FILE):
                os.remove(GeradorCombinacoesService.CACHE_FILE)
                total = 2629575

            # Resetar cache
            cache = CacheGeracao.obter_ou_criar()
            cache.total_geradas = 0
            cache.total_sorteadas = 0
            cache.total_disponiveis = 0
            cache.status = 'aguardando'
            cache.progresso_atual = 0
            cache.progresso_total = 0
            cache.progresso_percentual = 0.0
            cache.mensagem_progresso = ''
            db.session.commit()

            return {
                'sucesso': True,
                'total_removidas': total,
                'mensagem': f'Cache limpo!'
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }

    @staticmethod
    def obter_estatisticas():
        """Retorna estatísticas"""
        cache = CacheGeracao.obter_ou_criar()

        return {
            'total_combinacoes_possiveis': 2629575,
            'total_geradas': cache.total_geradas,
            'total_sorteadas': cache.total_sorteadas,
            'total_disponiveis': cache.total_disponiveis,
            'percentual_gerado': (cache.total_geradas / 2629575 * 100) if cache.total_geradas > 0 else 0,
            'percentual_sorteado': (cache.total_sorteadas / cache.total_geradas * 100) if cache.total_geradas > 0 else 0,
            'percentual_disponivel': (cache.total_disponiveis / cache.total_geradas * 100) if cache.total_geradas > 0 else 0,
            'status': cache.status,
            'data_geracao': cache.data_geracao.strftime('%d/%m/%Y %H:%M:%S') if cache.data_geracao else None,
            'ultimo_concurso_sincronizado': cache.ultimo_concurso_sincronizado,
            'data_ultima_sincronizacao': cache.data_ultima_sincronizacao.strftime('%d/%m/%Y %H:%M:%S') if cache.data_ultima_sincronizacao else None
        }

    # Alias para compatibilidade
    @staticmethod
    def gerar_todas_combinacoes():
        """Alias para gerar_arquivo_cache"""
        return GeradorCombinacoesService.gerar_arquivo_cache()

    @staticmethod
    def calcular_padrao_digito_inicial(numeros):
        """
        🔢 Calcula o padrão de dígito inicial de uma combinação

        Args:
            numeros (list): Lista de 7 números [1, 5, 11, 13, 25, 26, 27]

        Returns:
            list: Padrão [2, 2, 2, 1] significa:
                  - 2 números começam com 0 (01-09)
                  - 2 números começam com 1 (10-19)
                  - 2 números começam com 2 (20-29)
                  - 1 número começa com 3 (30-31)

        Exemplo:
            >>> calcular_padrao_digito_inicial([1, 5, 11, 13, 25, 26, 27])
            [2, 2, 2, 1]
        """
        contador = [0, 0, 0, 0]  # [dígito 0, dígito 1, dígito 2, dígito 3]

        for numero in numeros:
            digito_inicial = numero // 10
            if digito_inicial < 4:
                contador[digito_inicial] += 1

        return contador

    @staticmethod
    def descobrir_mes_mais_atrasado():
        """
        📅 Descobre qual mês está mais atrasado (há mais tempo sem sair)

        Returns:
            str: Nome do mês em português abreviado (Jan, Fev, Mar, etc.)

        Lógica:
        1. Busca todos os sorteios ordenados por data DESC
        2. Para cada mês (1-12), conta quantos sorteios se passaram desde a última vez que saiu
        3. Retorna o mês com maior atraso
        """
        from models.sorteio import Sorteio

        meses_nomes = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        # Buscar todos os sorteios (mais recente primeiro)
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return 'Jan'  # Padrão se não houver sorteios

        # Contar atraso de cada mês
        atrasos = {}

        for mes in range(1, 13):
            atraso = 0
            encontrou = False

            for sorteio in sorteios:
                if sorteio.mes_sorte == mes:
                    encontrou = True
                    break
                atraso += 1

            if encontrou:
                atrasos[mes] = atraso
            else:
                # Mês nunca saiu - atraso máximo
                atrasos[mes] = 99999

        # Encontrar mês com maior atraso
        mes_mais_atrasado = max(atrasos, key=atrasos.get)

        return meses_nomes[mes_mais_atrasado]

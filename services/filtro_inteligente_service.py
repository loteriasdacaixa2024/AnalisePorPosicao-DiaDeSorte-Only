# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Service: Filtro Inteligente de Combinações

from models import db
from models.combinacao_gerada import CombinacaoGerada
from sqlalchemy import and_, or_


class FiltroInteligenteService:
    """
    Aplica filtros inteligentes sobre as combinações geradas
    """

    @staticmethod
    def aplicar_filtros(filtros, pagina=1, por_pagina=100, ordenacao='score_desc'):
        """
        Aplica filtros - VERSÃO ARQUIVO (mais rápida)
        """
        from services.gerador_combinacoes_service import GeradorCombinacoesService

        # Usar método do arquivo
        return GeradorCombinacoesService.carregar_combinacoes_do_arquivo(
            pagina=pagina,
            por_pagina=por_pagina,
            excluir_sorteadas=filtros.get('excluir_ja_sorteadas', True)
        )

    @staticmethod
    def aplicar_filtros_OLD(filtros, pagina=1, por_pagina=100, ordenacao='score_desc'):
        """
        Aplica múltiplos filtros sobre as combinações

        Args:
            filtros (dict): Dicionário com critérios de filtro
            pagina (int): Página atual (paginação)
            por_pagina (int): Registros por página
            ordenacao (str): Tipo de ordenação

        Returns:
            dict: Resultados filtrados com paginação
        """
        try:
            # Iniciar query base
            query = CombinacaoGerada.query.filter_by(ativo=True)

            # ================================================================
            # FILTRO INTELIGENTE: EXCLUIR JÁ SORTEADAS
            # ================================================================
            if filtros.get('excluir_ja_sorteadas', True):
                query = query.filter_by(ja_sorteada=False)

            # ================================================================
            # FILTRO: SCORE MÍNIMO
            # ================================================================
            if filtros.get('score_minimo'):
                query = query.filter(CombinacaoGerada.score >= filtros['score_minimo'])

            # ================================================================
            # APLICAR ORDENAÇÃO
            # ================================================================
            if ordenacao == 'score_desc':
                query = query.order_by(CombinacaoGerada.score.desc())
            elif ordenacao == 'score_asc':
                query = query.order_by(CombinacaoGerada.score.asc())
            elif ordenacao == 'id_asc':
                query = query.order_by(CombinacaoGerada.id.asc())
            elif ordenacao == 'id_desc':
                query = query.order_by(CombinacaoGerada.id.desc())

            # ================================================================
            # EXECUTAR QUERY COM PAGINAÇÃO
            # ================================================================
            paginacao = query.paginate(
                page=pagina,
                per_page=por_pagina,
                error_out=False
            )

            # Converter para dicionários
            resultados = []
            for comb in paginacao.items:
                analises = comb.get_analises()

                resultados.append({
                    'id': comb.id,
                    'numeros_crescente': comb.get_numeros_crescente_list(),
                    'numeros_original': comb.get_numeros_original_list(),
                    'numeros_crescente_str': comb.numeros_crescente,
                    'numeros_original_str': comb.numeros_original,
                    'score': round(comb.score, 2),
                    'ja_sorteada': comb.ja_sorteada,
                    'concurso_sorteio': comb.concurso_sorteio,
                    'analises': analises,
                    'resumo_analises': FiltroInteligenteService._gerar_resumo_analises(analises)
                })

            return {
                'sucesso': True,
                'resultados': resultados,
                'paginacao': {
                    'pagina_atual': paginacao.page,
                    'por_pagina': paginacao.per_page,
                    'total_registros': paginacao.total,
                    'total_paginas': paginacao.pages,
                    'tem_anterior': paginacao.has_prev,
                    'tem_proximo': paginacao.has_next,
                    'pagina_anterior': paginacao.prev_num,
                    'pagina_proxima': paginacao.next_num
                },
                'filtros_aplicados': filtros
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }

    @staticmethod
    def filtrar_por_analises(filtros_analises, pagina=1, por_pagina=100):
        """
        Filtra combinações baseado em critérios de análise específicos

        Args:
            filtros_analises (dict): Critérios de análise
            Exemplo:
            {
                'pares': [3, 4],  # Aceita 3 ou 4 pares
                'soma_min': 70,
                'soma_max': 110,
                'sequencias_max': 1,
                'excluir_ja_sorteadas': True
            }

        Returns:
            dict: Resultados filtrados
        """
        try:
            # Query base
            query = CombinacaoGerada.query.filter_by(ativo=True)

            # Filtro inteligente
            if filtros_analises.get('excluir_ja_sorteadas', True):
                query = query.filter_by(ja_sorteada=False)

            # Buscar todas e filtrar em Python (análises estão em JSON)
            todas = query.all()
            filtradas = []

            for comb in todas:
                analises = comb.get_analises()

                # Aplicar filtros de análise
                passa = True

                # Pares
                if 'pares' in filtros_analises:
                    if analises.get('pares') not in filtros_analises['pares']:
                        passa = False

                # Soma
                if 'soma_min' in filtros_analises:
                    if analises.get('soma', 0) < filtros_analises['soma_min']:
                        passa = False

                if 'soma_max' in filtros_analises:
                    if analises.get('soma', 0) > filtros_analises['soma_max']:
                        passa = False

                # Sequências
                if 'sequencias_max' in filtros_analises:
                    if analises.get('sequencias', 0) > filtros_analises['sequencias_max']:
                        passa = False

                if passa:
                    filtradas.append(comb)

            # Paginação manual
            total = len(filtradas)
            inicio = (pagina - 1) * por_pagina
            fim = inicio + por_pagina
            pagina_atual = filtradas[inicio:fim]

            # Converter para dicionários
            resultados = []
            for comb in pagina_atual:
                analises = comb.get_analises()
                resultados.append({
                    'id': comb.id,
                    'numeros_crescente': comb.get_numeros_crescente_list(),
                    'numeros_original': comb.get_numeros_original_list(),
                    'score': round(comb.score, 2),
                    'analises': analises,
                    'resumo_analises': FiltroInteligenteService._gerar_resumo_analises(analises)
                })

            total_paginas = (total + por_pagina - 1) // por_pagina

            return {
                'sucesso': True,
                'resultados': resultados,
                'paginacao': {
                    'pagina_atual': pagina,
                    'por_pagina': por_pagina,
                    'total_registros': total,
                    'total_paginas': total_paginas,
                    'tem_anterior': pagina > 1,
                    'tem_proximo': pagina < total_paginas
                }
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }

    @staticmethod
    def _gerar_resumo_analises(analises):
        """
        Gera resumo textual das análises

        Args:
            analises (dict): Dicionário de análises

        Returns:
            str: Texto resumido
        """
        if not analises:
            return "Sem análises"

        partes = []

        # Pares/Ímpares
        if 'pares' in analises and 'impares' in analises:
            partes.append(f"{analises['pares']}P/{analises['impares']}I")

        # Soma
        if 'soma' in analises:
            partes.append(f"S:{analises['soma']}")

        # Sequências
        if 'sequencias' in analises:
            seq = analises['sequencias']
            if seq > 0:
                partes.append(f"Seq:{seq}")

        # Quadrantes
        if 'quadrantes' in analises:
            partes.append("Q:✓")

        return ", ".join(partes) if partes else "Sem dados"

    @staticmethod
    def buscar_combinacao_especifica(numeros):
        """
        Busca uma combinação específica pelo conjunto de números

        Args:
            numeros (list): Lista de 7 números

        Returns:
            dict: Dados da combinação ou None
        """
        try:
            # Ordenar números
            nums_ordenados = sorted(numeros)
            hash_busca = CombinacaoGerada.gerar_hash(nums_ordenados)

            comb = CombinacaoGerada.query.filter_by(
                hash_combinacao=hash_busca
            ).first()

            if not comb:
                return {
                    'encontrada': False,
                    'mensagem': 'Combinação não encontrada no cache'
                }

            return {
                'encontrada': True,
                'combinacao': comb.to_dict(incluir_analises=True),
                'ja_sorteada': comb.ja_sorteada,
                'concurso_sorteio': comb.concurso_sorteio if comb.ja_sorteada else None
            }

        except Exception as e:
            return {
                'encontrada': False,
                'erro': str(e)
            }

    @staticmethod
    def obter_top_combinacoes(limite=10, excluir_sorteadas=True):
        """
        Retorna as TOP combinações por score

        Args:
            limite (int): Quantidade de combinações
            excluir_sorteadas (bool): Excluir já sorteadas

        Returns:
            list: Lista de combinações
        """
        try:
            query = CombinacaoGerada.query.filter_by(ativo=True)

            if excluir_sorteadas:
                query = query.filter_by(ja_sorteada=False)

            query = query.order_by(CombinacaoGerada.score.desc()).limit(limite)

            resultados = []
            for comb in query.all():
                resultados.append({
                    'id': comb.id,
                    'numeros': comb.get_numeros_crescente_list(),
                    'score': round(comb.score, 2),
                    'analises': comb.get_analises()
                })

            return resultados

        except Exception as e:
            return []

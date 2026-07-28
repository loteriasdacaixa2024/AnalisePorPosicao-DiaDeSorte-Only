"""
Service para Conferência Histórica - Dia de Sorte
Processa apostas contra TODOS os resultados históricos e ranqueia por performance
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from itertools import combinations


class ConferenciaHistoricaService:
    """
    Serviço para processar apostas contra todo o histórico de resultados
    """

    # Mapeamento de nomes de meses para números
    MESES_MAP = {
        'jan': 1, 'janeiro': 1,
        'fev': 2, 'fevereiro': 2,
        'mar': 3, 'março': 3, 'marco': 3,
        'abr': 4, 'abril': 4,
        'mai': 5, 'maio': 5,
        'jun': 6, 'junho': 6,
        'jul': 7, 'julho': 7,
        'ago': 8, 'agosto': 8,
        'set': 9, 'setembro': 9,
        'out': 10, 'outubro': 10,
        'nov': 11, 'novembro': 11,
        'dez': 12, 'dezembro': 12
    }

    MESES_NOMES = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    # Pesos para cálculo do score de ranking
    PESO_7_ACERTOS = 1000
    PESO_6_ACERTOS = 100
    PESO_5_ACERTOS = 10
    PESO_4_ACERTOS = 1
    PESO_MES = 0.5

    @staticmethod
    def parse_linha_aposta(linha: str) -> Optional[Dict]:
        """
        Faz parse de uma linha de aposta em diversos formatos

        Formatos suportados:
        - "1 2 3 4 5 6 7 Janeiro"
        - "01,02,03,04,05,06,07,Jan"
        - "1-2-3-4-5-6-7-jan"
        - "1;2;3;4;5;6;7;1" (último = mês numérico)
        - "1 2 3 4 5 6 7" (sem mês)
        - "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 Maio" (até 15 números)

        Returns:
            Dict com 'numeros' (lista) e 'mes' (int ou None)
            None se linha inválida
        """
        linha = linha.strip()
        if not linha or linha.startswith('#'):
            return None

        # Separar números do mês
        # Primeiro, tentar extrair o mês (palavra ou número no final)
        mes = None
        texto_numeros = linha

        # Tentar encontrar mês como texto (Jan, Janeiro, etc.)
        for mes_texto, mes_num in ConferenciaHistoricaService.MESES_MAP.items():
            # Buscar no final da linha (case insensitive)
            pattern = rf'\b{mes_texto}\b'
            match = re.search(pattern, linha, re.IGNORECASE)
            if match:
                mes = mes_num
                # Remover o mês do texto para processar apenas números
                texto_numeros = linha[:match.start()] + linha[match.end():]
                break

        # Extrair todos os números da linha
        numeros_str = re.findall(r'\d+', texto_numeros)
        numeros = []

        for n_str in numeros_str:
            try:
                n = int(n_str)
                # Verificar se é número válido (1-31)
                if 1 <= n <= 31:
                    numeros.append(n)
                # Se não encontrou mês ainda e o número está entre 1-12, pode ser mês
                elif mes is None and 1 <= n <= 12 and len(numeros) >= 7:
                    # Último número pode ser o mês
                    mes = n
            except ValueError:
                continue

        # Validar quantidade de números (7 a 15)
        if len(numeros) < 7 or len(numeros) > 15:
            return None

        # Verificar duplicatas
        if len(set(numeros)) != len(numeros):
            return None

        return {
            'numeros': sorted(numeros),
            'mes': mes,
            'quantidade': len(numeros)
        }

    @staticmethod
    def parse_arquivo(conteudo: str) -> List[Dict]:
        """
        Faz parse de um arquivo completo de apostas

        Args:
            conteudo: Conteúdo do arquivo TXT

        Returns:
            Lista de apostas válidas com número da linha
        """
        apostas = []
        linhas = conteudo.split('\n')

        for idx, linha in enumerate(linhas, 1):
            resultado = ConferenciaHistoricaService.parse_linha_aposta(linha)
            if resultado:
                resultado['numero_linha'] = idx
                resultado['linha_original'] = linha.strip()
                apostas.append(resultado)

        return apostas

    @staticmethod
    def conferir_aposta_com_sorteio(numeros_apostados: List[int], mes_apostado: Optional[int],
                                      sorteio, usar_ordem_sorteio: bool = False) -> Dict:
        """
        Confere uma aposta com um sorteio específico

        Args:
            numeros_apostados: Lista de números apostados (7-15)
            mes_apostado: Mês apostado (1-12) ou None
            sorteio: Objeto Sorteio do banco de dados
            usar_ordem_sorteio: Se True, usa ordem de sorteio; se False, usa ordem crescente

        Returns:
            Dict com resultado da conferência
        """
        # Obter números sorteados
        if usar_ordem_sorteio:
            numeros_sorteados = sorteio.get_ordem_sorteio_lista()
        else:
            numeros_sorteados = sorteio.get_posicoes_lista()

        # Calcular acertos
        acertos = set(numeros_apostados) & set(numeros_sorteados)
        qtd_acertos = len(acertos)

        # Verificar mês
        acertou_mes = mes_apostado == sorteio.mes_sorte if mes_apostado else False

        # Calcular prêmio
        valor_premio = 0.0
        faixa = None

        if qtd_acertos == 7:
            faixa = '7_acertos'
            valor_premio = sorteio.valor_premio_7_acertos or 0.0
        elif qtd_acertos == 6:
            faixa = '6_acertos'
            valor_premio = sorteio.valor_premio_6_acertos or 0.0
        elif qtd_acertos == 5:
            faixa = '5_acertos'
            valor_premio = sorteio.valor_premio_5_acertos or 25.0
        elif qtd_acertos == 4:
            faixa = '4_acertos'
            valor_premio = sorteio.valor_premio_4_acertos or 5.0

        # Prêmio adicional por mês (sem acertos numéricos suficientes)
        if acertou_mes and qtd_acertos < 4:
            faixa = 'mes_sorte'
            valor_premio = sorteio.valor_premio_mes_sorte or 2.5

        return {
            'concurso': sorteio.concurso,
            'data_sorteio': sorteio.data_sorteio,
            'numeros_sorteados': numeros_sorteados,
            'mes_sorte': sorteio.mes_sorte,
            'acertos': list(acertos),
            'quantidade_acertos': qtd_acertos,
            'acertou_mes': acertou_mes,
            'valor_premio': valor_premio,
            'faixa': faixa,
            'tem_premiacao': qtd_acertos >= 4 or (acertou_mes and qtd_acertos < 4)
        }

    @staticmethod
    def calcular_score_ranking(total_7: int, total_6: int, total_5: int,
                                total_4: int, total_mes: int) -> float:
        """
        Calcula score ponderado para ranking
        """
        return (
            total_7 * ConferenciaHistoricaService.PESO_7_ACERTOS +
            total_6 * ConferenciaHistoricaService.PESO_6_ACERTOS +
            total_5 * ConferenciaHistoricaService.PESO_5_ACERTOS +
            total_4 * ConferenciaHistoricaService.PESO_4_ACERTOS +
            total_mes * ConferenciaHistoricaService.PESO_MES
        )

    @staticmethod
    def analisar_aposta(numeros: List[int]) -> Dict:
        """
        Analisa características estatísticas de uma aposta
        """
        soma = sum(numeros)
        pares = len([n for n in numeros if n % 2 == 0])
        impares = len(numeros) - pares

        return {
            'soma': soma,
            'pares': pares,
            'impares': impares
        }

    @classmethod
    def criar_sessao(cls, nome_arquivo: str, descricao: str = None,
                     estrategia: str = 'ordenada', filtro_min: int = 4) -> 'SessaoConferenciaHistorica':
        """
        Cria uma nova sessão de conferência histórica
        """
        from models.conferencia_historica import SessaoConferenciaHistorica, db

        sessao = SessaoConferenciaHistorica(
            nome_arquivo=nome_arquivo,
            descricao=descricao,
            estrategia=estrategia,
            filtro_acertos_min=filtro_min,
            status='pendente'
        )

        db.session.add(sessao)
        db.session.commit()

        return sessao

    @classmethod
    def processar_arquivo(cls, sessao_id: int, conteudo: str) -> Dict:
        """
        Processa arquivo de apostas e confere contra todo o histórico de forma otimizada
        """
        from models.conferencia_historica import (
            SessaoConferenciaHistorica, ApostaHistorica,
            ResultadoApostaHistorica, db
        )
        from models.sorteio import Sorteio

        sessao = SessaoConferenciaHistorica.query.get(sessao_id)
        if not sessao:
            return {'sucesso': False, 'erro': 'Sessão não encontrada'}

        try:
            sessao.status = 'processando'
            sessao.progresso = 0
            db.session.commit()

            apostas_parseadas = cls.parse_arquivo(conteudo)
            if not apostas_parseadas:
                sessao.status = 'erro'
                sessao.erro_mensagem = 'Nenhuma aposta válida encontrada no arquivo'
                db.session.commit()
                return {'sucesso': False, 'erro': 'Nenhuma aposta válida encontrada'}

            sorteios = Sorteio.query.order_by(Sorteio.concurso).all()
            if not sorteios:
                sessao.status = 'erro'
                sessao.erro_mensagem = 'Nenhum sorteio encontrado'
                db.session.commit()
                return {'sucesso': False, 'erro': 'Nenhum sorteio encontrado'}

            total_apostas = len(apostas_parseadas)
            total_sorteios = len(sorteios)
            usar_ordem_sorteio = (sessao.estrategia == 'sorteio')

            # --- OTIMIZAÇÃO: Cache e conversão antecipada de Sorteios ---
            sorteios_rapidos = []
            for s in sorteios:
                nums_sorteio = s.get_ordem_sorteio_lista() if usar_ordem_sorteio else s.get_posicoes_lista()
                sorteios_rapidos.append({
                    'concurso': s.concurso,
                    'mes_sorte': s.mes_sorte,
                    'numeros_set': set(nums_sorteio),
                    'v7': s.valor_premio_7_acertos or 0.0,
                    'v6': s.valor_premio_6_acertos or 0.0,
                    'v5': s.valor_premio_5_acertos or 25.0,
                    'v4': s.valor_premio_4_acertos or 5.0,
                    'vm': s.valor_premio_mes_sorte or 2.5
                })

            # FASE 1: Inserir todas as Apostas no banco e obter os IDs
            apostas_objects = []
            for aposta_data in apostas_parseadas:
                analise = cls.analisar_aposta(aposta_data['numeros'])
                apostas_objects.append(
                    ApostaHistorica(
                        sessao_id=sessao_id,
                        numero_linha=aposta_data['numero_linha'],
                        numeros_apostados=','.join(map(str, aposta_data['numeros'])),
                        quantidade_numeros=aposta_data['quantidade'],
                        mes_apostado=aposta_data['mes'],
                        soma_numeros=analise['soma'],
                        qtd_pares=analise['pares'],
                        qtd_impares=analise['impares'],
                        total_vitorias=0, total_4_acertos=0, total_5_acertos=0, 
                        total_6_acertos=0, total_7_acertos=0, total_mes_acertado=0,
                        valor_total_premios=0.0, score_ranking=0.0, melhor_acertos=0
                    )
                )

            # Inserir no banco de forma segura. add_all é melhor que bulk_save_objects aqui 
            # pois popula os IDs automaticamente no SQLite sem problemas de dialeto.
            db.session.add_all(apostas_objects)
            db.session.commit()

            # Desacoplar os dados do ORM para evitar que commits futuros expurem os objetos e causem milhares de SELECTs
            apostas_info = [{'id': aposta.id, 'numeros': set(map(int, aposta.numeros_apostados.split(','))), 'mes': aposta.mes_apostado} for aposta in apostas_objects]

            stats = {
                'total_4': 0, 'total_5': 0, 'total_6': 0, 'total_7': 0,
                'total_mes': 0, 'total_premios': 0.0, 'total_premiacoes': 0
            }

            batch_resultados = []
            batch_updates = []

            # FASE 2: Processar comparações em memória e preparar bulk inserts/updates
            for idx, aposta_data in enumerate(apostas_info):
                aposta_set = aposta_data['numeros']
                mes_apostado = aposta_data['mes']

                aposta_stats = {
                    'total_4': 0, 'total_5': 0, 'total_6': 0, 'total_7': 0,
                    'total_mes': 0, 'total_premios': 0.0, 'vitorias': 0,
                    'melhor_concurso': None, 'melhor_acertos': 0
                }

                # LOOP ULTRA-RÁPIDO
                for sr in sorteios_rapidos:
                    hit_nums = aposta_set & sr['numeros_set']
                    qtd_acertos = len(hit_nums)
                    acertou_mes = (mes_apostado == sr['mes_sorte']) if mes_apostado else False
                    
                    tem_premiacao = qtd_acertos >= 4 or (acertou_mes and qtd_acertos < 4)

                    if tem_premiacao:
                        valor_premio = 0.0
                        faixa = None
                        
                        if qtd_acertos == 7:
                            faixa = '7_acertos'
                            valor_premio = sr['v7']
                        elif qtd_acertos == 6:
                            faixa = '6_acertos'
                            valor_premio = sr['v6']
                        elif qtd_acertos == 5:
                            faixa = '5_acertos'
                            valor_premio = sr['v5']
                        elif qtd_acertos == 4:
                            faixa = '4_acertos'
                            valor_premio = sr['v4']
                            
                        if acertou_mes and qtd_acertos < 4:
                            faixa = 'mes_sorte'
                            valor_premio = sr['vm']
                            
                        # Usando dict para inserir muito mais rápido via mappings
                        batch_resultados.append({
                            'aposta_id': aposta_data['id'],
                            'concurso': sr['concurso'],
                            'quantidade_acertos': qtd_acertos,
                            'acertou_mes': acertou_mes,
                            'numeros_acertados': ','.join(map(str, sorted(hit_nums))),
                            'valor_premio': valor_premio,
                            'faixa_premiacao': faixa
                        })

                        aposta_stats['vitorias'] += 1
                        aposta_stats['total_premios'] += valor_premio

                        if qtd_acertos >= 4:
                            key = f"total_{qtd_acertos}"
                            aposta_stats[key] += 1
                            stats[key] += 1

                        if acertou_mes:
                            aposta_stats['total_mes'] += 1
                            stats['total_mes'] += 1

                        if qtd_acertos > aposta_stats['melhor_acertos']:
                            aposta_stats['melhor_acertos'] = qtd_acertos
                            aposta_stats['melhor_concurso'] = sr['concurso']

                score = cls.calcular_score_ranking(
                    aposta_stats['total_7'], aposta_stats['total_6'],
                    aposta_stats['total_5'], aposta_stats['total_4'],
                    aposta_stats['total_mes']
                )

                batch_updates.append({
                    'id': aposta_data['id'],
                    'total_vitorias': aposta_stats['vitorias'],
                    'total_4_acertos': aposta_stats['total_4'],
                    'total_5_acertos': aposta_stats['total_5'],
                    'total_6_acertos': aposta_stats['total_6'],
                    'total_7_acertos': aposta_stats['total_7'],
                    'total_mes_acertado': aposta_stats['total_mes'],
                    'valor_total_premios': aposta_stats['total_premios'],
                    'melhor_concurso': aposta_stats['melhor_concurso'],
                    'melhor_acertos': aposta_stats['melhor_acertos'],
                    'score_ranking': score,
                    'processado_em': datetime.utcnow()
                })

                stats['total_premios'] += aposta_stats['total_premios']
                stats['total_premiacoes'] += aposta_stats['vitorias']
                
                # Inserir em lotes menores para liberar o lock do SQLite rapidamente
                if len(batch_resultados) >= 5000:
                    db.session.bulk_insert_mappings(ResultadoApostaHistorica, batch_resultados)
                    batch_resultados = []
                    # COMMIT IMEDIATO: Libera a trava do banco para que a tela não congele e os próximos arquivos avancem
                    db.session.commit()

                # Atualizar progresso na sessão do banco
                if idx % max(1, (total_apostas // 20)) == 0 or idx == total_apostas - 1:
                    novo_progresso = int((idx + 1) / total_apostas * 100)
                    if novo_progresso != getattr(sessao, '_ultimo_prog', -1):
                        sessao._ultimo_prog = novo_progresso
                        from sqlalchemy import text
                        db.session.execute(
                            text("UPDATE sessoes_conferencia_historica SET progresso = :p, atualizado_em = CURRENT_TIMESTAMP WHERE id = :id"),
                            {"p": novo_progresso, "id": sessao_id}
                        )
                        db.session.commit()
                        
            # Finalizar inserts pendentes
            if batch_resultados:
                db.session.bulk_insert_mappings(ResultadoApostaHistorica, batch_resultados)
                db.session.commit()
                
            # FASE 3: Atualizar todas as estatísticas das apostas com bulk_update_mappings
            if batch_updates:
                # Ordenar por id (boas práticas SQLite)
                batch_updates.sort(key=lambda x: x['id'])
                db.session.bulk_update_mappings(ApostaHistorica, batch_updates)
                db.session.commit()

            # FASE 4: Calcular posições do ranking
            apostas_ordenadas = ApostaHistorica.query.filter_by(sessao_id=sessao_id)\
                .order_by(ApostaHistorica.score_ranking.desc()).all()

            updates_posicoes = []
            for posicao, aposta in enumerate(apostas_ordenadas, 1):
                updates_posicoes.append({
                    'id': aposta.id,
                    'posicao_ranking': posicao
                })
                
            db.session.bulk_update_mappings(ApostaHistorica, updates_posicoes)

            sessao.total_apostas = total_apostas
            sessao.total_concursos_analisados = total_sorteios
            sessao.total_premiacoes = stats['total_premiacoes']
            sessao.total_4_acertos = stats['total_4']
            sessao.total_5_acertos = stats['total_5']
            sessao.total_6_acertos = stats['total_6']
            sessao.total_7_acertos = stats['total_7']
            sessao.total_mes_acertado = stats['total_mes']
            sessao.valor_total_premios = stats['total_premios']
            sessao.status = 'concluido'
            sessao.progresso = 100
            sessao.processado_em = datetime.utcnow()

            db.session.commit()

            return {
                'sucesso': True,
                'sessao_id': sessao_id,
                'estatisticas': sessao.to_dict()
            }

        except Exception as e:
            db.session.rollback()
            try:
                # Tenta salvar o status de erro na sessão
                sessao.status = 'erro'
                sessao.erro_mensagem = str(e)
                db.session.commit()
            except Exception as nested_e:
                # Se o banco ainda estiver lockado, não crashamos a thread
                db.session.rollback()
                print(f"Erro fatal ao salvar status de erro (Sessão {sessao_id}): {nested_e}")
                
            return {'sucesso': False, 'erro': str(e)}

    @classmethod
    def obter_ranking(cls, sessao_id: int, pagina: int = 1, por_pagina: int = 50,
                      filtro_acertos: int = None, ordenacao: str = 'score',
                      ord_dir: str = 'desc', filtros_dinamicos: dict = None) -> Dict:
        """
        Obtém ranking das apostas de uma sessão suportando filtros dinâmicos
        """
        from models.conferencia_historica import SessaoConferenciaHistorica, ApostaHistorica

        sessao = SessaoConferenciaHistorica.query.get(sessao_id)
        if not sessao:
            return {'sucesso': False, 'erro': 'Sessão não encontrada'}

        # Query base para total geral
        query_base = ApostaHistorica.query.filter_by(sessao_id=sessao_id)
        total_geral = query_base.count()

        query = query_base

        # Aplicar filtro de acertos (legado dos dropdowns)
        if filtro_acertos:
            if filtro_acertos == 7:
                query = query.filter(ApostaHistorica.total_7_acertos > 0)
            elif filtro_acertos == 6:
                query = query.filter(ApostaHistorica.total_6_acertos > 0)
            elif filtro_acertos == 5:
                query = query.filter(ApostaHistorica.total_5_acertos > 0)
            elif filtro_acertos == 4:
                query = query.filter(ApostaHistorica.total_4_acertos > 0)

        # Aplicar filtros dinâmicos dos inputs da tabela (Ex: "0", ">5", "<=30")
        if filtros_dinamicos:
            col_map = {
                'vitorias': ApostaHistorica.total_vitorias,
                '7_acertos': ApostaHistorica.total_7_acertos,
                '6_acertos': ApostaHistorica.total_6_acertos,
                '5_acertos': ApostaHistorica.total_5_acertos,
                '4_acertos': ApostaHistorica.total_4_acertos,
                'score': ApostaHistorica.score_ranking,
                'premios': ApostaHistorica.valor_total_premios
            }
            
            for ch, val_str in filtros_dinamicos.items():
                if val_str and ch in col_map:
                    v = str(val_str).strip()
                    if not v: continue
                    col = col_map[ch]
                    try:
                        if v.startswith('>='): query = query.filter(col >= float(v[2:]))
                        elif v.startswith('<='): query = query.filter(col <= float(v[2:]))
                        elif v.startswith('≥'): query = query.filter(col >= float(v[1:]))
                        elif v.startswith('≤'): query = query.filter(col <= float(v[1:]))
                        elif v.startswith('>'): query = query.filter(col > float(v[1:]))
                        elif v.startswith('<'): query = query.filter(col < float(v[1:]))
                        elif v.startswith('='): query = query.filter(col == float(v[1:]))
                        else: query = query.filter(col == float(v))
                    except ValueError:
                        pass # ignora letras nao convertiveis

        # Ordenação dinâmica com controle de asc/desc
        ord_map = {
            'score': ApostaHistorica.score_ranking,
            'vitorias': ApostaHistorica.total_vitorias,
            '7_acertos': ApostaHistorica.total_7_acertos,
            '6_acertos': ApostaHistorica.total_6_acertos,
            '5_acertos': ApostaHistorica.total_5_acertos,
            '4_acertos': ApostaHistorica.total_4_acertos,
            'premios': ApostaHistorica.valor_total_premios,
            'posicao_ranking': ApostaHistorica.posicao_ranking
        }
        
        col_ord = ord_map.get(ordenacao, ApostaHistorica.score_ranking)
        
        if ord_dir == 'asc':
            query = query.order_by(col_ord.asc())
        else:
            query = query.order_by(col_ord.desc())

        # Paginação
        total_filtrado = query.count()
        apostas = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()

        return {
            'sucesso': True,
            'sessao': sessao.to_dict(),
            'apostas': [a.to_dict() for a in apostas],
            'paginacao': {
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total': total_filtrado,
                'total_geral': total_geral,
                'total_paginas': (total_filtrado + por_pagina - 1) // por_pagina
            }
        }

    @classmethod
    def obter_detalhes_aposta(cls, aposta_id: int) -> Dict:
        """
        Obtém detalhes completos de uma aposta, incluindo todos os resultados
        """
        from models.conferencia_historica import ApostaHistorica, ResultadoApostaHistorica

        aposta = ApostaHistorica.query.get(aposta_id)
        if not aposta:
            return {'sucesso': False, 'erro': 'Aposta não encontrada'}

        resultados = ResultadoApostaHistorica.query.filter_by(aposta_id=aposta_id)\
            .order_by(ResultadoApostaHistorica.quantidade_acertos.desc()).all()

        return {
            'sucesso': True,
            'aposta': aposta.to_dict(),
            'resultados': [r.to_dict() for r in resultados]
        }

    @classmethod
    def listar_sessoes(cls, pagina: int = 1, por_pagina: int = 20) -> Dict:
        """
        Lista todas as sessões de conferência histórica e auto-repara sessões presas
        """
        from models.conferencia_historica import SessaoConferenciaHistorica, db
        from datetime import datetime, timedelta

        # CRÍTICO: Em modo WAL do SQLite com multi-threading, é necessário forçar 
        # o fechamento de transações de leitura antigas. Senão a query só retorna o cache
        # e as sessoes "somem" (o usuário via somente 1 registro na tabela).
        try:
            db.session.commit()
        except:
            db.session.rollback()

        # Auto-reparo de tarefas "processando" presas há mais de 60 minutos
        try:
            limite = datetime.utcnow() - timedelta(minutes=60)
            sessoes_presas = SessaoConferenciaHistorica.query.filter(
                SessaoConferenciaHistorica.status == 'processando',
                SessaoConferenciaHistorica.atualizado_em < limite
            ).all()
            if sessoes_presas:
                for sp in sessoes_presas:
                    sp.status = 'erro'
                    sp.erro_mensagem = 'Interrompido/Travado abruptamente.'
                db.session.commit()
        except:
            db.session.rollback() # CRÍTICO: Previne "Database is locked" eterno em caso de erro!

        query = SessaoConferenciaHistorica.query.order_by(
            SessaoConferenciaHistorica.criado_em.desc()
        )

        total = query.count()
        sessoes = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()

        return {
            'sucesso': True,
            'sessoes': [s.to_dict() for s in sessoes],
            'paginacao': {
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total': total,
                'total_paginas': (total + por_pagina - 1) // por_pagina
            }
        }

    @classmethod
    def excluir_sessao(cls, sessao_id: int) -> Dict:
        """
        Exclui uma sessão e todos os dados relacionados.
        Usa DELETE direto via SQL com subquery para máxima velocidade no SQLite.
        """
        from models.conferencia_historica import SessaoConferenciaHistorica, ApostaHistorica, ResultadoApostaHistorica, db
        from sqlalchemy import text

        sessao = SessaoConferenciaHistorica.query.get(sessao_id)
        if not sessao:
            return {'sucesso': False, 'erro': 'Sessão não encontrada'}

        try:
            # Garante WAL checkpoint antes de deletar (evita "database is locked")
            try:
                db.session.execute(text('PRAGMA wal_checkpoint(PASSIVE)'))
            except Exception:
                pass

            # 1. DELETE direto em ResultadoApostaHistorica via subquery — UMA só operação
            #    Em vez de carregar todos os IDs e fazer loops de 500, deixamos o SQLite
            #    resolver o JOIN internamente. Muito mais rápido para sessões com milhões de linhas.
            db.session.execute(
                text("""
                    DELETE FROM resultados_apostas_historicas
                    WHERE aposta_id IN (
                        SELECT id FROM apostas_historicas WHERE sessao_id = :sid
                    )
                """),
                {'sid': sessao_id}
            )
            db.session.commit()

            # 2. DELETE de todas as apostas da sessão (bulk, sem loop)
            db.session.execute(
                text("DELETE FROM apostas_historicas WHERE sessao_id = :sid"),
                {'sid': sessao_id}
            )
            db.session.commit()

            # 3. Deletar a sessão base
            db.session.delete(sessao)
            db.session.commit()

            return {'sucesso': True, 'mensagem': 'Sessão excluída com sucesso'}

        except Exception as e:
            db.session.rollback()
            return {'sucesso': False, 'erro': str(e)}

    @classmethod
    def exportar_ranking(cls, sessao_id: int, formato: str = 'txt',
                         limite: int = None, filtro_acertos: int = None,
                         ordenacao: str = 'score', ord_dir: str = 'desc',
                         filtros_dinamicos: dict = None) -> str:
        """
        Exporta ranking em formato TXT, CSV ou HTML
        """
        from models.conferencia_historica import SessaoConferenciaHistorica, ApostaHistorica
        from sqlalchemy import asc, desc

        sessao = SessaoConferenciaHistorica.query.get(sessao_id)
        if not sessao:
            return None

        query = ApostaHistorica.query.filter_by(sessao_id=sessao_id)

        if filtro_acertos:
            if filtro_acertos == 7:
                query = query.filter(ApostaHistorica.total_7_acertos > 0)
            elif filtro_acertos == 6:
                query = query.filter(ApostaHistorica.total_6_acertos > 0)
            elif filtro_acertos == 5:
                query = query.filter(ApostaHistorica.total_5_acertos > 0)
            elif filtro_acertos == 4:
                query = query.filter(ApostaHistorica.total_4_acertos > 0)

        # Reaplicamos a magica do filtro dinamico
        if filtros_dinamicos:
            col_map = {
                'vitorias': ApostaHistorica.total_vitorias,
                '7_acertos': ApostaHistorica.total_7_acertos,
                '6_acertos': ApostaHistorica.total_6_acertos,
                '5_acertos': ApostaHistorica.total_5_acertos,
                '4_acertos': ApostaHistorica.total_4_acertos,
                'score': ApostaHistorica.score_ranking,
                'premios': ApostaHistorica.valor_total_premios
            }
            
            for ch, val_str in filtros_dinamicos.items():
                if val_str and ch in col_map:
                    v = str(val_str).strip()
                    if not v: continue
                    col = col_map[ch]
                    try:
                        if v.startswith('>='): query = query.filter(col >= float(v[2:]))
                        elif v.startswith('<='): query = query.filter(col <= float(v[2:]))
                        elif v.startswith('≥'): query = query.filter(col >= float(v[1:]))
                        elif v.startswith('≤'): query = query.filter(col <= float(v[1:]))
                        elif v.startswith('>'): query = query.filter(col > float(v[1:]))
                        elif v.startswith('<'): query = query.filter(col < float(v[1:]))
                        elif v.startswith('='): query = query.filter(col == float(v[1:]))
                        else: query = query.filter(col == float(v))
                    except ValueError:
                        pass
        
        # Ordenação igualzinha da tabela UI
        ord_map = {
            'posicao_ranking': ApostaHistorica.posicao_ranking,
            'vitorias': ApostaHistorica.total_vitorias,
            '7_acertos': ApostaHistorica.total_7_acertos,
            '6_acertos': ApostaHistorica.total_6_acertos,
            '5_acertos': ApostaHistorica.total_5_acertos,
            '4_acertos': ApostaHistorica.total_4_acertos,
            'score': ApostaHistorica.score_ranking,
            'premios': ApostaHistorica.valor_total_premios
        }
        ord_col = ord_map.get(ordenacao, ApostaHistorica.score_ranking)
        if ord_dir == 'asc':
            query = query.order_by(asc(ord_col))
        else:
            query = query.order_by(desc(ord_col))

        if limite:
            query = query.limit(limite)

        apostas = query.all()

        if formato == 'txt':
            linhas = []

            for aposta in apostas:
                numeros_str = ' '.join(f"{n:02d}" for n in aposta.get_numeros_lista())
                mes_str = aposta.get_mes_nome()[:3].capitalize() if aposta.mes_apostado else ''
                linha_aposta = f"{numeros_str} {mes_str}".strip()
                linhas.append(linha_aposta)

            return '\n'.join(linhas)

        elif formato == 'csv':
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'Posição', 'Números', 'Mês', 'Total Vitórias',
                '7 Acertos', '6 Acertos', '5 Acertos', '4 Acertos',
                'Mês Acertado', 'Score', 'Valor Prêmios'
            ])

            for aposta in apostas:
                writer.writerow([
                    aposta.posicao_ranking,
                    ' '.join(map(str, aposta.get_numeros_lista())),
                    aposta.get_mes_nome() if aposta.mes_apostado else '',
                    aposta.total_vitorias,
                    aposta.total_7_acertos,
                    aposta.total_6_acertos,
                    aposta.total_5_acertos,
                    aposta.total_4_acertos,
                    aposta.total_mes_acertado,
                    aposta.score_ranking,
                    f"{aposta.valor_total_premios:.2f}"
                ])

            return output.getvalue()

        return None

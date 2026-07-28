"""
Serviço de Geração de Combinações Inteligentes - Dia de Sorte
Gera todas as combinações possíveis a partir do universo de números apostados
e aplica filtros inteligentes para análise e ordenação.
"""

import os
import json
from itertools import combinations
from typing import Dict, List, Optional, Tuple
from models.sorteio import Sorteio


class CombinacoesService:
    """
    Service para geração e análise de combinações inteligentes
    """

    # Diretório base para arquivos de apostas
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conferencia_apostas')



    # Limites de faixa de soma baseados em análise histórica
    SOMA_MINIMA_IDEAL = 95
    SOMA_MAXIMA_IDEAL = 155

    # Proporções ideais par/ímpar (mais comuns historicamente)
    PROPORCOES_IDEAIS = [(3, 4), (4, 3)]

    # Mapeamento de meses
    MESES = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
        5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    @staticmethod
    def obter_apostas_concurso(numero_concurso: int) -> Dict:
        """
        Obtém as apostas cadastradas para um concurso específico

        Args:
            numero_concurso: Número do concurso

        Returns:
            Dicionário com apostas e informações do concurso
        """
        try:
            # Buscar sorteio no banco
            sorteio = Sorteio.query.filter_by(concurso=numero_concurso).first()

            if not sorteio:
                return {
                    'sucesso': False,
                    'erro': 'concurso_nao_encontrado',
                    'mensagem': f'Concurso {numero_concurso} não encontrado no banco de dados'
                }

            # Caminho da pasta do concurso
            pasta_concurso = os.path.join(CombinacoesService.BASE_DIR, str(numero_concurso))

            if not os.path.exists(pasta_concurso):
                return {
                    'sucesso': False,
                    'erro': 'pasta_nao_encontrada',
                    'mensagem': f'Pasta do concurso {numero_concurso} não encontrada'
                }

            # Procurar arquivo apostas.json
            arquivo_json = os.path.join(pasta_concurso, 'apostas.json')

            if not os.path.exists(arquivo_json):
                return {
                    'sucesso': False,
                    'erro': 'arquivo_nao_encontrado',
                    'mensagem': f'Arquivo apostas.json não encontrado para o concurso {numero_concurso}'
                }

            # Ler arquivo JSON
            with open(arquivo_json, 'r', encoding='utf-8-sig') as f:
                dados = json.load(f)

            # Extrair apostas
            apostas = dados.get('apostas', [])

            # Resultado do sorteio
            numeros_sorteados = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]

            return {
                'sucesso': True,
                'concurso': numero_concurso,
                'data_sorteio': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else None,
                'numeros_sorteados': numeros_sorteados,
                'mes_sorte': sorteio.mes_sorte,
                'apostas': apostas,
                'total_apostas': len(apostas)
            }

        except json.JSONDecodeError as e:
            return {
                'sucesso': False,
                'erro': 'json_malformado',
                'mensagem': f'Erro ao ler apostas.json: {str(e)}'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': 'excecao',
                'mensagem': f'Erro ao obter apostas: {str(e)}'
            }

    @staticmethod
    def extrair_universo(apostas: List[Dict]) -> List[int]:
        """
        Extrai o universo de números únicos das apostas

        Args:
            apostas: Lista de apostas

        Returns:
            Lista de números únicos ordenados
        """
        universo = set()

        for aposta in apostas:
            numeros = aposta.get('numeros', [])
            for num in numeros:
                if 1 <= num <= 31:
                    universo.add(num)

        return sorted(list(universo))

    @staticmethod
    def gerar_combinacoes(universo: List[int], tamanho: int = 7) -> List[Tuple[int, ...]]:
        """
        Gera todas as combinações possíveis do universo

        Args:
            universo: Lista de números disponíveis
            tamanho: Tamanho da combinação (padrão: 7 para Dia de Sorte)

        Returns:
            Lista de combinações (tuplas)
        """
        if len(universo) < tamanho:
            return []

        return list(combinations(universo, tamanho))

    @staticmethod
    def calcular_soma(numeros: Tuple[int, ...]) -> int:
        """Calcula a soma dos números"""
        return sum(numeros)

    @staticmethod
    def contar_pares_impares(numeros: Tuple[int, ...]) -> Tuple[int, int]:
        """Conta quantos pares e ímpares"""
        pares = sum(1 for n in numeros if n % 2 == 0)
        impares = len(numeros) - pares
        return (pares, impares)

    @staticmethod
    def calcular_distribuicao_faixas(numeros: Tuple[int, ...]) -> Dict[str, int]:
        """
        Calcula distribuição por faixas numéricas

        Faixas:
        - Baixa: 01-10
        - Média: 11-20
        - Alta: 21-31
        """
        baixa = sum(1 for n in numeros if 1 <= n <= 10)
        media = sum(1 for n in numeros if 11 <= n <= 20)
        alta = sum(1 for n in numeros if 21 <= n <= 31)

        return {
            'baixa': baixa,
            'media': media,
            'alta': alta
        }

    @staticmethod
    def contar_sequencias(numeros: Tuple[int, ...]) -> int:
        """
        Conta o tamanho da maior sequência consecutiva

        Ex: (1, 2, 3, 5, 7, 9, 10) -> retorna 3 (1,2,3)
        """
        if len(numeros) == 0:
            return 0

        nums_ordenados = sorted(numeros)
        max_seq = 1
        seq_atual = 1

        for i in range(1, len(nums_ordenados)):
            if nums_ordenados[i] == nums_ordenados[i - 1] + 1:
                seq_atual += 1
                max_seq = max(max_seq, seq_atual)
            else:
                seq_atual = 1

        return max_seq

    @staticmethod
    def contar_repeticoes(numeros: Tuple[int, ...], numeros_anteriores: List[int]) -> int:
        """Conta quantos números repetem do sorteio anterior"""
        return len(set(numeros) & set(numeros_anteriores))

    @staticmethod
    def calcular_digitos_finais(numeros: Tuple[int, ...]) -> Dict[int, int]:
        """Conta a distribuição de dígitos finais (0-9)"""
        digitos = {}
        for n in numeros:
            digito = n % 10
            digitos[digito] = digitos.get(digito, 0) + 1
        return digitos

    @staticmethod
    def calcular_score(
        numeros: Tuple[int, ...],
        numeros_anteriores: List[int] = None
    ) -> int:
        """
        Calcula o score de qualidade de uma combinação (0-100)

        Critérios:
        - Soma dentro da faixa ideal: +30 pontos
        - Proporção par/ímpar ideal: +25 pontos
        - Distribuição equilibrada de faixas: +20 pontos
        - Sem sequências longas (<=3): +15 pontos
        - Repetição moderada (1-2 do último): +10 pontos
        """
        score = 0

        # 1. Soma (0-30 pontos)
        soma = CombinacoesService.calcular_soma(numeros)
        if CombinacoesService.SOMA_MINIMA_IDEAL <= soma <= CombinacoesService.SOMA_MAXIMA_IDEAL:
            score += 30
        elif 85 <= soma <= 165:
            score += 15  # Faixa aceitável
        # Fora da faixa: 0 pontos

        # 2. Pares/Ímpares (0-25 pontos)
        pares, impares = CombinacoesService.contar_pares_impares(numeros)
        if (pares, impares) in CombinacoesService.PROPORCOES_IDEAIS:
            score += 25
        elif (pares, impares) in [(2, 5), (5, 2)]:
            score += 12  # Aceitável
        # Proporções extremas: 0 pontos

        # 3. Distribuição de faixas (0-20 pontos)
        dist = CombinacoesService.calcular_distribuicao_faixas(numeros)
        # Ideal: nenhuma faixa vazia, nenhuma com mais de 4
        if all(v >= 1 for v in dist.values()) and all(v <= 4 for v in dist.values()):
            score += 20
        elif all(v <= 5 for v in dist.values()):
            score += 10  # Aceitável
        # Concentração extrema: 0 pontos

        # 4. Sequências (0-15 pontos)
        max_seq = CombinacoesService.contar_sequencias(numeros)
        if max_seq <= 2:
            score += 15
        elif max_seq == 3:
            score += 10
        elif max_seq == 4:
            score += 5
        # Sequências longas: 0 pontos

        # 5. Repetição do último sorteio (0-10 pontos)
        if numeros_anteriores:
            repeticoes = CombinacoesService.contar_repeticoes(numeros, numeros_anteriores)
            if 1 <= repeticoes <= 2:
                score += 10
            elif repeticoes == 3:
                score += 5
            # 0 ou 4+ repetições: 0 pontos
        else:
            score += 5  # Sem referência, pontuação neutra

        return score

    @staticmethod
    def analisar_combinacao(
        numeros: Tuple[int, ...],
        numeros_anteriores: List[int] = None
    ) -> Dict:
        """
        Analisa uma combinação e retorna todas as métricas

        Returns:
            Dicionário com todas as análises
        """
        soma = CombinacoesService.calcular_soma(numeros)
        pares, impares = CombinacoesService.contar_pares_impares(numeros)
        distribuicao = CombinacoesService.calcular_distribuicao_faixas(numeros)
        max_seq = CombinacoesService.contar_sequencias(numeros)
        score = CombinacoesService.calcular_score(numeros, numeros_anteriores)

        repeticoes = 0
        acertos = 0
        if numeros_anteriores:
            repeticoes = CombinacoesService.contar_repeticoes(numeros, numeros_anteriores)
            acertos = len(set(numeros) & set(numeros_anteriores))

        return {
            'numeros': list(numeros),
            'soma': soma,
            'pares': pares,
            'impares': impares,
            'distribuicao': distribuicao,
            'max_sequencia': max_seq,
            'repeticoes': repeticoes,
            'acertos': acertos,
            'score': score,
            'soma_fora_faixa': soma < CombinacoesService.SOMA_MINIMA_IDEAL or soma > CombinacoesService.SOMA_MAXIMA_IDEAL,
            'proporcao_ideal': (pares, impares) in CombinacoesService.PROPORCOES_IDEAIS
        }

    @staticmethod
    def gerar_combinacoes_analisadas(
        numero_concurso: int,
        filtros: Dict = None,
        ordenacao: str = 'score_desc',
        pagina: int = 1,
        por_pagina: int = 50,
        mes_aposta: int = None
    ) -> Dict:
        """
        Gera e analisa todas as combinações para um concurso

        Args:
            numero_concurso: Número do concurso
            filtros: Dicionário com filtros opcionais
            ordenacao: Critério de ordenação
            pagina: Página atual
            por_pagina: Itens por página
            mes_aposta: Mês escolhido para as apostas (1-12)

        Returns:
            Dicionário com combinações analisadas e paginadas
        """
        # Obter apostas do concurso
        dados_apostas = CombinacoesService.obter_apostas_concurso(numero_concurso)

        if not dados_apostas['sucesso']:
            return dados_apostas

        apostas = dados_apostas['apostas']
        numeros_sorteados = dados_apostas['numeros_sorteados']

        # Extrair universo
        universo = CombinacoesService.extrair_universo(apostas)

        if len(universo) < 7:
            return {
                'sucesso': False,
                'erro': 'universo_insuficiente',
                'mensagem': f'Universo insuficiente: apenas {len(universo)} números únicos encontrados (mínimo: 7)'
            }

        # Calcular total de combinações possíveis
        from math import comb
        total_combinacoes = comb(len(universo), 7)

        # Aviso para universos grandes
        aviso = None
        if total_combinacoes > 100000:
            aviso = f'⚠️ Volume elevado: {total_combinacoes:,} combinações. O processamento pode levar alguns segundos.'

        # Gerar todas as combinações
        todas_combinacoes = CombinacoesService.gerar_combinacoes(universo, 7)

        # Analisar cada combinação
        combinacoes_analisadas = []
        for comb_tuple in todas_combinacoes:
            analise = CombinacoesService.analisar_combinacao(comb_tuple, numeros_sorteados)
            combinacoes_analisadas.append(analise)

        # Aplicar filtros
        total_geral = len(combinacoes_analisadas)
        if filtros:
            combinacoes_analisadas = CombinacoesService._aplicar_filtros(
                combinacoes_analisadas, filtros
            )

        total_filtradas = len(combinacoes_analisadas)

        # Aplicar ordenação
        combinacoes_analisadas = CombinacoesService._aplicar_ordenacao(
            combinacoes_analisadas, ordenacao
        )

        # Calcular paginação
        total_paginas = (total_filtradas + por_pagina - 1) // por_pagina
        inicio = (pagina - 1) * por_pagina
        fim = inicio + por_pagina

        combinacoes_paginadas = combinacoes_analisadas[inicio:fim]

        # Adicionar mês a cada combinação
        mes_nome = CombinacoesService.MESES.get(mes_aposta, '') if mes_aposta else ''

        return {
            'sucesso': True,
            'concurso': numero_concurso,
            'data_sorteio': dados_apostas['data_sorteio'],
            'universo': universo,
            'total_universo': len(universo),
            'total_combinacoes': total_combinacoes,
            'total_filtradas': total_filtradas,
            'aviso': aviso,
            'paginacao': {
                'pagina_atual': pagina,
                'por_pagina': por_pagina,
                'total_paginas': total_paginas,
                'total_itens': total_filtradas,
                'total_geral': total_geral
            },
            'ordenacao': ordenacao,
            'filtros_aplicados': filtros or {},
            'mes_aposta': mes_aposta,
            'mes_nome': mes_nome,
            'combinacoes': combinacoes_paginadas,
            'numeros_sorteados': numeros_sorteados,
            'mes_sorte': dados_apostas['mes_sorte']
        }

    @staticmethod
    def _aplicar_filtros(combinacoes: List[Dict], filtros: Dict) -> List[Dict]:
        """Aplica filtros às combinações"""
        resultado = combinacoes

        # Filtro: Soma mínima/máxima
        if 'soma_min' in filtros and filtros['soma_min']:
            resultado = [c for c in resultado if c['soma'] >= filtros['soma_min']]

        if 'soma_max' in filtros and filtros['soma_max']:
            resultado = [c for c in resultado if c['soma'] <= filtros['soma_max']]

        # Filtro: Pares/Ímpares
        if 'pares' in filtros and filtros['pares'] is not None:
            pares_lista = filtros['pares'] if isinstance(filtros['pares'], list) else [filtros['pares']]
            resultado = [c for c in resultado if c['pares'] in pares_lista]

        # Filtro: Máximo de sequências
        if 'max_sequencia' in filtros and filtros['max_sequencia']:
            resultado = [c for c in resultado if c['max_sequencia'] <= filtros['max_sequencia']]

        # Filtro: Repetições do último sorteio
        if 'repeticoes_min' in filtros and filtros['repeticoes_min'] is not None:
            resultado = [c for c in resultado if c['repeticoes'] >= filtros['repeticoes_min']]

        if 'repeticoes_max' in filtros and filtros['repeticoes_max'] is not None:
            resultado = [c for c in resultado if c['repeticoes'] <= filtros['repeticoes_max']]

        # Filtro: Score mínimo
        if 'score_min' in filtros and filtros['score_min']:
            resultado = [c for c in resultado if c['score'] >= filtros['score_min']]

        # Filtro: Apenas proporções ideais
        if filtros.get('apenas_proporcao_ideal'):
            resultado = [c for c in resultado if c['proporcao_ideal']]

        # Filtro: Excluir soma fora da faixa
        if filtros.get('excluir_soma_fora'):
            resultado = [c for c in resultado if not c['soma_fora_faixa']]

        # Filtro: Números específicos
        if 'numeros' in filtros and filtros['numeros']:
            numeros_buscados = filtros['numeros']
            busca_exata = filtros.get('busca_exata', False)

            if busca_exata:
                # Busca exata: combinação deve conter TODOS os números buscados
                resultado = [c for c in resultado if all(num in c['numeros'] for num in numeros_buscados)]
            else:
                # Busca parcial: combinação deve conter PELO MENOS UM dos números buscados
                resultado = [c for c in resultado if any(num in c['numeros'] for num in numeros_buscados)]

        return resultado

    @staticmethod
    def _aplicar_ordenacao(combinacoes: List[Dict], ordenacao: str) -> List[Dict]:
        """Aplica ordenação às combinações"""
        if ordenacao == 'score_desc':
            return sorted(combinacoes, key=lambda x: x['score'], reverse=True)
        elif ordenacao == 'score_asc':
            return sorted(combinacoes, key=lambda x: x['score'])
        elif ordenacao == 'soma_asc':
            return sorted(combinacoes, key=lambda x: x['soma'])
        elif ordenacao == 'soma_desc':
            return sorted(combinacoes, key=lambda x: x['soma'], reverse=True)
        elif ordenacao == 'pares_asc':
            return sorted(combinacoes, key=lambda x: x['pares'])
        elif ordenacao == 'pares_desc':
            return sorted(combinacoes, key=lambda x: x['pares'], reverse=True)
        elif ordenacao == 'repeticoes_desc':
            return sorted(combinacoes, key=lambda x: x['repeticoes'], reverse=True)
        elif ordenacao == 'repeticoes_asc':
            return sorted(combinacoes, key=lambda x: x['repeticoes'])
        elif ordenacao == 'acertos_desc':
            return sorted(combinacoes, key=lambda x: x['acertos'], reverse=True)
        elif ordenacao == 'acertos_asc':
            return sorted(combinacoes, key=lambda x: x['acertos'])
        elif ordenacao == 'crescente':
            return sorted(combinacoes, key=lambda x: tuple(x['numeros']))
        elif ordenacao == 'sorteio':
            # Ordem natural (como foi gerado)
            return combinacoes
        else:
            return sorted(combinacoes, key=lambda x: x['score'], reverse=True)

    @staticmethod
    def exportar_combinacoes(
        numero_concurso: int,
        filtros: Dict = None,
        ordenacao: str = 'score_desc',
        limite: int = None,
        mes_aposta: int = None,
        formato: str = 'txt'
    ) -> Dict:
        """
        Exporta combinações para arquivo TXT

        Args:
            numero_concurso: Número do concurso
            filtros: Filtros a aplicar
            ordenacao: Critério de ordenação
            limite: Limite de combinações (None = todas)
            mes_aposta: Mês para incluir no arquivo
            formato: Formato de exportação ('txt')

        Returns:
            Dicionário com conteúdo do arquivo
        """
        # Gerar todas as combinações sem paginação
        resultado = CombinacoesService.gerar_combinacoes_analisadas(
            numero_concurso=numero_concurso,
            filtros=filtros,
            ordenacao=ordenacao,
            pagina=1,
            por_pagina=999999,  # Obter todas
            mes_aposta=mes_aposta
        )

        if not resultado['sucesso']:
            return resultado

        combinacoes = resultado['combinacoes']

        # Aplicar limite se especificado
        if limite and limite > 0:
            combinacoes = combinacoes[:limite]

        # Obter nome do mês
        mes_nome = CombinacoesService.MESES.get(mes_aposta, '') if mes_aposta else ''

        # Gerar conteúdo TXT
        linhas = []
        for comb in combinacoes:
            numeros_str = ' '.join(str(n).zfill(2) for n in comb['numeros'])
            if mes_nome:
                linhas.append(f"{numeros_str} {mes_nome}")
            else:
                linhas.append(numeros_str)

        conteudo = '\n'.join(linhas)

        return {
            'sucesso': True,
            'formato': formato,
            'total_exportadas': len(combinacoes),
            'conteudo': conteudo,
            'nome_arquivo': f'combinacoes_concurso_{numero_concurso}.txt'
        }

    @staticmethod
    def obter_estatisticas_combinacoes(numero_concurso: int) -> Dict:
        """
        Obtém estatísticas gerais das combinações possíveis

        Returns:
            Dicionário com estatísticas resumidas
        """
        # Obter apostas do concurso
        dados_apostas = CombinacoesService.obter_apostas_concurso(numero_concurso)

        if not dados_apostas['sucesso']:
            return dados_apostas

        apostas = dados_apostas['apostas']
        numeros_sorteados = dados_apostas['numeros_sorteados']

        # Extrair universo
        universo = CombinacoesService.extrair_universo(apostas)

        if len(universo) < 7:
            return {
                'sucesso': False,
                'erro': 'universo_insuficiente',
                'mensagem': f'Universo insuficiente: apenas {len(universo)} números únicos'
            }

        from math import comb
        total_combinacoes = comb(len(universo), 7)

        # Gerar todas e calcular estatísticas
        todas_combinacoes = CombinacoesService.gerar_combinacoes(universo, 7)

        # Estatísticas
        scores = []
        somas = []
        distribuicao_pares = {i: 0 for i in range(8)}  # 0-7 pares
        combinacoes_ideais = 0
        combinacoes_score_alto = 0  # score >= 70

        for comb_tuple in todas_combinacoes:
            analise = CombinacoesService.analisar_combinacao(comb_tuple, numeros_sorteados)
            scores.append(analise['score'])
            somas.append(analise['soma'])
            distribuicao_pares[analise['pares']] += 1

            if analise['proporcao_ideal'] and not analise['soma_fora_faixa']:
                combinacoes_ideais += 1

            if analise['score'] >= 70:
                combinacoes_score_alto += 1

        return {
            'sucesso': True,
            'concurso': numero_concurso,
            'universo': universo,
            'total_universo': len(universo),
            'total_combinacoes': total_combinacoes,
            'estatisticas': {
                'score_medio': sum(scores) / len(scores) if scores else 0,
                'score_maximo': max(scores) if scores else 0,
                'score_minimo': min(scores) if scores else 0,
                'soma_media': sum(somas) / len(somas) if somas else 0,
                'soma_maxima': max(somas) if somas else 0,
                'soma_minima': min(somas) if somas else 0,
                'distribuicao_pares': distribuicao_pares,
                'combinacoes_ideais': combinacoes_ideais,
                'percentual_ideais': round((combinacoes_ideais / total_combinacoes) * 100, 2) if total_combinacoes > 0 else 0,
                'combinacoes_score_alto': combinacoes_score_alto,
                'percentual_score_alto': round((combinacoes_score_alto / total_combinacoes) * 100, 2) if total_combinacoes > 0 else 0
            },
            'numeros_sorteados': numeros_sorteados,
            'mes_sorte': dados_apostas['mes_sorte']
        }

    @staticmethod
    def listar_concursos_com_apostas() -> Dict:
        """
        Lista todos os concursos que possuem arquivo apostas.json

        Returns:
            Dicionário com lista de concursos disponíveis
        """
        try:
            if not os.path.exists(CombinacoesService.BASE_DIR):
                return {
                    'sucesso': True,
                    'concursos': [],
                    'total': 0
                }

            concursos = []

            for pasta in os.listdir(CombinacoesService.BASE_DIR):
                pasta_path = os.path.join(CombinacoesService.BASE_DIR, pasta)

                if not os.path.isdir(pasta_path):
                    continue

                try:
                    numero_concurso = int(pasta)
                except ValueError:
                    continue

                # Verificar se tem apostas.json
                arquivo_json = os.path.join(pasta_path, 'apostas.json')
                if not os.path.exists(arquivo_json):
                    continue

                # Contar apostas
                try:
                    with open(arquivo_json, 'r', encoding='utf-8-sig') as f:
                        dados = json.load(f)
                    total_apostas = len(dados.get('apostas', []))
                except Exception:
                    total_apostas = 0

                # Verificar se concurso existe no banco
                sorteio = Sorteio.query.filter_by(concurso=numero_concurso).first()

                concursos.append({
                    'numero_concurso': numero_concurso,
                    'total_apostas': total_apostas,
                    'resultado_disponivel': sorteio is not None,
                    'data_sorteio': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio and sorteio.data_sorteio else None
                })

            # Ordenar por número do concurso (mais recente primeiro)
            concursos.sort(key=lambda x: x['numero_concurso'], reverse=True)

            return {
                'sucesso': True,
                'concursos': concursos,
                'total': len(concursos)
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'mensagem': f'Erro ao listar concursos: {str(e)}'
            }

from collections import Counter
from datetime import datetime
from typing import List, Set


class AnaliseGapsTransicoesApostasService:
    @staticmethod
    def _validar_apostas(apostas_list: List[List[int]]) -> List[Set[int]]:
        if not isinstance(apostas_list, list) or len(apostas_list) == 0:
            raise ValueError('Informe uma lista de apostas')

        apostas_processadas = []
        for idx, aposta in enumerate(apostas_list, start=1):
            if not isinstance(aposta, (list, tuple, set)):
                raise ValueError(f'Aposta {idx} deve ser lista/tupla')

            numeros = [int(n) for n in aposta]
            if len(numeros) < 7 or len(numeros) > 15:
                raise ValueError(f'Aposta {idx} deve ter entre 7 e 15 dezenas')
            if any(n < 1 or n > 31 for n in numeros):
                raise ValueError(f'Aposta {idx} possui dezenas fora do intervalo 1-31')

            aposta_set = set(numeros)
            if len(aposta_set) != len(numeros):
                raise ValueError(f'Aposta {idx} possui dezenas repetidas')

            apostas_processadas.append(aposta_set)

        return apostas_processadas

    @staticmethod
    def _validar_anterior(dezenas_anterior: List[int]) -> List[int]:
        if not dezenas_anterior or len(dezenas_anterior) != 7:
            raise ValueError('Resultado anterior deve ter exatamente 7 dezenas')
        numeros = [int(n) for n in dezenas_anterior]
        if any(n < 1 or n > 31 for n in numeros):
            raise ValueError('Dezenas do concurso anterior devem estar entre 1 e 31')
        if len(set(numeros)) != 7:
            raise ValueError('Dezenas do concurso anterior nao podem repetir')
        return sorted(numeros)

    @staticmethod
    def analisar_gaps_transicoes(dezenas_anterior: List[int], apostas_list: List[List[int]]):
        anterior = sorted(AnaliseGapsTransicoesApostasService._validar_anterior(dezenas_anterior))
        apostas = AnaliseGapsTransicoesApostasService._validar_apostas(apostas_list)
        total_apostas = len(apostas)

        # Estatísticas acumuladas
        soma_repetidas = 0
        soma_vizinhas = 0
        soma_novas = 0

        # Conjuntos para listagem única
        set_repetidas = set()
        set_vizinhas = set()
        set_novas = set()

        for aposta in apostas:
            # Contagem por aposta
            rep = 0
            viz = 0
            nov = 0
            
            for num in aposta:
                if num in anterior:
                    rep += 1
                    set_repetidas.add(num)
                elif (num - 1 in anterior) or (num + 1 in anterior) or \
                     (num - 2 in anterior) or (num + 2 in anterior):
                    viz += 1
                    set_vizinhas.add(num)
                else:
                    nov += 1
                    set_novas.add(num)
            
            soma_repetidas += rep
            soma_vizinhas += viz
            soma_novas += nov

        # Médias
        media_repetidas = soma_repetidas / total_apostas if total_apostas else 0
        media_vizinhas = soma_vizinhas / total_apostas if total_apostas else 0
        media_novas = soma_novas / total_apostas if total_apostas else 0

        # Diagnóstico baseado na MÉDIA POR APOSTA (Muito mais útil para o jogador)
        # Padrão Dia de Sorte (7 dezenas): Média esperada ~1 a 3 repetidas.
        risco = 'Equilibrado'
        recomendacoes = []

        if media_repetidas > 4:
            risco = 'Muito Repetitivo'
            recomendacoes.append('Muitas dezenas do concurso anterior em cada jogo. Reduza para 1 a 3 repetidas por bilhete.')
        elif media_repetidas < 0.5:
            risco = 'Muito Frio'
            recomendacoes.append('Poucas repetidas. O padrão costuma ter pelo menos 1 repetida do anterior.')
        
        if media_vizinhas > 4:
            if risco == 'Equilibrado': risco = 'Muito Deslocado'
            recomendacoes.append('Excesso de números vizinhos. Tente espalhar mais.')

        if not recomendacoes:
            recomendacoes.append('Manter média de 1-3 repetidas e 2-3 vizinhas por aposta.')

        return {
            'status': 'sucesso',
            'timestamp': datetime.utcnow().isoformat(),
            'classificacao_dezenas': {
                'repetidas': sorted(list(set_repetidas)),
                'deslocadas': sorted(list(set_vizinhas)),
                'novas': sorted(list(set_novas))
            },
            'medias_por_aposta': {
                'repetidas': round(media_repetidas, 2),
                'vizinhas': round(media_vizinhas, 2),
                'novas': round(media_novas, 2)
            },
            'diagnostico': risco,
            'recomendacoes': recomendacoes
        }

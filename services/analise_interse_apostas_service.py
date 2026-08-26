from collections import Counter
from datetime import datetime
from typing import List, Set


class AnaliseInterseApostasService:
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
    def calcular_interse_apostas(apostas_list: List[List[int]]):
        """Calcula intersecoes par-a-par e diagnostico estrutural das apostas."""
        apostas = AnaliseInterseApostasService._validar_apostas(apostas_list)
        total = len(apostas)

        matriz = {}
        pares_intersecao = []
        union_all = set().union(*apostas)
        intersecao_com_total = {}

        for i, aposta_i in enumerate(apostas, start=1):
            chave_i = f'aposta_{i}'
            matriz[chave_i] = {}
            intersecao_com_total[chave_i] = len(aposta_i & (union_all - aposta_i))

            for j, aposta_j in enumerate(apostas, start=1):
                if i == j:
                    continue
                chave_j = f'aposta_{j}'
                valor = len(aposta_i & aposta_j)
                matriz[chave_i][chave_j] = valor
                if j > i:
                    pares_intersecao.append(valor)

        media = round(sum(pares_intersecao) / len(pares_intersecao), 2) if pares_intersecao else 0.0
        maxima = max(pares_intersecao) if pares_intersecao else 0
        minima = min(pares_intersecao) if pares_intersecao else 0

        recomendacoes = []
        if media < 2:
            diagnostico = 'PULVERIZACAO CRITICA - intersecao media muito baixa'
            recomendacoes.append('Aumentar repeticao de dezenas entre jogos para segurar faltantes')
        elif media < 3:
            diagnostico = 'ATENCAO - intersecao moderada, pode dispersar faltantes'
            recomendacoes.append('Repetir pares-chave em pelo menos 2 apostas')
        else:
            diagnostico = 'OK - intersecao adequada para concentrar faltantes'
            recomendacoes.append('Manter intersecao acima de 3 para jogos de 7-15 dezenas')

        dispersao = dict(Counter(pares_intersecao))

        return {
            'status': 'sucesso',
            'timestamp': datetime.utcnow().isoformat(),
            'total_apostas': total,
            'matriz_intersecao': matriz,
            'media_intersecao': media,
            'maxima_intersecao': maxima,
            'minima_intersecao': minima,
            'intersecao_conjunto_total': intersecao_com_total,
            'distribuicao_intersecoes': dispersao,
            'diagnostico': diagnostico,
            'recomendacoes': recomendacoes
        }

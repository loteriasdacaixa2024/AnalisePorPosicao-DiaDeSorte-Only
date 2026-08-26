from datetime import datetime
from itertools import combinations
from typing import List, Set
from collections import Counter


class AnaliseDesdobramentoValidatorService:
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
    def validar_desdobramento(dezenas_anterior: List[int], apostas_list: List[List[int]]):
        anterior = AnaliseDesdobramentoValidatorService._validar_anterior(dezenas_anterior)
        apostas = AnaliseDesdobramentoValidatorService._validar_apostas(apostas_list)

        pares_possiveis = list(combinations(anterior, 2))
        total_pares = len(pares_possiveis)

        freq_dezenas = Counter()
        for aposta in apostas:
            freq_dezenas.update(aposta)

        pares_cobertos = []
        pares_faltantes = []

        for par in pares_possiveis:
            coberto = any(par[0] in aposta and par[1] in aposta for aposta in apostas)
            if coberto:
                pares_cobertos.append(par)
            else:
                freq_min = min(freq_dezenas.get(par[0], 0), freq_dezenas.get(par[1], 0))
                importancia = 'alta' if freq_min <= 1 else 'media'
                pares_faltantes.append({
                    'par': list(par),
                    'importancia': importancia
                })

        cobertura_percentual = round((len(pares_cobertos) / total_pares) * 100, 2) if total_pares else 0.0

        if cobertura_percentual >= 90:
            diagnostico = 'Desdobramento bem aplicado; cobertura alta dos 21 pares'
        elif cobertura_percentual >= 75:
            diagnostico = 'Cobertura razoavel; alguns pares criticos ficaram de fora'
        else:
            diagnostico = 'Cobertura baixa; revise distribuicao dos pares do concurso anterior'

        return {
            'status': 'sucesso',
            'timestamp': datetime.utcnow().isoformat(),
            'total_pares_possiveis': total_pares,
            'pares_cobertos': len(pares_cobertos),
            'pares_presentes': [list(p) for p in pares_cobertos],
            'cobertura_percentual': cobertura_percentual,
            'pares_faltantes': pares_faltantes,
            'diagnostico': diagnostico,
            'recomendacoes': [
                'Garanta que cada par do concurso anterior apareca em pelo menos uma aposta',
                'Priorize pares marcados como importancia alta'
            ]
        }

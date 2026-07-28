from collections import Counter
from datetime import datetime
from typing import List, Set


class AnaliseFrequenciaInternaApostasService:
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
    def calcular_frequencia_interna(apostas_list: List[List[int]]):
        apostas = AnaliseFrequenciaInternaApostasService._validar_apostas(apostas_list)
        freq = Counter()
        for aposta in apostas:
            freq.update(aposta)

        dezenas_altas = [d for d, c in freq.items() if c >= 6]
        dezenas_medias = [d for d, c in freq.items() if 3 <= c <= 5]
        dezenas_baixas = [d for d, c in freq.items() if 1 <= c <= 2]

        recomendacoes = []
        if len(dezenas_baixas) > len(dezenas_altas):
            recomendacoes.append('Cobertura baixa em muitas dezenas; aumente a presenca das mais fracas')
        if max(freq.values() or [0]) >= 8:
            recomendacoes.append('Ha dezenas muito repetidas; avalie distribuir melhor para evitar concentracao excessiva')
        if not recomendacoes:
            recomendacoes.append('Cobertura equilibrada; mantenha frequencias entre 3 e 6 por dezena')

        return {
            'status': 'sucesso',
            'timestamp': datetime.utcnow().isoformat(),
            'frequencia_dezenas': dict(sorted(freq.items())),
            'dezenas_altas': sorted(dezenas_altas),
            'dezenas_medias': sorted(dezenas_medias),
            'dezenas_baixas': sorted(dezenas_baixas),
            'diagnostico': 'Cobertura interna analisada',
            'recomendacoes': recomendacoes
        }

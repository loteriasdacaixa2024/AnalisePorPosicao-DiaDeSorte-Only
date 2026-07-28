from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseProbabilidadePosicaoService:

    @staticmethod
    def calcular_matriz():
        sorteios = Sorteio.query.all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)

        matriz = {}
        for numero in range(1, 32):
            matriz[numero] = {
                'numero': numero,
                'posicoes': {}
            }
            for posicao in range(1, 8):
                matriz[numero]['posicoes'][posicao] = {
                    'aparicoes': 0,
                    'percentual': 0,
                    'ultima_vez': None,
                    'atraso': 0
                }

        for idx, sorteio in enumerate(sorteios):
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    matriz[numero]['posicoes'][posicao]['aparicoes'] += 1
                    matriz[numero]['posicoes'][posicao]['ultima_vez'] = idx

        for numero in range(1, 32):
            for posicao in range(1, 8):
                aparicoes = matriz[numero]['posicoes'][posicao]['aparicoes']
                percentual = round((aparicoes / total_concursos) * 100, 2)
                matriz[numero]['posicoes'][posicao]['percentual'] = percentual

                ultima_vez = matriz[numero]['posicoes'][posicao]['ultima_vez']
                if ultima_vez is not None:
                    atraso = total_concursos - 1 - ultima_vez
                    matriz[numero]['posicoes'][posicao]['atraso'] = atraso
                else:
                    matriz[numero]['posicoes'][posicao]['atraso'] = total_concursos

        numeros_favoritos_por_posicao = {}
        for posicao in range(1, 8):
            numeros_sorted = sorted(
                range(1, 32),
                key=lambda n: matriz[n]['posicoes'][posicao]['percentual'],
                reverse=True
            )
            numeros_favoritos_por_posicao[posicao] = [
                {
                    'numero': num,
                    'percentual': matriz[num]['posicoes'][posicao]['percentual'],
                    'aparicoes': matriz[num]['posicoes'][posicao]['aparicoes']
                }
                for num in numeros_sorted[:5]
            ]

        posicoes_favoritas_por_numero = {}
        for numero in range(1, 32):
            posicoes_sorted = sorted(
                range(1, 8),
                key=lambda p: matriz[numero]['posicoes'][p]['percentual'],
                reverse=True
            )
            posicoes_favoritas_por_numero[numero] = [
                {
                    'posicao': pos,
                    'percentual': matriz[numero]['posicoes'][pos]['percentual'],
                    'aparicoes': matriz[numero]['posicoes'][pos]['aparicoes']
                }
                for pos in posicoes_sorted
            ]

        combinacoes_raras = []
        for numero in range(1, 32):
            for posicao in range(1, 8):
                if matriz[numero]['posicoes'][posicao]['aparicoes'] == 0:
                    combinacoes_raras.append({
                        'numero': numero,
                        'posicao': posicao
                    })

        return {
            'matriz': matriz,
            'total_concursos': total_concursos,
            'numeros_favoritos_por_posicao': numeros_favoritos_por_posicao,
            'posicoes_favoritas_por_numero': posicoes_favoritas_por_numero,
            'combinacoes_raras': combinacoes_raras,
            'total_combinacoes_raras': len(combinacoes_raras)
        }
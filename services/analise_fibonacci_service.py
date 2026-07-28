from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseFibonacciService:

    @staticmethod
    def eh_fibonacci(numero):
        numeros_fibonacci = [1, 2, 3, 5, 8, 13, 21]
        return numero in numeros_fibonacci

    @staticmethod
    def analisar_fibonacci():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        numeros_fibonacci_disponiveis = [1, 2, 3, 5, 8, 13, 21]

        frequencia_fibonacci = defaultdict(int)
        ultimo_aparecimento = defaultdict(int)

        sorteios_com_fibonacci = 0
        sorteios_sem_fibonacci = 0

        frequencia_quantidade = defaultdict(int)

        soma_quantidade = 0

        detalhes_sorteios = []

        for sorteio in sorteios:
            numeros = []
            fibonacci_encontrados = []

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

                    if AnaliseFibonacciService.eh_fibonacci(numero):
                        fibonacci_encontrados.append(numero)
                        frequencia_fibonacci[numero] += 1
                        ultimo_aparecimento[numero] = sorteio.concurso

            quantidade_fibonacci = len(fibonacci_encontrados)
            frequencia_quantidade[quantidade_fibonacci] += 1
            soma_quantidade += quantidade_fibonacci

            if quantidade_fibonacci > 0:
                sorteios_com_fibonacci += 1
            else:
                sorteios_sem_fibonacci += 1

            detalhes_sorteios.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': sorted(numeros),
                'fibonacci': sorted(fibonacci_encontrados),
                'quantidade': quantidade_fibonacci
            })

        percentual_com_fibonacci = round((sorteios_com_fibonacci / total_concursos * 100), 2)
        percentual_sem_fibonacci = round((sorteios_sem_fibonacci / total_concursos * 100), 2)
        media_quantidade = round(soma_quantidade / total_concursos, 2)

        lista_fibonacci = []
        for numero in numeros_fibonacci_disponiveis:
            freq = frequencia_fibonacci.get(numero, 0)
            percentual = round((freq / total_concursos * 100), 2)
            ultimo = ultimo_aparecimento.get(numero, 0)
            atraso = ultimo_concurso - ultimo

            lista_fibonacci.append({
                'numero': numero,
                'frequencia': freq,
                'porcentagem': percentual,
                'ultimo_concurso': ultimo,
                'atraso': atraso
            })

        lista_fibonacci.sort(key=lambda x: x['frequencia'], reverse=True)

        distribuicao_quantidade = []
        for qtd in sorted(frequencia_quantidade.keys()):
            freq = frequencia_quantidade[qtd]
            percentual = round((freq / total_concursos * 100), 2)

            distribuicao_quantidade.append({
                'quantidade': qtd,
                'frequencia': freq,
                'porcentagem': percentual
            })

        return {
            'total_concursos': total_concursos,
            'sorteios_com_fibonacci': sorteios_com_fibonacci,
            'percentual_com_fibonacci': percentual_com_fibonacci,
            'sorteios_sem_fibonacci': sorteios_sem_fibonacci,
            'percentual_sem_fibonacci': percentual_sem_fibonacci,
            'media_quantidade': media_quantidade,
            'lista_fibonacci': lista_fibonacci,
            'distribuicao_quantidade': distribuicao_quantidade,
            'detalhes_sorteios': detalhes_sorteios[:100]
        }
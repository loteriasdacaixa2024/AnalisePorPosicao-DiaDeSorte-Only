from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseCapicuaService:

    @staticmethod
    def eh_capicua(numero):
        str_numero = str(numero)
        return str_numero == str_numero[::-1]

    @staticmethod
    def analisar_capicua():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        numeros_capicua_disponiveis = [11, 22]

        frequencia_capicuas = defaultdict(int)
        ultimo_aparecimento = defaultdict(int)

        sorteios_com_capicua = 0
        sorteios_sem_capicua = 0

        frequencia_quantidade = defaultdict(int)

        detalhes_sorteios_com_capicua = []

        for sorteio in sorteios:
            numeros = []
            capicuas_encontrados = []

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

                    if AnaliseCapicuaService.eh_capicua(numero):
                        capicuas_encontrados.append(numero)
                        frequencia_capicuas[numero] += 1
                        ultimo_aparecimento[numero] = sorteio.concurso

            quantidade_capicuas = len(capicuas_encontrados)
            frequencia_quantidade[quantidade_capicuas] += 1

            if quantidade_capicuas > 0:
                sorteios_com_capicua += 1
                detalhes_sorteios_com_capicua.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': sorted(numeros),
                    'capicuas': sorted(capicuas_encontrados),
                    'quantidade': quantidade_capicuas
                })
            else:
                sorteios_sem_capicua += 1

        percentual_com_capicua = round((sorteios_com_capicua / total_concursos * 100), 2)
        percentual_sem_capicua = round((sorteios_sem_capicua / total_concursos * 100), 2)

        lista_capicuas = []
        for numero in numeros_capicua_disponiveis:
            freq = frequencia_capicuas.get(numero, 0)
            percentual = round((freq / total_concursos * 100), 2)
            ultimo = ultimo_aparecimento.get(numero, 0)
            atraso = ultimo_concurso - ultimo

            lista_capicuas.append({
                'numero': numero,
                'frequencia': freq,
                'porcentagem': percentual,
                'ultimo_concurso': ultimo,
                'atraso': atraso
            })

        lista_capicuas.sort(key=lambda x: x['frequencia'], reverse=True)

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
            'sorteios_com_capicua': sorteios_com_capicua,
            'percentual_com_capicua': percentual_com_capicua,
            'sorteios_sem_capicua': sorteios_sem_capicua,
            'percentual_sem_capicua': percentual_sem_capicua,
            'lista_capicuas': lista_capicuas,
            'distribuicao_quantidade': distribuicao_quantidade,
            'detalhes_sorteios': detalhes_sorteios_com_capicua[:100]
        }
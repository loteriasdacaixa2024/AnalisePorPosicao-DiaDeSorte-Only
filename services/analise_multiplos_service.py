from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseMultiplosService:

    @staticmethod
    def analisar_multiplos():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        frequencia_padroes = defaultdict(lambda: {
            'frequencia': 0,
            'ultimo_concurso': 0,
            'concursos': []
        })

        soma_mult3 = 0
        soma_mult5 = 0
        soma_mult7 = 0

        multiplos_3_encontrados = defaultdict(int)
        multiplos_5_encontrados = defaultdict(int)
        multiplos_7_encontrados = defaultdict(int)

        for sorteio in sorteios:
            numeros = []
            mult_3 = []
            mult_5 = []
            mult_7 = []

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

                    if numero % 3 == 0:
                        mult_3.append(numero)
                        multiplos_3_encontrados[numero] += 1

                    if numero % 5 == 0:
                        mult_5.append(numero)
                        multiplos_5_encontrados[numero] += 1

                    if numero % 7 == 0:
                        mult_7.append(numero)
                        multiplos_7_encontrados[numero] += 1

            qtd_mult3 = len(mult_3)
            qtd_mult5 = len(mult_5)
            qtd_mult7 = len(mult_7)

            soma_mult3 += qtd_mult3
            soma_mult5 += qtd_mult5
            soma_mult7 += qtd_mult7

            padrao = f"M3:{qtd_mult3} M5:{qtd_mult5} M7:{qtd_mult7}"

            frequencia_padroes[padrao]['frequencia'] += 1
            frequencia_padroes[padrao]['concursos'].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': sorted(numeros),
                'mult_3': sorted(mult_3),
                'mult_5': sorted(mult_5),
                'mult_7': sorted(mult_7)
            })

            if sorteio.concurso > frequencia_padroes[padrao]['ultimo_concurso']:
                frequencia_padroes[padrao]['ultimo_concurso'] = sorteio.concurso

        media_mult3 = round(soma_mult3 / total_concursos, 2)
        media_mult5 = round(soma_mult5 / total_concursos, 2)
        media_mult7 = round(soma_mult7 / total_concursos, 2)

        padroes_lista = []
        for padrao, dados in frequencia_padroes.items():
            percentual = round((dados['frequencia'] / total_concursos * 100), 2)
            atraso = ultimo_concurso - dados['ultimo_concurso']

            partes = padrao.split()
            qtd_mult3 = int(partes[0].split(':')[1])
            qtd_mult5 = int(partes[1].split(':')[1])
            qtd_mult7 = int(partes[2].split(':')[1])

            padroes_lista.append({
                'padrao': padrao,
                'mult_3': qtd_mult3,
                'mult_5': qtd_mult5,
                'mult_7': qtd_mult7,
                'frequencia': dados['frequencia'],
                'percentual': percentual,
                'ultimo_concurso': dados['ultimo_concurso'],
                'atraso': atraso,
                'concursos': dados['concursos']
            })

        padroes_lista.sort(key=lambda x: x['frequencia'], reverse=True)

        top_multiplos_3 = sorted(multiplos_3_encontrados.items(), key=lambda x: x[1], reverse=True)[:10]
        top_multiplos_5 = sorted(multiplos_5_encontrados.items(), key=lambda x: x[1], reverse=True)[:10]
        top_multiplos_7 = sorted(multiplos_7_encontrados.items(), key=lambda x: x[1], reverse=True)[:10]

        multiplos_3_lista = [{'numero': num, 'frequencia': freq} for num, freq in top_multiplos_3]
        multiplos_5_lista = [{'numero': num, 'frequencia': freq} for num, freq in top_multiplos_5]
        multiplos_7_lista = [{'numero': num, 'frequencia': freq} for num, freq in top_multiplos_7]

        return {
            'total_concursos': total_concursos,
            'media_mult3': media_mult3,
            'media_mult5': media_mult5,
            'media_mult7': media_mult7,
            'padroes': padroes_lista,
            'top_multiplos_3': multiplos_3_lista,
            'top_multiplos_5': multiplos_5_lista,
            'top_multiplos_7': multiplos_7_lista
        }
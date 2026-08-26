from collections import defaultdict, Counter
from models import Sorteio


class AnalisePadroesSequenciasService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'erro': 'Nenhum sorteio encontrado', 'total_concursos': 0}

        return {
            'total_concursos': len(sorteios),
            'numeros_consecutivos': AnalisePadroesSequenciasService.analisar_numeros_consecutivos(sorteios),
            'padroes_espacamento': AnalisePadroesSequenciasService.analisar_espacamento(sorteios),
            'sequencias_aritmeticas': AnalisePadroesSequenciasService.identificar_progressoes_aritmeticas(sorteios),
            'duplicatas_triplas': AnalisePadroesSequenciasService.analisar_duplicatas_triplas(sorteios),
            'padroes_inicio_fim': AnalisePadroesSequenciasService.analisar_padroes_extremos(sorteios)
        }

    @staticmethod
    def analisar_numeros_consecutivos(sorteios):
        distribuicao_consecutivos = Counter()
        jogos_com_consecutivos = 0

        for sorteio in sorteios:
            numeros = sorted(sorteio.get_posicoes_lista())
            total_consecutivos = 0

            for i in range(len(numeros) - 1):
                if numeros[i + 1] - numeros[i] == 1:
                    total_consecutivos += 1

            distribuicao_consecutivos[total_consecutivos] += 1
            if total_consecutivos > 0:
                jogos_com_consecutivos += 1

        total = len(sorteios)
        resultado_distribuicao = []

        for qtd, freq in sorted(distribuicao_consecutivos.items()):
            resultado_distribuicao.append({
                'quantidade_consecutivos': qtd,
                'frequencia': freq,
                'percentual': round((freq / total * 100), 2)
            })

        return {
            'distribuicao': resultado_distribuicao,
            'total_com_consecutivos': jogos_com_consecutivos,
            'percentual_com_consecutivos': round((jogos_com_consecutivos / total * 100), 2)
        }

    @staticmethod
    def analisar_espacamento(sorteios):
        espacamentos = []

        for sorteio in sorteios:
            numeros = sorted(sorteio.get_posicoes_lista())
            espacos = [numeros[i + 1] - numeros[i] for i in range(len(numeros) - 1)]

            espacamentos.append({
                'concurso': sorteio.concurso,
                'espacos': espacos,
                'media_espaco': round(sum(espacos) / len(espacos), 2),
                'min_espaco': min(espacos),
                'max_espaco': max(espacos)
            })

        # Padrões de espaçamento mais comuns
        padroes_espacamento = Counter()
        for e in espacamentos:
            padrao = tuple(sorted(e['espacos']))
            padroes_espacamento[padrao] += 1

        resultado_padroes = []
        for padrao, freq in padroes_espacamento.most_common(15):
            resultado_padroes.append({
                'padrao': str(padrao),
                'frequencia': freq
            })

        # Média geral
        todas_medias = [e['media_espaco'] for e in espacamentos]
        media_geral = round(sum(todas_medias) / len(todas_medias), 2)

        return {
            'media_geral_espacamento': media_geral,
            'padroes_mais_comuns': resultado_padroes,
            'ultimos_20_espacamentos': espacamentos[-20:]
        }

    @staticmethod
    def identificar_progressoes_aritmeticas(sorteios):
        jogos_com_pa = []

        for sorteio in sorteios:
            numeros = sorted(sorteio.get_posicoes_lista())

            # Verifica se há PA de tamanho >= 3
            pas_encontradas = []
            for i in range(len(numeros) - 2):
                for j in range(i + 1, len(numeros) - 1):
                    razao = numeros[j] - numeros[i]
                    sequencia = [numeros[i], numeros[j]]

                    proximo = numeros[j] + razao
                    while proximo in numeros and proximo <= 31:
                        sequencia.append(proximo)
                        proximo += razao

                    if len(sequencia) >= 3 and sequencia not in pas_encontradas:
                        pas_encontradas.append(sequencia)

            if pas_encontradas:
                jogos_com_pa.append({
                    'concurso': sorteio.concurso,
                    'progressoes': pas_encontradas,
                    'total_pas': len(pas_encontradas)
                })

        # Padrões de PA mais comuns
        todas_pas = []
        for jogo in jogos_com_pa:
            for pa in jogo['progressoes']:
                todas_pas.append(tuple(pa))

        contador_pas = Counter(todas_pas)

        return {
            'total_jogos_com_pa': len(jogos_com_pa),
            'percentual_jogos_com_pa': round((len(jogos_com_pa) / len(sorteios) * 100), 2),
            'pas_mais_comuns': [
                {
                    'progressao': list(pa),
                    'razao': pa[1] - pa[0],
                    'frequencia': freq
                }
                for pa, freq in contador_pas.most_common(20)
            ],
            'ultimos_10_jogos_com_pa': jogos_com_pa[-10:]
        }

    @staticmethod
    def analisar_duplicatas_triplas(sorteios):
        # Analisa terminações iguais (ex: 03, 13, 23)
        terminacoes = defaultdict(list)
        jogos_com_duplicatas = 0
        jogos_com_triplas = 0

        for sorteio in sorteios:
            numeros = sorteio.get_posicoes_lista()
            terminacoes_jogo = defaultdict(list)

            for num in numeros:
                final = num % 10
                terminacoes_jogo[final].append(num)

            tem_duplicata = False
            tem_tripla = False

            for final, nums in terminacoes_jogo.items():
                if len(nums) >= 2:
                    tem_duplicata = True
                    terminacoes[final].append({
                        'concurso': sorteio.concurso,
                        'numeros': nums
                    })
                if len(nums) >= 3:
                    tem_tripla = True

            if tem_duplicata:
                jogos_com_duplicatas += 1
            if tem_tripla:
                jogos_com_triplas += 1

        # Terminações mais frequentes em duplicatas/triplas
        freq_terminacoes = Counter()
        for final, ocorrencias in terminacoes.items():
            freq_terminacoes[final] = len(ocorrencias)

        total = len(sorteios)

        return {
            'total_jogos_com_duplicatas': jogos_com_duplicatas,
            'percentual_duplicatas': round((jogos_com_duplicatas / total * 100), 2),
            'total_jogos_com_triplas': jogos_com_triplas,
            'percentual_triplas': round((jogos_com_triplas / total * 100), 2),
            'terminacoes_mais_frequentes': [
                {
                    'final': final,
                    'frequencia': freq
                }
                for final, freq in freq_terminacoes.most_common()
            ]
        }

    @staticmethod
    def analisar_padroes_extremos(sorteios):
        # Analisa padrões nos números menor e maior de cada jogo
        padroes_inicio = Counter()
        padroes_fim = Counter()
        amplitudes = []

        for sorteio in sorteios:
            numeros = sorted(sorteio.get_posicoes_lista())
            menor = numeros[0]
            maior = numeros[-1]
            amplitude = maior - menor

            padroes_inicio[menor] += 1
            padroes_fim[maior] += 1
            amplitudes.append(amplitude)

        media_amplitude = round(sum(amplitudes) / len(amplitudes), 2)

        return {
            'numeros_inicio_mais_comuns': [
                {
                    'numero': num,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios) * 100), 2)
                }
                for num, freq in padroes_inicio.most_common(10)
            ],
            'numeros_fim_mais_comuns': [
                {
                    'numero': num,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios) * 100), 2)
                }
                for num, freq in padroes_fim.most_common(10)
            ],
            'amplitude_media': media_amplitude,
            'amplitude_minima': min(amplitudes),
            'amplitude_maxima': max(amplitudes)
        }

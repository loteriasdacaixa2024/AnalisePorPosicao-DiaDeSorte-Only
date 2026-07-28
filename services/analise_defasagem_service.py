from models.sorteio import Sorteio, db
from collections import defaultdict
import statistics

class AnaliseDefasagemService:

    @staticmethod
    def analisar_defasagem():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        aparicoes_por_numero = defaultdict(list)

        for idx, sorteio in enumerate(sorteios):
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    aparicoes_por_numero[numero].append(idx)

        analise_defasagem = []

        for numero in range(1, 32):
            aparicoes = aparicoes_por_numero.get(numero, [])

            if len(aparicoes) < 2:
                continue

            intervalos = [aparicoes[i] - aparicoes[i-1] for i in range(1, len(aparicoes))]

            intervalo_medio = statistics.mean(intervalos)
            intervalo_mediano = statistics.median(intervalos)
            desvio_padrao = statistics.stdev(intervalos) if len(intervalos) > 1 else 0

            defasagens = [aparicoes[i] - i * intervalo_medio for i in range(len(aparicoes))]

            defasagem_media = statistics.mean(defasagens)
            defasagem_maxima = max(defasagens)
            defasagem_minima = min(defasagens)
            defasagem_atual = defasagens[-1] if defasagens else 0

            atraso_atual = total_concursos - 1 - aparicoes[-1]
            aparicao_esperada_proxima = aparicoes[-1] + intervalo_medio
            defasagem_projetada = (total_concursos - 1) - aparicao_esperada_proxima

            if defasagem_atual > intervalo_medio * 0.5:
                status_defasagem = "Muito Atrasado"
                classe_defasagem = "danger"
            elif defasagem_atual > intervalo_medio * 0.2:
                status_defasagem = "Atrasado"
                classe_defasagem = "warning"
            elif defasagem_atual < -intervalo_medio * 0.5:
                status_defasagem = "Muito Adiantado"
                classe_defasagem = "success"
            elif defasagem_atual < -intervalo_medio * 0.2:
                status_defasagem = "Adiantado"
                classe_defasagem = "info"
            else:
                status_defasagem = "No Ritmo"
                classe_defasagem = "secondary"

            tendencia_defasagem = "Estável"
            if len(defasagens) >= 3:
                primeiros = defasagens[:len(defasagens)//2]
                ultimos = defasagens[len(defasagens)//2:]
                if statistics.mean(ultimos) > statistics.mean(primeiros) + intervalo_medio * 0.1:
                    tendencia_defasagem = "Aumentando"
                elif statistics.mean(ultimos) < statistics.mean(primeiros) - intervalo_medio * 0.1:
                    tendencia_defasagem = "Diminuindo"

            regularidade = (desvio_padrao / intervalo_medio * 100) if intervalo_medio > 0 else 0

            analise_defasagem.append({
                'numero': numero,
                'total_aparicoes': len(aparicoes),
                'intervalo_medio': round(intervalo_medio, 1),
                'intervalo_mediano': intervalo_mediano,
                'desvio_padrao': round(desvio_padrao, 1),
                'regularidade': round(regularidade, 1),
                'defasagem_media': round(defasagem_media, 1),
                'defasagem_atual': round(defasagem_atual, 1),
                'defasagem_maxima': round(defasagem_maxima, 1),
                'defasagem_minima': round(defasagem_minima, 1),
                'defasagem_projetada': round(defasagem_projetada, 1),
                'status_defasagem': status_defasagem,
                'classe_defasagem': classe_defasagem,
                'tendencia_defasagem': tendencia_defasagem,
                'atraso_atual': atraso_atual,
                'ultima_aparicao': aparicoes[-1]
            })

        analise_defasagem.sort(key=lambda x: abs(x['defasagem_atual']), reverse=True)

        muito_atrasados = [n for n in analise_defasagem if n['status_defasagem'] == 'Muito Atrasado']
        atrasados = [n for n in analise_defasagem if n['status_defasagem'] == 'Atrasado']
        no_ritmo = [n for n in analise_defasagem if n['status_defasagem'] == 'No Ritmo']
        adiantados = [n for n in analise_defasagem if n['status_defasagem'] == 'Adiantado']
        muito_adiantados = [n for n in analise_defasagem if n['status_defasagem'] == 'Muito Adiantado']

        maior_defasagem_positiva = max(analise_defasagem, key=lambda x: x['defasagem_atual']) if analise_defasagem else None
        maior_defasagem_negativa = min(analise_defasagem, key=lambda x: x['defasagem_atual']) if analise_defasagem else None

        return {
            'analise_defasagem': analise_defasagem,
            'total_concursos': total_concursos,
            'muito_atrasados': len(muito_atrasados),
            'atrasados': len(atrasados),
            'no_ritmo': len(no_ritmo),
            'adiantados': len(adiantados),
            'muito_adiantados': len(muito_adiantados),
            'top_atrasados': muito_atrasados[:10] if muito_atrasados else atrasados[:10],
            'top_adiantados': muito_adiantados[:10] if muito_adiantados else adiantados[:10],
            'maior_defasagem_positiva': maior_defasagem_positiva,
            'maior_defasagem_negativa': maior_defasagem_negativa
        }

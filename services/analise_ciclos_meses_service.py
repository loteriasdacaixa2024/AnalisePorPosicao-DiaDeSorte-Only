from models.sorteio import Sorteio, db
from sqlalchemy import func
from collections import defaultdict
import statistics

class AnaliseCiclosMesesService:

    @staticmethod
    def analisar_ciclos():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)

        posicoes_por_mes = defaultdict(list)

        for idx, sorteio in enumerate(sorteios):
            mes = sorteio.mes_sorte
            posicoes_por_mes[mes].append(idx)

        analise_ciclos = []

        for mes in range(1, 13):
            posicoes = posicoes_por_mes[mes]

            if len(posicoes) < 2:
                continue

            intervalos = []
            for i in range(1, len(posicoes)):
                intervalo = posicoes[i] - posicoes[i-1]
                intervalos.append(intervalo)

            intervalo_medio = statistics.mean(intervalos)
            intervalo_mediano = statistics.median(intervalos)
            intervalo_min = min(intervalos)
            intervalo_max = max(intervalos)
            desvio_padrao = statistics.stdev(intervalos) if len(intervalos) > 1 else 0

            coeficiente_variacao = (desvio_padrao / intervalo_medio * 100) if intervalo_medio > 0 else 0

            if coeficiente_variacao < 30:
                regularidade = "Muito Regular"
                regularidade_classe = "success"
            elif coeficiente_variacao < 50:
                regularidade = "Regular"
                regularidade_classe = "info"
            elif coeficiente_variacao < 70:
                regularidade = "Irregular"
                regularidade_classe = "warning"
            else:
                regularidade = "Muito Irregular"
                regularidade_classe = "danger"

            meio = len(intervalos) // 2
            if meio > 0:
                primeira_metade = statistics.mean(intervalos[:meio])
                segunda_metade = statistics.mean(intervalos[meio:])
                diferenca_percentual = ((segunda_metade - primeira_metade) / primeira_metade * 100) if primeira_metade > 0 else 0

                if diferenca_percentual < -15:
                    tendencia = "Frequência Aumentando"
                    tendencia_icone = "📈"
                    tendencia_classe = "success"
                elif diferenca_percentual > 15:
                    tendencia = "Frequência Diminuindo"
                    tendencia_icone = "📉"
                    tendencia_classe = "danger"
                else:
                    tendencia = "Estável"
                    tendencia_icone = "➡️"
                    tendencia_classe = "secondary"
            else:
                tendencia = "Dados Insuficientes"
                tendencia_icone = "❓"
                tendencia_classe = "secondary"

            ultimo_concurso_idx = posicoes[-1]
            atraso_atual = total_concursos - 1 - ultimo_concurso_idx

            if atraso_atual > intervalo_medio * 1.5:
                fase_atual = "Seca"
                fase_classe = "warning"
            elif atraso_atual < intervalo_medio * 0.5:
                fase_atual = "Abundância"
                fase_classe = "success"
            else:
                fase_atual = "Normal"
                fase_classe = "secondary"

            if intervalo_medio > 0:
                fator_atraso = atraso_atual / intervalo_medio
                probabilidade_proxima = min(fator_atraso * 8.33, 95)
            else:
                probabilidade_proxima = 8.33

            analise_ciclos.append({
                'mes': mes,
                'total_aparicoes': len(posicoes),
                'intervalo_medio': round(intervalo_medio, 1),
                'intervalo_mediano': intervalo_mediano,
                'intervalo_min': intervalo_min,
                'intervalo_max': intervalo_max,
                'desvio_padrao': round(desvio_padrao, 1),
                'coeficiente_variacao': round(coeficiente_variacao, 1),
                'regularidade': regularidade,
                'regularidade_classe': regularidade_classe,
                'tendencia': tendencia,
                'tendencia_icone': tendencia_icone,
                'tendencia_classe': tendencia_classe,
                'atraso_atual': atraso_atual,
                'fase_atual': fase_atual,
                'fase_classe': fase_classe,
                'probabilidade_proxima': round(probabilidade_proxima, 1)
            })

        analise_ciclos.sort(key=lambda x: x['probabilidade_proxima'], reverse=True)

        matriz_transicoes = AnaliseCiclosMesesService.analisar_transicoes(sorteios)

        padroes_fortes = []
        for mes_origem, transicoes in matriz_transicoes.items():
            if transicoes:
                mes_destino_max = max(transicoes.items(), key=lambda x: x[1])
                if mes_destino_max[1] >= 10:
                    padroes_fortes.append({
                        'mes_origem': mes_origem,
                        'mes_destino': mes_destino_max[0],
                        'frequencia': mes_destino_max[1],
                        'percentual': round(mes_destino_max[1] / sum(transicoes.values()) * 100, 1)
                    })

        padroes_fortes.sort(key=lambda x: x['percentual'], reverse=True)

        return {
            'analise_ciclos': analise_ciclos,
            'matriz_transicoes': matriz_transicoes,
            'padroes_fortes': padroes_fortes[:10],
            'total_concursos': total_concursos
        }

    @staticmethod
    def analisar_transicoes(sorteios):
        matriz = defaultdict(lambda: defaultdict(int))

        for i in range(len(sorteios) - 1):
            mes_atual = sorteios[i].mes_sorte
            mes_proximo = sorteios[i + 1].mes_sorte
            matriz[mes_atual][mes_proximo] += 1

        return dict(matriz)
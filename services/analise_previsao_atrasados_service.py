from models.sorteio import Sorteio, db
import math

class AnalisePrevisaoAtrasadosService:
    
    @staticmethod
    def obter_previsao_atrasados():
        """
        Calcula previsão de aparição de números atrasados por posição
        Probabilidade de um número em uma posição específica = 1/217
        """
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        total_concursos = len(concursos)
        ultimo_concurso = concursos[0].concurso if concursos else 0
        
        # Estrutura: {posicao: {numero: ultimo_concurso}}
        ultimos_por_posicao = {}
        for pos in range(1, 8):
            ultimos_por_posicao[pos] = {numero: None for numero in range(1, 32)}
        
        # Analisar histórico
        for concurso in concursos:
            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso, campo, None)
                if numero and 1 <= numero <= 31:
                    if ultimos_por_posicao[pos][numero] is None:
                        ultimos_por_posicao[pos][numero] = concurso.concurso
        
        # Probabilidade de aparecer em uma posição específica
        prob_por_concurso = 1 / 217  # 1 número específico em 1 posição específica
        
        # Calcular previsões para cada posição
        previsoes_por_posicao = {}
        
        for pos in range(1, 8):
            numeros_info = []
            
            for numero in range(1, 32):
                ultimo = ultimos_por_posicao[pos][numero]
                atraso = ultimo_concurso - ultimo if ultimo else 999
                
                # Probabilidade acumulada em N concursos: 1 - (1 - 1/217)^N
                prob_10 = (1 - math.pow(1 - prob_por_concurso, 10)) * 100
                prob_20 = (1 - math.pow(1 - prob_por_concurso, 20)) * 100
                prob_50 = (1 - math.pow(1 - prob_por_concurso, 50)) * 100
                prob_100 = (1 - math.pow(1 - prob_por_concurso, 100)) * 100
                prob_217 = (1 - math.pow(1 - prob_por_concurso, 217)) * 100
                
                # Índice de urgência: quanto maior o atraso, maior a urgência
                # Números com atraso > 217 (1 ciclo) têm urgência crítica
                if atraso >= 217:
                    urgencia = 'Crítica'
                elif atraso >= 150:
                    urgencia = 'Alta'
                elif atraso >= 100:
                    urgencia = 'Média'
                else:
                    urgencia = 'Baixa'
                
                numeros_info.append({
                    'numero': numero,
                    'ultimo_concurso': ultimo if ultimo else 'Nunca',
                    'atraso': atraso if atraso < 999 else 999,
                    'urgencia': urgencia,
                    'prob_10': f"{prob_10:.2f}",
                    'prob_20': f"{prob_20:.2f}",
                    'prob_50': f"{prob_50:.2f}",
                    'prob_100': f"{prob_100:.2f}",
                    'prob_217': f"{prob_217:.2f}"
                })
            
            # Ordenar por atraso (maior primeiro)
            numeros_info_sorted = sorted(numeros_info, key=lambda x: x['atraso'], reverse=True)
            previsoes_por_posicao[pos] = numeros_info_sorted
        
        # Criar ranking geral de números mais atrasados (todas posições)
        ranking_geral = []
        for pos in range(1, 8):
            for num_info in previsoes_por_posicao[pos][:5]:  # Top 5 por posição
                if num_info['atraso'] < 999:
                    ranking_geral.append({
                        'posicao': pos,
                        'numero': num_info['numero'],
                        'atraso': num_info['atraso'],
                        'urgencia': num_info['urgencia'],
                        'prob_50': num_info['prob_50']
                    })
        
        # Ordenar ranking geral por atraso
        ranking_geral_sorted = sorted(ranking_geral, key=lambda x: x['atraso'], reverse=True)[:20]
        
        return {
            'total_concursos': total_concursos,
            'ultimo_concurso': ultimo_concurso,
            'probabilidade_base': f"{(prob_por_concurso * 100):.4f}",
            'ciclo_esperado': 217,
            'previsoes_por_posicao': previsoes_por_posicao,
            'ranking_geral': ranking_geral_sorted
        }
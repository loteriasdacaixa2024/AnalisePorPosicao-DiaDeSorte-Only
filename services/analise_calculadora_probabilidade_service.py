from models.sorteio import Sorteio, db
import math

class AnaliseCalculadoraProbabilidadeService:
    
    @staticmethod
    def calcular_probabilidade(numero, posicao, num_concursos):
        """
        Calcula probabilidade acumulada de um número em uma posição específica
        aparecer em N concursos
        """
        # Validações
        if not (1 <= numero <= 31):
            return {'error': 'Número deve estar entre 1 e 31'}
        
        if not (1 <= posicao <= 7):
            return {'error': 'Posição deve estar entre 1 e 7'}
        
        if not (1 <= num_concursos <= 1000):
            return {'error': 'Número de concursos deve estar entre 1 e 1000'}
        
        # Probabilidade base: 1 número específico em 1 posição específica
        prob_por_concurso = 1 / 217
        
        # Probabilidade acumulada: P = 1 - (1 - p)^N
        prob_acumulada = (1 - math.pow(1 - prob_por_concurso, num_concursos)) * 100
        
        # Número esperado de concursos para 50% e 90%
        concursos_50 = math.log(0.5) / math.log(1 - prob_por_concurso)
        concursos_90 = math.log(0.1) / math.log(1 - prob_por_concurso)
        
        # Buscar histórico do número na posição
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        ultimo_concurso = concursos[0].concurso if concursos else 0
        
        ultimo_apareceu = None
        for concurso in concursos:
            campo = f'posicao_{posicao}'
            num = getattr(concurso, campo, None)
            if num == numero:
                ultimo_apareceu = concurso.concurso
                break
        
        atraso_atual = ultimo_concurso - ultimo_apareceu if ultimo_apareceu else 999
        
        # Gerar pontos para gráfico (probabilidade crescente)
        pontos_grafico = []
        intervalos = [1, 5, 10, 20, 50, 100, 150, 200, 217, 300, 500]
        for n in intervalos:
            if n <= num_concursos:
                p = (1 - math.pow(1 - prob_por_concurso, n)) * 100
                pontos_grafico.append({'concursos': n, 'probabilidade': f"{p:.2f}"})
        
        # Classificação
        if prob_acumulada >= 90:
            classificacao = 'Muito Alta'
            cor = 'success'
        elif prob_acumulada >= 70:
            classificacao = 'Alta'
            cor = 'info'
        elif prob_acumulada >= 50:
            classificacao = 'Moderada'
            cor = 'warning'
        elif prob_acumulada >= 30:
            classificacao = 'Baixa'
            cor = 'secondary'
        else:
            classificacao = 'Muito Baixa'
            cor = 'danger'
        
        return {
            'numero': numero,
            'posicao': posicao,
            'num_concursos': num_concursos,
            'probabilidade_por_concurso': f"{(prob_por_concurso * 100):.4f}",
            'probabilidade_acumulada': f"{prob_acumulada:.2f}",
            'classificacao': classificacao,
            'cor': cor,
            'ultimo_apareceu': ultimo_apareceu if ultimo_apareceu else 'Nunca',
            'atraso_atual': atraso_atual if atraso_atual < 999 else 999,
            'concursos_para_50': f"{concursos_50:.0f}",
            'concursos_para_90': f"{concursos_90:.0f}",
            'pontos_grafico': pontos_grafico
        }
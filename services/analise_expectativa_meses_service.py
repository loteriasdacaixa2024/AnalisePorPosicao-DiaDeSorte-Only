from models.sorteio import Sorteio, db
import math

class AnaliseExpectativaMesesService:
    MESES = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    @staticmethod
    def obter_expectativa_meses():
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        total_concursos = len(concursos)
        
        # Contadores
        frequencia_meses = {mes: 0 for mes in range(1, 13)}
        ultimo_sorteio = {mes: None for mes in range(1, 13)}
        
        # Analisar cada concurso
        for concurso in concursos:
            mes = concurso.mes_sorte
            if mes and 1 <= mes <= 12:
                frequencia_meses[mes] += 1
                if ultimo_sorteio[mes] is None:
                    ultimo_sorteio[mes] = concurso.concurso
        
        # Calcular estatísticas para cada mês
        ultimo_concurso = concursos[0].concurso if concursos else 0
        
        meses_info = []
        for mes in range(1, 13):
            freq = frequencia_meses[mes]
            perc = (freq / total_concursos * 100) if total_concursos > 0 else 0
            atraso = ultimo_concurso - ultimo_sorteio[mes] if ultimo_sorteio[mes] else 999
            
            # Probabilidade de 1 mês específico = 1/12
            prob_por_concurso = 1 / 12
            
            # Número esperado de concursos = 1 / prob = 12
            concursos_esperados = 12
            
            # Probabilidade acumulada em N concursos: 1 - (11/12)^N
            prob_5 = (1 - math.pow(11/12, 5)) * 100
            prob_10 = (1 - math.pow(11/12, 10)) * 100
            prob_20 = (1 - math.pow(11/12, 20)) * 100
            prob_50 = (1 - math.pow(11/12, 50)) * 100
            prob_100 = (1 - math.pow(11/12, 100)) * 100
            
            meses_info.append({
                'mes': mes,
                'nome': AnaliseExpectativaMesesService.MESES[mes],
                'frequencia': freq,
                'percentual': f"{perc:.2f}",
                'ultimo_sorteio': ultimo_sorteio[mes] if ultimo_sorteio[mes] else 'Nunca',
                'atraso': atraso if atraso < 999 else 999,
                'concursos_esperados': concursos_esperados,
                'prob_5': f"{prob_5:.2f}",
                'prob_10': f"{prob_10:.2f}",
                'prob_20': f"{prob_20:.2f}",
                'prob_50': f"{prob_50:.2f}",
                'prob_100': f"{prob_100:.2f}"
            })
        
        # Ordenar por frequência (maior primeiro)
        meses_info_sorted = sorted(meses_info, key=lambda x: x['frequencia'], reverse=True)
        
        return {
            'total_concursos': total_concursos,
            'meses': meses_info,
            'meses_ranking': meses_info_sorted,
            'probabilidade_base': f"{(1/12 * 100):.2f}"
        }
    
    @staticmethod
    def calcular_probabilidade_customizada(meses_selecionados, num_concursos):
        """
        Calcula probabilidade customizada para meses escolhidos pelo usuário
        meses_selecionados: lista de números de mês (ex: [2, 3] para Fev e Mar)
        num_concursos: número de concursos futuros
        """
        num_meses = len(meses_selecionados)
        
        # Probabilidade de um dos meses selecionados = num_meses / 12
        prob_por_concurso = num_meses / 12
        
        # Número esperado de concursos = 1 / prob
        concursos_esperados = 1 / prob_por_concurso if prob_por_concurso > 0 else 0
        
        # Probabilidade de NÃO sair em 1 concurso
        prob_nao = 1 - prob_por_concurso
        
        # Probabilidade acumulada: 1 - (prob_nao)^N
        prob_acumulada = (1 - math.pow(prob_nao, num_concursos)) * 100
        
        return {
            'meses_selecionados': [AnaliseExpectativaMesesService.MESES[m] for m in meses_selecionados],
            'num_meses': num_meses,
            'probabilidade_por_concurso': f"{(prob_por_concurso * 100):.2f}",
            'concursos_esperados': f"{concursos_esperados:.2f}",
            'num_concursos': num_concursos,
            'probabilidade_acumulada': f"{prob_acumulada:.2f}"
        }
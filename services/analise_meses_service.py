from models.sorteio import Sorteio, db

class AnaliseMesesService:
    
    @staticmethod
    def obter_nome_mes(numero):
        nomes = [
            '', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
        ]
        if 1 <= numero <= 12:
            return nomes[numero]
        return "Des"
    
    @staticmethod
    def obter_estatisticas_meses():
        total_sorteios = Sorteio.query.count()
        ultimo_concurso_geral = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
        proximo_concurso = ultimo_concurso_geral.concurso + 1
        
        meses_freq = db.session.query(
            Sorteio.mes_sorte,
            db.func.count(Sorteio.mes_sorte).label('frequencia')
        ).group_by(Sorteio.mes_sorte).all()
        
        meses_dict = {mes: freq for mes, freq in meses_freq}
        
        nomes_meses = [
            '', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
        ]
        
        resultado = []
        
        for mes in range(1, 13):
            frequencia = meses_dict.get(mes, 0)
            percentual = (frequencia / total_sorteios * 100) if total_sorteios > 0 else 0
            
            ultimo_sorteio = Sorteio.query.filter_by(mes_sorte=mes).order_by(Sorteio.concurso.desc()).first()
            
            if ultimo_sorteio:
                atraso = ultimo_concurso_geral.concurso - ultimo_sorteio.concurso
            else:
                atraso = total_sorteios
            
            resultado.append({
                'mes': mes,
                'numero': mes,
                'nome': nomes_meses[mes],
                'frequencia': frequencia,
                'percentual': round(percentual, 2),
                'atraso': atraso,
                'ultimo_concurso': ultimo_sorteio.concurso if ultimo_sorteio else None,
                'plano_apostas': {
                    'proximo_concurso': proximo_concurso,
                    'ate_5': proximo_concurso + 4,
                    'ate_10': proximo_concurso + 9,
                    'ate_20': proximo_concurso + 19
                }
            })
        
        resultado.sort(key=lambda x: x['atraso'], reverse=True)
        
        return {
            'total_sorteios': total_sorteios,
            'ultimo_concurso': ultimo_concurso_geral.concurso,
            'proximo_concurso': proximo_concurso,
            'meses': resultado
        }
    
    @staticmethod
    def calcular_probabilidade(num_concursos, qtd_meses=1):
        prob_errar_um = (12 - qtd_meses) / 12
        prob_errar_todos = prob_errar_um ** num_concursos
        prob_acertar = 1 - prob_errar_todos
        return round(prob_acertar * 100, 2)
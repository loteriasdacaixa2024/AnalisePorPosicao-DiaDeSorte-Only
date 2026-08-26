from models.sorteio import Sorteio, db

class AnaliseAtrasadosService:
    
    @staticmethod
    def obter_frequencia_por_posicao(posicao, modo='crescente'):
        if posicao < 1 or posicao > 7:
            return {'erro': 'Posição deve estar entre 1 e 7'}

        # Escolhe a coluna baseada no modo
        if modo == 'sorteio':
            campo = f'sorteio_{posicao}'
        else:
            campo = f'posicao_{posicao}'
        
        query = db.session.query(
            db.func.coalesce(getattr(Sorteio, campo), getattr(Sorteio, f'posicao_{posicao}')).label('numero'),
            db.func.count(db.func.coalesce(getattr(Sorteio, campo), getattr(Sorteio, f'posicao_{posicao}'))).label('frequencia')
        ).group_by(db.func.coalesce(getattr(Sorteio, campo), getattr(Sorteio, f'posicao_{posicao}'))).order_by(db.func.count(db.func.coalesce(getattr(Sorteio, campo), getattr(Sorteio, f'posicao_{posicao}'))).desc()).all()

        total_sorteios = Sorteio.query.count()
        ultimo_concurso_geral = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
        proximo_concurso = ultimo_concurso_geral.concurso + 1

        resultado = []
        numeros_encontrados = set()

        for numero, freq in query:
            percentual = (freq / total_sorteios * 100) if total_sorteios > 0 else 0

            ultimo_sorteio = Sorteio.query.filter(
                db.func.coalesce(getattr(Sorteio, campo), getattr(Sorteio, f'posicao_{posicao}')) == numero
            ).order_by(Sorteio.concurso.desc()).first()

            atraso = ultimo_concurso_geral.concurso - ultimo_sorteio.concurso if ultimo_sorteio else total_sorteios

            resultado.append({
                'numero': numero,
                'frequencia': freq,
                'percentual': round(percentual, 2),
                'atraso': atraso,
                'ultimo_concurso': ultimo_sorteio.concurso if ultimo_sorteio else None,
                'plano_apostas': {
                    'proximo_concurso': proximo_concurso,
                    'ate_50': proximo_concurso + 49,
                    'ate_100': proximo_concurso + 99,
                    'ate_217': proximo_concurso + 216
                }
            })

            numeros_encontrados.add(numero)

        for num in range(1, 32):
            if num not in numeros_encontrados:
                resultado.append({
                    'numero': num,
                    'frequencia': 0,
                    'percentual': 0.0,
                    'atraso': total_sorteios,
                    'ultimo_concurso': None,
                    'plano_apostas': {
                        'proximo_concurso': proximo_concurso,
                        'ate_50': proximo_concurso + 49,
                        'ate_100': proximo_concurso + 99,
                        'ate_217': proximo_concurso + 216
                    }
                })

        resultado.sort(key=lambda x: x['atraso'], reverse=True)

        return {
            'posicao': posicao,
            'total_sorteios': total_sorteios,
            'ultimo_concurso': ultimo_concurso_geral.concurso,
            'proximo_concurso': proximo_concurso,
            'numeros': resultado
        }
    @staticmethod
    def calcular_probabilidade(num_concursos):
        prob_errar_um = 30 / 31
        prob_errar_todos = prob_errar_um ** num_concursos
        prob_acertar = 1 - prob_errar_todos
        return round(prob_acertar * 100, 2)

    @staticmethod
    def obter_rank_vertical(modo='sorteio', qtd=30):
        all_per_pos = {}
        for pos in range(1, 8):
            res = AnaliseAtrasadosService.obter_frequencia_por_posicao(pos, modo=modo)
            if 'erro' in res:
                return []
            all_per_pos[pos] = [item['numero'] for item in res['numeros']]
            
        valid_games = []
        for i in range(qtd):
            bet = []
            for p in range(1, 8):
                ranking_list = all_per_pos[p]
                offset = 0
                target_idx = i
                while offset < len(ranking_list):
                    candidato = ranking_list[(target_idx + offset) % len(ranking_list)]
                    if candidato not in bet:
                        bet.append(candidato)
                        break
                    offset += 1
            if len(bet) == 7:
                valid_games.append(sorted(bet))
        return valid_games
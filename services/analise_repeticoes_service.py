from models.sorteio import Sorteio, db

class AnaliseRepeticoesService:
    @staticmethod
    def obter_numeros_que_repetem():
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        
        if len(concursos) < 2:
            return {
                'numeros': [],
                'total_concursos': 0,
                'total_repeticoes': 0,
                'percentual_com_repeticao': '0.00'
            }
        
        total_concursos = len(concursos)
        
        repeticoes_por_numero = {}
        for numero in range(1, 32):
            repeticoes_por_numero[numero] = {
                'numero': numero,
                'repeticoes': 0,
                'ultima_repeticao': None,
                'atraso': 0
            }
        
        concursos_com_repeticao = 0
        total_repeticoes = 0
        
        for i in range(len(concursos) - 1):
            concurso_atual = concursos[i]
            concurso_anterior = concursos[i + 1]
            
            numeros_atual = set()
            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso_atual, campo, None)
                if numero:
                    numeros_atual.add(numero)
            
            numeros_anterior = set()
            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso_anterior, campo, None)
                if numero:
                    numeros_anterior.add(numero)
            
            numeros_repetidos = numeros_atual.intersection(numeros_anterior)
            
            if numeros_repetidos:
                concursos_com_repeticao += 1
                total_repeticoes += len(numeros_repetidos)
                
                for numero in numeros_repetidos:
                    repeticoes_por_numero[numero]['repeticoes'] += 1
                    if repeticoes_por_numero[numero]['ultima_repeticao'] is None:
                        repeticoes_por_numero[numero]['ultima_repeticao'] = concurso_atual.concurso
        
        lista_numeros = list(repeticoes_por_numero.values())
        lista_numeros.sort(key=lambda x: x['repeticoes'], reverse=True)
        
        ultimo_concurso = concursos[0].concurso if concursos else 0
        
        for numero in lista_numeros:
            if numero['ultima_repeticao']:
                numero['atraso'] = ultimo_concurso - numero['ultima_repeticao']
            else:
                numero['atraso'] = 999
        
        percentual_com_repeticao = (concursos_com_repeticao / (total_concursos - 1) * 100) if total_concursos > 1 else 0
        
        return {
            'numeros': lista_numeros,
            'total_concursos': total_concursos - 1,
            'total_repeticoes': total_repeticoes,
            'concursos_com_repeticao': concursos_com_repeticao,
            'percentual_com_repeticao': f"{percentual_com_repeticao:.2f}",
            'media_repeticoes_por_concurso': f"{(total_repeticoes / (total_concursos - 1)):.2f}" if total_concursos > 1 else '0.00'
        }
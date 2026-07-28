from models.sorteio import Sorteio

class AnaliseCombinacoesService:
    
    @staticmethod
    def numeros_que_saem_juntos(top=20):
        sorteios = Sorteio.query.all()
        total_sorteios = len(sorteios)
        
        combinacoes = {}
        
        for sorteio in sorteios:
            numeros = sorteio.get_posicoes_lista()
            
            for i in range(len(numeros)):
                for j in range(i + 1, len(numeros)):
                    dupla = tuple(sorted([numeros[i], numeros[j]]))
                    
                    if dupla not in combinacoes:
                        combinacoes[dupla] = {
                            'frequencia': 0,
                            'concursos': []
                        }
                    
                    combinacoes[dupla]['frequencia'] += 1
                    combinacoes[dupla]['concursos'].append(sorteio.concurso)
        
        resultado = []
        for dupla, dados in combinacoes.items():
            percentual = (dados['frequencia'] / total_sorteios * 100) if total_sorteios > 0 else 0
            
            resultado.append({
                'numero1': dupla[0],
                'numero2': dupla[1],
                'frequencia': dados['frequencia'],
                'percentual': round(percentual, 2),
                'ultimo_concurso': max(dados['concursos']) if dados['concursos'] else None
            })
        
        resultado.sort(key=lambda x: x['frequencia'], reverse=True)
        
        return {
            'total_sorteios': total_sorteios,
            'total_combinacoes': len(resultado),
            'top_combinacoes': resultado[:top]
        }
    
    @staticmethod
    def buscar_combinacoes_com_numero(numero, top=10):
        sorteios = Sorteio.query.all()
        total_sorteios = len(sorteios)
        
        combinacoes = {}
        
        for sorteio in sorteios:
            numeros = sorteio.get_posicoes_lista()
            
            if numero in numeros:
                for num in numeros:
                    if num != numero:
                        if num not in combinacoes:
                            combinacoes[num] = {
                                'frequencia': 0,
                                'concursos': []
                            }
                        
                        combinacoes[num]['frequencia'] += 1
                        combinacoes[num]['concursos'].append(sorteio.concurso)
        
        resultado = []
        for num, dados in combinacoes.items():
            percentual = (dados['frequencia'] / total_sorteios * 100) if total_sorteios > 0 else 0
            
            resultado.append({
                'numero_par': num,
                'frequencia': dados['frequencia'],
                'percentual': round(percentual, 2),
                'ultimo_concurso': max(dados['concursos']) if dados['concursos'] else None
            })
        
        resultado.sort(key=lambda x: x['frequencia'], reverse=True)
        
        return {
            'numero_base': numero,
            'total_sorteios': total_sorteios,
            'combinacoes': resultado[:top]
        }
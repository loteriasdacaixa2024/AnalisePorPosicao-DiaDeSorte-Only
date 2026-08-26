from models.sorteio import Sorteio, db
from collections import defaultdict
import statistics

class AnaliseNumerosDevidosService:

    @staticmethod
    def analisar_devidos():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        
        aparicoes_reais = defaultdict(int)
        ultima_aparicao = {}
        
        for idx, sorteio in enumerate(sorteios):
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    aparicoes_reais[numero] += 1
                    ultima_aparicao[numero] = idx
        
        total_numeros_sorteados = total_concursos * 7
        probabilidade_teorica = 7 / 31
        
        analise_devidos = []
        
        for numero in range(1, 32):
            aparicoes = aparicoes_reais.get(numero, 0)
            aparicoes_esperadas = total_concursos * probabilidade_teorica
            
            diferenca = aparicoes - aparicoes_esperadas
            percentual_diferenca = (diferenca / aparicoes_esperadas * 100) if aparicoes_esperadas > 0 else 0
            
            indice_divida = -diferenca
            
            ultima_vez = ultima_aparicao.get(numero)
            if ultima_vez is not None:
                atraso_atual = total_concursos - 1 - ultima_vez
            else:
                atraso_atual = total_concursos
            
            frequencia_real = (aparicoes / total_concursos * 100) if total_concursos > 0 else 0
            frequencia_esperada = probabilidade_teorica * 100
            
            if percentual_diferenca < -10:
                status = "Muito Devedor"
                status_classe = "danger"
                prioridade = "Alta"
            elif percentual_diferenca < -5:
                status = "Devedor"
                status_classe = "warning"
                prioridade = "Média"
            elif percentual_diferenca < 5:
                status = "Equilibrado"
                status_classe = "secondary"
                prioridade = "Baixa"
            elif percentual_diferenca < 10:
                status = "Credor"
                status_classe = "info"
                prioridade = "Baixa"
            else:
                status = "Muito Credor"
                status_classe = "success"
                prioridade = "Muito Baixa"
            
            analise_devidos.append({
                'numero': numero,
                'aparicoes_reais': aparicoes,
                'aparicoes_esperadas': round(aparicoes_esperadas, 1),
                'diferenca': round(diferenca, 1),
                'percentual_diferenca': round(percentual_diferenca, 1),
                'indice_divida': round(indice_divida, 1),
                'status': status,
                'status_classe': status_classe,
                'prioridade': prioridade,
                'atraso_atual': atraso_atual,
                'frequencia_real': round(frequencia_real, 1),
                'frequencia_esperada': round(frequencia_esperada, 1)
            })
        
        analise_devidos.sort(key=lambda x: x['indice_divida'], reverse=True)
        
        numeros_devedores = [n for n in analise_devidos if n['diferenca'] < 0]
        numeros_credores = [n for n in analise_devidos if n['diferenca'] > 0]
        numeros_equilibrados = [n for n in analise_devidos if abs(n['percentual_diferenca']) < 5]
        
        maior_devedor = max(analise_devidos, key=lambda x: x['indice_divida']) if analise_devidos else None
        maior_credor = min(analise_devidos, key=lambda x: x['indice_divida']) if analise_devidos else None
        
        return {
            'analise_devidos': analise_devidos,
            'total_concursos': total_concursos,
            'probabilidade_teorica': round(probabilidade_teorica * 100, 2),
            'numeros_devedores': len(numeros_devedores),
            'numeros_credores': len(numeros_credores),
            'numeros_equilibrados': len(numeros_equilibrados),
            'maior_devedor': maior_devedor,
            'maior_credor': maior_credor,
            'top_devedores': numeros_devedores[:10],
            'top_credores': sorted(numeros_credores, key=lambda x: abs(x['diferenca']), reverse=True)[:10]
        }
from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseFatiamentoService:

    @staticmethod
    def get_digitos_de_dezena(dezena):
        """Retorna os dígitos únicos que compõem uma dezena (01 a 31)."""
        d1 = dezena // 10
        d2 = dezena % 10
        return {d1, d2}

    @staticmethod
    def analisar_fatiamento_historico():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        
        # Estruturas para armazenar estatísticas de cada dígito (0 a 9)
        estatisticas_digitos = {d: {'total_aparicoes': 0, 'maximo_juntos': 0, 'frequencia_por_qnt': defaultdict(int)} for d in range(10)}
        historico_detalhado = []

        for sorteio in sorteios:
            numeros = []
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)
            
            # Contar quantas dezenas no sorteio atual possuem cada dígito
            contagem_sorteio = {d: 0 for d in range(10)}
            
            for num in numeros:
                digitos_do_numero = AnaliseFatiamentoService.get_digitos_de_dezena(num)
                for d in digitos_do_numero:
                    contagem_sorteio[d] += 1
                    
            # Guardar o histórico detalhado do sorteio
            historico_detalhado.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'dezenas': numeros,
                'contagem': contagem_sorteio
            })

            # Atualizar as estatísticas globais
            for d in range(10):
                qtd = contagem_sorteio[d]
                estatisticas_digitos[d]['total_aparicoes'] += qtd
                estatisticas_digitos[d]['frequencia_por_qnt'][qtd] += 1
                if qtd > estatisticas_digitos[d]['maximo_juntos']:
                    estatisticas_digitos[d]['maximo_juntos'] = qtd

        # Formatar a resposta
        resultado_formatado = []
        for d in range(10):
            media_por_concurso = round(estatisticas_digitos[d]['total_aparicoes'] / total_concursos, 2)
            
            # Formatar a frequência por quantidade
            freq_formatada = []
            for qtd in sorted(estatisticas_digitos[d]['frequencia_por_qnt'].keys()):
                ocorrencias = estatisticas_digitos[d]['frequencia_por_qnt'][qtd]
                percentual = round((ocorrencias / total_concursos) * 100, 2)
                freq_formatada.append({
                    'quantidade': qtd,
                    'ocorrencias': ocorrencias,
                    'percentual': percentual
                })
                
            resultado_formatado.append({
                'digito': d,
                'media_por_concurso': media_por_concurso,
                'maximo_juntos': estatisticas_digitos[d]['maximo_juntos'],
                'distribuicao': freq_formatada
            })

        return {
            'total_concursos': total_concursos,
            'estatisticas': resultado_formatado,
            'historico_sorteios': historico_detalhado
        }

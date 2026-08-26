from models.sorteio import Sorteio, db
from collections import defaultdict

class AnalisePrimosCompostosService:

    @staticmethod
    def eh_primo(n):
        """Verifica se um número é primo"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    @staticmethod
    def analisar_primos_compostos():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        # Estruturas de dados
        frequencia_padroes = defaultdict(lambda: {
            'frequencia': 0,
            'ultimo_concurso': 0,
            'concursos': []
        })

        soma_primos = 0
        soma_compostos = 0

        # Análise de cada sorteio
        for sorteio in sorteios:
            numeros = []
            primos = []
            compostos = []

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)
                    if AnalisePrimosCompostosService.eh_primo(numero):
                        primos.append(numero)
                    else:
                        compostos.append(numero)

            qtd_primos = len(primos)
            qtd_compostos = len(compostos)

            soma_primos += qtd_primos
            soma_compostos += qtd_compostos

            # Criar padrão (ex: "3P+4C" = 3 primos + 4 compostos)
            padrao = f"{qtd_primos}P+{qtd_compostos}C"

            frequencia_padroes[padrao]['frequencia'] += 1
            frequencia_padroes[padrao]['concursos'].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': sorted(numeros),
                'primos': sorted(primos),
                'compostos': sorted(compostos)
            })

            if sorteio.concurso > frequencia_padroes[padrao]['ultimo_concurso']:
                frequencia_padroes[padrao]['ultimo_concurso'] = sorteio.concurso

        # Calcular médias
        media_primos = round(soma_primos / total_concursos, 2)
        media_compostos = round(soma_compostos / total_concursos, 2)

        # Ordenar padrões por frequência
        padroes_lista = []
        for padrao, dados in frequencia_padroes.items():
            qtd_primos = int(padrao.split('P')[0])
            qtd_compostos = int(padrao.split('+')[1].replace('C', ''))

            percentual = round((dados['frequencia'] / total_concursos * 100), 2)
            atraso = ultimo_concurso - dados['ultimo_concurso']

            descricao = f"{qtd_primos} primo{'s' if qtd_primos != 1 else ''} + {qtd_compostos} composto{'s' if qtd_compostos != 1 else ''}"

            padroes_lista.append({
                'padrao': padrao,
                'descricao': descricao,
                'primos': qtd_primos,
                'compostos': qtd_compostos,
                'frequencia': dados['frequencia'],
                'percentual': percentual,
                'ultimo_concurso': dados['ultimo_concurso'],
                'atraso': atraso,
                'concursos': dados['concursos']
            })

        # Ordenar por frequência (decrescente)
        padroes_lista.sort(key=lambda x: x['frequencia'], reverse=True)

        return {
            'total_concursos': total_concursos,
            'media_primos_por_sorteio': media_primos,
            'media_compostos_por_sorteio': media_compostos,
            'padroes': padroes_lista
        }

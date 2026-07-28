from models.sorteio import Sorteio, db
from sqlalchemy import func, desc


class AnaliseQuentesFriosService:

    @staticmethod
    def obter_numeros_quentes_frios(top=15):
        """
        Retorna análise completa de números quentes (mais frequentes) e frios (menos frequentes)
        considerando todas as posições (1 a 7) de cada concurso.
        """
        total_concursos = Sorteio.query.count()

        if total_concursos == 0:
            return {
                'quentes': [],
                'frios': [],
                'total_concursos': 0
            }

        frequencias = {}
        ultimos_concursos = {}

        for numero in range(1, 32):
            frequencias[numero] = 0
            ultimos_concursos[numero] = None

        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        for concurso in concursos:
            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso, campo, None)
                
                if numero and 1 <= numero <= 31:
                    frequencias[numero] += 1
                    if ultimos_concursos[numero] is None:
                        ultimos_concursos[numero] = concurso.concurso

        ultimo_concurso_geral = concursos[0] if concursos else None

        estatisticas = []
        for numero in range(1, 32):
            freq = frequencias[numero]
            percentual = round((freq / total_concursos) * 100, 2) if total_concursos > 0 else 0
            atraso_atual = (ultimo_concurso_geral.concurso - ultimos_concursos[numero]
                            if ultimos_concursos[numero] else total_concursos)

            estatisticas.append({
                'numero': numero,
                'frequencia': freq,
                'percentual': f"{percentual:.2f}",
                'ultimo_concurso': ultimos_concursos[numero] or 0,
                'atraso': atraso_atual
            })

        estatisticas_ordenadas = sorted(estatisticas, key=lambda x: x['frequencia'], reverse=True)

        quentes = estatisticas_ordenadas[:top]
        frios = estatisticas_ordenadas[-top:]
        frios.reverse()

        return {
            'quentes': quentes,
            'frios': frios,
            'total_concursos': total_concursos,
            'total_numeros': 31
        }

    @staticmethod
    def obter_estatisticas_completas():
        """
        Retorna estatísticas de todos os 31 números ordenados por frequência
        """
        resultado = AnaliseQuentesFriosService.obter_numeros_quentes_frios(top=31)
        todos_numeros = resultado['quentes']

        return {
            'numeros': todos_numeros,
            'total_concursos': resultado['total_concursos']
        }

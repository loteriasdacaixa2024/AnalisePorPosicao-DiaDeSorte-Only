# Concentração Estratégica — score de união (co-ocorrência histórica)
from models.sorteio import Sorteio


class ConcentracaoEstrategicaService:
    @staticmethod
    def _dezenas_sorteio(sorteio):
        return sorted([
            sorteio.posicao_1,
            sorteio.posicao_2,
            sorteio.posicao_3,
            sorteio.posicao_4,
            sorteio.posicao_5,
            sorteio.posicao_6,
            sorteio.posicao_7,
        ])

    @staticmethod
    def calcular_score_uniao(limite_concursos=250):
        """
        Calcula co-ocorrência de pares de dezenas nos últimos N concursos.
        Usado para manter dezenas que historicamente caminham juntas.
        """
        try:
            limite = max(50, min(int(limite_concursos or 250), 800))
            sorteios = (
                Sorteio.query.order_by(Sorteio.concurso.desc())
                .limit(limite)
                .all()
            )
            total = len(sorteios)
            if total == 0:
                return {
                    'sucesso': False,
                    'erro': 'Nenhum sorteio no banco de dados.',
                    'pares': [],
                    'dezenas_freq': {},
                    'total_concursos': 0,
                }

            pair_count = {}
            dezena_count = {i: 0 for i in range(1, 32)}

            for s in sorteios:
                nums = ConcentracaoEstrategicaService._dezenas_sorteio(s)
                for n in nums:
                    dezena_count[n] = dezena_count.get(n, 0) + 1
                for i in range(len(nums)):
                    for j in range(i + 1, len(nums)):
                        a, b = nums[i], nums[j]
                        key = (a, b)
                        pair_count[key] = pair_count.get(key, 0) + 1

            pares = []
            for (a, b), cnt in pair_count.items():
                pares.append({
                    'a': a,
                    'b': b,
                    'coocorrencias': cnt,
                    'score': round(cnt / total, 4),
                    'juntos_pct': round(100.0 * cnt / total, 2),
                })
            pares.sort(key=lambda x: (-x['score'], x['a'], x['b']))

            dezenas_freq = [
                {'dezena': d, 'freq': c, 'pct': round(100.0 * c / total, 2)}
                for d, c in dezena_count.items()
                if c > 0
            ]
            dezenas_freq.sort(key=lambda x: (-x['freq'], x['dezena']))

            return {
                'sucesso': True,
                'total_concursos': total,
                'pares': pares[:400],
                'top_pares': pares[:30],
                'dezenas_freq': dezenas_freq,
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'pares': [],
                'dezenas_freq': {},
                'total_concursos': 0,
            }

    @staticmethod
    def score_par(pares_index, a, b):
        """Lookup O(1) após indexação no cliente; helper para testes."""
        if a > b:
            a, b = b, a
        return pares_index.get(f'{a}-{b}', 0.0)

# Peso de score por correlação Mês da Sorte × dezenas (histórico completo)
# Reutilizável por motor de ciclos, afinidade e demais análises que recebam mês 1–12 ou nome.

from services.analise_correlacao_mes_dezenas_service import AnaliseCorrelacaoMesDezenaService

_cache_top = {}


class MesSorteScoreService:
    """Dezenas que mais saem juntas com o mês escolhido — bônus de prioridade / score."""

    @classmethod
    def dezenas_prioridade_mes(cls, mes_ref, top=10):
        """Lista de dezenas (ordem de prioridade / frequência com o mês), mais frequentes primeiro."""
        mes_num = AnaliseCorrelacaoMesDezenaService.resolver_numero_mes(mes_ref)
        if not mes_num:
            return []
        key = (int(mes_num), int(top))
        if key not in _cache_top:
            info = AnaliseCorrelacaoMesDezenaService.obter_top_dezenas_do_mes(mes_num, top=top)
            nums = list(info.get('numeros') or []) if info else []
            _cache_top[key] = tuple(nums)
        return list(_cache_top[key])

    @classmethod
    def bonus_por_dezena(cls, mes_ref, top=10, peso_max=14.0):
        """
        Mapa dezena -> bônus (0 .. peso_max) decrescente pelo ranking do top do mês.
        Evita duplicidade: cada dezena recebe um único peso.
        """
        nums = cls.dezenas_prioridade_mes(mes_ref, top=top)
        if not nums:
            return {}
        n = len(nums)
        out = {}
        for i, d in enumerate(nums):
            out[int(d)] = round(peso_max * (n - i) / n, 2)
        return out

    @classmethod
    def aplicar_bonus_em_scores(cls, scores_por_dezena, mes_ref, top=10, peso_max=12.0, teto=99):
        """
        scores_por_dezena: dict[int] -> float ou int
        Soma bônus às dezenas do top do mês (cap opcional por dezena).
        """
        bonus = cls.bonus_por_dezena(mes_ref, top=top, peso_max=peso_max)
        if not bonus:
            return scores_por_dezena
        out = dict(scores_por_dezena)
        for d, b in bonus.items():
            out[d] = min(teto, float(out.get(d, 0)) + float(b))
        return out

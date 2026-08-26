# Sistema: Análise por Posição - Dia de Sorte
# Ciclo 01–31 por posição de sorteio (1ª a 7ª bola)

import random
from statistics import mean, median

from models.sorteio import Sorteio
from services.estatistica_service import EstatisticaService


class CicloPorPosicaoService:
    """
    Ciclo por posição: em cada posição P (1ª bola … 7ª bola),
    conta quantos concursos levam para as 31 dezenas aparecerem ao menos uma vez na P.
    Usa sorteio_1…7 (ordem real); fallback posicao_* se sorteio_* ausente.
    """

    @staticmethod
    def dezena_na_posicao(sorteio, posicao):
        if posicao < 1 or posicao > 7:
            return None
        val = getattr(sorteio, f'sorteio_{posicao}', None)
        if val is not None:
            return int(val)
        return int(getattr(sorteio, f'posicao_{posicao}'))

    @staticmethod
    def _faixa(n):
        if n <= 10:
            return 1
        if n <= 20:
            return 2
        if n <= 30:
            return 3
        return 4

    @staticmethod
    def _sorteios_asc():
        return Sorteio.query.order_by(Sorteio.concurso.asc()).all()

    @staticmethod
    def _sorteios_desc():
        return Sorteio.query.order_by(Sorteio.concurso.desc()).all()

    @classmethod
    def _calcular_ciclos_posicao_from_sorteios(cls, sorteios, posicao):
        if not sorteios:
            return []

        ciclos = []
        ciclo = {
            'numero': 1,
            'concurso_inicio': sorteios[0].concurso,
            'concurso_fim': None,
            'dezenas_saidas': set(),
            'quantidade_concursos': 0,
            'sequencia': [],
            'em_aberto': False,
        }

        for s in sorteios:
            n = cls.dezena_na_posicao(s, posicao)
            if n is None or n < 1 or n > 31:
                continue
            ciclo['dezenas_saidas'].add(n)
            ciclo['quantidade_concursos'] += 1
            ciclo['sequencia'].append({'concurso': s.concurso, 'dezena': n})

            if len(ciclo['dezenas_saidas']) >= 31:
                ciclo['concurso_fim'] = s.concurso
                ciclo['dezenas_saidas'] = sorted(ciclo['dezenas_saidas'])
                ciclos.append(ciclo)
                ciclo = {
                    'numero': len(ciclos) + 1,
                    'concurso_inicio': s.concurso,
                    'concurso_fim': None,
                    'dezenas_saidas': set(),
                    'quantidade_concursos': 0,
                    'sequencia': [],
                    'em_aberto': False,
                }

        if ciclo['quantidade_concursos'] > 0:
            ciclo['em_aberto'] = True
            ciclo['dezenas_saidas'] = sorted(ciclo['dezenas_saidas'])
            ciclos.append(ciclo)

        return ciclos

    @classmethod
    def calcular_ciclos_posicao(cls, posicao):
        return cls._calcular_ciclos_posicao_from_sorteios(cls._sorteios_asc(), posicao)

    @classmethod
    def _atrasos_na_posicao_from_sorteios(cls, sorteios, posicao):
        atrasos = {}
        for n in range(1, 32):
            atrasos[n] = len(sorteios)
        for i, s in enumerate(sorteios):
            n = cls.dezena_na_posicao(s, posicao)
            if n and atrasos.get(n, 0) == len(sorteios):
                atrasos[n] = i
        return atrasos

    @classmethod
    def atrasos_na_posicao(cls, posicao):
        return cls._atrasos_na_posicao_from_sorteios(cls._sorteios_desc(), posicao)

    @classmethod
    def _montar_analise_posicao(cls, posicao, ciclos, atrasos, total_concursos_base):
        fechados = [c for c in ciclos if not c.get('em_aberto')]
        atual = ciclos[-1] if ciclos else None

        duracoes = [c['quantidade_concursos'] for c in fechados]
        pendentes = []
        saidas = []
        progresso = 0
        if atual:
            saidas = list(atual.get('dezenas_saidas') or [])
            pendentes = sorted(set(range(1, 32)) - set(saidas))
            progresso = round((len(saidas) / 31) * 100, 1)

        ultima = None
        if atual and atual.get('sequencia'):
            ultima = atual['sequencia'][-1]

        ranking_pendentes = sorted(
            pendentes,
            key=lambda n: (atrasos.get(n, 0), n),
            reverse=True,
        )
        pendentes_com_atraso = [
            {'dezena': n, 'atraso': int(atrasos.get(n, 0))}
            for n in ranking_pendentes
        ]

        return {
            'posicao': posicao,
            'total_concursos_base': total_concursos_base,
            'ciclos_fechados': len(fechados),
            'ciclo_atual': {
                'numero': atual.get('numero') if atual else None,
                'concurso_inicio': atual.get('concurso_inicio') if atual else None,
                'concursos_no_ciclo': atual.get('quantidade_concursos', 0) if atual else 0,
                'dezenas_saidas': saidas,
                'dezenas_pendentes': pendentes,
                'pendentes_prioritarios': ranking_pendentes[:15],
                'pendentes_com_atraso': pendentes_com_atraso,
                'progresso_pct': progresso,
                'ultimo': ultima,
            },
            'metricas_fechados': {
                'media_concursos': round(mean(duracoes), 1) if duracoes else None,
                'mediana_concursos': median(duracoes) if duracoes else None,
                'minimo': min(duracoes) if duracoes else None,
                'maximo': max(duracoes) if duracoes else None,
                'ultimos_5': [c['quantidade_concursos'] for c in fechados[-5:]],
            },
            'historico_ciclos': [
                {
                    'numero': c['numero'],
                    'concurso_inicio': c['concurso_inicio'],
                    'concurso_fim': c.get('concurso_fim'),
                    'concursos': c['quantidade_concursos'],
                    'em_aberto': bool(c.get('em_aberto')),
                }
                for c in ciclos[-12:]
            ],
        }

    @classmethod
    def analise_posicao(cls, posicao):
        sorteios_asc = cls._sorteios_asc()
        ciclos = cls._calcular_ciclos_posicao_from_sorteios(sorteios_asc, posicao)
        atrasos = cls._atrasos_na_posicao_from_sorteios(
            list(reversed(sorteios_asc)), posicao
        )
        return cls._montar_analise_posicao(
            posicao, ciclos, atrasos, Sorteio.query.count()
        )

    @classmethod
    def resumo_todas_posicoes(cls):
        sorteios_asc = cls._sorteios_asc()
        if not sorteios_asc:
            return {p: cls._montar_analise_posicao(p, [], {}, 0) for p in range(1, 8)}
        sorteios_desc = list(reversed(sorteios_asc))
        total = len(sorteios_asc)
        return {
            p: cls._montar_analise_posicao(
                p,
                cls._calcular_ciclos_posicao_from_sorteios(sorteios_asc, p),
                cls._atrasos_na_posicao_from_sorteios(sorteios_desc, p),
                total,
            )
            for p in range(1, 8)
        }

    @classmethod
    def simular_n_concursos(cls, posicao, n_concursos):
        ciclos = cls.calcular_ciclos_posicao(posicao)
        fechados = [c for c in ciclos if not c.get('em_aberto')]
        if not fechados:
            return {'n': n_concursos, 'percentual_fecharia': None, 'amostra': 0}

        dentro = sum(1 for c in fechados if c['quantidade_concursos'] <= n_concursos)
        return {
            'n': n_concursos,
            'percentual_fecharia': round((dentro / len(fechados)) * 100, 1),
            'amostra': len(fechados),
            'media_historica': round(mean([c['quantidade_concursos'] for c in fechados]), 1),
        }

    @classmethod
    def _score_dezena_posicao(cls, n, posicao, pendentes, atrasos, foco=False):
        score = 0.0
        if n in pendentes:
            score += 60 + len(pendentes) * 0.5
        score += min(atrasos.get(n, 0), 80) * 1.2
        if foco:
            score *= 1.35
        return score

    @classmethod
    def _montar_jogo(cls, resumo_posicoes, posicao_foco=None, variacao=0):
        rng = random.Random((variacao + 1) * 9973 + (posicao_foco or 0) * 31)

        escolhidos = []
        faixa_count = {1: 0, 2: 0, 3: 0, 4: 0}
        max_faixa = 3

        ordem_pos = list(range(1, 8))
        if posicao_foco and posicao_foco in ordem_pos:
            ordem_pos = [posicao_foco] + [p for p in ordem_pos if p != posicao_foco]
        rng.shuffle(ordem_pos[1:] if posicao_foco else ordem_pos)

        for p in ordem_pos:
            data = resumo_posicoes[p]['ciclo_atual']
            pendentes = set(data.get('dezenas_pendentes') or [])
            atrasos = cls.atrasos_na_posicao(p)

            candidatos = []
            for n in range(1, 32):
                if n in escolhidos:
                    continue
                f = cls._faixa(n)
                if faixa_count[f] >= max_faixa:
                    continue
                sc = cls._score_dezena_posicao(n, p, pendentes, atrasos, foco=(p == posicao_foco))
                candidatos.append((sc, n, f))

            candidatos.sort(key=lambda x: (-x[0], x[1]))
            if not candidatos:
                continue
            pick = candidatos[rng.randint(0, min(4, len(candidatos) - 1))]
            escolhidos.append(pick[1])
            faixa_count[pick[2]] += 1

        if len(escolhidos) < 7:
            pool = []
            for p in range(1, 8):
                data = resumo_posicoes[p]['ciclo_atual']
                pendentes = set(data.get('dezenas_pendentes') or [])
                atrasos = cls.atrasos_na_posicao(p)
                for n in pendentes:
                    if n in escolhidos:
                        continue
                    f = cls._faixa(n)
                    if faixa_count[f] >= max_faixa:
                        continue
                    sc = cls._score_dezena_posicao(n, p, pendentes, atrasos, foco=(p == posicao_foco))
                    pool.append((sc, n, f))
            pool.sort(key=lambda x: (-x[0], x[1]))
            for sc, n, f in pool:
                if len(escolhidos) >= 7:
                    break
                if n in escolhidos:
                    continue
                escolhidos.append(n)
                faixa_count[f] += 1

        while len(escolhidos) < 7:
            n = rng.randint(1, 31)
            if n not in escolhidos:
                escolhidos.append(n)

        return sorted(escolhidos[:7])

    @classmethod
    def gerar_apostas_inteligentes(
        cls,
        quantidade=10,
        dezenas_por_aposta=7,
        posicao_foco=None,
    ):
        quantidade = max(1, min(int(quantidade), 150))
        dezenas_por_aposta = max(7, min(int(dezenas_por_aposta), 15))

        if posicao_foco is not None:
            posicao_foco = int(posicao_foco)
            if posicao_foco < 1 or posicao_foco > 7:
                posicao_foco = None

        resumo = cls.resumo_todas_posicoes()
        apostas = []
        chaves = set()

        tentativa = 0
        while len(apostas) < quantidade and tentativa < quantidade * 40:
            jogo = cls._montar_jogo(resumo, posicao_foco, tentativa)
            if dezenas_por_aposta != 7:
                extras = [n for n in range(1, 32) if n not in jogo]
                rng = random.Random(tentativa * 17)
                rng.shuffle(extras)
                while len(jogo) < dezenas_por_aposta and extras:
                    cand = extras.pop()
                    f = cls._faixa(cand)
                    cnt = sum(1 for x in jogo if cls._faixa(x) == f)
                    if cnt < 4:
                        jogo.append(cand)
                jogo = sorted(jogo[:dezenas_por_aposta])

            chave = ','.join(map(str, jogo))
            if chave not in chaves:
                chaves.add(chave)
                detalhe_pos = []
                for p in range(1, 8):
                    pend = set(resumo[p]['ciclo_atual']['dezenas_pendentes'])
                    cobre = [n for n in jogo if n in pend]
                    if cobre:
                        detalhe_pos.append({'posicao': p, 'pendentes_cobertas': cobre})
                apostas.append(
                    {
                        'numeros': jogo,
                        'cobertura_pendentes': detalhe_pos,
                        'qtd_pendentes_no_jogo': sum(len(d['pendentes_cobertas']) for d in detalhe_pos),
                    }
                )
            tentativa += 1

        mes_info = EstatisticaService.estatisticas_mes_sorte()
        mes_sugerido = None
        if mes_info and mes_info.get('menos_sorteado'):
            mes_sugerido = mes_info['menos_sorteado'].get('mes')

        sims = {}
        for p in range(1, 8):
            sims[str(p)] = cls.simular_n_concursos(p, quantidade)

        return {
            'sucesso': True,
            'quantidade': len(apostas),
            'dezenas_por_aposta': dezenas_por_aposta,
            'posicao_foco': posicao_foco,
            'mes_sugerido': mes_sugerido,
            'apostas': apostas,
            'resumo_posicoes': {
                str(p): {
                    'progresso_pct': resumo[p]['ciclo_atual']['progresso_pct'],
                    'pendentes': len(resumo[p]['ciclo_atual']['dezenas_pendentes']),
                    'concursos_ciclo_atual': resumo[p]['ciclo_atual']['concursos_no_ciclo'],
                }
                for p in range(1, 8)
            },
            'simulacao_orcamento': sims,
            'estrategia': (
                'Prioriza dezenas PENDENTES no ciclo de cada posição (ordem real do sorteio), '
                'com peso extra na posição em foco e limite por faixa 01–10 / 11–20 / 21–30 / 31.'
            ),
        }

# Motor Analítico Inteligente de Ciclos — Dia de Sorte
from collections import Counter, defaultdict
import random
import math

from services.analise_ciclos_dezenas_service import AnaliseCiclosDezenasService
from services.analise_quentes_frios_service import AnaliseQuentesFriosService
from services.analise_repeticoes_service import AnaliseRepeticoesService
from services.analise_correlacao_mes_dezenas_service import AnaliseCorrelacaoMesDezenaService
from models.sorteio import Sorteio


class CicloInteligenciaService:
    FAIXA_BAIXA = (1, 10)
    FAIXA_MEDIA = (11, 20)
    FAIXA_ALTA = (21, 31)

    @staticmethod
    def _faixa(dezena):
        if dezena <= 10:
            return 'baixa'
        if dezena <= 20:
            return 'media'
        return 'alta'

    @staticmethod
    def _ultimo_sorteio_dezenas():
        ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
        if not ultimo:
            return []
        return [
            ultimo.posicao_1, ultimo.posicao_2, ultimo.posicao_3,
            ultimo.posicao_4, ultimo.posicao_5, ultimo.posicao_6, ultimo.posicao_7
        ]

    @staticmethod
    def _coletar_snapshots_historicos():
        """Para cada concurso em cada ciclo, guarda estado antes do sorteio e novas no sorteio."""
        ciclos = AnaliseCiclosDezenasService.calcular_ciclos_completos()
        snapshots = []

        for ciclo in ciclos:
            saidas = set()
            n_concurso = 0
            for det in ciclo.get('detalhes_concursos', []):
                n_concurso += 1
                pendentes_antes = 31 - len(saidas)
                novas = set(det.get('novas', []))
                qtd_faltantes_entraram = len(novas)

                snapshots.append({
                    'numero_ciclo': ciclo['numero'],
                    'concurso': det['concurso'],
                    'concursos_no_ciclo': n_concurso,
                    'pendentes_antes': pendentes_antes,
                    'percentual_antes': round((len(saidas) / 31) * 100, 1),
                    'qtd_faltantes_entraram': qtd_faltantes_entraram,
                    'qtd_novas': det.get('qtd_novas', 0),
                    'em_andamento': ciclo.get('em_andamento', False),
                })
                saidas.update(novas)
                saidas.update(det.get('repetidas', []))

        return snapshots

    @staticmethod
    def _cenarios_semelhantes(pendentes_atual, concursos_atual, tolerancia_pendentes=1):
        snapshots = CicloInteligenciaService._coletar_snapshots_historicos()
        similares = [
            s for s in snapshots
            if abs(s['pendentes_antes'] - pendentes_atual) <= tolerancia_pendentes
            and s['pendentes_antes'] > 0
        ]
        if len(similares) < 5:
            similares = [
                s for s in snapshots
                if s['pendentes_antes'] > 0
                and abs(s['pendentes_antes'] - pendentes_atual) <= 3
            ]
        return similares

    @staticmethod
    def _distribuicao_faltantes_entrada(similares):
        if not similares:
            return {'1': 0, '2': 0, '3': 0, '4+': 0}, 0

        contagem = Counter()
        for s in similares:
            q = s['qtd_faltantes_entraram']
            if q <= 0:
                contagem['0'] += 1
            elif q == 1:
                contagem['1'] += 1
            elif q == 2:
                contagem['2'] += 1
            elif q == 3:
                contagem['3'] += 1
            else:
                contagem['4+'] += 1

        total = len(similares)
        perc = {}
        for chave in ['0', '1', '2', '3', '4+']:
            perc[chave] = round((contagem.get(chave, 0) / total) * 100, 1)
        return perc, total

    @staticmethod
    def _classificar_estado_ciclo(concursos, media, percentual):
        if concursos < max(3, media * 0.55):
            return 'Inicial'
        if concursos > media * 1.15:
            return 'Crítico'
        if concursos >= media * 0.85 or percentual >= 72:
            return 'Avançado'
        if concursos >= media * 0.55:
            return 'Médio'
        return 'Inicial'

    @staticmethod
    def _calcular_pressao(pendentes, concursos, media, perc_fechamento_gradual):
        score = 0
        if pendentes <= 3:
            score += 35
        elif pendentes <= 6:
            score += 28
        elif pendentes <= 10:
            score += 18
        elif pendentes <= 15:
            score += 10
        else:
            score += 4

        if media > 0:
            ratio = concursos / media
            if ratio > 1.25:
                score += 30
            elif ratio > 1.05:
                score += 22
            elif ratio > 0.9:
                score += 15
            elif ratio > 0.7:
                score += 8

        if perc_fechamento_gradual > 55:
            score += 12
        elif perc_fechamento_gradual < 30:
            score -= 5

        if score >= 70:
            nivel = 'extrema'
        elif score >= 50:
            nivel = 'alta'
        elif score >= 30:
            nivel = 'média'
        else:
            nivel = 'baixa'
        return nivel, min(100, score)

    @staticmethod
    def _analisar_faltantes(pendentes):
        baixas = [d for d in pendentes if CicloInteligenciaService.FAIXA_BAIXA[0] <= d <= CicloInteligenciaService.FAIXA_BAIXA[1]]
        medias = [d for d in pendentes if CicloInteligenciaService.FAIXA_MEDIA[0] <= d <= CicloInteligenciaService.FAIXA_MEDIA[1]]
        altas = [d for d in pendentes if CicloInteligenciaService.FAIXA_ALTA[0] <= d <= CicloInteligenciaService.FAIXA_ALTA[1]]
        pares = [d for d in pendentes if d % 2 == 0]
        impares = [d for d in pendentes if d % 2 == 1]

        ordenadas = sorted(pendentes)
        consecutivas = []
        i = 0
        while i < len(ordenadas):
            seq = [ordenadas[i]]
            j = i + 1
            while j < len(ordenadas) and ordenadas[j] == ordenadas[j - 1] + 1:
                seq.append(ordenadas[j])
                j += 1
            if len(seq) >= 2:
                consecutivas.append(seq)
            i = j if j > i + 1 else i + 1

        gaps = []
        for i in range(len(ordenadas) - 1):
            gaps.append(ordenadas[i + 1] - ordenadas[i])

        return {
            'baixas': baixas,
            'medias': medias,
            'altas': altas,
            'pares': pares,
            'impares': impares,
            'consecutivas': consecutivas,
            'espacamento_medio': round(sum(gaps) / len(gaps), 1) if gaps else 0,
            'distribuicao': {
                'baixas': len(baixas),
                'medias': len(medias),
                'altas': len(altas),
            },
        }

    @staticmethod
    def _tipo_fechamento_historico(similares):
        if not similares:
            return 'gradual', 'Dados insuficientes para classificar fechamento.'
        agressivos = sum(1 for s in similares if s['qtd_faltantes_entraram'] >= 4)
        graduais = sum(1 for s in similares if 1 <= s['qtd_faltantes_entraram'] <= 3)
        nulos = sum(1 for s in similares if s['qtd_faltantes_entraram'] == 0)
        total = len(similares)
        pct_agr = agressivos / total * 100
        pct_grad = graduais / total * 100

        if pct_agr > 35:
            tipo = 'agressivo'
            texto = (
                f'Histórico indica tendência a fechamento mais intenso '
                f'({pct_agr:.0f}% dos cenários semelhantes entraram com 4+ faltantes de uma vez).'
            )
        else:
            tipo = 'gradual'
            texto = (
                f'Histórico favorece fechamento gradual '
                f'({pct_grad:.0f}% dos cenários entraram 1 a 3 faltantes; '
                f'{nulos / total * 100:.0f}% sem entrada de faltantes).'
            )
        return tipo, texto

    @staticmethod
    def _correlacao_mes_contexto(mes_ref):
        if not mes_ref or str(mes_ref).lower() in ('aleatorio', 'aleatório', ''):
            return None
        info = AnaliseCorrelacaoMesDezenaService.obter_top_dezenas_do_mes(mes_ref, top=10)
        if not info:
            return None
        numeros = info['numeros']
        ordenados = sorted(info.get('numeros_ordenados') or numeros)
        qtd = info.get('quantidade', len(ordenados))
        leitura = (
            f"Quando sai o mês {info['mes_nome']}, historicamente {qtd} dezenas "
            f"({', '.join(str(n).zfill(2) for n in ordenados)}) aparecem com mais frequência "
            f"no mesmo sorteio ({info['total_sorteios']} concursos com esse mês no histórico)."
        )
        return {**info, 'numeros_ordenados': ordenados, 'quantidade': qtd, 'leitura': leitura}

    @staticmethod
    def _scores_dezenas(ciclo, pendentes, mes_ref=None):
        correlacao = CicloInteligenciaService._correlacao_mes_contexto(mes_ref)
        top_mes = set(correlacao['numeros']) if correlacao else set()
        rank_mes = {d: i for i, d in enumerate(correlacao['numeros'])} if correlacao else {}

        ultimo = set(CicloInteligenciaService._ultimo_sorteio_dezenas())
        quentes_data = AnaliseQuentesFriosService.obter_numeros_quentes_frios(15)
        quentes = {n['numero'] for n in quentes_data.get('quentes', [])} if quentes_data else set()
        frios = {n['numero'] for n in quentes_data.get('frios', [])} if quentes_data else set()

        rep_data = AnaliseRepeticoesService.obter_numeros_que_repetem()
        rep_map = {n['numero']: n['repeticoes'] for n in rep_data.get('numeros', [])}

        detalhes = ciclo.get('detalhes_concursos', [])
        concursos_ciclo = [d for d in detalhes if d.get('numero_ciclo') == ciclo.get('numero_ciclo') or True]
        if ciclo.get('numero_ciclo'):
            concursos_ciclo = [d for d in detalhes if d.get('numero_ciclo') == ciclo['numero_ciclo']]
        if not concursos_ciclo:
            concursos_ciclo = detalhes[: ciclo.get('quantidade_concursos', 20)]

        scores = []
        for d in range(1, 32):
            score = 30
            if d in pendentes:
                score += 35
            if d in ultimo:
                score += 12
            if d in quentes:
                score += 10
            if d in frios and d in pendentes:
                score += 8
            score += min(15, rep_map.get(d, 0))
            if CicloInteligenciaService._faixa(d) == 'media' and d in pendentes:
                score += 5
            if d in top_mes:
                bonus = 18 - min(rank_mes.get(d, 9), 9) * 1.5
                score += int(bonus)
            scores.append({
                'dezena': d,
                'score': min(99, score),
                'pendente': d in pendentes,
                'correlacao_mes': d in top_mes,
            })

        scores.sort(key=lambda x: (-x['score'], x['dezena']))
        return scores[:15], correlacao

    @staticmethod
    def analisar_ciclo_completo(mes_ref=None):
        ciclo = AnaliseCiclosDezenasService.obter_ciclo_atual()
        metricas = AnaliseCiclosDezenasService.obter_metricas_historicas()
        comparacao = AnaliseCiclosDezenasService.comparar_ciclo_atual_com_historico()

        if not ciclo:
            return None

        media = metricas.get('media_concursos', 18) or 18
        concursos = ciclo['quantidade_concursos']
        pendentes = ciclo['dezenas_pendentes']
        n_pend = len(pendentes)
        percentual = ciclo['percentual_completo']

        similares = CicloInteligenciaService._cenarios_semelhantes(n_pend, concursos)
        dist, total_sim = CicloInteligenciaService._distribuicao_faltantes_entrada(similares)
        tipo_fech, texto_fech = CicloInteligenciaService._tipo_fechamento_historico(similares)
        pct_gradual = dist.get('1', 0) + dist.get('2', 0) + dist.get('3', 0)

        estado = CicloInteligenciaService._classificar_estado_ciclo(concursos, media, percentual)
        pressao_nivel, pressao_score = CicloInteligenciaService._calcular_pressao(
            n_pend, concursos, media, pct_gradual
        )

        distancia_media = round(concursos - media, 1)
        analise_falt = CicloInteligenciaService._analisar_faltantes(pendentes)
        scores, correlacao_mes = CicloInteligenciaService._scores_dezenas(ciclo, pendentes, mes_ref)

        media_entrada = 0
        if similares:
            media_entrada = round(
                sum(s['qtd_faltantes_entraram'] for s in similares) / len(similares), 1
            )

        leitura = CicloInteligenciaService._gerar_leitura(
            estado, n_pend, percentual, pressao_nivel, media_entrada, tipo_fech, distancia_media, media
        )
        if correlacao_mes:
            leitura += ' ' + correlacao_mes['leitura']
            pendentes_mes = [d for d in correlacao_mes['numeros'] if d in pendentes]
            if pendentes_mes:
                leitura += (
                    f" Entre as pendentes do ciclo, priorize as que combinam com "
                    f"{correlacao_mes['mes_nome']}: "
                    f"{', '.join(str(d).zfill(2) for d in pendentes_mes[:5])}."
                )

        estrategia = CicloInteligenciaService._definir_estrategia(
            estado, pressao_nivel, n_pend, tipo_fech, dist, analise_falt,
            ultimo=CicloInteligenciaService._ultimo_sorteio_dezenas(),
            correlacao_mes=correlacao_mes,
        )

        return {
            'estado_atual': {
                'numero_ciclo': ciclo['numero_ciclo'],
                'faltando': n_pend,
                'fechamento_percentual': percentual,
                'concursos_decorridos': concursos,
                'media_historica_fechamento': media,
                'distancia_media': distancia_media,
                'classificacao': estado,
                'pressao': pressao_nivel,
                'pressao_score': pressao_score,
            },
            'faltantes': analise_falt,
            'historico_semelhante': {
                'amostras': total_sim,
                'distribuicao_entrada': dist,
                'media_faltantes_entrada': media_entrada,
            },
            'fechamento': {
                'tipo': tipo_fech,
                'interpretacao': texto_fech,
            },
            'scores_dezenas': scores,
            'correlacao_mes': correlacao_mes,
            'leitura_automatica': leitura,
            'estrategia': estrategia,
        }

    @staticmethod
    def _gerar_leitura(estado, n_pend, pct, pressao, media_entrada, tipo_fech, dist_media, media_hist):
        partes = [
            f'Ciclo {estado.lower()} com {n_pend} dezena(s) faltante(s) e {pct:.0f}% de fechamento.',
            f'Pressão estatística {pressao}.',
        ]
        if media_entrada > 0:
            lo = max(1, int(media_entrada - 0.5))
            hi = min(7, int(media_entrada + 1))
            partes.append(
                f'Cenários semelhantes apresentam entrada média de {lo} a {hi} faltante(s) no próximo concurso.'
            )
        if tipo_fech == 'gradual':
            partes.append('Não recomendado utilizar todas as pendentes no mesmo jogo.')
        if dist_media > 2:
            partes.append(
                f'O ciclo está {dist_media:.0f} concursos acima da média histórica ({media_hist:.1f}).'
            )
        elif dist_media < -2:
            partes.append('O ciclo ainda está abaixo da média histórica de duração.')
        return ' '.join(partes)

    @staticmethod
    def _definir_estrategia(estado, pressao, n_pend, tipo_fech, dist, analise_falt, ultimo, correlacao_mes=None):
        if n_pend <= 4 and pressao in ('alta', 'extrema'):
            qtd_faltantes = min(3, n_pend)
        elif tipo_fech == 'gradual':
            qtd_faltantes = 2 if n_pend >= 2 else n_pend
        else:
            qtd_faltantes = min(4, max(2, n_pend // 2))

        pct_2 = dist.get('2', 0) + dist.get('3', 0)
        if pct_2 > 50:
            qtd_faltantes = min(qtd_faltantes, 3)

        repetentes = 1
        if len(ultimo) >= 7:
            repetentes = 1

        faixa_prior = 'media'
        dist_f = analise_falt.get('distribuicao', {})
        if dist_f.get('medias', 0) >= dist_f.get('altas', 0):
            faixa_prior = 'media'
        elif dist_f.get('altas', 0) > dist_f.get('baixas', 0) + 2:
            faixa_prior = 'baixa'

        modo = 'equilibrado'
        if pressao in ('alta', 'extrema') and n_pend <= 8:
            modo = 'agressivo' if tipo_fech == 'agressivo' else 'equilibrado'
        elif estado == 'Inicial' or n_pend > 12:
            modo = 'conservador'

        alertas = []
        if n_pend > 10 and estado != 'Crítico':
            alertas.append('Ciclo ainda distante da zona crítica — evite fechamento completo.')
        if dist_f.get('altas', 0) > dist_f.get('baixas', 0) + 3:
            alertas.append('Excesso de dezenas altas (21–31) entre as pendentes.')
        if tipo_fech == 'gradual' and qtd_faltantes >= n_pend:
            alertas.append('Risco elevado de fechamento incompleto se usar todas as faltantes.')
        if dist.get('0', 0) > 25:
            alertas.append('Histórico mostra possível retenção (sorteio sem novas faltantes).')
        if correlacao_mes:
            ordenados = sorted(correlacao_mes.get('numeros_ordenados') or correlacao_mes['numeros'])
            qtd = correlacao_mes.get('quantidade', len(ordenados))
            nums = ', '.join(str(d).zfill(2) for d in ordenados)
            alertas.append(
                f"Mês {correlacao_mes['mes_nome']}: {qtd} dezenas que costumam sair juntas — {nums}."
            )

        sugestao_mes = ''
        if correlacao_mes:
            sugestao_mes = (
                f"incluir 1–2 dezenas do top do mês {correlacao_mes['mes_nome']} "
                f"({', '.join(str(d).zfill(2) for d in correlacao_mes['numeros'][:4])})"
            )

        return {
            'modo_recomendado': modo,
            'faltantes_por_jogo': qtd_faltantes,
            'repetentes_por_jogo': repetentes,
            'fechamento_parcial': tipo_fech == 'gradual' or n_pend > 6,
            'priorizar_faixa': faixa_prior,
            'evitar_todas_faltantes': n_pend > 3,
            'alertas': alertas,
            'sugestao': {
                'usar_faltantes': f'{qtd_faltantes} ou {min(qtd_faltantes + 1, n_pend)} dezenas faltantes por jogo',
                'repetentes': f'{repetentes} repetente(s) do último concurso',
                'pares_impares': 'manter equilíbrio entre pares e ímpares',
                'faixa': f'priorizar dezenas {faixa_prior}as' if faixa_prior != 'media' else 'priorizar dezenas médias (11–20)',
                'mes_correlacao': sugestao_mes or None,
            },
        }

    @staticmethod
    def obter_inteligencia_operacional(mes_ref=None):
        analise = CicloInteligenciaService.analisar_ciclo_completo(mes_ref)
        if not analise:
            return None

        est = analise['estado_atual']
        estr = analise['estrategia']

        respostas = {
            'como_jogar': analise['leitura_automatica'],
            'quantas_faltantes': estr['faltantes_por_jogo'],
            'vale_fechamento': not estr['fechamento_parcial'] if est['faltando'] <= 4 else 'parcial',
            'vale_agressividade': estr['modo_recomendado'] in ('agressivo', 'fechamento'),
            'estrutura_segura': 'equilibrada' if estr['modo_recomendado'] == 'equilibrado' else estr['modo_recomendado'],
        }

        return {
            **analise,
            'operacional': {
                'respostas': respostas,
                'estrategia_recomendada': estr,
                'resumo_final': analise['leitura_automatica'],
            },
        }

    @staticmethod
    def gerar_apostas_inteligentes(
        quantidade_apostas=5,
        dezenas_por_aposta=7,
        modo='equilibrado',
        dezenas_fixas=None,
        analise=None,
        mes_ref=None,
    ):
        if analise is None:
            analise = CicloInteligenciaService.analisar_ciclo_completo(mes_ref)
        if not analise:
            return [], {}

        ciclo = AnaliseCiclosDezenasService.obter_ciclo_atual()
        if not ciclo:
            return [], {}

        estr = analise['estrategia']
        pendentes = ciclo['dezenas_pendentes']
        saidas = ciclo['dezenas_saidas']
        ultimo = CicloInteligenciaService._ultimo_sorteio_dezenas()
        scores_map = {s['dezena']: s['score'] for s in analise['scores_dezenas']}

        modos_config = {
            'conservador': {'faltantes': max(1, estr['faltantes_por_jogo'] - 1), 'repetentes': 2},
            'equilibrado': {'faltantes': estr['faltantes_por_jogo'], 'repetentes': estr['repetentes_por_jogo']},
            'agressivo': {'faltantes': min(len(pendentes), estr['faltantes_por_jogo'] + 1), 'repetentes': 1},
            'fechamento': {'faltantes': min(len(pendentes), estr['faltantes_por_jogo'] + 2), 'repetentes': 0},
        }
        cfg = modos_config.get(modo, modos_config['equilibrado'])

        def peso(d):
            return scores_map.get(d, 50) + random.random() * 5

        dezenas_fixas = dezenas_fixas or []
        fixas_pend = [d for d in dezenas_fixas if d in pendentes]
        fixas_out = [d for d in dezenas_fixas if d not in pendentes]

        apostas = []
        apostas_set = set()
        tentativas = 0
        max_tent = quantidade_apostas * 150

        pool_pend = sorted(pendentes, key=peso, reverse=True)
        pool_rep = [d for d in ultimo if d in saidas and d not in dezenas_fixas]
        pool_saidas = sorted(
            [d for d in saidas if d not in dezenas_fixas and d not in ultimo],
            key=peso,
            reverse=True,
        )

        while len(apostas) < quantidade_apostas and tentativas < max_tent:
            tentativas += 1
            aposta = list(dezenas_fixas)

            alvo_pend = min(cfg['faltantes'], dezenas_por_aposta - len(aposta))
            alvo_pend = max(0, alvo_pend - len(fixas_pend))
            alvo_rep = min(cfg['repetentes'], dezenas_por_aposta - len(aposta) - alvo_pend)

            esc_pend = []
            dispon_pend = [d for d in pool_pend if d not in aposta]
            if alvo_pend > 0 and dispon_pend:
                k = min(alvo_pend, len(dispon_pend))
                esc_pend = random.sample(dispon_pend[: min(12, len(dispon_pend))], k)

            esc_rep = []
            dispon_rep = [d for d in pool_rep if d not in aposta and d not in esc_pend]
            if alvo_rep > 0 and dispon_rep:
                k = min(alvo_rep, len(dispon_rep))
                esc_rep = random.sample(dispon_rep, k)

            aposta.extend(esc_pend)
            aposta.extend(esc_rep)

            faltam = dezenas_por_aposta - len(aposta)
            if faltam > 0:
                restante = [d for d in pool_saidas if d not in aposta]
                if len(restante) < faltam:
                    restante = [d for d in range(1, 32) if d not in aposta and d not in pendentes]
                if len(restante) >= faltam:
                    aposta.extend(random.sample(restante[:15], faltam))
                else:
                    continue

            if len(aposta) != dezenas_por_aposta:
                continue

            t = tuple(sorted(aposta))
            if t in apostas_set:
                continue
            apostas_set.add(t)
            apostas.append(list(t))

        meta = {
            'modo': modo,
            'analise_resumo': analise['leitura_automatica'],
            'estrategia': estr,
            'ciclo': ciclo['numero_ciclo'],
        }
        return apostas, meta

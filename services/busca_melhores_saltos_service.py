"""
Busca automática dos melhores presets de Salto por Coluna (Aba 6A).

Modo principal: Base × próximo concurso (walk-forward no banco).
Reutiliza GeradorAtrasoPosicaoExperimentalService (mesmo algoritmo).
"""

from __future__ import annotations

import itertools
import random
import threading
import time
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple

from services.conferencia_historica_service import ConferenciaHistoricaService
from services.gerador_atraso_posicao_experimental_service import (
    GeradorAtrasoPosicaoExperimentalService,
)
from services.gerador_atraso_posicao_service import GeradorAtrasoPosicaoService
from services.gerador_especial_service import GeradorEspecialService


class BuscaMelhoresSaltosService:
    """Orquestra amostragem de presets por coluna + ranking Base→próximo."""

    _jobs: Dict[str, Dict[str, Any]] = {}
    _lock = threading.Lock()
    MAX_JOBS = 8
    TOP_GUARDAR_APOSTAS = 50

    # -------------------------------------------------------------------------
    # Job store
    # -------------------------------------------------------------------------

    @classmethod
    def _purge_jobs(cls) -> None:
        if len(cls._jobs) <= cls.MAX_JOBS:
            return
        ordenados = sorted(
            cls._jobs.items(),
            key=lambda kv: kv[1].get('criado_em', 0),
        )
        for jid, _ in ordenados[: max(0, len(cls._jobs) - cls.MAX_JOBS)]:
            cls._jobs.pop(jid, None)

    @classmethod
    def criar_job(cls, params: Dict[str, Any]) -> str:
        job_id = uuid.uuid4().hex[:16]
        with cls._lock:
            cls._purge_jobs()
            cls._jobs[job_id] = {
                'id': job_id,
                'status': 'pendente',
                'progresso': 0,
                'testados': 0,
                'total': 0,
                'mensagem': 'Aguardando início…',
                'criado_em': time.time(),
                'params': params,
                'ranking': [],
                'top_apostas': {},
                'erro': None,
                'cancelar': False,
                'estatisticas': {},
            }
        return job_id

    @classmethod
    def obter_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        with cls._lock:
            job = cls._jobs.get(job_id)
            if not job:
                return None
            return {
                'id': job['id'],
                'status': job['status'],
                'progresso': job['progresso'],
                'testados': job['testados'],
                'total': job['total'],
                'mensagem': job['mensagem'],
                'erro': job['erro'],
                'estatisticas': job.get('estatisticas') or {},
                'ranking': list(job.get('ranking') or []),
                'params': job.get('params') or {},
            }

    @classmethod
    def cancelar_job(cls, job_id: str) -> bool:
        with cls._lock:
            job = cls._jobs.get(job_id)
            if not job:
                return False
            job['cancelar'] = True
            if job['status'] in ('pendente', 'processando'):
                job['status'] = 'cancelado'
                job['mensagem'] = 'Busca cancelada pelo usuário.'
            return True

    @classmethod
    def obter_apostas_rank(cls, job_id: str, rank: int) -> Optional[Dict[str, Any]]:
        with cls._lock:
            job = cls._jobs.get(job_id)
            if not job:
                return None
            return job.get('top_apostas', {}).get(int(rank))

    # -------------------------------------------------------------------------
    # Presets
    # -------------------------------------------------------------------------

    @staticmethod
    def _chave_preset(mais: List[int], menos: List[int]) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
        return (tuple(mais), tuple(menos))

    @staticmethod
    def _fmt_preset(mais: List[int], menos: List[int]) -> str:
        if mais == menos:
            return '±' + ','.join(str(v) for v in mais)
        return '+' + ','.join(str(v) for v in mais) + ' / −' + ','.join(str(v) for v in menos)

    @classmethod
    def gerar_lista_presets(
        cls,
        limite: int,
        max_testes: int,
        simetrico: bool,
        modo: str,
        seed: Optional[int] = None,
    ) -> List[Tuple[List[int], List[int]]]:
        limite = GeradorAtrasoPosicaoExperimentalService._validar_limite(limite)
        limite = max(1, min(int(limite), 30))
        max_testes = max(1, min(int(max_testes), 20000))
        rng = random.Random(seed if seed is not None else time.time_ns())
        modo = (modo or 'aleatorio').lower()

        valores = list(range(1, limite + 1))
        vistos = set()
        out: List[Tuple[List[int], List[int]]] = []

        def add(mais: List[int], menos: List[int]) -> bool:
            k = cls._chave_preset(mais, menos)
            if k in vistos:
                return False
            vistos.add(k)
            out.append((mais, menos))
            return True

        if modo == 'exaustivo' and simetrico:
            espaco = limite ** 7
            if espaco <= max_testes:
                for combo in itertools.product(valores, repeat=7):
                    m = list(combo)
                    add(m, list(m))
                return out
            modo = 'aleatorio'

        if modo == 'grade':
            base = [1] * 7
            add(list(base), list(base) if simetrico else list(base))
            for col in range(7):
                for v in valores:
                    mais = list(base)
                    mais[col] = v
                    if simetrico:
                        add(mais, list(mais))
                    else:
                        for vn in valores:
                            menos = list(base)
                            menos[col] = vn
                            add(mais, menos)
                            if len(out) >= max_testes:
                                return out[:max_testes]
            while len(out) < max_testes:
                mais = [rng.choice(valores) for _ in range(7)]
                menos = list(mais) if simetrico else [rng.choice(valores) for _ in range(7)]
                add(mais, menos)
            return out[:max_testes]

        tentativas = 0
        limite_tentativas = max_testes * 20
        while len(out) < max_testes and tentativas < limite_tentativas:
            tentativas += 1
            mais = [rng.choice(valores) for _ in range(7)]
            menos = list(mais) if simetrico else [rng.choice(valores) for _ in range(7)]
            add(mais, menos)
        return out

    # -------------------------------------------------------------------------
    # Walk-forward (Base × próximo)
    # -------------------------------------------------------------------------

    @staticmethod
    def _mask_nums(nums: Iterable[int]) -> int:
        m = 0
        for n in nums:
            m |= 1 << int(n)
        return m

    @staticmethod
    def _atrasos_globais_ate(sorteios_slice: List[Any]) -> List[int]:
        """Atrasos globais como se o 'último' fosse o fim de sorteios_slice."""
        if not sorteios_slice:
            return list(range(1, 32))
        last_seen = {i: 0 for i in range(1, 32)}
        # percorre do mais recente para o mais antigo
        for s in reversed(sorteios_slice):
            for n in s['posicoes']:
                if 1 <= n <= 31 and last_seen[n] == 0:
                    last_seen[n] = s['concurso']
        ultimo_c = sorteios_slice[-1]['concurso']
        delays = []
        for i in range(1, 32):
            atraso = (ultimo_c - last_seen[i]) if last_seen[i] > 0 else 150
            delays.append((i, atraso))
        delays.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in delays]

    @classmethod
    def _preparar_sorteios_rapidos(cls, sorteios_orm) -> List[Dict[str, Any]]:
        out = []
        for s in sorteios_orm:
            pos = [int(n) for n in s.get_posicoes_lista()]
            ordem = [int(n) for n in s.get_ordem_sorteio_lista()]
            out.append({
                'concurso': s.concurso,
                'posicoes': pos,
                'ordem': ordem,
                'mask': cls._mask_nums(pos),
            })
        return out

    @classmethod
    def _precomputar_contexto_base(cls, s_rapido: Dict[str, Any], atrasos: List[int]) -> Dict[str, Any]:
        base_nums = list(s_rapido['ordem'])
        r_min, r_max = GeradorAtrasoPosicaoExperimentalService._calcular_faixa_offset(base_nums)
        linhas = []
        for r in range(r_min, r_max + 1):
            if r == 0:
                continue
            cells = []
            for idx, b in enumerate(base_nums):
                linear = b + r
                v_orig = GeradorAtrasoPosicaoService.dezena_ciclica(b, r)
                wrap = not (1 <= linear <= 31)
                cells.append((v_orig, wrap, idx))
            linhas.append((r, cells))
        return {
            'concurso': s_rapido['concurso'],
            'base_nums': base_nums,
            'atrasos_globais': atrasos,
            'linhas': linhas,
        }

    @classmethod
    def _finais_do_contexto(
        cls,
        ctx: Dict[str, Any],
        saltos_mais: List[int],
        saltos_menos: List[int],
        dezenas_por_jogo: int,
        usar_ajustada: bool,
    ) -> List[int]:
        """
        Mesma lógica da matriz experimental (FINAL / opcionalmente Ajustada),
        retorna só máscaras bit — para scoring walk-forward rápido.
        """
        atrasos = ctx['atrasos_globais']
        masks = []
        for r, cells in ctx['linhas']:
            esqueleto = []
            for v_orig, wrap, idx in cells:
                if not wrap:
                    esqueleto.append(v_orig)
                    continue
                salto = saltos_mais[idx] if r > 0 else saltos_menos[idx]
                if r > 0:
                    shift = int(salto) - 1
                else:
                    shift = 0 if int(salto) <= 1 else int(salto)
                if shift <= 0:
                    esqueleto.append(v_orig)
                else:
                    v = ((v_orig - 1 + shift) % 31) + 1
                    esqueleto.append(v)

            aposta_final, preenchimento = GeradorAtrasoPosicaoService._eliminar_repeticoes_linha(
                esqueleto, atrasos
            )

            if len(aposta_final) < dezenas_por_jogo:
                faltam = dezenas_por_jogo - len(aposta_final)
                candidatos = [n for n in atrasos if n not in aposta_final]
                for _ in range(faltam):
                    bx = sum(1 for n in aposta_final if n <= 10)
                    mx = sum(1 for n in aposta_final if 11 <= n <= 20)
                    ax = sum(1 for n in aposta_final if n >= 21)
                    if bx <= mx and bx <= ax:
                        faixa_alvo = 'baixo'
                    elif mx <= bx and mx <= ax:
                        faixa_alvo = 'medio'
                    else:
                        faixa_alvo = 'alto'
                    escolhido = None
                    for c in candidatos:
                        if GeradorEspecialService.classify_number(c) == faixa_alvo:
                            escolhido = c
                            break
                    if not escolhido and candidatos:
                        escolhido = candidatos[0]
                    if escolhido:
                        aposta_final.append(escolhido)
                        preenchimento.append(escolhido)
                        candidatos.remove(escolhido)

            aposta_final.sort()
            nums = aposta_final

            if usar_ajustada:
                aposta_ajustada = list(aposta_final)
                bx_adj = sum(1 for n in aposta_ajustada if n <= 10)
                mx_adj = sum(1 for n in aposta_ajustada if 11 <= n <= 20)
                ax_adj = sum(1 for n in aposta_ajustada if n >= 21)
                candidatos_ajuste = [n for n in atrasos if n not in aposta_ajustada]
                if bx_adj >= 4 or mx_adj >= 4 or ax_adj >= 4:
                    zonas = {'baixo': bx_adj, 'medio': mx_adj, 'alto': ax_adj}
                    trocas = 0
                    for i in range(len(aposta_ajustada) - 1, -1, -1):
                        n = aposta_ajustada[i]
                        zona_excesso = max(zonas, key=zonas.get)
                        zona_falta = min(zonas, key=zonas.get)
                        if GeradorEspecialService.classify_number(n) == zona_excesso and zonas[zona_excesso] > 3:
                            escolhido = None
                            for c in candidatos_ajuste:
                                if GeradorEspecialService.classify_number(c) == zona_falta:
                                    escolhido = c
                                    break
                            if escolhido:
                                aposta_ajustada.remove(n)
                                aposta_ajustada.append(escolhido)
                                candidatos_ajuste.remove(escolhido)
                                trocas += 1
                                zonas[zona_excesso] -= 1
                                zonas[zona_falta] += 1
                        if trocas >= 2 or max(zonas.values()) <= 3:
                            break
                aposta_ajustada.sort()
                nums = aposta_ajustada

            masks.append(cls._mask_nums(nums))
        return masks

    @classmethod
    def avaliar_walk_forward(
        cls,
        saltos_mais: List[int],
        saltos_menos: List[int],
        contextos: List[Dict[str, Any]],
        alvos_mask: List[int],
        dezenas_por_jogo: int,
        usar_ajustada: bool,
    ) -> Dict[str, Any]:
        """
        Para cada par i: gera a partir de contextos[i] e confere contra alvos_mask[i]
        (máscara do concurso seguinte).
        """
        total = len(contextos)
        if total == 0:
            return {
                'total_concursos': 0,
                'qtd_7': 0, 'qtd_6': 0, 'qtd_5': 0, 'qtd_4': 0,
                'media_acertos': 0.0,
                'percentual_sucesso': 0.0,
                'maior_seq_positiva': 0,
                'pior_seq': 0,
                'soma_acertos': 0,
                'score': 0.0,
            }

        qtd = {4: 0, 5: 0, 6: 0, 7: 0}
        soma = 0
        seq_pos = 0
        maior_seq = 0
        seq_seca = 0
        pior_seca = 0

        for ctx, dmask in zip(contextos, alvos_mask):
            masks = cls._finais_do_contexto(
                ctx, saltos_mais, saltos_menos, dezenas_por_jogo, usar_ajustada
            )
            best = 0
            for b in masks:
                h = (b & dmask).bit_count()
                if h > best:
                    best = h
                    if best == 7:
                        break
            soma += best
            if best in qtd:
                qtd[best] += 1
            if best >= 5:
                seq_pos += 1
                if seq_pos > maior_seq:
                    maior_seq = seq_pos
                seq_seca = 0
            else:
                seq_pos = 0
                seq_seca += 1
                if seq_seca > pior_seca:
                    pior_seca = seq_seca

        sucesso = qtd[5] + qtd[6] + qtd[7]
        score = (
            qtd[7] * ConferenciaHistoricaService.PESO_7_ACERTOS +
            qtd[6] * ConferenciaHistoricaService.PESO_6_ACERTOS +
            qtd[5] * ConferenciaHistoricaService.PESO_5_ACERTOS
        )
        return {
            'total_concursos': total,
            'qtd_7': qtd[7],
            'qtd_6': qtd[6],
            'qtd_5': qtd[5],
            'qtd_4': qtd[4],
            'media_acertos': round(soma / total, 4),
            'percentual_sucesso': round(100.0 * sucesso / total, 2),
            'maior_seq_positiva': maior_seq,
            'pior_seq': pior_seca,
            'soma_acertos': soma,
            'score': float(score),
        }

    @staticmethod
    def _serializar_apostas(resultado_geracao: Dict[str, Any], usar_ajustada: bool) -> List[Dict[str, Any]]:
        out = []
        for ap in resultado_geracao.get('apostas') or []:
            nums_final = list(ap.get('aposta_final_numeros') or [])
            nums_aj = list(ap.get('aposta_ajustada_numeros') or nums_final)
            nums = nums_aj if usar_ajustada else nums_final
            out.append({
                'linha_offset': ap.get('linha_offset'),
                'numeros': nums,
                'aposta_final_numeros': nums_final,
                'aposta_ajustada_numeros': nums_aj,
                'mes_num': ap.get('mes_num'),
                'mes_nome': ap.get('mes_nome'),
            })
        return out

    # -------------------------------------------------------------------------
    # Execução
    # -------------------------------------------------------------------------

    @classmethod
    def executar_busca(cls, job_id: str, app) -> None:
        with app.app_context():
            cls._executar_busca_interno(job_id)

    @classmethod
    def _atualizar(cls, job_id: str, **kwargs) -> bool:
        with cls._lock:
            job = cls._jobs.get(job_id)
            if not job:
                return False
            if job.get('cancelar'):
                job['status'] = 'cancelado'
                job['mensagem'] = 'Busca cancelada pelo usuário.'
                return False
            job.update(kwargs)
            return True

    @classmethod
    def _executar_busca_interno(cls, job_id: str) -> None:
        from models.sorteio import Sorteio

        with cls._lock:
            job = cls._jobs.get(job_id)
            if not job:
                return
            params = dict(job['params'])
            job['status'] = 'processando'
            job['mensagem'] = 'Preparando pares Base -> proximo…'

        try:
            concurso_base_id = params.get('concurso_base_id', 'ultimo')
            dezenas = int(params.get('dezenas_por_jogo', 7))
            mes_tipo = params.get('mes_tipo', 'sequencial')
            if mes_tipo == 'aleatorio':
                mes_tipo = 'sequencial'
            limite = int(params.get('limite_salto_max', 6))
            max_testes = int(params.get('max_testes', 1000))
            simetrico = bool(params.get('simetrico', True))
            modo = params.get('modo_busca', 'aleatorio')
            seed = params.get('seed')
            usar_ajustada = bool(params.get('usar_ajustada', False))
            janela = int(params.get('janela_concursos', 200))
            top_n = max(10, min(int(params.get('top_n', 50)), cls.TOP_GUARDAR_APOSTAS))
            # 'todos' | 'desde_base' — pares N→N+1 usados no ranking
            escopo = (params.get('escopo_percurso') or 'todos').lower()

            presets = cls.gerar_lista_presets(limite, max_testes, simetrico, modo, seed)
            total = len(presets)

            sorteios_orm = Sorteio.query.order_by(Sorteio.concurso).all()
            if len(sorteios_orm) < 2:
                cls._atualizar(job_id, status='erro', erro='Histórico insuficiente.',
                               mensagem='Erro: precisa de ao menos 2 concursos.')
                return

            rapidos = cls._preparar_sorteios_rapidos(sorteios_orm)

            if str(concurso_base_id) == 'ultimo':
                concurso_base = rapidos[-1]['concurso']
            else:
                concurso_base = int(concurso_base_id)

            # Índices dos pares (i = base, i+1 = gabarito)
            indices_pares = list(range(len(rapidos) - 1))
            if escopo == 'desde_base':
                indices_pares = [
                    i for i in indices_pares
                    if rapidos[i]['concurso'] >= concurso_base
                ]
                # Se a base escolhida é a última, não há pares à frente:
                # usa todo o histórico para aprender o preset.
                if not indices_pares:
                    indices_pares = list(range(len(rapidos) - 1))
                    escopo = 'todos_fallback'

            if janela > 0 and len(indices_pares) > janela:
                indices_pares = indices_pares[-janela:]

            if not indices_pares:
                cls._atualizar(job_id, status='erro', erro='Nenhum par Base→próximo.',
                               mensagem='Erro: sem pares para percorrer.')
                return

            if not cls._atualizar(
                job_id, total=total, testados=0, progresso=0,
                mensagem=f'Pre-computando {len(indices_pares)} pares Base->proximo…',
            ):
                return

            # Pré-computa contexto de cada base do walk-forward
            contextos = []
            alvos_mask = []
            for i in indices_pares:
                # atrasos como se estivéssemos no concurso i (últimos 150 até i)
                ini = max(0, i - 149)
                atrasos = cls._atrasos_globais_ate(rapidos[ini: i + 1])
                contextos.append(cls._precomputar_contexto_base(rapidos[i], atrasos))
                alvos_mask.append(rapidos[i + 1]['mask'])

            def chave_score(x: Dict[str, Any]) -> Tuple:
                return (x['score'], x['qtd_7'], x['qtd_6'], x['qtd_5'], x['media'])

            ranking_parcial: List[Dict[str, Any]] = []
            apostas_por_chave: Dict[Tuple, Dict[str, Any]] = {}
            top_apostas: Dict[int, Dict[str, Any]] = {}
            t0 = time.perf_counter()

            if not cls._atualizar(
                job_id,
                mensagem=f'Testando {total} presets x {len(indices_pares)} pares…',
            ):
                return

            for idx, (mais, menos) in enumerate(presets):
                if not cls._atualizar(job_id):
                    return

                met = cls.avaliar_walk_forward(
                    mais, menos, contextos, alvos_mask, dezenas, usar_ajustada
                )
                item = {
                    'rank': 0,
                    'preset': cls._fmt_preset(mais, menos),
                    'saltos_coluna': list(mais),
                    'saltos_coluna_menos': list(menos),
                    'score': met['score'],
                    'qtd_7': met['qtd_7'],
                    'qtd_6': met['qtd_6'],
                    'qtd_5': met['qtd_5'],
                    'qtd_4': met['qtd_4'],
                    'media': met['media_acertos'],
                    'total_concursos': met['total_concursos'],
                    'percentual': met['percentual_sucesso'],
                    'maior_seq_positiva': met['maior_seq_positiva'],
                    'pior_seq': met['pior_seq'],
                    'qtd_apostas': 0,
                    'concurso_base': concurso_base,
                }

                entra = (
                    len(ranking_parcial) < top_n
                    or chave_score(item) > chave_score(ranking_parcial[-1])
                )
                if entra:
                    # Apostas para export = geradas na BASE ESCOLHIDA (jogo real)
                    gerado = GeradorAtrasoPosicaoExperimentalService.gerar_apostas_atraso_posicao_experimental(
                        concurso_base_id=concurso_base_id,
                        quantidade=0,
                        dezenas_por_jogo=dezenas,
                        mes_selecionado=mes_tipo,
                        salto_modo='por_coluna',
                        salto_global=mais[0],
                        salto_global_menos=menos[0],
                        salto_simetrico=False,
                        saltos_coluna=mais,
                        saltos_coluna_menos=menos,
                        limite_salto_max=limite,
                    )
                    if gerado.get('sucesso'):
                        apostas_ser = cls._serializar_apostas(gerado, usar_ajustada)
                        item['qtd_apostas'] = len(apostas_ser)
                        item['concurso_base'] = gerado.get('concurso_base', concurso_base)
                        chave = cls._chave_preset(mais, menos)
                        apostas_por_chave[chave] = {
                            'saltos_coluna': list(mais),
                            'saltos_coluna_menos': list(menos),
                            'preset': item['preset'],
                            'usar_ajustada': usar_ajustada,
                            'concurso_base': gerado.get('concurso_base'),
                            'dezenas_base': gerado.get('dezenas_base'),
                            'apostas': apostas_ser,
                            'metricas': {k: item[k] for k in (
                                'score', 'qtd_7', 'qtd_6', 'qtd_5', 'qtd_4',
                                'media', 'total_concursos', 'percentual',
                                'maior_seq_positiva', 'pior_seq', 'qtd_apostas',
                            )},
                        }
                    ranking_parcial.append(item)
                    ranking_parcial.sort(key=chave_score, reverse=True)
                    ranking_parcial = ranking_parcial[:top_n]
                    chaves_vivas = {
                        cls._chave_preset(r['saltos_coluna'], r['saltos_coluna_menos'])
                        for r in ranking_parcial
                    }
                    for k in list(apostas_por_chave.keys()):
                        if k not in chaves_vivas:
                            del apostas_por_chave[k]

                testados = idx + 1
                progresso = int(testados / total * 100)
                if testados == total or testados % max(1, total // 40) == 0:
                    top_preview = []
                    for i, r in enumerate(ranking_parcial[:10], 1):
                        prev = dict(r)
                        prev['rank'] = i
                        top_preview.append(prev)
                    elapsed = time.perf_counter() - t0
                    rpm = testados / elapsed * 60 if elapsed > 0 else 0
                    cls._atualizar(
                        job_id,
                        testados=testados,
                        progresso=progresso,
                        ranking=top_preview,
                        mensagem=(
                            f'Testando {testados}/{total} presets ({progresso}%) · '
                            f'{len(indices_pares)} pares Base->proximo · {rpm:.0f}/min'
                        ),
                    )

            ranking_final = []
            for i, r in enumerate(ranking_parcial, 1):
                r = dict(r)
                r['rank'] = i
                ranking_final.append(r)
                chave = cls._chave_preset(r['saltos_coluna'], r['saltos_coluna_menos'])
                blob = apostas_por_chave.get(chave)
                if blob:
                    top_apostas[i] = blob

            elapsed = time.perf_counter() - t0
            stats = {
                'presets_testados': total,
                'concursos_analisados': len(indices_pares),
                'pares_base_proximo': len(indices_pares),
                'concurso_base': concurso_base,
                'primeiro_par': rapidos[indices_pares[0]]['concurso'],
                'ultimo_par_base': rapidos[indices_pares[-1]]['concurso'],
                'ultimo_par_alvo': rapidos[indices_pares[-1] + 1]['concurso'],
                'tempo_segundos': round(elapsed, 2),
                'simetrico': simetrico,
                'limite_salto_max': limite,
                'usar_ajustada': usar_ajustada,
                'modo_busca': modo,
                'modo_janela': 'base_x_proximo',
                'escopo_percurso': escopo,
            }

            with cls._lock:
                job = cls._jobs.get(job_id)
                if not job or job.get('cancelar'):
                    if job:
                        job['status'] = 'cancelado'
                    return
                job['status'] = 'concluido'
                job['progresso'] = 100
                job['testados'] = total
                job['ranking'] = ranking_final
                job['top_apostas'] = top_apostas
                job['estatisticas'] = stats
                job['mensagem'] = (
                    f'Concluido: {total} presets x {len(indices_pares)} pares '
                    f'Base->proximo em {elapsed:.1f}s.'
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            cls._atualizar(
                job_id,
                status='erro',
                erro=str(e),
                mensagem=f'Erro na busca: {e}',
            )

    @classmethod
    def iniciar_busca_background(cls, app, params: Dict[str, Any]) -> str:
        job_id = cls.criar_job(params)
        thread = threading.Thread(
            target=cls.executar_busca,
            args=(job_id, app),
            daemon=True,
        )
        thread.start()
        return job_id

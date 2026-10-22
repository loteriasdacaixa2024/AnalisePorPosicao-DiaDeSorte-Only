# -*- coding: utf-8 -*-
"""
Orquestrador [C] — ciclo AUTOMÁTICO pelas cards de #/inicio-bolao.

Fluxo:
  1) Login 1× (Entrar automático após senha)
  2) Abre inicio-bolao e LÊ os cards (modalidade + concurso)
  3) Sem confirmação — clica "Compre seu bolão" e extrai até o fim
  4) Aviso sonoro/voz → próxima modalidade (sem SIM / ENTER)
  5) Grava 1 JSON por modalidade — sem misturar
  6) Ao final: relatório + Excel + JSON consolidado
"""
from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from boloes_cards_inicio import (
    URL_INICIO_BOLAO,
    abrir_lista_do_card,
    ir_para_inicio_bolao,
    listar_cards_modalidades,
    ordenar_cards_por_prioridade,
)
from boloes_checkpoint_ciclo import (
    STATUS_AGUARDANDO,
    STATUS_ANDAMENTO,
    STATUS_CICLO_OK,
    STATUS_CICLO_PAUSA,
    STATUS_CICLO_EXEC,
    STATUS_CONCLUIDO,
    STATUS_ERRO,
    STATUS_PAUSADO,
    STATUS_PENDENTE,
    STATUS_VAZIO,
    atualizar_modalidade,
    atualizar_uf,
    calcular_resumo,
    hidratar_ciclo_com_jsons,
    modalidade_concluida_pelas_ufs,
    novo_ciclo,
    resolver_retomada_ciclo_automatica,
    salvar_ciclo,
    set_operacao,
    STATUS_CICLO_OCORRENCIAS,
)
from boloes_modalidades import MODALIDADES_MENU, modalidade_por_slug

UNIDADE_LISTA = 'LISTA'
LogFn = Callable[[str], None]


def _barra(pct: float, largura: int = 20) -> str:
    pct = max(0.0, min(100.0, float(pct)))
    cheios = int(round(largura * pct / 100.0))
    return '█' * cheios + '░' * (largura - cheios)


def _ufs_dos_boloes(boloes: list) -> List[str]:
    return sorted({
        str(b.get('uf') or '').upper()
        for b in (boloes or [])
        if str(b.get('uf') or '').strip()
    })


def imprimir_painel_ciclo(ciclo: Dict[str, Any], out_fn: LogFn = print, ordem_slugs: Optional[List[str]] = None) -> None:
    res = ciclo.get('resumo') or calcular_resumo(ciclo)
    mods = ciclo.get('modalidades') or {}
    total = len(mods) or 1
    feitos = sum(
        1 for m in mods.values()
        if str(m.get('status') or '') in (STATUS_CONCLUIDO, STATUS_VAZIO, STATUS_ERRO)
    )
    pct = 100.0 * feitos / total

    out_fn('')
    out_fn('=' * 64)
    out_fn('  CICLO COMPLETO — AUTOMÁTICO (cards inicio-bolao)')
    out_fn('  Ordem: 1º Dia de Sorte → 2º maior premiação nos cards')
    out_fn('  1 JSON por modalidade | sem filtro UF | SEM POPUP')
    out_fn('=' * 64)
    out_fn(f'  Status     : {ciclo.get("status")}')
    out_fn(f'  Modalidade : {ciclo.get("modalidade_atual") or "—"}')
    out_fn(f'  Operação   : {ciclo.get("operacao") or "—"}')
    out_fn(f'  Progresso  : {_barra(pct)} {pct:.0f}%  ({feitos}/{total} modalidades)')
    out_fn(f'  Bolões≈    : {res.get("boloes_total", 0)} | Erros: {res.get("erros", 0)}')
    out_fn('-' * 64)
    slugs = list(ordem_slugs) if ordem_slugs else list(mods.keys())
    for slug in slugs:
        if slug not in mods:
            continue
        mod = mods[slug]
        st = str(mod.get('status') or STATUS_AGUARDANDO)
        label = mod.get('label') or slug
        lista = (mod.get('ufs') or {}).get(UNIDADE_LISTA) or {}
        pag = int(lista.get('pagina_atual') or 0)
        n = int(lista.get('boloes') or 0)
        conc = mod.get('concurso') or ''
        ufs_txt = mod.get('ufs_encontradas') or ''
        extra = f'pág {pag} | {n} bolões'
        if conc:
            extra += f' | conc {conc}'
        if ufs_txt:
            extra += f' | UFs: {ufs_txt}'
        out_fn(f'  {label:<28} {st:<14} {extra}')
    out_fn('=' * 64)


def imprimir_resumo_final(ciclo: Dict[str, Any], out_fn: LogFn = print) -> None:
    res = calcular_resumo(ciclo)
    inicio = ciclo.get('inicio') or ''
    fim = ciclo.get('fim') or ''
    out_fn('')
    out_fn('=' * 64)
    out_fn('  EXTRAÇÃO COMPLETA — RESUMO')
    out_fn('=' * 64)
    out_fn(f'  Início : {inicio}')
    out_fn(f'  Fim    : {fim}')
    if inicio and fim:
        try:
            t0 = datetime.strptime(inicio, '%Y-%m-%d %H:%M:%S')
            t1 = datetime.strptime(fim, '%Y-%m-%d %H:%M:%S')
            secs = int((t1 - t0).total_seconds())
            h, rem = divmod(secs, 3600)
            m, s = divmod(rem, 60)
            out_fn(f'  Duração: {h:02d}:{m:02d}:{s:02d}')
        except Exception:
            pass
    out_fn(f'  Modalidades concluídas : {res.get("modalidades_ok")}')
    out_fn(f'  Bolões                 : {res.get("boloes_total")}')
    out_fn(f'  Erros / pendências     : {res.get("erros")} / {res.get("ufs_pendente")}')
    out_fn('=' * 64)


def _garantir_unidade_lista(ciclo: Dict[str, Any], slug: str, label: str) -> None:
    mods = ciclo.setdefault('modalidades', {})
    if slug not in mods:
        mods[slug] = {
            'label': label,
            'status': STATUS_AGUARDANDO,
            'concurso': '',
            'arquivo_base': '',
            'ufs': {},
            'ufs_encontradas': '',
            'inicio': '',
            'fim': '',
        }
    else:
        mods[slug]['label'] = label or mods[slug].get('label') or slug
    ufs = mods[slug].setdefault('ufs', {})
    for k in list(ufs.keys()):
        if k != UNIDADE_LISTA:
            ufs.pop(k, None)
    if UNIDADE_LISTA not in ufs:
        ufs[UNIDADE_LISTA] = {
            'status': STATUS_AGUARDANDO,
            'pagina_atual': 0,
            'total_paginas': 0,
            'boloes': 0,
            'tentativas': 0,
            'erro': '',
            'atualizado_em': '',
        }


def _mod_de_card(card: dict):
    mod = card.get('mod')
    if mod is not None:
        return mod
    return modalidade_por_slug(str(card.get('slug') or ''))


def _proximo_card_pendente(cards: List[dict], ciclo: Dict[str, Any], idx_atual: int):
    for card in cards[idx_atual:]:
        mod = _mod_de_card(card)
        if mod is None:
            continue
        st = str((ciclo.get('modalidades') or {}).get(mod.slug, {}).get('status') or '')
        if st not in (STATUS_CONCLUIDO, STATUS_VAZIO):
            return mod
    return None


def _avisar_inicio_modalidade(label: str, out_fn: LogFn) -> None:
    try:
        from boloes_avisos import avisar_nova_modalidade
        avisar_nova_modalidade(label, out_fn=out_fn)
    except Exception:
        out_fn(f'\n  🔔 NOVA MODALIDADE — {label}')


def _avisar_fim_modalidade(label: str, out_fn: LogFn) -> None:
    try:
        from boloes_avisos import avisar_modalidade_concluida
        avisar_modalidade_concluida(label, out_fn=out_fn)
    except Exception:
        out_fn(f'\n  🔔 MODALIDADE CONCLUÍDA — {label}')


def _continuar_apos_falha(label: str, out_fn: LogFn, motivo: str = '') -> None:
    out_fn(f'  [ERRO] {label}')
    if motivo:
        out_fn(f'  [ERRO] {motivo}')
    out_fn('  [AVISO] Modalidade não concluída.')
    out_fn('  [INFO] Continuando para a próxima modalidade.')
    try:
        from boloes_avisos import avisar_modalidade_erro
        avisar_modalidade_erro(label, out_fn=out_fn)
    except Exception:
        pass


def _imprimir_resumo_da_modalidade(ciclo: Dict[str, Any], slug: str, pasta: str, out_fn: LogFn) -> None:
    try:
        from boloes_relatorio_execucao import coletar_linhas_modalidades, imprimir_resumo_modalidade
        linhas = coletar_linhas_modalidades(ciclo, pasta, [slug])
        if linhas:
            imprimir_resumo_modalidade(linhas[0], out_fn=out_fn)
    except Exception as exc:
        out_fn(f'  [RELATÓRIO] Aviso ao montar resumo da modalidade: {exc}')


def _gerar_entregaveis(ciclo: Dict[str, Any], pasta: str, ordem_slugs: List[str], out_fn: LogFn, pausado: bool) -> None:
    try:
        from boloes_relatorio_execucao import gerar_entregaveis_finais
        gerar_entregaveis_finais(
            pasta, ciclo, ordem_slugs, out_fn=out_fn, pausado=pausado,
        )
    except Exception as exc:
        out_fn(f'  [RELATÓRIO] Falha ao gerar Excel/consolidado: {exc}')
        imprimir_resumo_final(ciclo, out_fn)


def executar_ciclo_completo(
    api,
    *,
    modalidades_slugs: Optional[List[str]] = None,
    out_fn: LogFn = print,
) -> Dict[str, Any]:
    """
    Login 1× → lê cards → abre lista e extrai até o fim (sem SIM/ENTER).
    """
    pasta = api.PASTA_JSON
    wanted = None
    if modalidades_slugs:
        wanted = {s.strip().lower() for s in modalidades_slugs if s and str(s).strip()}

    continuar, ciclo_existente = resolver_retomada_ciclo_automatica(pasta, out_fn=out_fn)

    if continuar and ciclo_existente:
        ciclo = ciclo_existente
        ciclo['status'] = STATUS_CICLO_EXEC
    else:
        out_fn('')
        out_fn('  CICLO AUTOMÁTICO (sem intervenção):')
        out_fn('  — App abre inicio-bolao e lê os cards (modalidade + concurso)')
        out_fn('  — Clica Compre seu bolão e extrai até o fim')
        out_fn('  — Ao terminar uma modalidade, inicia a próxima sozinho')
        out_fn('  — 1 JSON por modalidade | sem misturar | sem SIM/ENTER')
        # Placeholder; modalidades reais vêm dos cards após login
        seed = list(MODALIDADES_MENU)
        ciclo = novo_ciclo(
            [{'slug': m.slug, 'label': m.label} for m in seed],
            [UNIDADE_LISTA],
        )
        ciclo['modo'] = 'cards-auto'
        ciclo['concurso_inicial'] = ''

    hidratar_ciclo_com_jsons(pasta, ciclo, out_fn=out_fn)
    salvar_ciclo(pasta, ciclo)

    if getattr(api, 'driver', None) is None:
        if not api.iniciar_navegador():
            ciclo['status'] = STATUS_CICLO_PAUSA
            set_operacao(ciclo, operacao='Falha ao abrir navegador')
            salvar_ciclo(pasta, ciclo)
            return ciclo

    from boloes_pasta_bds import detectar_lista_boloes_aberta
    lista_inicio = detectar_lista_boloes_aberta(api.driver)

    # Continuar com a lista já aberta: NÃO volta ao hub (senão perde a página e mistura arquivo)
    if continuar and lista_inicio and lista_inicio.get('slug'):
        out_fn(
            f'  [CICLO] Continuar: site já em {lista_inicio["label"]} '
            f'conc {lista_inicio.get("concurso") or "?"} — mantém esta lista.'
        )
        cards = []
    else:
        # 1) Hub de cards (Bolões) — ainda SEM extrair
        try:
            if not ir_para_inicio_bolao(api.driver, log_fn=out_fn, espera=3.0):
                api.driver.get(getattr(api, 'URL_BOLOES', URL_INICIO_BOLAO))
                time.sleep(2)
        except Exception:
            pass
        cards = listar_cards_modalidades(api.driver, log_fn=out_fn)

    if wanted:
        cards = [c for c in cards if c['slug'] in wanted or c.get('parser_slug') in wanted]
    if not cards and ciclo.get('modalidades'):
        for slug, m in (ciclo.get('modalidades') or {}).items():
            cards.append({
                'slug': slug,
                'label': m.get('label') or slug,
                'concurso': str(m.get('concurso') or ''),
            })
        if cards:
            out_fn('  [CICLO] Cards do checkpoint (lista já estava aberta ou hub vazio).')
    # Ordem de prioridade (Dia de Sorte → maior premiação), sem mudar o fluxo
    if cards:
        cards = ordenar_cards_por_prioridade(cards)
    if lista_inicio and lista_inicio.get('slug'):
        # Continuar: mantém a lista já aberta na frente; o restante segue a prioridade
        slug_pri = lista_inicio['slug']
        cards = [c for c in cards if c.get('slug') == slug_pri] + [
            c for c in cards if c.get('slug') != slug_pri
        ]
        if lista_inicio.get('concurso'):
            atualizar_modalidade(ciclo, slug_pri, concurso=str(lista_inicio['concurso']))
    if not cards:
        out_fn('  [CICLO] Nenhum card reconhecido em inicio-bolao.')
        out_fn('  Abra Bolões no Edge (inicio-bolao) ou a lista da modalidade e rode [C] de novo.')
        ciclo['status'] = STATUS_CICLO_PAUSA
        set_operacao(ciclo, operacao='Sem cards')
        salvar_ciclo(pasta, ciclo)
        return ciclo

    ordem_slugs: List[str] = []
    for card in cards:
        slug = card['slug']
        label = card['label']
        ordem_slugs.append(slug)
        _garantir_unidade_lista(ciclo, slug, label)
        if card.get('concurso'):
            atualizar_modalidade(ciclo, slug, concurso=str(card['concurso']))
    if not continuar:
        extras = [s for s in list((ciclo.get('modalidades') or {}).keys()) if s not in ordem_slugs]
        for s in extras:
            ciclo['modalidades'].pop(s, None)

    salvar_ciclo(pasta, ciclo)
    imprimir_painel_ciclo(ciclo, out_fn, ordem_slugs=ordem_slugs)

    # 3) Sem confirmação — cards já detectados, segue sozinho
    out_fn('\n  [AUTO] Cards detectados — iniciando extração sem SIM/ENTER.')
    if not api.garantir_sessao_ciclo(out_fn):
        ciclo['status'] = STATUS_CICLO_PAUSA
        set_operacao(ciclo, operacao='Sessão/login indisponível no início do ciclo')
        salvar_ciclo(pasta, ciclo)
        return ciclo
    api.SESSAO_AUTORIZADA = True

    from boloes_pasta_bds import detectar_lista_boloes_aberta
    lista_aberta = detectar_lista_boloes_aberta(api.driver)
    if lista_aberta and lista_aberta.get('slug') and continuar:
        out_fn(
            f'  [CICLO] Lista já aberta no site: {lista_aberta["label"]} '
            f'conc {lista_aberta.get("concurso") or "?"} — continua neste JSON, sem voltar ao hub.'
        )
        slug_pri = lista_aberta['slug']
        cards = ordenar_cards_por_prioridade(cards)
        cards = [c for c in cards if c.get('slug') == slug_pri] + [
            c for c in cards if c.get('slug') != slug_pri
        ]
        ordem_slugs = [c['slug'] for c in cards]
        if lista_aberta.get('concurso'):
            atualizar_modalidade(ciclo, slug_pri, concurso=str(lista_aberta['concurso']))
        salvar_ciclo(pasta, ciclo)
    else:
        # Volta ao hub (usuário pode ter navegado no Edge durante a pausa)
        if not ir_para_inicio_bolao(api.driver, log_fn=out_fn, espera=2.0):
            ciclo['status'] = STATUS_CICLO_PAUSA
            set_operacao(ciclo, operacao='Falha ao reabrir inicio-bolao')
            salvar_ciclo(pasta, ciclo)
            return ciclo

        # Re-lê cards no hub (site pode ter mudado)
        cards_pos = listar_cards_modalidades(api.driver, log_fn=out_fn)
        if wanted and cards_pos:
            cards_pos = [c for c in cards_pos if c['slug'] in wanted or c.get('parser_slug') in wanted]
        if cards_pos:
            cards = cards_pos
            ordem_slugs = []
            for card in cards:
                slug = card['slug']
                label = card['label']
                ordem_slugs.append(slug)
                _garantir_unidade_lista(ciclo, slug, label)
                if card.get('concurso'):
                    atualizar_modalidade(ciclo, slug, concurso=str(card['concurso']))
            salvar_ciclo(pasta, ciclo)

    out_fn('\n  [AUTO] Clicando Compre seu bolão e extraindo automaticamente...')
    imprimir_painel_ciclo(ciclo, out_fn, ordem_slugs=ordem_slugs)

    pausado = False
    total = len(cards)
    for idx, card in enumerate(cards, start=1):
        if pausado:
            break
        mod = _mod_de_card(card)
        if mod is None:
            out_fn(f'  [CICLO] Card sem modalidade: {card!r}')
            continue
        slug = mod.slug
        _garantir_unidade_lista(ciclo, slug, mod.label)
        lista = ciclo['modalidades'][slug]['ufs'][UNIDADE_LISTA]
        st_lista = str(lista.get('status') or '')
        pag_lista = int(lista.get('pagina_atual') or 0)
        tot_lista = int(lista.get('total_paginas') or 0)
        # Wrap falso marcava CONCLUÍDO com páginas ainda na API (ex.: 8/9 com pág. 10 no site)
        if (
            st_lista == STATUS_CONCLUIDO
            and pag_lista > 0
            and tot_lista > 0
            and pag_lista < tot_lista
        ):
            out_fn(
                f'  [CICLO] {mod.label} estava CONCLUÍDO cedo demais '
                f'(pág. {pag_lista}/{tot_lista}) — reabre para continuar.'
            )
            atualizar_uf(
                ciclo, slug, UNIDADE_LISTA,
                status=STATUS_PENDENTE, pagina_atual=pag_lista,
                total_paginas=tot_lista,
                erro='parcial — wrap/fim aparente com páginas restantes',
            )
            atualizar_modalidade(ciclo, slug, status=STATUS_PENDENTE)
            ciclo['modalidades'][slug]['fim'] = ''
            salvar_ciclo(pasta, ciclo)
            st_lista = STATUS_PENDENTE
            lista = ciclo['modalidades'][slug]['ufs'][UNIDADE_LISTA]
        if st_lista in (STATUS_CONCLUIDO, STATUS_VAZIO):
            out_fn(f'  [CICLO] {mod.label} já ok — pulando.')
            continue

        conc_mod = str(card.get('concurso') or ciclo['modalidades'][slug].get('concurso') or '')
        if conc_mod:
            atualizar_modalidade(ciclo, slug, concurso=conc_mod)

        atualizar_modalidade(ciclo, slug, status=STATUS_ANDAMENTO, marcar_inicio=True)
        set_operacao(
            ciclo,
            modalidade=slug,
            uf=UNIDADE_LISTA,
            operacao=f'Auto card — {mod.label} ({idx}/{total})',
        )
        atualizar_uf(ciclo, slug, UNIDADE_LISTA, status=STATUS_ANDAMENTO, incrementar_tentativa=True)
        salvar_ciclo(pasta, ciclo)
        imprimir_painel_ciclo(ciclo, out_fn, ordem_slugs=ordem_slugs)

        out_fn('')
        out_fn('=' * 64)
        out_fn(f'  {idx}/{total} — {mod.label} | conc {conc_mod or "?"} | AUTO')
        from boloes_modalidades import nome_arquivo_sessao
        arq_prev = nome_arquivo_sessao(conc_mod or 'sem-concurso', mod)
        out_fn(f'  Arquivo destino: json-boloes/{arq_prev}.json')
        out_fn('=' * 64)
        _avisar_inicio_modalidade(mod.label, out_fn)

        # Troca de modalidade: Caixa costuma expirar / Edge cair após longas extrações.
        out_fn('  [SESSÃO] Conferindo Edge/login antes de abrir o card...')
        if not api.garantir_sessao_ciclo(out_fn):
            atualizar_uf(
                ciclo, slug, UNIDADE_LISTA,
                status=STATUS_PENDENTE, pagina_atual=pag_lista,
                boloes=int(lista.get('boloes') or 0),
                erro='sessão Caixa/Edge indisponível na troca de modalidade',
            )
            atualizar_modalidade(ciclo, slug, status=STATUS_PENDENTE)
            ciclo['status'] = STATUS_CICLO_PAUSA
            set_operacao(ciclo, operacao='Pausa — sessão expirada (troca de modalidade)')
            salvar_ciclo(pasta, ciclo)
            out_fn(
                '  [SESSÃO] Não recuperou login/Edge. '
                'Ciclo PAUSADO (PENDENTE). Rode [C] → Continuar após login.'
            )
            pausado = True
            break

        ok_lista = False
        try:
            ok_lista = abrir_lista_do_card(
                api.driver,
                label=mod.label,
                concurso=conc_mod,
                slug=slug,
                log_fn=out_fn,
            )
        except Exception as exc_abrir:
            out_fn(f'  [SESSÃO] Erro ao abrir lista: {exc_abrir}')
            if api._erro_indica_janela_morta(exc_abrir) or not api._janela_edge_viva():
                out_fn('  [SESSÃO] Edge morreu ao abrir lista — recuperando e tentando de novo...')
                if api.garantir_sessao_ciclo(out_fn):
                    try:
                        ok_lista = abrir_lista_do_card(
                            api.driver,
                            label=mod.label,
                            concurso=conc_mod,
                            slug=slug,
                            log_fn=out_fn,
                        )
                    except Exception as exc2:
                        out_fn(f'  [SESSÃO] 2ª tentativa falhou: {exc2}')
                        ok_lista = False

        if not ok_lista:
            out_fn(
                f'  [SESSÃO] Lista de {mod.label} não abriu (0 Detalhes / sessão). '
                f'Recuperando login e tentando 1×...'
            )
            if api.garantir_sessao_ciclo(out_fn):
                try:
                    ok_lista = abrir_lista_do_card(
                        api.driver,
                        label=mod.label,
                        concurso=conc_mod,
                        slug=slug,
                        log_fn=out_fn,
                    )
                except Exception as exc_retry:
                    out_fn(f'  [SESSÃO] Retry falhou: {exc_retry}')
                    ok_lista = False

        if not ok_lista:
            # PENDENTE (não ERRO): [C] Continuar reabre estas modalidades.
            janela_ok = api._janela_edge_viva()
            atualizar_uf(
                ciclo, slug, UNIDADE_LISTA,
                status=STATUS_PENDENTE, pagina_atual=pag_lista,
                boloes=int(lista.get('boloes') or 0),
                erro='falha ao abrir lista (sessão/site)',
            )
            atualizar_modalidade(ciclo, slug, status=STATUS_PENDENTE)
            salvar_ciclo(pasta, ciclo)
            if not janela_ok:
                ciclo['status'] = STATUS_CICLO_PAUSA
                set_operacao(ciclo, operacao='Pausa — Edge fechou na troca de modalidade')
                salvar_ciclo(pasta, ciclo)
                out_fn(
                    f'  [CICLO] Edge fechado — {mod.label} PENDENTE. '
                    f'Ciclo PAUSADO (não marca as demais como ERRO).'
                )
                pausado = True
                break
            _continuar_apos_falha(mod.label, out_fn, 'falha ao abrir lista (sessão/site)')
            continue

        conferida = detectar_lista_boloes_aberta(api.driver)
        if conferida and conferida.get('slug') and conferida['slug'] != slug:
            out_fn(
                f'  [CICLO] Site está em {conferida["label"]}, esperado {mod.label}. '
                f'Não extrai — evitaria gravar no arquivo errado.'
            )
            atualizar_uf(
                ciclo, slug, UNIDADE_LISTA,
                status=STATUS_PENDENTE, pagina_atual=pag_lista,
                boloes=int(lista.get('boloes') or 0),
                erro='lista de outra modalidade aberta',
            )
            atualizar_modalidade(ciclo, slug, status=STATUS_PENDENTE)
            salvar_ciclo(pasta, ciclo)
            _continuar_apos_falha(mod.label, out_fn, 'lista de outra modalidade aberta')
            continue

        out_fn(
            f'\n  [AUTO] Lista aberta: {mod.label} conc {conc_mod or "?"} — '
            f'extraindo sem confirmação.'
        )
        api.SESSAO_AUTORIZADA = True

        # Retomada: só pula página se JÁ existir JSON desta modalidade com dados.
        # Modalidade nova → sempre página 1 (não herda pág. 4 de checkpoint errado).
        pagina_ini = None
        from boloes_modalidades import nome_arquivo_sessao
        arq_mod = nome_arquivo_sessao(conc_mod or 'sem-concurso', mod)
        path_mod = os.path.join(pasta, f'{arq_mod}.json')
        n_arq = 0
        try:
            from boloes_consolidar import carregar_json_boloes
            if os.path.isfile(path_mod):
                n_arq = len(carregar_json_boloes(path_mod))
        except Exception:
            n_arq = 0
        if (
            st_lista in (STATUS_ANDAMENTO, STATUS_PAUSADO, STATUS_PENDENTE)
            and n_arq > 0
            and pag_lista > 0
        ):
            pagina_ini = max(1, int(pag_lista) + 1)
            out_fn(
                f'  [CICLO] Retoma {mod.label} na pág. {pagina_ini} '
                f'(JSON tem {n_arq} bolões).'
            )
        else:
            out_fn(
                f'  [CICLO] {mod.label} começa na pág. 1 — '
                f'arquivo {arq_mod}.json '
                + ('será criado agora.' if n_arq == 0 else f'já tem {n_arq} reg.')
            )

        try:
            boloes_final, ab, painel = api._extrair_como_opcao_1(
                mod,
                conc_mod,
                rodada_filtro=idx,
                forcar_pagina_inicial=pagina_ini,
                sem_popup=True,
            )
        except Exception as exc:
            if api._erro_indica_janela_morta(exc) or not api._janela_edge_viva():
                atualizar_uf(
                    ciclo, slug, UNIDADE_LISTA,
                    status=STATUS_PENDENTE, pagina_atual=pag_lista,
                    boloes=int(lista.get('boloes') or 0),
                    erro=f'Edge/sessão caiu: {exc}',
                )
                atualizar_modalidade(ciclo, slug, status=STATUS_PENDENTE)
                ciclo['status'] = STATUS_CICLO_PAUSA
                set_operacao(ciclo, operacao='Pausa — Edge fechou durante extração')
                salvar_ciclo(pasta, ciclo)
                out_fn(
                    f'  [SESSÃO] Edge/sessão caiu em {mod.label}. '
                    f'Ciclo PAUSADO (PENDENTE). [C] → Continuar após login.'
                )
                api.SESSAO_AUTORIZADA = False
                pausado = True
                break
            atualizar_uf(ciclo, slug, UNIDADE_LISTA, status=STATUS_ERRO, erro=str(exc))
            atualizar_modalidade(ciclo, slug, status=STATUS_ERRO, marcar_fim=True)
            salvar_ciclo(pasta, ciclo)
            _continuar_apos_falha(mod.label, out_fn, str(exc))
            _imprimir_resumo_da_modalidade(ciclo, slug, pasta, out_fn)
            api.SESSAO_AUTORIZADA = False
            continue

        if ab:
            atualizar_modalidade(ciclo, slug, arquivo_base=ab)
        conc = (painel or {}).get('concurso_alvo') or conc_mod
        if conc:
            atualizar_modalidade(ciclo, slug, concurso=conc)

        paginas = int((painel or {}).get('paginas_processadas') or 0)
        total_pag = int(((painel or {}).get('paginacao_api') or {}).get('ultima_pagina') or 0)
        n_boloes = len(boloes_final or [])
        path_json = os.path.join(pasta, f'{(ab or "x")}.json')
        try:
            from boloes_consolidar import carregar_json_boloes
            disco = carregar_json_boloes(path_json)
            n_boloes = max(n_boloes, len(disco))
            ufs_found = _ufs_dos_boloes(disco or boloes_final)
        except Exception:
            ufs_found = _ufs_dos_boloes(boloes_final)
        if ufs_found:
            ciclo['modalidades'][slug]['ufs_encontradas'] = ', '.join(ufs_found)

        if bool((painel or {}).get('pausado_operador')):
            atualizar_uf(
                ciclo, slug, UNIDADE_LISTA,
                status=STATUS_PAUSADO, pagina_atual=paginas,
                total_paginas=total_pag, boloes=n_boloes,
            )
            atualizar_modalidade(ciclo, slug, status=STATUS_PAUSADO)
            ciclo['status'] = STATUS_CICLO_PAUSA
            set_operacao(ciclo, operacao='Pausado pelo operador')
            salvar_ciclo(pasta, ciclo)
            pausado = True
            break

        if (painel or {}).get('uf_concluida') or (painel or {}).get('chegou_ao_fim'):
            st = STATUS_VAZIO if (paginas <= 0 and n_boloes <= 0) else STATUS_CONCLUIDO
            atualizar_uf(
                ciclo, slug, UNIDADE_LISTA,
                status=st, pagina_atual=paginas,
                total_paginas=total_pag, boloes=n_boloes,
            )
            atualizar_modalidade(ciclo, slug, status=st, marcar_fim=True)
            out_fn(f'\n  [OK] {mod.label} concluída → JSON isolado.')
            _imprimir_resumo_da_modalidade(ciclo, slug, pasta, out_fn)
            _avisar_fim_modalidade(mod.label, out_fn)
        elif paginas <= 0 and n_boloes <= 0:
            atualizar_uf(
                ciclo, slug, UNIDADE_LISTA,
                status=STATUS_PENDENTE, pagina_atual=0, boloes=0,
                erro='lista vazia',
            )
            atualizar_modalidade(ciclo, slug, status=STATUS_PENDENTE)
            _continuar_apos_falha(mod.label, out_fn, 'lista vazia')
            _imprimir_resumo_da_modalidade(ciclo, slug, pasta, out_fn)
        else:
            atualizar_uf(
                ciclo, slug, UNIDADE_LISTA,
                status=STATUS_PENDENTE, pagina_atual=paginas,
                total_paginas=total_pag, boloes=n_boloes,
                erro='parcial',
            )
            atualizar_modalidade(ciclo, slug, status=STATUS_PENDENTE)
            _continuar_apos_falha(mod.label, out_fn, 'parcial')
            _imprimir_resumo_da_modalidade(ciclo, slug, pasta, out_fn)

        salvar_ciclo(pasta, ciclo)
        imprimir_painel_ciclo(ciclo, out_fn, ordem_slugs=ordem_slugs)
        api.SESSAO_AUTORIZADA = False

        # Limpa capturas da modalidade anterior (evita misturar +Milionária etc.)
        try:
            from boloes_api_caixa import limpar_capturas_api
            limpar_capturas_api(api.driver)
        except Exception:
            pass

        # Volta ao hub com sessão viva antes da próxima modalidade
        out_fn('  [SESSÃO] Voltando ao hub / conferindo login para a próxima...')
        if not api.garantir_sessao_ciclo(out_fn):
            ciclo['status'] = STATUS_CICLO_PAUSA
            set_operacao(ciclo, operacao='Pausa — sessão caiu após modalidade')
            salvar_ciclo(pasta, ciclo)
            out_fn(
                '  [SESSÃO] Sessão caiu após a modalidade. '
                'Ciclo PAUSADO — [C] Continuar após login.'
            )
            pausado = True
            break
        try:
            ir_para_inicio_bolao(api.driver, log_fn=out_fn, espera=2.0)
        except Exception as exc_hub:
            out_fn(f'  [SESSÃO] Aviso ao voltar ao hub: {exc_hub}')
            if api._erro_indica_janela_morta(exc_hub) or not api._janela_edge_viva():
                if not api.garantir_sessao_ciclo(out_fn):
                    ciclo['status'] = STATUS_CICLO_PAUSA
                    set_operacao(ciclo, operacao='Pausa — Edge fechou no hub')
                    salvar_ciclo(pasta, ciclo)
                    pausado = True
                    break
                try:
                    ir_para_inicio_bolao(api.driver, log_fn=out_fn, espera=2.0)
                except Exception:
                    pass

    if not pausado:
        todas_ok = True
        for slug in ordem_slugs:
            st = str(ciclo['modalidades'].get(slug, {}).get('status') or '')
            if st != STATUS_CONCLUIDO:
                if modalidade_concluida_pelas_ufs(ciclo, slug):
                    atualizar_modalidade(ciclo, slug, status=STATUS_CONCLUIDO, marcar_fim=True)
                else:
                    todas_ok = False
        from boloes_checkpoint_ciclo import agora_iso
        ciclo['fim'] = agora_iso()
        ciclo['status'] = STATUS_CICLO_OK if todas_ok else STATUS_CICLO_OCORRENCIAS
        set_operacao(ciclo, modalidade='', uf='', operacao='Finalizado')
        salvar_ciclo(pasta, ciclo)
        _gerar_entregaveis(ciclo, pasta, ordem_slugs, out_fn, pausado=False)
        try:
            from boloes_avisos import avisar_ciclo_finalizado
            avisar_ciclo_finalizado(ciclo.get('status') or '', out_fn=out_fn)
        except Exception:
            pass
    else:
        from boloes_checkpoint_ciclo import agora_iso
        if not ciclo.get('fim'):
            ciclo['fim'] = agora_iso()
        salvar_ciclo(pasta, ciclo)
        out_fn('\n  [CICLO] Pausado (sessão/Edge). Relatório parcial será gerado.')
        _gerar_entregaveis(ciclo, pasta, ordem_slugs, out_fn, pausado=True)

    return ciclo

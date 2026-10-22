# -*- coding: utf-8 -*-
"""
Diagnóstico de paginação API × interface visual da Caixa.

A extração NÃO deve usar o número visual como fonte da verdade.
Este módulo só formata mensagens e detecta divergência.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _int_ou_none(v: Any) -> Optional[int]:
    if v is None or v == '':
        return None
    try:
        n = int(v)
        return n if n > 0 else None
    except (TypeError, ValueError):
        return None


def divergencia_paginacao(
    pagina_api: Any,
    pagina_visual: Any,
    *,
    tolerancia: int = 0,
) -> bool:
    """True se a barra visual e a API mostram páginas diferentes."""
    api = _int_ou_none(pagina_api)
    ui = _int_ou_none(pagina_visual)
    if api is None or ui is None:
        return False
    return abs(api - ui) > int(tolerancia)


def linhas_divergencia_paginacao(
    pagina_api: Any = None,
    ultima_api: Any = None,
    pagina_visual: Any = None,
) -> List[str]:
    api = _int_ou_none(pagina_api)
    ultima = _int_ou_none(ultima_api)
    ui = _int_ou_none(pagina_visual)
    api_txt = f'{api}/{ultima}' if api and ultima else (str(api) if api else '?')
    return [
        '  [INFO] Paginação visual da interface diverge da paginação da API.',
        '  [INFO] Extração continuará utilizando a paginação da API.',
        f'  [INFO] Visual: página {ui or "?"} | API: página {api_txt}.',
    ]


def formatar_monitor_consistencia(
    *,
    modalidade: str = '',
    concurso: str = '',
    estado: str = '',
    pagina_api: Any = None,
    ultima_api: Any = None,
    registros_recebidos: Any = 0,
    total_acumulado: Any = 0,
    arquivo: str = '',
    tamanho_kb: Any = None,
    pagina_visual: Any = None,
    total_registros_api: Any = None,
) -> List[str]:
    """Bloco de diagnóstico pedido para o terminal (fonte da verdade = API + JSON)."""
    pa = _int_ou_none(pagina_api)
    up = _int_ou_none(ultima_api)
    api_txt = f'{pa}/{up}' if pa and up else (str(pa) if pa else '?')
    tam = ''
    if tamanho_kb is not None:
        try:
            tam = f'{float(tamanho_kb):.1f} KB'
        except (TypeError, ValueError):
            tam = str(tamanho_kb)

    linhas = [
        '  ------------------------------------------------------------',
        f'  [MODALIDADE] {modalidade or "—"}',
        f'  [CONCURSO] {concurso or "—"}',
        f'  [ESTADO] {estado or "—"}',
        f'  [API] Página {api_txt}',
        f'  [REGISTROS RECEBIDOS] {int(registros_recebidos or 0)}',
        f'  [TOTAL ACUMULADO] {int(total_acumulado or 0)}',
        f'  [ARQUIVO] {arquivo or "—"}',
        f'  [TAMANHO] {tam or "—"}',
    ]
    if total_registros_api not in (None, ''):
        linhas.append(f'  [API TOTAL] {total_registros_api} bolões (metadado da lista)')
    ui = _int_ou_none(pagina_visual)
    if divergencia_paginacao(pa, ui):
        linhas.extend(linhas_divergencia_paginacao(pa, up, ui))
    linhas.append('  ------------------------------------------------------------')
    return linhas


def extrair_ufs_texto(boloes: Optional[List[dict]]) -> str:
    ufs = sorted({
        str(b.get('uf') or '').upper()
        for b in (boloes or [])
        if str(b.get('uf') or '').strip()
    })
    return ', '.join(ufs)


def resumo_paginacao_painel(painel: Optional[Dict[str, Any]], pagina: int) -> Tuple[Optional[int], Optional[int], Any]:
    meta = (painel or {}).get('paginacao_api') or {}
    pa = _int_ou_none(meta.get('pagina_atual')) or pagina
    up = _int_ou_none(meta.get('ultima_pagina'))
    return pa, up, meta.get('total_registros')

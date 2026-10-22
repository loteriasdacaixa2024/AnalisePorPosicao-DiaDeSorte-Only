# -*- coding: utf-8 -*-
"""
Avisos sonoros e por voz (Windows) — nunca controlam o fluxo.

Som e fala rodam em segundo plano. Falha de áudio é ignorada.
"""
from __future__ import annotations

import subprocess
import threading
from typing import Optional

_lock = threading.Lock()


def _em_fundo(fn) -> threading.Thread:
    t = threading.Thread(target=fn, daemon=True, name='aviso-extracao')
    t.start()
    return t


def aviso_sonoro(tipo: str = 'ok') -> None:
    """Beep nativo do Windows. tipo: ok | nova | erro | fim."""

    def _tocar() -> None:
        try:
            import winsound
            if tipo == 'nova':
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                for freq, dur in ((988, 140), (1175, 220)):
                    winsound.Beep(freq, dur)
            elif tipo == 'erro':
                winsound.MessageBeep(winsound.MB_ICONHAND)
                winsound.Beep(440, 280)
            elif tipo == 'fim':
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                for freq, dur in ((784, 160), (988, 160), (1175, 280), (1318, 360)):
                    winsound.Beep(freq, dur)
            else:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                for freq, dur in ((784, 160), (988, 160), (1175, 320)):
                    winsound.Beep(freq, dur)
        except Exception:
            try:
                print('\a', end='', flush=True)
            except Exception:
                pass

    _em_fundo(_tocar)


def _escapar_ps(texto: str) -> str:
    return (texto or '').replace("'", "''")[:280]


def _falar_sapi(texto: str) -> None:
    frase = (texto or '').strip()
    if not frase:
        return
    safe = _escapar_ps(frase)
    cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate = 1; "
        f"$s.Speak('{safe}');"
    )
    flags = 0
    flags |= int(getattr(subprocess, 'CREATE_NO_WINDOW', 0) or 0)
    try:
        subprocess.Popen(
            ['powershell', '-NoProfile', '-WindowStyle', 'Hidden', '-Command', cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
    except Exception:
        pass


def aviso_voz(texto: str) -> None:
    """Síntese de voz do Windows em segundo plano. Não bloqueia."""
    frase = (texto or '').strip()
    if not frase:
        return
    _em_fundo(lambda: _falar_sapi(frase))


def avisar_modalidade_concluida(label: str, out_fn=print) -> None:
    nome = (label or 'modalidade').strip() or 'modalidade'
    try:
        out_fn(f'\n  🔔 MODALIDADE CONCLUÍDA — {nome}')
    except Exception:
        pass
    aviso_sonoro('ok')
    aviso_voz(f'A extração da modalidade {nome} foi concluída.')


def avisar_nova_modalidade(label: str, out_fn=print) -> None:
    nome = (label or 'modalidade').strip() or 'modalidade'
    try:
        out_fn(f'\n  🔔 NOVA MODALIDADE — {nome}')
    except Exception:
        pass
    aviso_sonoro('nova')
    aviso_voz(f'A extração da modalidade {nome} está iniciando.')


def avisar_modalidade_erro(label: str, out_fn=print) -> None:
    nome = (label or 'modalidade').strip() or 'modalidade'
    try:
        out_fn(f'\n  🔔 [ERRO] {nome}')
    except Exception:
        pass
    aviso_sonoro('erro')
    aviso_voz(f'A modalidade {nome} apresentou erro. Continuando para a próxima.')


def avisar_ciclo_finalizado(status: str = '', out_fn=print) -> None:
    try:
        out_fn('\n  🔔 EXTRAÇÃO FINALIZADA')
    except Exception:
        pass
    aviso_sonoro('fim')
    extra = f' Status: {status}.' if status else ''
    aviso_voz(f'A extração de todas as modalidades foi finalizada.{extra}')


def aviso_disponivel() -> dict:
    """Diagnóstico simples (testes / painel)."""
    win = False
    try:
        import winsound  # noqa: F401
        win = True
    except Exception:
        win = False
    return {'winsound': win, 'voz': True}

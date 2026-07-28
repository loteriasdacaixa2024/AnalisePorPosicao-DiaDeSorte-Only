# -*- coding: utf-8 -*-
"""Laboratório de Alterações — lógica de diversificação e conferência."""

import json
import random
from typing import Any, Dict, List, Optional

from models.sorteio import Sorteio
from models.laboratorio_alteracoes import LaboratorioAlteracoesRegistro
from models.shared import db

MESES_NOME = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}

MAX_APOSTAS = 10
MAX_APOSTAS_EXPANDIDO = 100
MAX_DEZENAS_CONCURSO_POR_APOSTA = 2
MIN_DEZENAS_APOSTA = 7
MIN_TROCAS_ABSOLUTO = 3
FAIXA_BAIXA = range(1, 11)
FAIXA_MEDIA = range(11, 21)
FAIXA_ALTA = range(21, 32)


class LaboratorioAlteracoesService:
    MAX_APOSTAS = MAX_APOSTAS
    MAX_APOSTAS_EXPANDIDO = MAX_APOSTAS_EXPANDIDO
    MAX_DEZENAS_CONCURSO_POR_APOSTA = MAX_DEZENAS_CONCURSO_POR_APOSTA

    _MES_TOKEN = {
        'jan': 1, 'janeiro': 1,
        'fev': 2, 'fevereiro': 2,
        'mar': 3, 'marco': 3, 'março': 3,
        'abr': 4, 'abril': 4,
        'mai': 5, 'maio': 5,
        'jun': 6, 'junho': 6,
        'jul': 7, 'julho': 7,
        'ago': 8, 'agosto': 8,
        'set': 9, 'setembro': 9,
        'out': 10, 'outubro': 10,
        'nov': 11, 'novembro': 11,
        'dez': 12, 'dezembro': 12,
    }

    @staticmethod
    def _parse_mes_valor(mes: Any) -> Optional[int]:
        if mes is None or mes == '':
            return None
        if isinstance(mes, int):
            return mes if 1 <= mes <= 12 else None
        if isinstance(mes, str):
            s = mes.strip().lower()
            if s.isdigit():
                n = int(s)
                return n if 1 <= n <= 12 else None
            import unicodedata
            s = unicodedata.normalize('NFD', s)
            s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
            return LaboratorioAlteracoesService._MES_TOKEN.get(s)
        try:
            n = int(mes)
            return n if 1 <= n <= 12 else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def normalizar_aposta(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not raw:
            return None
        nums = raw.get('numeros') or raw.get('dezenas') or []
        if isinstance(nums, str):
            nums = [int(x) for x in nums.replace(',', ' ').split() if str(x).strip().isdigit()]
        else:
            nums = [int(n) for n in nums if n is not None and str(n).strip().isdigit()]
        nums = sorted({n for n in nums if 1 <= n <= 31})
        if len(nums) < 7:
            return None
        mes = (
            LaboratorioAlteracoesService._parse_mes_valor(raw.get('mes'))
            or LaboratorioAlteracoesService._parse_mes_valor(raw.get('mes_sorte'))
            or LaboratorioAlteracoesService._parse_mes_valor(raw.get('mes_nome'))
        )
        return {'numeros': nums[:15], 'mes': mes}

    @staticmethod
    def limitar_apostas(lista: List[Dict], limite: Optional[int] = None) -> List[Dict]:
        cap = limite if limite is not None else MAX_APOSTAS
        cap = min(max(1, int(cap)), MAX_APOSTAS_EXPANDIDO)
        out = []
        for item in lista:
            if len(out) >= cap:
                break
            norm = LaboratorioAlteracoesService.normalizar_aposta(item)
            if norm:
                out.append(norm)
        return out

    @staticmethod
    def sorteio_para_dict(sorteio: Sorteio) -> Dict[str, Any]:
        return {
            'concurso': sorteio.concurso,
            'data_sorteio': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else None,
            'numeros': sorteio.get_posicoes_lista(),
            'mes_sorte': sorteio.mes_sorte,
            'mes_nome': sorteio.get_nome_mes(),
            'valor_premio_7': getattr(sorteio, 'valor_premio_7_acertos', None),
            'valor_premio_6': getattr(sorteio, 'valor_premio_6_acertos', None),
        }

    @staticmethod
    def obter_concurso(concurso_num: Optional[int] = None) -> Optional[Dict]:
        try:
            if concurso_num:
                s = Sorteio.query.filter_by(concurso=concurso_num).first()
            else:
                s = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
        except Exception:
            return None
        if not s:
            return None
        return LaboratorioAlteracoesService.sorteio_para_dict(s)

    @staticmethod
    def listar_concursos_recentes(limite: int = 80) -> List[Dict]:
        try:
            rows = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(limite).all()
        except Exception:
            return []
        return [
            {
                'concurso': s.concurso,
                'data': s.data_sorteio.strftime('%d/%m/%Y') if s.data_sorteio else '',
                'label': f"#{s.concurso} ({s.data_sorteio.strftime('%d/%m/%Y') if s.data_sorteio else '—'})",
            }
            for s in rows
        ]

    @staticmethod
    def _faixa_dezena(n: int) -> str:
        if n in FAIXA_BAIXA:
            return 'baixa'
        if n in FAIXA_MEDIA:
            return 'media'
        return 'alta'

    @staticmethod
    def conferir_aposta(aposta: Dict, resultado: Dict) -> Dict[str, Any]:
        nums = aposta.get('numeros') or []
        sorteados = set(resultado.get('numeros') or [])
        acertos = len([n for n in nums if n in sorteados])
        mes_ap = aposta.get('mes')
        mes_res = resultado.get('mes_sorte')
        mes_ok = mes_ap is not None and mes_res is not None and int(mes_ap) == int(mes_res)
        return {
            'acertos_dezenas': acertos,
            'mes_acertou': bool(mes_ok),
            'faixa_destaque': acertos >= 6,
            'premiada': acertos >= 4,
        }

    @staticmethod
    def _pool_por_faixa(excluir: set) -> Dict[str, List[int]]:
        pools = {'baixa': [], 'media': [], 'alta': []}
        for n in range(1, 32):
            if n in excluir:
                continue
            pools[LaboratorioAlteracoesService._faixa_dezena(n)].append(n)
        return pools

    @staticmethod
    def _contar_dezenas_do_concurso(numeros: List[int], numeros_concurso: set) -> int:
        if not numeros_concurso:
            return 0
        return sum(1 for n in numeros if n in numeros_concurso)

    @staticmethod
    def _pode_incluir_dezena(n: int, escolhidas: List[int], numeros_concurso: set) -> bool:
        if n in escolhidas:
            return False
        if n in numeros_concurso:
            return (
                LaboratorioAlteracoesService._contar_dezenas_do_concurso(escolhidas, numeros_concurso)
                < MAX_DEZENAS_CONCURSO_POR_APOSTA
            )
        return True

    @staticmethod
    def _sortear_mes_alterado(mes_original: Optional[int], fixar_mes: bool = False) -> int:
        """Apostas alteradas devem ter mês diferente da original (exceto híbrido com mês travado)."""
        if fixar_mes and mes_original is not None:
            return int(mes_original)
        opcoes = [m for m in range(1, 13) if m != mes_original]
        return random.choice(opcoes or list(range(1, 13)))

    @staticmethod
    def _limitar_fixas_concurso(fixas: List[int], numeros_concurso: set) -> List[int]:
        if not numeros_concurso:
            return fixas
        out: List[int] = []
        conc = 0
        for n in sorted(fixas):
            if n in numeros_concurso:
                if conc >= MAX_DEZENAS_CONCURSO_POR_APOSTA:
                    continue
                conc += 1
            out.append(n)
        return out

    @staticmethod
    def _qtd_alvo_aposta(original_nums: List[int]) -> int:
        """Mesma quantidade colada na original (mín. 7 na importação)."""
        return len(original_nums or [])

    @staticmethod
    def _garantir_qtd_exata(
        numeros: List[int],
        qtd_alvo: int,
        numeros_concurso: set,
        preferir_manter: Optional[set] = None,
    ) -> List[int]:
        preferir_manter = preferir_manter or set()
        nums = LaboratorioAlteracoesService._enforcar_limite_concurso(
            numeros, numeros_concurso, preferir_manter, qtd_alvo=qtd_alvo,
        )
        nums = sorted({n for n in nums if 1 <= n <= 31})
        while len(nums) > qtd_alvo:
            removiveis = [n for n in nums if n not in preferir_manter]
            if not removiveis:
                removiveis = nums[:]
            nums.remove(random.choice(removiveis))
        while len(nums) < qtd_alvo:
            cand = LaboratorioAlteracoesService._candidatos_fora_aposta(
                set(nums), nums, numeros_concurso,
            )
            if not cand:
                break
            nums.append(random.choice(cand))
            nums = sorted(set(nums))
        return sorted(nums)[:qtd_alvo]

    @staticmethod
    def _ajustar_concurso_por_delta(
        numeros: List[int],
        qtd_alvo: int,
        numeros_concurso: set,
        preferir_manter: Optional[set] = None,
    ) -> List[int]:
        preferir_manter = preferir_manter or set()
        nums = sorted({n for n in numeros if 1 <= n <= 31})
        for _ in range(12):
            if (
                LaboratorioAlteracoesService._contar_dezenas_do_concurso(nums, numeros_concurso)
                <= MAX_DEZENAS_CONCURSO_POR_APOSTA
            ):
                return nums
            excesso = [n for n in nums if n in numeros_concurso and n not in preferir_manter]
            if not excesso:
                excesso = [n for n in nums if n in numeros_concurso]
            if not excesso:
                break
            n = random.choice(excesso)
            ajustou = False
            for delta in (1, -1, 2, -2):
                novo = n + delta
                if novo < 1 or novo > 31 or novo in nums:
                    continue
                alt = sorted([x for x in nums if x != n] + [novo])
                if LaboratorioAlteracoesService._validar_aposta_alterada(alt, qtd_alvo, numeros_concurso):
                    nums = alt
                    ajustou = True
                    break
            if not ajustou:
                break
        return nums

    @staticmethod
    def _finalizar_aposta_alterada(
        numeros: List[int],
        qtd_alvo: int,
        numeros_concurso: set,
        preferir_manter: Optional[set] = None,
    ) -> List[int]:
        preferir_manter = preferir_manter or set()
        nums = sorted({n for n in numeros if 1 <= n <= 31})
        if LaboratorioAlteracoesService._validar_aposta_alterada(nums, qtd_alvo, numeros_concurso):
            return nums
        nums = LaboratorioAlteracoesService._ajustar_concurso_por_delta(
            nums, qtd_alvo, numeros_concurso, preferir_manter,
        )
        if LaboratorioAlteracoesService._validar_aposta_alterada(nums, qtd_alvo, numeros_concurso):
            return nums
        return LaboratorioAlteracoesService._garantir_qtd_exata(
            nums, qtd_alvo, numeros_concurso, preferir_manter,
        )

    @staticmethod
    def _enforcar_limite_concurso(
        numeros: List[int],
        numeros_concurso: set,
        preferir_manter: Optional[set] = None,
        qtd_alvo: Optional[int] = None,
    ) -> List[int]:
        if not numeros_concurso:
            return sorted(numeros)
        preferir_manter = preferir_manter or set()
        nums = sorted({n for n in numeros if 1 <= n <= 31})
        do_concurso = [n for n in nums if n in numeros_concurso]
        if len(do_concurso) <= MAX_DEZENAS_CONCURSO_POR_APOSTA:
            return nums
        manter: List[int] = []
        for n in do_concurso:
            if n in preferir_manter and len(manter) < MAX_DEZENAS_CONCURSO_POR_APOSTA:
                manter.append(n)
        for n in do_concurso:
            if n not in manter and len(manter) < MAX_DEZENAS_CONCURSO_POR_APOSTA:
                manter.append(n)
        remover = set(do_concurso) - set(manter)
        base = [n for n in nums if n not in remover]
        alvo = qtd_alvo if qtd_alvo is not None else len(nums)
        while len(base) < alvo:
            cand = LaboratorioAlteracoesService._candidatos_fora_aposta(
                set(base), base, numeros_concurso,
            )
            if not cand:
                break
            base.append(random.choice(cand))
        return sorted(base)

    @staticmethod
    def _candidatos_fora_aposta(
        excluir: set,
        escolhidas: List[int],
        numeros_concurso: set,
    ) -> List[int]:
        return [
            n for n in range(1, 32)
            if n not in excluir
            and LaboratorioAlteracoesService._pode_incluir_dezena(n, escolhidas, numeros_concurso)
        ]

    @staticmethod
    def _contar_dezenas_diferentes(orig: List[int], alt: List[int]) -> int:
        return len(set(orig) - set(alt))

    @staticmethod
    def _minimo_dezenas_trocadas(qtd_alvo: int, qtd_imutaveis: int = 0) -> int:
        livres = max(0, qtd_alvo - qtd_imutaveis)
        if livres <= 0:
            return 0
        metade = max(2, (livres + 1) // 2)
        if qtd_alvo >= MIN_DEZENAS_APOSTA:
            metade = max(MIN_TROCAS_ABSOLUTO, metade)
        return min(metade, livres)

    @staticmethod
    def _gerar_substituto(
        dezena_saida: int,
        escolhidas_parciais: List[int],
        orig_set: set,
        numeros_concurso: set,
        preferir: str,
    ) -> Optional[int]:
        base = set(escolhidas_parciais)
        if preferir == 'nova':
            candidatos = [n for n in range(1, 32) if n not in orig_set and n not in base]
            random.shuffle(candidatos)
        elif preferir == 'delta_p1':
            candidatos = [dezena_saida + 1]
        elif preferir == 'delta_m1':
            candidatos = [dezena_saida - 1]
        elif preferir == 'delta_p2':
            candidatos = [dezena_saida + 2]
        elif preferir == 'delta_m2':
            candidatos = [dezena_saida - 2]
        else:
            candidatos = [n for n in range(1, 32) if n not in base]
            random.shuffle(candidatos)

        for cand in candidatos:
            if cand < 1 or cand > 31 or cand in base:
                continue
            if LaboratorioAlteracoesService._pode_incluir_dezena(
                cand, escolhidas_parciais, numeros_concurso,
            ):
                return cand

        for modo in ('nova', 'delta_p1', 'delta_m1', 'delta_p2', 'delta_m2', 'aleatoria'):
            if modo == preferir:
                continue
            sub = LaboratorioAlteracoesService._gerar_substituto(
                dezena_saida, escolhidas_parciais, orig_set, numeros_concurso, modo,
            )
            if sub is not None:
                return sub
        return None

    @staticmethod
    def _reformular_aposta(
        orig_nums: List[int],
        qtd_alvo: int,
        numeros_concurso: set,
        indice_linha: int = 0,
        imutaveis: Optional[set] = None,
    ) -> Optional[List[int]]:
        """
        Remove várias dezenas da aposta original e entra com números novos.
        O substituto pode ser dezena nova (fora da original) ou deslocamento ±1/±2
        da dezena que saiu — mas sempre troca de fato, não só empurra a original.
        """
        imutaveis = imutaveis or set()
        nums = sorted({n for n in orig_nums if 1 <= n <= 31})
        if len(nums) != qtd_alvo or qtd_alvo < MIN_DEZENAS_APOSTA:
            return None
        orig_set = set(nums)
        qtd_trocar = LaboratorioAlteracoesService._minimo_dezenas_trocadas(
            qtd_alvo, len([n for n in nums if n in imutaveis]),
        )
        mutaveis = [n for n in nums if n not in imutaveis] or nums[:]
        qtd_trocar = max(1, min(qtd_trocar, len(mutaveis)))

        preferencias = [
            'nova', 'nova', 'nova', 'delta_p1', 'delta_m1', 'delta_p2', 'delta_m2', 'aleatoria',
        ]

        for tent in range(80):
            remover = random.sample(mutaveis, qtd_trocar)
            restante = [n for n in nums if n not in remover]
            parcial = list(restante)
            novos: List[int] = []
            falhou = False
            for j, n_out in enumerate(remover):
                pref = preferencias[(indice_linha + j + tent) % len(preferencias)]
                sub = LaboratorioAlteracoesService._gerar_substituto(
                    n_out, parcial, orig_set, numeros_concurso, pref,
                )
                if sub is None:
                    falhou = True
                    break
                novos.append(sub)
                parcial.append(sub)
            if falhou:
                continue
            alt = sorted(restante + novos)
            if (
                alt != nums
                and LaboratorioAlteracoesService._contar_dezenas_diferentes(nums, alt) >= qtd_trocar
                and LaboratorioAlteracoesService._validar_aposta_alterada(alt, qtd_alvo, numeros_concurso)
            ):
                return alt
        return None

    @staticmethod
    def _validar_aposta_alterada(nums: List[int], qtd_alvo: int, numeros_concurso: set) -> bool:
        if len(nums) != qtd_alvo or len(set(nums)) != qtd_alvo:
            return False
        if any(n < 1 or n > 31 for n in nums):
            return False
        return (
            LaboratorioAlteracoesService._contar_dezenas_do_concurso(nums, numeros_concurso)
            <= MAX_DEZENAS_CONCURSO_POR_APOSTA
        )

    @staticmethod
    def _aplicar_delta_valor(
        base: List[int],
        delta: int,
        qtd_alvo: int,
        numeros_concurso: set,
        qtd_dezenas: int = 1,
        imutaveis: Optional[set] = None,
    ) -> Optional[List[int]]:
        """
        Desloca o valor numérico de dezena(s) importada(s): ex. 10+1=11, 10-1=9.
        Mantém a mesma quantidade de dezenas na aposta.
        """
        imutaveis = imutaveis or set()
        nums = sorted({n for n in base if 1 <= n <= 31})
        if len(nums) != qtd_alvo:
            return None
        mutaveis = [n for n in nums if n not in imutaveis] or nums[:]
        qtd_dezenas = min(max(1, qtd_dezenas), len(mutaveis))

        candidatos_ordem = list(mutaveis)
        random.shuffle(candidatos_ordem)
        for _ in range(max(12, len(candidatos_ordem))):
            escolhidas = random.sample(candidatos_ordem, qtd_dezenas)
            substituicoes: Dict[int, int] = {}
            invalido = False
            for n in escolhidas:
                novo = n + delta
                if novo < 1 or novo > 31:
                    invalido = True
                    break
                if novo in set(nums) - {n}:
                    invalido = True
                    break
                if novo in substituicoes.values():
                    invalido = True
                    break
                substituicoes[n] = novo
            if invalido:
                random.shuffle(candidatos_ordem)
                continue
            alt = sorted((set(nums) - set(substituicoes.keys())) | set(substituicoes.values()))
            if (
                alt != nums
                and LaboratorioAlteracoesService._validar_aposta_alterada(alt, qtd_alvo, numeros_concurso)
            ):
                return alt
            random.shuffle(candidatos_ordem)

        for n in mutaveis:
            novo = n + delta
            if novo < 1 or novo > 31 or novo in nums:
                continue
            alt = sorted([x for x in nums if x != n] + [novo])
            if (
                alt != nums
                and LaboratorioAlteracoesService._validar_aposta_alterada(alt, qtd_alvo, numeros_concurso)
            ):
                return alt
        return None

    @staticmethod
    def _parse_estrategia_delta(estrategia: str) -> Optional[tuple]:
        mapa = {
            'delta_p1': (1, 1),
            'delta_p2': (2, 1),
            'delta_m1': (-1, 1),
            'delta_m2': (-2, 1),
            'delta_p1_x2': (1, 2),
            'delta_m2_x2': (-2, 2),
            'delta_m1_x2': (-1, 2),
        }
        return mapa.get(estrategia)

    @staticmethod
    def _estrategias_alteracao(indice_linha: int = 0) -> List[str]:
        """Prioriza deslocamento numérico (+1/+2/−1/−2); fallback: troca aleatória."""
        opcoes = [
            'delta_p1', 'delta_m1', 'delta_p2', 'delta_m2',
            'delta_p1_x2', 'delta_m1_x2', 'delta_m2_x2',
            'trocar_1', 'trocar_2',
        ]
        preferida = opcoes[indice_linha % len(opcoes)]
        return [preferida] + [e for e in opcoes if e != preferida]

    @staticmethod
    def _aplicar_trocas(
        base: List[int],
        qtd_trocar: int,
        numeros_concurso: set,
        qtd_alvo: int,
    ) -> Optional[List[int]]:
        if qtd_trocar <= 0:
            return None
        nums = sorted(set(base))
        if len(nums) != qtd_alvo:
            return None
        qtd_trocar = min(qtd_trocar, len(nums))
        remover = set(random.sample(nums, qtd_trocar))
        restante = [n for n in nums if n not in remover]
        excluir = set(restante) | remover
        cand = LaboratorioAlteracoesService._candidatos_fora_aposta(
            excluir, restante, numeros_concurso,
        )
        if len(cand) < qtd_trocar:
            return None
        novos = random.sample(cand, qtd_trocar)
        result = sorted(restante + novos)
        return result if len(result) == qtd_alvo else None

    @staticmethod
    def _mutar_dezenas(
        original_nums: List[int],
        numeros_concurso: set,
        estrategia: str,
        qtd_alvo: int,
        imutaveis: Optional[set] = None,
    ) -> Optional[List[int]]:
        nums = sorted({n for n in original_nums if 1 <= n <= 31})
        if len(nums) != qtd_alvo or qtd_alvo < MIN_DEZENAS_APOSTA:
            return None
        delta_info = LaboratorioAlteracoesService._parse_estrategia_delta(estrategia)
        if delta_info:
            delta, qtd_d = delta_info
            return LaboratorioAlteracoesService._aplicar_delta_valor(
                nums, delta, qtd_alvo, numeros_concurso, qtd_d, imutaveis,
            )
        if estrategia == 'trocar_1':
            return LaboratorioAlteracoesService._aplicar_trocas(nums, 1, numeros_concurso, qtd_alvo)
        if estrategia == 'trocar_2':
            return LaboratorioAlteracoesService._aplicar_trocas(nums, 2, numeros_concurso, qtd_alvo)
        if estrategia == 'trocar_3':
            return LaboratorioAlteracoesService._aplicar_trocas(nums, 3, numeros_concurso, qtd_alvo)
        return None

    @staticmethod
    def _mutar_dezenas_obrigatorio(
        original_nums: List[int],
        numeros_concurso: set,
        qtd_alvo: Optional[int] = None,
        imutaveis: Optional[set] = None,
        indice_linha: int = 0,
    ) -> List[int]:
        nums = sorted({n for n in original_nums if 1 <= n <= 31})
        qtd_alvo = qtd_alvo or len(nums)
        imutaveis = imutaveis or set()
        alt = LaboratorioAlteracoesService._reformular_aposta(
            nums, qtd_alvo, numeros_concurso, indice_linha, imutaveis,
        )
        if alt:
            return alt
        qtd_trocar = LaboratorioAlteracoesService._minimo_dezenas_trocadas(
            qtd_alvo, len([n for n in nums if n in imutaveis]),
        )
        for qt in range(qtd_trocar, 0, -1):
            t = LaboratorioAlteracoesService._aplicar_trocas(
                nums, qt, numeros_concurso, qtd_alvo,
            )
            if t and t != nums:
                return t
        return nums[:]

    @staticmethod
    def _sortear_dezenas(
        qtd: int,
        fixas: List[int],
        usados_globais: set,
        numeros_concurso: Optional[set] = None,
    ) -> List[int]:
        numeros_concurso = numeros_concurso or set()
        fixas = LaboratorioAlteracoesService._limitar_fixas_concurso(
            sorted({n for n in fixas if 1 <= n <= 31}),
            numeros_concurso,
        )
        excluir = set(fixas) | usados_globais
        pools = LaboratorioAlteracoesService._pool_por_faixa(excluir)
        escolhidas = list(fixas)
        ordem_faixas = ['baixa', 'media', 'alta']
        random.shuffle(ordem_faixas)
        while len(escolhidas) < qtd:
            progresso = False
            for fa in ordem_faixas:
                if len(escolhidas) >= qtd:
                    break
                cand = [
                    n for n in pools[fa]
                    if LaboratorioAlteracoesService._pode_incluir_dezena(n, escolhidas, numeros_concurso)
                ]
                if not cand:
                    continue
                n = random.choice(cand)
                escolhidas.append(n)
                pools[fa].remove(n)
                progresso = True
            if not progresso:
                rest = [
                    n for n in range(1, 32)
                    if LaboratorioAlteracoesService._pode_incluir_dezena(n, escolhidas, numeros_concurso)
                ]
                if not rest:
                    break
                escolhidas.append(random.choice(rest))
        return sorted(escolhidas[:qtd])

    @staticmethod
    def gerar_alterada(
        original: Dict,
        fixas_dezenas: Optional[List[int]] = None,
        fixar_mes: bool = False,
        usados_globais: Optional[set] = None,
        numeros_concurso: Optional[set] = None,
        indice_linha: int = 0,
    ) -> Dict:
        numeros_concurso = numeros_concurso or set()
        orig_nums = sorted({n for n in (original.get('numeros') or []) if 1 <= n <= 31})
        qtd_alvo = LaboratorioAlteracoesService._qtd_alvo_aposta(orig_nums)
        fixas = LaboratorioAlteracoesService._limitar_fixas_concurso(
            fixas_dezenas or [], numeros_concurso,
        )
        imutaveis = set(fixas)

        nums = LaboratorioAlteracoesService._reformular_aposta(
            orig_nums, qtd_alvo, numeros_concurso, indice_linha, imutaveis,
        )
        if not nums:
            if fixas:
                nums = LaboratorioAlteracoesService._sortear_dezenas(
                    qtd_alvo, fixas, set(), numeros_concurso,
                )
            else:
                nums = LaboratorioAlteracoesService._mutar_dezenas_obrigatorio(
                    orig_nums, numeros_concurso, qtd_alvo, imutaveis, indice_linha,
                )

        mes_orig = original.get('mes')
        mes = LaboratorioAlteracoesService._sortear_mes_alterado(mes_orig, fixar_mes)
        nums = LaboratorioAlteracoesService._finalizar_aposta_alterada(
            nums, qtd_alvo, numeros_concurso, imutaveis,
        )
        min_trocas = LaboratorioAlteracoesService._minimo_dezenas_trocadas(
            qtd_alvo, len([n for n in orig_nums if n in imutaveis]),
        )
        if (
            sorted(nums) == sorted(orig_nums)
            or LaboratorioAlteracoesService._contar_dezenas_diferentes(orig_nums, nums) < min_trocas
        ):
            nums = LaboratorioAlteracoesService._mutar_dezenas_obrigatorio(
                orig_nums, numeros_concurso, qtd_alvo, imutaveis, indice_linha,
            )
            nums = LaboratorioAlteracoesService._finalizar_aposta_alterada(
                nums, qtd_alvo, numeros_concurso, imutaveis,
            )
        return {'numeros': nums, 'mes': mes}

    @staticmethod
    def gerar_alteradas_lote(
        originais: List[Dict],
        modo: str = 'auto',
        fixas_por_linha: Optional[List[List[int]]] = None,
        fixar_mes_por_linha: Optional[List[bool]] = None,
        numeros_concurso: Optional[List[int]] = None,
    ) -> List[Dict]:
        concurso_set = set(numeros_concurso or [])
        alteradas = []
        usados = set()
        for i, orig in enumerate(originais):
            chave_orig = tuple(orig['numeros'])
            usados.add(chave_orig)
            fixas = (fixas_por_linha[i] if fixas_por_linha and i < len(fixas_por_linha) else []) if modo == 'hibrido' else []
            fixar_mes = (fixar_mes_por_linha[i] if fixar_mes_por_linha and i < len(fixar_mes_por_linha) else False) if modo == 'hibrido' else False
            qtd_alvo = LaboratorioAlteracoesService._qtd_alvo_aposta(orig['numeros'])
            min_trocas = LaboratorioAlteracoesService._minimo_dezenas_trocadas(
                qtd_alvo, len(fixas),
            )
            tentativas = 0
            alt = None
            while tentativas < 50:
                alt = LaboratorioAlteracoesService.gerar_alterada(
                    orig, fixas, fixar_mes, usados, concurso_set, indice_linha=i,
                )
                chave = tuple(alt['numeros'])
                ok_concurso = (
                    LaboratorioAlteracoesService._contar_dezenas_do_concurso(alt['numeros'], concurso_set)
                    <= MAX_DEZENAS_CONCURSO_POR_APOSTA
                )
                ok_trocas = (
                    LaboratorioAlteracoesService._contar_dezenas_diferentes(orig['numeros'], alt['numeros'])
                    >= min_trocas
                )
                nums_diferentes = chave != chave_orig and ok_trocas
                mes_diferente = (
                    not fixar_mes
                    and orig.get('mes') is not None
                    and alt.get('mes') is not None
                    and int(alt['mes']) != int(orig['mes'])
                )
                if nums_diferentes and chave not in usados and ok_concurso:
                    usados.add(chave)
                    break
                if not nums_diferentes and mes_diferente and ok_concurso:
                    usados.add(chave)
                    break
                tentativas += 1
            if not alt or tuple(alt['numeros']) == chave_orig:
                nums_forc = LaboratorioAlteracoesService._mutar_dezenas_obrigatorio(
                    orig['numeros'], concurso_set, qtd_alvo, set(fixas), i,
                )
                nums_forc = LaboratorioAlteracoesService._finalizar_aposta_alterada(
                    nums_forc, qtd_alvo, concurso_set,
                )
                mes_alt = LaboratorioAlteracoesService._sortear_mes_alterado(orig.get('mes'), fixar_mes)
                alt = {'numeros': nums_forc, 'mes': mes_alt}
            else:
                qtd_alvo = LaboratorioAlteracoesService._qtd_alvo_aposta(orig['numeros'])
                alt['numeros'] = LaboratorioAlteracoesService._finalizar_aposta_alterada(
                    alt['numeros'], qtd_alvo, concurso_set,
                )
            alteradas.append(alt)
        return alteradas

    @staticmethod
    def formatar_apostas_txt(apostas: List[Dict]) -> str:
        """Uma aposta por linha: dezenas + abreviatura do mês (ex.: 01 05 … Ago)."""
        linhas = []
        for ap in apostas or []:
            nums = ap.get('numeros') or []
            partes = [str(n).zfill(2) for n in sorted(nums)]
            mes = ap.get('mes')
            if mes and 1 <= int(mes) <= 12:
                nome = MESES_NOME.get(int(mes), '')
                token = nome[:3] if nome else str(mes)
                partes.append(token)
            linhas.append(' '.join(partes))
        return '\n'.join(linhas) + ('\n' if linhas else '')

    @staticmethod
    def montar_analise(
        originais: List[Dict],
        alteradas: List[Dict],
        resultado: Dict,
    ) -> Dict[str, Any]:
        linhas = []
        ranking = []
        for i, (orig, alt) in enumerate(zip(originais, alteradas)):
            co = LaboratorioAlteracoesService.conferir_aposta(orig, resultado)
            ca = LaboratorioAlteracoesService.conferir_aposta(alt, resultado)
            linhas.append({
                'indice': i + 1,
                'original': orig,
                'alterada': alt,
                'conf_orig': co,
                'conf_alt': ca,
            })
            ranking.append({
                'posicao': 0,
                'tipo': 'original',
                'indice': i + 1,
                'acertos': co['acertos_dezenas'],
                'mes_ok': co['mes_acertou'],
                'chave': f"O{i+1}",
            })
            ranking.append({
                'posicao': 0,
                'tipo': 'alterada',
                'indice': i + 1,
                'acertos': ca['acertos_dezenas'],
                'mes_ok': ca['mes_acertou'],
                'chave': f"A{i+1}",
            })
        ranking.sort(key=lambda x: (-x['acertos'], -int(x['mes_ok']), x['tipo'] == 'alterada'))
        for pos, r in enumerate(ranking, start=1):
            r['posicao'] = pos

        ac_o = [l['conf_orig']['acertos_dezenas'] for l in linhas]
        ac_a = [l['conf_alt']['acertos_dezenas'] for l in linhas]
        media_o = sum(ac_o) / len(ac_o) if ac_o else 0
        media_a = sum(ac_a) / len(ac_a) if ac_a else 0
        diff_pct = ((media_a - media_o) / media_o * 100) if media_o else (100 if media_a else 0)

        superaram = empataram = inferiores = 0
        for l in linhas:
            ao, aa = l['conf_orig']['acertos_dezenas'], l['conf_alt']['acertos_dezenas']
            if aa > ao:
                superaram += 1
            elif aa == ao:
                empataram += 1
            else:
                inferiores += 1

        melhor_o = max(linhas, key=lambda x: x['conf_orig']['acertos_dezenas']) if linhas else None
        melhor_a = max(linhas, key=lambda x: x['conf_alt']['acertos_dezenas']) if linhas else None

        return {
            'linhas': linhas,
            'ranking': ranking,
            'resumo': {
                'media_originais': round(media_o, 2),
                'media_alteradas': round(media_a, 2),
                'diferenca_percentual': round(diff_pct, 2),
                'evolucao': 'positiva' if media_a > media_o else ('negativa' if media_a < media_o else 'neutra'),
                'superaram': superaram,
                'empataram': empataram,
                'inferiores': inferiores,
                'premiadas_originais': sum(1 for l in linhas if l['conf_orig']['premiada']),
                'premiadas_alteradas': sum(1 for l in linhas if l['conf_alt']['premiada']),
                'melhor_original': melhor_o['indice'] if melhor_o else None,
                'melhor_alterada': melhor_a['indice'] if melhor_a else None,
            },
        }

    @staticmethod
    def json_para_persistencia(
        concurso_ref: int,
        origem: str,
        analise: Dict,
    ) -> str:
        payload = {
            'concurso_ref': concurso_ref,
            'origem': origem,
            'resumo': analise.get('resumo'),
            'linhas_acertos': [
                {
                    'indice': l['indice'],
                    'original': {
                        'acertos_dezenas': l['conf_orig']['acertos_dezenas'],
                        'mes_acertou': l['conf_orig']['mes_acertou'],
                        'faixa': l['conf_orig']['acertos_dezenas'],
                    },
                    'alterada': {
                        'acertos_dezenas': l['conf_alt']['acertos_dezenas'],
                        'mes_acertou': l['conf_alt']['mes_acertou'],
                        'faixa': l['conf_alt']['acertos_dezenas'],
                    },
                }
                for l in analise.get('linhas', [])
            ],
            'ranking_acertos': [
                {
                    'posicao': r['posicao'],
                    'tipo': r['tipo'],
                    'indice': r['indice'],
                    'acertos': r['acertos'],
                    'mes_ok': r['mes_ok'],
                }
                for r in analise.get('ranking', [])
            ],
        }
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def salvar_registro(concurso_ref: int, origem: str, analise: Dict) -> Dict:
        try:
            reg = LaboratorioAlteracoesRegistro(
                concurso_ref=concurso_ref,
                origem=origem or 'manual',
                dados_json=LaboratorioAlteracoesService.json_para_persistencia(concurso_ref, origem, analise),
            )
            db.session.add(reg)
            db.session.commit()
            return {'sucesso': True, 'id': reg.id}
        except Exception as e:
            db.session.rollback()
            return {'sucesso': False, 'erro': str(e)}

    @staticmethod
    def listar_historico(limite: int = 30) -> List[Dict]:
        try:
            rows = LaboratorioAlteracoesRegistro.query.order_by(
                LaboratorioAlteracoesRegistro.criado_em.desc()
            ).limit(limite).all()
        except Exception:
            return []
        out = []
        for r in rows:
            try:
                dados = json.loads(r.dados_json)
            except Exception:
                dados = {}
            out.append({
                'id': r.id,
                'criado_em': r.criado_em.strftime('%d/%m/%Y %H:%M') if r.criado_em else '',
                'concurso_ref': r.concurso_ref,
                'origem': r.origem,
                'resumo': dados.get('resumo'),
            })
        return out

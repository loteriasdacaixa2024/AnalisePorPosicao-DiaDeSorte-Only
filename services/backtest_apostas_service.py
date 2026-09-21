"""
Backtest das apostas da conferência atual contra sorteios anteriores do Dia de Sorte.

Não gera apostas novas e não altera apostas.json. Compara dezenas já cadastradas
com o histórico oficial (tabela sorteios), de forma vetorial em memória.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class BacktestApostasService:
    """Compara N apostas × N concursos anteriores e ranqueia os melhores desempenhos."""

    BASE_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'conferencia_apostas',
    )
    MAX_HITS_RETORNADOS = 5000

    @staticmethod
    def _parse_data(valor) -> Optional[datetime]:
        if not valor:
            return None
        if isinstance(valor, datetime):
            return valor
        texto = str(valor).strip()
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S'):
            try:
                return datetime.strptime(texto[:19] if 'T' in texto else texto, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def _ints(valores) -> List[int]:
        out = []
        for n in valores or []:
            try:
                out.append(int(n))
            except (TypeError, ValueError):
                continue
        return out

    @classmethod
    def normalizar_apostas(cls, apostas_raw: List[Dict]) -> List[Dict]:
        """Extrai número da aposta, dezenas e mês de estruturas JSON ou OCR."""
        normalizadas = []
        for idx, aposta in enumerate(apostas_raw or [], 1):
            if not isinstance(aposta, dict):
                continue
            if aposta.get('erro') or aposta.get('erro_ocr') or aposta.get('dados_incompletos'):
                continue
            extraidos = aposta.get('dados_extraidos') or {}
            numeros = cls._ints(
                aposta.get('numeros')
                or aposta.get('numeros_apostados')
                or extraidos.get('numeros_apostados')
                or aposta.get('dezenas')
            )
            if len(numeros) < 7:
                continue
            numero = aposta.get('numero_aposta') or aposta.get('numero') or aposta.get('indice') or idx
            try:
                numero = int(numero)
            except (TypeError, ValueError):
                numero = idx
            mes = (
                aposta.get('mes')
                or aposta.get('mes_apostado')
                or extraidos.get('mes_apostado')
            )
            normalizadas.append({
                'numero': numero,
                'numeros': numeros,
                'mes': mes,
            })
        return normalizadas

    @classmethod
    def carregar_apostas_pasta(cls, concurso: int) -> List[Dict]:
        caminho = os.path.join(cls.BASE_DIR, str(concurso), 'apostas.json')
        if not os.path.isfile(caminho):
            return []
        try:
            with open(caminho, 'r', encoding='utf-8') as fh:
                dados = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return []
        lista = dados.get('apostas', []) if isinstance(dados, dict) else dados
        return cls.normalizar_apostas(lista if isinstance(lista, list) else [])

    @classmethod
    def _normalizar_mes(cls, mes) -> Optional[int]:
        try:
            from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
            return ConferenciaApostasOCRService.normalizar_mes(mes)
        except Exception:
            try:
                n = int(mes)
                return n if 1 <= n <= 12 else None
            except (TypeError, ValueError):
                return None

    @classmethod
    def executar(
        cls,
        apostas: List[Dict],
        concurso_origem: Optional[int] = None,
        limite_concursos: Optional[int] = None,
        concurso_min: Optional[int] = None,
        concurso_max: Optional[int] = None,
        data_ini: Optional[str] = None,
        data_fim: Optional[str] = None,
        min_acertos: int = 3,
    ) -> Dict[str, Any]:
        from models.sorteio import Sorteio

        apostas_ok = cls.normalizar_apostas(apostas)
        if not apostas_ok and concurso_origem:
            apostas_ok = cls.carregar_apostas_pasta(int(concurso_origem))

        if not apostas_ok:
            return {
                'sucesso': False,
                'erro': 'sem_apostas',
                'mensagem': 'Nenhuma aposta válida encontrada na conferência atual.',
            }

        query = Sorteio.query
        if concurso_origem is not None:
            query = query.filter(Sorteio.concurso != int(concurso_origem))
        if concurso_min is not None:
            query = query.filter(Sorteio.concurso >= int(concurso_min))
        if concurso_max is not None:
            query = query.filter(Sorteio.concurso <= int(concurso_max))

        dt_ini = cls._parse_data(data_ini)
        dt_fim = cls._parse_data(data_fim)
        if dt_ini:
            query = query.filter(Sorteio.data_sorteio >= dt_ini.date())
        if dt_fim:
            query = query.filter(Sorteio.data_sorteio <= dt_fim.date())

        query = query.order_by(Sorteio.concurso.desc())
        if limite_concursos:
            query = query.limit(int(limite_concursos))

        sorteios = query.all()
        if not sorteios:
            return {
                'sucesso': False,
                'erro': 'sem_sorteios',
                'mensagem': 'Nenhum concurso anterior encontrado para o filtro informado.',
            }

        draws: List[Tuple[int, str, List[int], frozenset, int]] = []
        for sorteio in sorteios:
            nums = [int(n) for n in sorteio.get_posicoes_lista()]
            data_txt = sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else ''
            draws.append((
                int(sorteio.concurso),
                data_txt,
                nums,
                frozenset(nums),
                int(sorteio.mes_sorte) if sorteio.mes_sorte else 0,
            ))

        bets = []
        for aposta in apostas_ok:
            nums = [int(n) for n in aposta['numeros']]
            bets.append((
                int(aposta['numero']),
                nums,
                frozenset(nums),
                cls._normalizar_mes(aposta.get('mes')),
            ))

        min_hit = max(0, int(min_acertos or 0))
        n_apostas = len(bets)
        n_concursos = len(draws)
        n_comparacoes = n_apostas * n_concursos

        dist_geral = Counter()
        hits: List[Dict] = []
        por_concurso: Dict[int, Dict] = {}
        por_aposta: Dict[int, Dict] = {}

        for numero, nums_list, nums_set, mes_ap in bets:
            por_aposta[numero] = {
                'numero_aposta': numero,
                'numeros': sorted(nums_list),
                'mes': mes_ap,
                'melhor': 0,
                'soma': 0,
                'dist': Counter(),
                'top': [],
                'qtd_4': 0,
                'qtd_5': 0,
                'qtd_6': 0,
                'qtd_7': 0,
                'qtd_mes': 0,
            }

        for concurso, data_txt, sorteados, sorteados_set, mes_sorte in draws:
            melhor_local = -1
            melhores_apostas: List[int] = []
            for numero, nums_list, nums_set, mes_ap in bets:
                acertos = len(nums_set & sorteados_set)
                acertou_mes = bool(mes_ap and mes_sorte and mes_ap == mes_sorte)
                dist_geral[acertos] += 1

                info = por_aposta[numero]
                info['soma'] += acertos
                info['dist'][acertos] += 1
                if acertos >= 4:
                    info['qtd_4'] += 1
                if acertos >= 5:
                    info['qtd_5'] += 1
                if acertos >= 6:
                    info['qtd_6'] += 1
                if acertos >= 7:
                    info['qtd_7'] += 1
                if acertou_mes:
                    info['qtd_mes'] += 1

                acertados = sorted(nums_set & sorteados_set)
                if acertos > info['melhor']:
                    info['melhor'] = acertos
                info['top'].append((acertos, concurso, data_txt, sorted(sorteados), acertados, acertou_mes))
                if len(info['top']) > 12:
                    info['top'].sort(key=lambda t: (-t[0], -t[1]))
                    del info['top'][10:]

                if acertos > melhor_local:
                    melhor_local = acertos
                    melhores_apostas = [numero]
                elif acertos == melhor_local:
                    melhores_apostas.append(numero)

                if acertos >= min_hit:
                    hits.append({
                        'concurso': concurso,
                        'data': data_txt,
                        'numero_aposta': numero,
                        'acertos': acertos,
                        'dezenas_aposta': sorted(nums_list),
                        'dezenas_sorteadas': sorted(sorteados),
                        'dezenas_acertadas': acertados,
                        'acertou_mes': acertou_mes,
                    })

            por_concurso[concurso] = {
                'concurso': concurso,
                'data': data_txt,
                'dezenas_sorteadas': sorted(sorteados),
                'melhor_aposta': min(melhores_apostas) if melhores_apostas else None,
                'melhores_apostas': sorted(melhores_apostas),
                'melhor_pontuacao': max(melhor_local, 0),
                'qtd_com_melhor': len(melhores_apostas),
            }

        hits.sort(key=lambda h: (-h['acertos'], -h['concurso'], h['numero_aposta']))
        total_hits_qualificados = len(hits)
        hits_out = hits[: cls.MAX_HITS_RETORNADOS]
        for i, row in enumerate(hits_out, 1):
            row['classificacao'] = i

        ranking_concursos = sorted(
            por_concurso.values(),
            key=lambda c: (-c['melhor_pontuacao'], -c['qtd_com_melhor'], -c['concurso']),
        )
        for i, row in enumerate(ranking_concursos, 1):
            row['classificacao'] = i

        ranking_apostas = []
        for numero, info in por_aposta.items():
            top_ord = sorted(info['top'], key=lambda t: (-t[0], -t[1]))[:10]
            ranking_apostas.append({
                'numero_aposta': numero,
                'numeros': info['numeros'],
                'mes': info['mes'],
                'concursos_analisados': n_concursos,
                'melhor': info['melhor'],
                'media': round(info['soma'] / n_concursos, 3) if n_concursos else 0,
                'segundo': top_ord[1][0] if len(top_ord) > 1 else None,
                'terceiro': top_ord[2][0] if len(top_ord) > 2 else None,
                'qtd_4': info['qtd_4'],
                'qtd_5': info['qtd_5'],
                'qtd_6': info['qtd_6'],
                'qtd_7': info['qtd_7'],
                'qtd_mes': info['qtd_mes'],
                'dist': {str(k): int(v) for k, v in sorted(info['dist'].items())},
                'melhores': [
                    {
                        'acertos': t[0],
                        'concurso': t[1],
                        'data': t[2],
                        'dezenas_sorteadas': t[3],
                        'dezenas_acertadas': t[4],
                        'acertou_mes': t[5],
                    }
                    for t in top_ord[:5]
                ],
            })
        ranking_apostas.sort(key=lambda a: (-a['melhor'], -a['qtd_4'], -a['media'], a['numero_aposta']))

        melhor_geral = hits_out[0] if hits_out else None
        dist_out = {str(k): int(dist_geral.get(k, 0)) for k in range(0, 8)}
        for k, v in dist_geral.items():
            if k > 7:
                dist_out[str(k)] = int(v)

        return {
            'sucesso': True,
            'meta': {
                'concurso_origem': concurso_origem,
                'n_apostas': n_apostas,
                'n_concursos': n_concursos,
                'n_comparacoes': n_comparacoes,
                'min_acertos_tabela': min_hit,
                'total_hits_qualificados': total_hits_qualificados,
                'hits_retornados': len(hits_out),
                'concurso_mais_antigo': draws[-1][0] if draws else None,
                'concurso_mais_recente': draws[0][0] if draws else None,
            },
            'melhor_geral': melhor_geral,
            'distribuicao': dist_out,
            'ranking_hits': hits_out,
            'ranking_concursos': ranking_concursos,
            'ranking_apostas': ranking_apostas,
        }

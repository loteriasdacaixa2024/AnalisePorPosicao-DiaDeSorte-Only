from datetime import datetime
from typing import List, Set, Dict
from models.sorteio import Sorteio


class AnaliseSimulacaoReversaService:
    @staticmethod
    def _gerar_jogos(prev_nums: List[int]) -> List[Set[int]]:
        base = sorted(set(prev_nums))
        if len(base) != 7:
            return []

        jogos: List[Set[int]] = []

        transformacoes = [
            lambda n: n,
            lambda n: min(n + 1, 31),
            lambda n: max(n - 1, 1),
            lambda n: min(n + 2, 31),
            lambda n: max(n - 2, 1),
        ]

        for tf in transformacoes:
            jogo = sorted({tf(n) for n in base})
            jogos.append(set(jogo[:7]))
            if len(jogos) >= 10:
                break

        # Preencher ate 10 jogos com rotacoes simples
        offset = 1
        while len(jogos) < 10:
            rotacionado = base[offset:] + base[:offset]
            jogos.append(set(rotacionado))
            offset = (offset + 1) % len(base)

        # Garantir unicidade mantendo ordem
        jogos_unicos: List[Set[int]] = []
        seen = set()
        for jogo in jogos:
            chave = tuple(sorted(jogo))
            if chave not in seen:
                jogos_unicos.append(jogo)
                seen.add(chave)
        return jogos_unicos[:10]

    @staticmethod
    def _converte_lista(sorteio_obj) -> List[int]:
        return sorteio_obj.get_posicoes_lista() if hasattr(sorteio_obj, 'get_posicoes_lista') else []

    @staticmethod
    def analisar_simulacao_reversa(num_concursos_historico: int = 20):
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
        if len(sorteios) < 2:
            return {'error': 'Historico insuficiente para simulacao reversa'}

        inicio = max(1, len(sorteios) - num_concursos_historico)
        historico: List[Dict] = []
        distrib_hit_best = []

        for idx in range(inicio, len(sorteios)):
            anterior = AnaliseSimulacaoReversaService._converte_lista(sorteios[idx - 1])
            atual = AnaliseSimulacaoReversaService._converte_lista(sorteios[idx])
            if len(anterior) != 7 or len(atual) != 7:
                continue

            jogos = AnaliseSimulacaoReversaService._gerar_jogos(anterior)
            if not jogos:
                continue

            melhor_hits = -1
            melhor_jogo_idx = 0
            melhor_jogo = set()
            distribuicao_acertos = []

            for pos, jogo in enumerate(jogos, start=1):
                acertos = jogo & set(atual)
                distribuicao_acertos.append({'aposta': pos, 'acertos': sorted(acertos)})
                if len(acertos) > melhor_hits:
                    melhor_hits = len(acertos)
                    melhor_jogo_idx = pos
                    melhor_jogo = jogo

            faltantes = set(atual) - melhor_jogo
            falta_map = {str(num): [] for num in faltantes}
            for pos, jogo in enumerate(jogos, start=1):
                for num in faltantes:
                    if num in jogo:
                        falta_map[str(num)].append(pos)

            distrib_hit_best.append(melhor_hits)
            historico.append({
                'concurso': sorteios[idx].concurso,
                'resultado_real': sorted(atual),
                'base_concurso_anterior': sorted(anterior),
                'aposta_com_mais_acertos': {
                    'numero': melhor_jogo_idx,
                    'dezenas': sorted(melhor_jogo),
                    'acertos': melhor_hits
                },
                'os_3_faltantes': sorted(faltantes),
                'onde_estavam': falta_map,
                'distribuicao_acertos_jogos': distribuicao_acertos
            })

        if not historico:
            return {'error': 'Nao foi possivel processar concursos suficientes'}

        media_hits = sum(distrib_hit_best) / len(distrib_hit_best) if distrib_hit_best else 0
        pct_hits_4plus = (len([h for h in distrib_hit_best if h >= 4]) / len(distrib_hit_best) * 100) if distrib_hit_best else 0

        padrao_geral = (
            f'Em {pct_hits_4plus:.1f}% dos casos, uma aposta atingiu 4+ acertos; '
            f'intersecoes medias de {media_hits:.2f} entre jogos simulados e resultado real.'
        )

        return {
            'status': 'sucesso',
            'timestamp': datetime.utcnow().isoformat(),
            'total_concursos_analisados': len(historico),
            'historico_analise': historico,
            'padrao_geral': padrao_geral,
            'recomendacoes': [
                'Reforce pares do concurso anterior em pelo menos 2 apostas',
                'Inclua vizinhos (+/-1) para aumentar captacao dos faltantes'
            ]
        }

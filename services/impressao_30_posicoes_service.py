# Sistema: Análise por Posição - Dia de Sorte
# Listas por posição (impressão) + 30 apostas de 7 dezenas

import random

from models.sorteio import Sorteio
from services.analise_digitos_unicos_service import AnaliseDigitosUnicosService
from services.ciclo_por_posicao_service import CicloPorPosicaoService
from services.matriz_padrao_aderencia_service import MatrizPadraoAderenciaService


class Impressao30PosicoesService:
    """
    Por posição P: lista de dezenas jogáveis (pendentes do ciclo, sem a que saiu no último concurso na P).
    Gera N apostas de 7 dezenas (únicas no volante), excluindo as 7 do último sorteio, todas diferentes entre si.
    """

    @classmethod
    def _ultimo_sorteio(cls):
        return Sorteio.query.order_by(Sorteio.concurso.desc()).first()

    @classmethod
    def ultimo_resultado(cls):
        s = cls._ultimo_sorteio()
        if not s:
            return None
        posicoes = []
        for p in range(1, 8):
            d = CicloPorPosicaoService.dezena_na_posicao(s, p)
            posicoes.append({'posicao': p, 'dezena': d})
        return {
            'concurso': s.concurso,
            'data': s.data_sorteio.strftime('%d/%m/%Y') if s.data_sorteio else None,
            'posicoes': posicoes,
            'numeros_ultimo': sorted(
                {x['dezena'] for x in posicoes if x['dezena'] is not None}
            ),
        }

    @classmethod
    def historico_coluna_posicao(cls, posicao, limite=12):
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(limite).all()
        seq = []
        for s in reversed(sorteios):
            d = CicloPorPosicaoService.dezena_na_posicao(s, posicao)
            if d is not None:
                seq.append({'concurso': s.concurso, 'dezena': int(d)})
        return seq

    @classmethod
    def dezenas_jogaveis_posicao(cls, posicao):
        """Pendentes do ciclo na posição, exceto a dezena do último concurso nessa posição."""
        analise = CicloPorPosicaoService.analise_posicao(posicao)
        pendentes = list(analise['ciclo_atual'].get('dezenas_pendentes') or [])
        ult = cls._ultimo_sorteio()
        if ult:
            ult_d = CicloPorPosicaoService.dezena_na_posicao(ult, posicao)
            if ult_d is not None:
                pendentes = [n for n in pendentes if n != int(ult_d)]
        atrasos = CicloPorPosicaoService.atrasos_na_posicao(posicao)
        pendentes = sorted(set(pendentes), key=lambda n: (atrasos.get(n, 0), n), reverse=True)
        return {
            'posicao': posicao,
            'quantidade': len(pendentes),
            'excluida_ultimo': (
                CicloPorPosicaoService.dezena_na_posicao(ult, posicao) if ult else None
            ),
            'dezenas': pendentes,
        }

    @classmethod
    def tabela_regra_proximo_concurso(cls):
        """
        Tabela resumo: por posição, o que saiu no último concurso e o que entra na aposta do próximo.
        """
        ult = cls._ultimo_sorteio()
        if not ult:
            return None
        concurso = ult.concurso
        proximo = concurso + 1
        linhas = []
        for p in range(1, 8):
            saiu = CicloPorPosicaoService.dezena_na_posicao(ult, p)
            jog = cls.dezenas_jogaveis_posicao(p)
            linhas.append(
                {
                    'posicao': p,
                    'rotulo': f'{p}º sorteio',
                    'saiu_ultimo_concurso': int(saiu) if saiu is not None else None,
                    'nao_apostar': int(saiu) if saiu is not None else None,
                    'quantidade_jogaveis': jog['quantidade'],
                    'dezenas_jogaveis': jog['dezenas'],
                    'dezenas_texto': ' '.join(f'{n:02d}' for n in jog['dezenas']),
                }
            )
        return {
            'concurso_base': concurso,
            'proximo_concurso': proximo,
            'data_ultimo': ult.data_sorteio.strftime('%d/%m/%Y') if ult.data_sorteio else None,
            'linhas': linhas,
            'explicacao': (
                f'Apostar no concurso {proximo}: em cada posição, use as dezenas jogáveis '
                f'(pendentes do ciclo menos a que saiu no concurso {concurso}).'
            ),
        }

    @classmethod
    def _duplicatas_lista(cls, dezenas):
        vistos = set()
        dup = set()
        for n in dezenas:
            if n in vistos:
                dup.add(n)
            vistos.add(n)
        return sorted(dup)

    @classmethod
    def _carregar_jogaveis_por_posicao(cls):
        return {p: cls.dezenas_jogaveis_posicao(p) for p in range(1, 8)}

    @classmethod
    def _meta_coluna_posicao(cls, posicao, jogaveis_info, analise=None):
        if analise is None:
            analise = CicloPorPosicaoService.analise_posicao(posicao)
        jog = list(jogaveis_info['dezenas'])
        jog_set = set(jog)
        saidas = set(analise['ciclo_atual'].get('dezenas_saidas') or [])
        ult_d = jogaveis_info.get('excluida_ultimo')
        if ult_d is not None:
            ult_d = int(ult_d)
        complemento = sorted(n for n in range(1, 32) if n not in jog_set)
        dup = cls._duplicatas_lista(jog)
        return {
            **jogaveis_info,
            'dezenas_jogaveis': jog,
            'dezenas_complemento': complemento,
            'quantidade_jogaveis': len(jog),
            'quantidade_complemento': len(complemento),
            'sem_duplicata': len(dup) == 0,
            'duplicatas': dup,
            'saidas_ciclo': sorted(saidas),
            'ultimo_excluido': ult_d,
        }

    @classmethod
    def _tipo_celula_matriz(cls, dezena, jog_set, ult_d, saidas):
        if dezena in jog_set:
            return 'jogavel'
        if ult_d is not None and dezena == ult_d:
            return 'nao_apostar'
        if dezena in saidas:
            return 'saida'
        return 'complemento'

    @classmethod
    def _linha_tem_duplicata(cls, row):
        vistos = set()
        for p in range(1, 8):
            cel = row['celulas'].get(p)
            if not cel:
                continue
            n = cel['dezena']
            if n in vistos:
                return True
            vistos.add(n)
        return False

    @classmethod
    def _trocar_celulas_se_valido(cls, grid, i, p1, j, p2):
        ci = grid[i]['celulas'].get(p1)
        cj = grid[j]['celulas'].get(p2)
        if not ci or not cj:
            return False
        grid[i]['celulas'][p1], grid[j]['celulas'][p2] = cj, ci
        if cls._linha_tem_duplicata(grid[i]) or cls._linha_tem_duplicata(grid[j]):
            grid[i]['celulas'][p1], grid[j]['celulas'][p2] = ci, cj
            return False
        return True

    @classmethod
    def _reparar_duplicatas_linha_grid(cls, grid):
        for _pass in range(400):
            melhorou = False
            for i in range(len(grid)):
                if not cls._linha_tem_duplicata(grid[i]):
                    continue
                for p_fix in range(1, 8):
                    for j in range(len(grid)):
                        if j == i:
                            continue
                        if cls._trocar_celulas_se_valido(grid, i, p_fix, j, p_fix):
                            melhorou = True
                            break
                        for p2 in range(1, 8):
                            if p2 == p_fix:
                                continue
                            if cls._trocar_celulas_se_valido(grid, i, p_fix, j, p2):
                                melhorou = True
                                break
                        if melhorou:
                            break
                    if melhorou:
                        break
            if not melhorou:
                break
        return grid

    @classmethod
    def _celula_matriz(cls, dezena, meta):
        return {
            'dezena': dezena,
            'tipo': cls._tipo_celula_matriz(
                dezena,
                set(meta['dezenas_jogaveis']),
                meta['ultimo_excluido'],
                set(meta['saidas_ciclo']),
            ),
        }

    @classmethod
    def _escolher_offsets_colunas(cls, colunas):
        """7 deslocamentos distintos (mod 31) → nenhuma dezena repetida na mesma linha."""
        ordem_pos = sorted(
            range(1, 8),
            key=lambda p: len(colunas[p]['dezenas_jogaveis']),
            reverse=True,
        )
        offsets = {}
        usados = set()
        for p in ordem_pos:
            jog = set(colunas[p]['dezenas_jogaveis'])
            n_jog = len(jog)
            melhor_off = 0
            melhor_score = -1
            for off in range(31):
                if off in usados:
                    continue
                score = sum(
                    1
                    for i in range(n_jog)
                    if ((i + off) % 31) + 1 in jog
                )
                if score > melhor_score:
                    melhor_score = score
                    melhor_off = off
            if melhor_off in usados:
                for off in range(31):
                    if off not in usados:
                        melhor_off = off
                        break
            offsets[p] = melhor_off
            usados.add(melhor_off)
        return offsets

    @classmethod
    def _montar_grid_linhas_unicas(cls, colunas):
        """
        Cada coluna exibe 01–31 (jogáveis + complemento com cores).
        Deslocamento por coluna garante dezenas distintas em cada linha.
        """
        offsets = cls._escolher_offsets_colunas(colunas)
        for p in range(1, 8):
            colunas[p]['offset_linha'] = offsets[p]
        grid = []
        for i in range(31):
            celulas = {}
            for p in range(1, 8):
                n = ((i + offsets[p]) % 31) + 1
                celulas[p] = cls._celula_matriz(n, colunas[p])
            grid.append({'linha': i + 1, 'celulas': celulas})
        return grid

    @classmethod
    def _validar_duplicatas_linha_grid(cls, grid):
        alertas = []
        for row in grid:
            vistos = {}
            for p in range(1, 8):
                cel = row['celulas'].get(p)
                if not cel:
                    continue
                n = cel['dezena']
                if n in vistos:
                    alertas.append(
                        {
                            'linha': row['linha'],
                            'dezena': n,
                            'posicoes': sorted([vistos[n], p]),
                        }
                    )
                else:
                    vistos[n] = p
        return alertas

    @classmethod
    def matriz_impressao_30(cls, jogaveis=None, analises=None):
        """
        7 colunas × 31 linhas: cada coluna lista 01–31 uma vez.
        Primeiro as jogáveis (pendentes − último), depois o complemento (cor diferente).
        """
        if jogaveis is None:
            jogaveis = cls._carregar_jogaveis_por_posicao()
        if analises is None:
            analises = CicloPorPosicaoService.resumo_todas_posicoes()

        colunas = {}
        listas_por_pos = {}
        for p in range(1, 8):
            analise = analises.get(p) or analises.get(str(p))
            meta = cls._meta_coluna_posicao(p, jogaveis[p], analise)
            sequencia = meta['dezenas_jogaveis'] + meta['dezenas_complemento']
            listas_por_pos[p] = sequencia
            colunas[p] = {
                **meta,
                'quantidade': len(meta['dezenas_jogaveis']),
                'sequencia_completa': sequencia,
            }

        linhas_alvo = 31
        for p in range(1, 8):
            colunas[p]['sequencia_completa'] = listas_por_pos[p]
        grid = cls._montar_grid_linhas_unicas(colunas)
        referencia_padrao = MatrizPadraoAderenciaService.referencia_historica()
        grid = MatrizPadraoAderenciaService.enriquecer_grid_com_padrao(grid)
        dup_linhas = cls._validar_duplicatas_linha_grid(grid)
        todas_ok = all(colunas[p]['sem_duplicata'] for p in range(1, 8))

        return {
            'linhas': linhas_alvo,
            'colunas': colunas,
            'grid': grid,
            'referencia_padrao': referencia_padrao,
            'colunas_sem_duplicata': todas_ok,
            'linhas_sem_duplicata': len(dup_linhas) == 0,
            'duplicatas_entre_colunas': dup_linhas,
            'legenda': {
                'jogavel': 'Pendente jogável (ciclo atual, exceto último sorteio na posição)',
                'complemento': 'Completa 01–31 — já saiu no ciclo ou não está na lista jogável',
                'nao_apostar': 'Saiu no último concurso nesta posição',
                'saida': 'Já saiu no ciclo atual',
            },
        }

    @classmethod
    def validar_sequencia_coluna(cls, posicao, jogaveis=None):
        """Histórico recente da coluna: aponta repetições consecutivas da mesma dezena."""
        seq = cls.historico_coluna_posicao(posicao, 30)
        alertas = []
        for i in range(1, len(seq)):
            if seq[i]['dezena'] == seq[i - 1]['dezena']:
                alertas.append(
                    {
                        'dezena': seq[i]['dezena'],
                        'concurso': seq[i]['concurso'],
                        'anterior': seq[i - 1]['concurso'],
                    }
                )
        if jogaveis is None:
            jogaveis = cls._carregar_jogaveis_por_posicao()
        dezenas_unicas_lista = jogaveis[posicao]['dezenas']
        duplicata_na_lista = len(dezenas_unicas_lista) != len(set(dezenas_unicas_lista))
        return {
            'posicao': posicao,
            'sequencia_recente': seq,
            'repeticoes_consecutivas_historico': alertas,
            'lista_jogaveis_sem_duplicata': not duplicata_na_lista,
            'qtd_jogaveis': len(dezenas_unicas_lista),
        }

    @classmethod
    def validar_aposta(cls, numeros):
        nums = sorted(set(int(n) for n in numeros if n is not None))
        erros = []
        if len(nums) != len(numeros):
            erros.append('Há dezenas repetidas no mesmo jogo.')
        if any(n < 1 or n > 31 for n in nums):
            erros.append('Dezena fora do intervalo 01–31.')
        return {'valida': len(erros) == 0, 'numeros': nums, 'erros': erros}

    @classmethod
    def _candidatas_globais(cls, jogaveis=None, atrasos=None, excluir=None):
        if jogaveis is None:
            jogaveis = cls._carregar_jogaveis_por_posicao()
        if atrasos is None:
            atrasos = {p: CicloPorPosicaoService.atrasos_na_posicao(p) for p in range(1, 8)}
        if excluir is None:
            ult = cls.ultimo_resultado()
            excluir = set(ult['numeros_ultimo']) if ult else set()
        matriz = {}
        for p in range(1, 8):
            for n in jogaveis[p]['dezenas']:
                if n in excluir:
                    continue
                if n not in matriz:
                    matriz[n] = {'dezena': n, 'posicoes': [], 'score': 0}
                matriz[n]['posicoes'].append(p)
        for item in matriz.values():
            atraso_max = 0
            for p in item['posicoes']:
                atraso_max = max(atraso_max, atrasos[p].get(item['dezena'], 0))
            item['score'] = len(item['posicoes']) * 1000 + atraso_max
        return sorted(matriz.values(), key=lambda x: (-x['score'], x['dezena']))

    @classmethod
    def _montar_uma_aposta(cls, qtd_dezenas, variacao, ja_usadas, excluir_ultimo, candidatas_base):
        rng = random.Random(variacao * 7919 + qtd_dezenas * 31)
        candidatas = [c for c in candidatas_base if c['dezena'] not in excluir_ultimo]
        rng.shuffle(candidatas)
        candidatas.sort(key=lambda c: (-c['score'], (c['dezena'] + variacao) % 31))

        escolhidos = []
        faixa_count = {1: 0, 2: 0, 3: 0, 4: 0}
        max_faixa = 3

        for item in candidatas:
            if len(escolhidos) >= qtd_dezenas:
                break
            n = item['dezena']
            f = CicloPorPosicaoService._faixa(n)
            if faixa_count[f] >= max_faixa:
                continue
            chave = tuple(sorted(escolhidos + [n]))
            if chave in ja_usadas:
                continue
            escolhidos.append(n)
            faixa_count[f] += 1

        if len(escolhidos) < qtd_dezenas:
            for item in candidatas:
                if len(escolhidos) >= qtd_dezenas:
                    break
                if item['dezena'] not in escolhidos:
                    escolhidos.append(item['dezena'])

        escolhidos = sorted(escolhidos)[:qtd_dezenas]
        chave = tuple(escolhidos)
        return chave, escolhidos

    @classmethod
    def _parse_relacao_digitos_soma(cls, relacao):
        partes = str(relacao).strip().split('/')
        if len(partes) != 2:
            return None, None
        try:
            return int(partes[0]), int(partes[1])
        except ValueError:
            return None, None

    @classmethod
    def _top_relacoes_historicas(cls, limite=30):
        data = AnaliseDigitosUnicosService.analisar_digitos_unicos()
        if not data or data.get('error'):
            return []
        return list(data.get('top_relacoes_soma') or [])[:limite]

    @classmethod
    def _pools_por_posicao(cls, colunas, excluir):
        pools = {}
        for p in range(1, 8):
            meta = colunas[p]
            itens = []
            for d in meta['dezenas_jogaveis']:
                if d not in excluir:
                    itens.append((int(d), 'jogavel'))
            for d in meta['dezenas_complemento']:
                if d not in excluir:
                    itens.append((int(d), 'complemento'))
            pools[p] = itens
        return pools

    @classmethod
    def _volantes_por_posicao_relacao(cls, relacao, limite=150):
        """Sorteios reais com a relação dígitos/soma, na ordem das posições."""
        out = []
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        for s in sorteios:
            nums = []
            for p in range(1, 8):
                d = CicloPorPosicaoService.dezena_na_posicao(s, p)
                if d is None:
                    nums = []
                    break
                nums.append(int(d))
            if len(nums) != 7:
                continue
            pad = MatrizPadraoAderenciaService.padrao_digitos_soma(nums)
            if pad['texto'] != relacao:
                continue
            out.append(nums)
            if len(out) >= limite:
                break
        return out

    @classmethod
    def _volante_cabe_nas_colunas(cls, nums_por_pos, pools, excluir):
        usados = set()
        tipos = []
        for p in range(1, 8):
            d = nums_por_pos[p - 1]
            if d in excluir or d in usados:
                return None
            tipo = None
            for cand, t in pools[p]:
                if cand == d:
                    tipo = t
                    break
            if tipo is None:
                return None
            usados.add(d)
            tipos.append(tipo)
        return tuple(nums_por_pos), tuple(tipos)

    @classmethod
    def _score_volante_elite(cls, numeros, tipos, relacao_alvo):
        pad = MatrizPadraoAderenciaService.padrao_digitos_soma(numeros)
        dig_t, soma_t = cls._parse_relacao_digitos_soma(relacao_alvo)
        score = 0
        if pad['texto'] == relacao_alvo:
            score += 100_000
        elif dig_t is not None and soma_t is not None:
            score -= abs(pad['digitos'] - dig_t) * 800
            score -= abs(pad['soma'] - soma_t) * 12
        score += sum(400 if t == 'jogavel' else 40 for t in tipos)
        return score, pad['texto']

    @classmethod
    def _buscar_volante_backtrack(cls, relacao_alvo, pools, rng, variacao=0):
        dig_t, soma_t = cls._parse_relacao_digitos_soma(relacao_alvo)
        melhor = None
        melhor_score = -10**9
        nodes = [0]
        limite_nodes = 80_000

        ordem_pos = list(range(1, 8))
        rng.shuffle(ordem_pos)
        pools_ord = {}
        for p in range(1, 8):
            jog = [(d, t) for d, t in pools[p] if t == 'jogavel']
            comp = [(d, t) for d, t in pools[p] if t == 'complemento']
            rng.shuffle(jog)
            rng.shuffle(comp)
            pools_ord[p] = jog + comp

        def dfs(pos_idx, escolhidos, tipos_por_pos, soma_parcial):
            nonlocal melhor, melhor_score
            if nodes[0] > limite_nodes:
                return
            nodes[0] += 1
            if pos_idx >= 7:
                nums = [escolhidos[p] for p in range(1, 8)]
                tipos = [tipos_por_pos[p] for p in range(1, 8)]
                sc, txt = cls._score_volante_elite(nums, tipos, relacao_alvo)
                if sc > melhor_score:
                    melhor_score = sc
                    melhor = (tuple(nums), tuple(tipos), txt)
                return
            p = ordem_pos[pos_idx]
            restantes = 7 - pos_idx - 1
            for d, t in pools_ord[p]:
                if d in escolhidos.values():
                    continue
                nova_soma = soma_parcial + d
                if soma_t is not None:
                    if nova_soma > soma_t + restantes * 31:
                        continue
                    if nova_soma + restantes * 1 < soma_t:
                        continue
                escolhidos[p] = d
                tipos_por_pos[p] = t
                dfs(pos_idx + 1, escolhidos, tipos_por_pos, nova_soma)
                del tipos_por_pos[p]
                del escolhidos[p]

        dfs(0, {}, {}, 0)
        return melhor

    @classmethod
    def _montar_aposta_por_relacao_elite(cls, relacao_alvo, colunas, excluir, rng):
        pools = cls._pools_por_posicao(colunas, excluir)
        if any(len(pools[p]) == 0 for p in range(1, 8)):
            return None

        melhor = None
        melhor_score = -10**9
        hist = cls._volantes_por_posicao_relacao(relacao_alvo)
        rng.shuffle(hist)
        for vol in hist:
            fit = cls._volante_cabe_nas_colunas(vol, pools, excluir)
            if not fit:
                continue
            sc, txt = cls._score_volante_elite(fit[0], fit[1], relacao_alvo)
            sc += 15_000
            if sc > melhor_score:
                melhor_score = sc
                melhor = (fit[0], fit[1], txt)

        if melhor is None or melhor_score < 50_000:
            bt = cls._buscar_volante_backtrack(
                relacao_alvo, pools, rng, rng.randint(0, 9999)
            )
            if bt and (melhor is None or melhor_score < cls._score_volante_elite(bt[0], bt[1], relacao_alvo)[0]):
                melhor = bt

        if melhor is None:
            return None
        nums = sorted(melhor[0])
        qtd_azul = sum(1 for t in melhor[1] if t == 'complemento')
        return {
            'numeros': nums,
            'chave': tuple(nums),
            'padrao': melhor[2],
            'relacao_alvo': relacao_alvo,
            'qtd_complemento': qtd_azul,
        }

    @classmethod
    def gerar_apostas_30(
        cls,
        quantidade_apostas=30,
        dezenas_por_aposta=7,
        candidatas_base=None,
        excluir=None,
        colunas=None,
    ):
        if excluir is None:
            ult = cls.ultimo_resultado()
            excluir = set(ult['numeros_ultimo']) if ult else set()
        referencia = MatrizPadraoAderenciaService.referencia_historica()
        top_rel = cls._top_relacoes_historicas(max(quantidade_apostas, 10))
        apostas = []
        ja_usadas = set()

        if colunas and top_rel:
            for i in range(quantidade_apostas):
                meta = top_rel[i % len(top_rel)]
                rel = meta.get('relacao')
                if not rel:
                    continue
                rng = random.Random(i * 7919 + 17)
                for tent in range(12):
                    cand = cls._montar_aposta_por_relacao_elite(
                        rel, colunas, excluir, random.Random(rng.randint(0, 10**6) + tent)
                    )
                    if not cand or cand['chave'] in ja_usadas:
                        continue
                    val = cls.validar_aposta(cand['numeros'])
                    if not val['valida']:
                        continue
                    ja_usadas.add(cand['chave'])
                    apostas.append(cand)
                    break

        if len(apostas) < quantidade_apostas:
            if candidatas_base is None:
                candidatas_base = cls._candidatas_globais(excluir=excluir)
            extras = []
            tentativas = max((quantidade_apostas - len(apostas)) * 10, 60)
            for v in range(tentativas):
                chave, nums = cls._montar_uma_aposta(
                    dezenas_por_aposta, v + 1000, ja_usadas, excluir, candidatas_base
                )
                if len(nums) < dezenas_por_aposta:
                    continue
                val = cls.validar_aposta(nums)
                if not val['valida'] or chave in ja_usadas:
                    continue
                ja_usadas.add(chave)
                pad = MatrizPadraoAderenciaService.padrao_digitos_soma(val['numeros'])
                dist = MatrizPadraoAderenciaService.distancia_padrao_ideal(
                    val['numeros'], referencia
                )
                extras.append(
                    {
                        'numeros': val['numeros'],
                        'chave': chave,
                        'padrao': pad['texto'],
                        'distancia_ideal': dist,
                    }
                )
            extras.sort(key=lambda x: x.get('distancia_ideal', 999))
            for c in extras:
                if len(apostas) >= quantidade_apostas:
                    break
                apostas.append(c)

        saida = []
        for i, c in enumerate(apostas[:quantidade_apostas]):
            nums = c['numeros']
            saida.append(
                {
                    'numero': i + 1,
                    'numeros': nums,
                    'texto': ' '.join(f'{n:02d}' for n in nums),
                    'padrao_digitos_soma': c.get('padrao')
                    or MatrizPadraoAderenciaService.padrao_digitos_soma(nums)['texto'],
                    'relacao_alvo': c.get('relacao_alvo'),
                    'qtd_complemento': c.get('qtd_complemento', 0),
                }
            )

        return {
            'quantidade': len(saida),
            'dezenas_por_aposta': dezenas_por_aposta,
            'excluidas_ultimo_sorteio': sorted(excluir),
            'referencia_padrao': referencia,
            'top_relacoes_usadas': [t.get('relacao') for t in top_rel[:10]],
            'modo_geracao': 'elite_top10_colunas' if colunas and top_rel else 'ciclo_global',
            'apostas': saida,
        }

    @classmethod
    def pacote_impressao_completo(cls, qtd_apostas=30, dezenas=7):
        analises = CicloPorPosicaoService.resumo_todas_posicoes()
        jogaveis = cls._carregar_jogaveis_por_posicao()
        atrasos = {p: CicloPorPosicaoService.atrasos_na_posicao(p) for p in range(1, 8)}
        ult = cls.ultimo_resultado()
        excluir = set(ult['numeros_ultimo']) if ult else set()
        candidatas = cls._candidatas_globais(jogaveis, atrasos, excluir)
        matriz = cls.matriz_impressao_30(jogaveis, analises)
        validacoes = [cls.validar_sequencia_coluna(p, jogaveis) for p in range(1, 8)]
        apostas = cls.gerar_apostas_30(
            qtd_apostas, dezenas, candidatas, excluir, colunas=matriz.get('colunas')
        )
        tabela = cls.tabela_regra_proximo_concurso()
        if tabela and jogaveis:
            for lin in tabela['linhas']:
                p = lin['posicao']
                lin['dezenas_jogaveis'] = jogaveis[p]['dezenas']
                lin['dezenas_texto'] = ' '.join(f'{n:02d}' for n in lin['dezenas_jogaveis'])
                lin['quantidade_jogaveis'] = len(lin['dezenas_jogaveis'])
        return {
            'sucesso': True,
            'ultimo_sorteio': ult,
            'tabela_regra': tabela,
            'matriz_30': matriz,
            'referencia_padrao': matriz.get('referencia_padrao')
            or apostas.get('referencia_padrao'),
            'validacoes_colunas': validacoes,
            'apostas': apostas,
            'regra': (
                f'Listas por posição = pendentes do ciclo menos a dezena do último concurso naquela posição. '
                f'{qtd_apostas} jogos de {dezenas} dezenas (Top 10 dígitos/soma do histórico, como Simulador Elite): '
                f'prioriza amarelas (jogáveis) e usa azuis (complemento) só para fechar o padrão real dos sorteios.'
            ),
        }

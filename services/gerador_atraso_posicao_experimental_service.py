"""Gerador Atraso Posicional — versão experimental (saltos configuráveis). Aba 6A."""
from models.sorteio import Sorteio
from services.gerador_especial_service import GeradorEspecialService
from services.gerador_atraso_posicao_service import GeradorAtrasoPosicaoService
import random


class GeradorAtrasoPosicaoExperimentalService:
    LIMITES_SALTO = (6, 15, 30)

    @staticmethod
    def _validar_limite(limite):
        lim = int(limite)
        if lim not in GeradorAtrasoPosicaoExperimentalService.LIMITES_SALTO:
            return 30
        return lim

    @staticmethod
    def _clamp_salto(valor, limite_max, fallback=1):
        try:
            v = int(valor)
        except (TypeError, ValueError):
            v = fallback
        return max(1, min(v, limite_max))

    @staticmethod
    def _normalizar_saltos(
        salto_modo,
        salto_global,
        salto_global_menos,
        saltos_coluna,
        saltos_coluna_menos,
        salto_simetrico,
        limite_max,
    ):
        simetrico = bool(salto_simetrico) if salto_simetrico is not None else True
        sg_mais = GeradorAtrasoPosicaoExperimentalService._clamp_salto(
            salto_global, limite_max
        )
        sg_menos = sg_mais if simetrico else GeradorAtrasoPosicaoExperimentalService._clamp_salto(
            salto_global_menos, limite_max, sg_mais
        )

        if salto_modo == 'por_coluna' and saltos_coluna:
            mais, menos = [], []
            for i in range(7):
                try:
                    vm = int(saltos_coluna[i])
                except (TypeError, ValueError, IndexError):
                    vm = sg_mais
                sm = GeradorAtrasoPosicaoExperimentalService._clamp_salto(vm, limite_max, sg_mais)
                mais.append(sm)
                if simetrico:
                    menos.append(sm)
                else:
                    try:
                        vn = int(saltos_coluna_menos[i])
                    except (TypeError, ValueError, IndexError):
                        vn = sg_menos
                    menos.append(
                        GeradorAtrasoPosicaoExperimentalService._clamp_salto(vn, limite_max, sg_menos)
                    )
            return mais, menos, 'por_coluna'

        return [sg_mais] * 7, [sg_menos] * 7, 'global'

    @staticmethod
    def _calcular_faixa_offset(base_nums):
        return -(max(base_nums) - 1), 31 - min(base_nums)

    @staticmethod
    def _celula_matriz_experimental(base, r, idx, saltos_mais, saltos_menos):
        """
        Matriz base = Aba 6 original (+1/−1 por linha, ciclo 1..31).
        Saltos aplicam SOMENTE nas células azuis (linear fora de 1..31).
        Salto 1 = igual à original na zona azul.
        Salto N = deslocamento extra (N−1) no ciclo sobre o valor azul original.
        """
        b = int(base)
        r = int(r)
        linear = b + r
        v_orig = GeradorAtrasoPosicaoService.dezena_ciclica(b, r)
        wrap = not (1 <= linear <= 31)

        if not wrap:
            return v_orig, False

        salto = saltos_mais[idx] if r > 0 else saltos_menos[idx]
        if r > 0:
            shift = int(salto) - 1
        else:
            shift = 0 if int(salto) <= 1 else int(salto)
        if shift <= 0:
            return v_orig, True

        v = ((v_orig - 1 + shift) % 31) + 1
        return v, True

    @staticmethod
    def gerar_apostas_atraso_posicao_experimental(
        concurso_base_id,
        quantidade,
        dezenas_por_jogo,
        mes_selecionado,
        salto_modo='global',
        salto_global=1,
        salto_global_menos=None,
        salto_simetrico=True,
        saltos_coluna=None,
        saltos_coluna_menos=None,
        limite_salto_max=30,
        contexto_precarregado=None,
    ):
        """
        contexto_precarregado (opcional, só para busca em lote):
          {
            'concurso': int,
            'base_nums': [7 ints],
            'atrasos_globais': [ints 1..31 ordenados por atraso],
          }
        Quando informado, não consulta o banco (mesmo algoritmo).
        """
        limite_max = GeradorAtrasoPosicaoExperimentalService._validar_limite(limite_salto_max)
        saltos_mais, saltos_menos, modo_efetivo = GeradorAtrasoPosicaoExperimentalService._normalizar_saltos(
            salto_modo,
            salto_global,
            salto_global_menos,
            saltos_coluna or [],
            saltos_coluna_menos or [],
            salto_simetrico,
            limite_max,
        )

        if contexto_precarregado:
            base_nums = [int(n) for n in contexto_precarregado['base_nums']]
            atrasos_globais = list(contexto_precarregado['atrasos_globais'])
            concurso_num = int(contexto_precarregado['concurso'])
        else:
            if concurso_base_id == 'ultimo':
                sorteio_base = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
            else:
                sorteio_base = Sorteio.query.filter_by(concurso=int(concurso_base_id)).first()

            if not sorteio_base:
                return {'sucesso': False, 'mensagem': 'Concurso base não encontrado.'}

            base_nums = [int(n) for n in sorteio_base.get_ordem_sorteio_lista()]
            concurso_num = sorteio_base.concurso

            ultimos_sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(150).all()
            last_seen = {i: 0 for i in range(1, 32)}
            for s in ultimos_sorteios:
                for n in s.get_posicoes_lista():
                    if 1 <= n <= 31 and last_seen[n] == 0:
                        last_seen[n] = s.concurso

            ultimo_c = ultimos_sorteios[0].concurso if ultimos_sorteios else 0
            delays = []
            for i in range(1, 32):
                atraso = (ultimo_c - last_seen[i]) if last_seen[i] > 0 else 150
                delays.append((i, atraso))
            delays.sort(key=lambda x: x[1], reverse=True)
            atrasos_globais = [x[0] for x in delays]

        meses_nomes = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        r_min, r_max = GeradorAtrasoPosicaoExperimentalService._calcular_faixa_offset(base_nums)
        apostas_finais = []

        for r in range(r_min, r_max + 1):
            if r == 0:
                continue

            grid_row = []
            grid_wrap = []
            esqueleto = []

            for idx, b in enumerate(base_nums):
                v, wrap = GeradorAtrasoPosicaoExperimentalService._celula_matriz_experimental(
                    b, r, idx, saltos_mais, saltos_menos
                )
                grid_row.append(v)
                grid_wrap.append(wrap)
                esqueleto.append(v)

            aposta_final, preenchimento = GeradorAtrasoPosicaoService._eliminar_repeticoes_linha(
                esqueleto, atrasos_globais
            )

            if len(aposta_final) < dezenas_por_jogo:
                faltam = dezenas_por_jogo - len(aposta_final)
                candidatos = [n for n in atrasos_globais if n not in aposta_final]
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

            aposta_ajustada = list(aposta_final)
            bx_adj = sum(1 for n in aposta_ajustada if n <= 10)
            mx_adj = sum(1 for n in aposta_ajustada if 11 <= n <= 20)
            ax_adj = sum(1 for n in aposta_ajustada if n >= 21)
            candidatos_ajuste = [n for n in atrasos_globais if n not in aposta_ajustada]

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

            if mes_selecionado == 'aleatorio':
                mes_num = random.randint(1, 12)
            elif mes_selecionado == 'sequencial':
                mes_num = (len(apostas_finais) % 12) + 1
            else:
                mes_num = int(mes_selecionado)

            apostas_finais.append({
                'linha_offset': r,
                'grid': grid_row,
                'grid_wrap': grid_wrap,
                'esqueleto': sorted(esqueleto),
                'preenchimento': preenchimento,
                'faltantes_atrasadas': list(preenchimento),
                'aposta_final_numeros': aposta_final,
                'aposta_ajustada_numeros': aposta_ajustada,
                'mes_num': mes_num,
                'mes_nome': meses_nomes[mes_num],
            })

        if not apostas_finais:
            return {'sucesso': False, 'mensagem': 'Não foi possível gerar apostas com os parâmetros fornecidos.'}

        tabela_precos = {
            7: 2.50, 8: 20.00, 9: 90.00, 10: 300.00,
            11: 825.00, 12: 1980.00, 13: 4290.00, 14: 8580.00, 15: 16087.50
        }
        valor_aposta = tabela_precos.get(dezenas_por_jogo, 2.50)

        return {
            'sucesso': True,
            'experimental': True,
            'apostas': apostas_finais,
            'quantidade': len(apostas_finais),
            'valor_unitario': valor_aposta,
            'valor_total': valor_aposta * len(apostas_finais),
            'concurso_base': concurso_num,
            'dezenas_base': base_nums,
            'salto_modo': modo_efetivo,
            'salto_simetrico': bool(salto_simetrico) if salto_simetrico is not None else True,
            'salto_global': saltos_mais[0] if modo_efetivo == 'global' else salto_global,
            'salto_global_menos': saltos_menos[0] if modo_efetivo == 'global' else salto_global_menos,
            'saltos_coluna': saltos_mais,
            'saltos_coluna_menos': saltos_menos,
            'limite_salto_max': limite_max,
            'offset_min': r_min,
            'offset_max': r_max,
        }

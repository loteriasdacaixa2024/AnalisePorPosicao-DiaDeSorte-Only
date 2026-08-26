from models.sorteio import Sorteio, db
from services.analise_atrasados_service import AnaliseAtrasadosService
from services.gerador_especial_service import GeradorEspecialService
import random

class GeradorAtrasoPosicaoService:
    @staticmethod
    def dezena_ciclica(base, offset):
        """Sequência cíclica 1..31: ao passar de 31 volta a 1, abaixo de 1 volta a 31."""
        return ((int(base) + int(offset) - 1) % 31) + 1

    @staticmethod
    def _eliminar_repeticoes_linha(esqueleto, atrasos_globais):
        """Se a mesma linha tiver dezena repetida, troca por atrasada equilibrada."""
        vistos = set()
        resultado = []
        preenchimento = []

        for n in esqueleto:
            if n not in vistos:
                vistos.add(n)
                resultado.append(n)
                continue

            candidatos = [c for c in atrasos_globais if c not in vistos]
            bx = sum(1 for x in resultado if x <= 10)
            mx = sum(1 for x in resultado if 11 <= x <= 20)
            ax = sum(1 for x in resultado if x >= 21)
            if bx <= mx and bx <= ax:
                faixa = 'baixo'
            elif mx <= bx and mx <= ax:
                faixa = 'medio'
            else:
                faixa = 'alto'

            escolhido = None
            for c in candidatos:
                if GeradorEspecialService.classify_number(c) == faixa:
                    escolhido = c
                    break
            if not escolhido and candidatos:
                escolhido = candidatos[0]
            if escolhido:
                resultado.append(escolhido)
                preenchimento.append(escolhido)
                vistos.add(escolhido)

        return resultado, preenchimento

    @staticmethod
    def gerar_apostas_atraso_posicao(concurso_base_id, quantidade, dezenas_por_jogo, mes_selecionado):
        # 1. Pegar Sorteio Base
        if concurso_base_id == 'ultimo':
            sorteio_base = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
        else:
            sorteio_base = Sorteio.query.filter_by(concurso=int(concurso_base_id)).first()
            
        if not sorteio_base:
            return {'sucesso': False, 'mensagem': 'Concurso base não encontrado.'}
            
        # A matriz da aba 6 deve seguir a ordem real em que as dezenas foram sorteadas
        # (1º Sorteio, 2º Sorteio, ...), não a ordem crescente usada em outras análises.
        base_nums = [int(n) for n in sorteio_base.get_ordem_sorteio_lista()]
        
        # 2. Pegar atrasos posicionais (top 5 de cada posição)
        atrasos_por_posicao = {}
        for pos in range(1, 8):
            res = AnaliseAtrasadosService.obter_frequencia_por_posicao(pos, modo='sorteio')
            if 'numeros' in res:
                # Pega os 10 mais atrasados para cada posição
                atrasos_por_posicao[pos] = [n['numero'] for n in res['numeros'][:10]]
            else:
                atrasos_por_posicao[pos] = list(range(1, 32))
                
        # 3. Pegar atrasos globais (para completar >7 dezenas)
        atrasos_globais = []
        res_global = AnaliseAtrasadosService.obter_frequencia_por_posicao(1, modo='sorteio') # Só pra usar o histórico
        # Para atraso global real, podemos calcular baseado no último sorteio de cada número
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

        apostas_finais = []

        meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        # 4. Matriz estilo Excel: cada coluna avança +1/-1 por linha com ciclo 1..31
        # Linha r=0 é o sorteio base; r<0 desce (laranja), r>0 sobe (verde)
        r_min = -(max(base_nums) - 1)
        r_max = 31 - min(base_nums)

        for r in range(r_min, r_max + 1):
            if r == 0:
                continue

            grid_row = []
            grid_wrap = []
            esqueleto = []

            for b in base_nums:
                linear = b + r
                v = GeradorAtrasoPosicaoService.dezena_ciclica(b, r)
                grid_row.append(v)
                grid_wrap.append(not (1 <= linear <= 31))
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
            
            # --- Lógica de Equilíbrio Leve (Aposta Ajustada) ---
            aposta_ajustada = list(aposta_final)
            bx_adj = sum(1 for n in aposta_ajustada if n <= 10)
            mx_adj = sum(1 for n in aposta_ajustada if 11 <= n <= 20)
            ax_adj = sum(1 for n in aposta_ajustada if n >= 21)
            
            candidatos_ajuste = [n for n in atrasos_globais if n not in aposta_ajustada]
            
            if bx_adj >= 4 or mx_adj >= 4 or ax_adj >= 4:
                zonas = {'baixo': bx_adj, 'medio': mx_adj, 'alto': ax_adj}
                
                trocas = 0
                # Tentar trocar de 1 a 2 dezenas da zona em excesso para a zona deficiente
                # Varre a aposta de trás para frente ou aleatoriamente (aqui remove do final para evitar tirar os primeiros menores)
                for i in range(len(aposta_ajustada)-1, -1, -1):
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
            # ----------------------------------------------------

            # Cada linha (offset) deve aparecer na matriz — sem omitir -14, -13, etc.
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
                'mes_nome': meses_nomes[mes_num]
            })
                
        if len(apostas_finais) == 0:
            return {'sucesso': False, 'mensagem': 'Não foi possível gerar apostas com os parâmetros fornecidos.'}
            
        valor_unitario = 2.50
        tabela_precos = {
            7: 2.50, 8: 20.00, 9: 90.00, 10: 300.00,
            11: 825.00, 12: 1980.00, 13: 4290.00, 14: 8580.00, 15: 16087.50
        }
        
        valor_aposta = tabela_precos.get(dezenas_por_jogo, 2.50)
        valor_total = valor_aposta * len(apostas_finais)
        
        return {
            'sucesso': True,
            'apostas': apostas_finais,
            'quantidade': len(apostas_finais),
            'valor_unitario': valor_aposta,
            'valor_total': valor_total,
            'concurso_base': sorteio_base.concurso,
            'dezenas_base': base_nums
        }

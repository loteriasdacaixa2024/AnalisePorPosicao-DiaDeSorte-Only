import math
from models.sorteio import Sorteio

class AnaliseSimuladorFiltrosService:

    @staticmethod
    def simular_jogos(jogos, filtro_digitos_unicos=None):
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado na base de dados.'}

        # Validar Jogos
        jogos_validos = []
        for j in jogos:
            numeros = j.get('numeros', [])
            mes = j.get('mes', 1)
            if not isinstance(numeros, list) or len(numeros) < 7 or len(numeros) > 15:
                continue
            
            numeros_unicos = list(set(numeros))
            if len(numeros_unicos) != len(numeros):
                continue

            if any(n < 1 or n > 31 for n in numeros_unicos):
                continue
                
            custo_jogo = math.comb(len(numeros_unicos), 7) * 2.50
            jogos_validos.append({
                'numeros_set': set(numeros_unicos),
                'numeros_lista': sorted(numeros_unicos),
                'mes': int(mes),
                'custo': custo_jogo
            })

        if not jogos_validos:
            return {'error': 'Nenhum jogo válido fornecido. Cada jogo deve ter entre 7 e 15 números únicos.'}

        # Filtrar sorteios se necessário
        sorteios_filtrados = []
        if filtro_digitos_unicos and filtro_digitos_unicos.isdigit():
            filtro_qtd = int(filtro_digitos_unicos)
            for s in sorteios:
                numeros_sorteados = [getattr(s, f'posicao_{i}') for i in range(1, 8) if getattr(s, f'posicao_{i}')]
                digitos_unicos = set()
                for num in numeros_sorteados:
                    str_num = str(num).zfill(2)
                    digitos_unicos.add(str_num[0])
                    digitos_unicos.add(str_num[1])
                
                if len(digitos_unicos) == filtro_qtd:
                    sorteios_filtrados.append(s)
        else:
            sorteios_filtrados = sorteios
            
        if not sorteios_filtrados:
            return {'error': 'Nenhum concurso histórico corresponde ao filtro de Dígitos Únicos atual.'}

        total_concursos_analisados = len(sorteios_filtrados)
        acertos_por_quantidade = {i: 0 for i in range(8)} # 0 a 7
        total_acertos_mes = 0
        premio_total = 0
        
        # Considerar que os jogos sao jogados a cada concurso!
        custo_total_por_concurso = sum(j['custo'] for j in jogos_validos)
        custo_total_acumulado = custo_total_por_concurso * total_concursos_analisados
        
        melhor_concurso = None
        melhor_premio = -1
        
        # Apenas retornamos os utimos 10 resultados para a UI
        resultados_finais = []

        for sorteio in sorteios_filtrados:
            numeros_sorteio = {getattr(sorteio, f'posicao_{i}') for i in range(1, 8) if getattr(sorteio, f'posicao_{i}')}
            mes_sorteio = sorteio.mes_sorte
            
            premio_concurso = 0
            melhor_qtd_acertos_no_concurso = 0
            lista_acertos_no_concurso = []
            
            for jogo in jogos_validos:
                acertos = jogo['numeros_set'] & numeros_sorteio
                qtd_acertos = len(acertos)
                acertou_mes = mes_sorteio == jogo['mes']
                
                if acertou_mes:
                    total_acertos_mes += 1
                
                if qtd_acertos > melhor_qtd_acertos_no_concurso:
                    melhor_qtd_acertos_no_concurso = qtd_acertos
                    lista_acertos_no_concurso = sorted(list(acertos))
                    
                acertos_por_quantidade[min(qtd_acertos, 7)] += 1
                
                # Simulacao simplificada de premios.
                premio_local = 0
                if qtd_acertos == 7:
                    premio_local += 50000
                elif qtd_acertos == 6:
                    premio_local += 1000
                elif qtd_acertos == 5:
                    premio_local += 100
                elif qtd_acertos == 4:
                    premio_local += 10
                    
                # Premiação do mês
                if acertou_mes:
                    premio_local += 2.50 # Prêmio do mês da sorte é 2.50 (reembolso)

                # Se a aposta tem mais de 7, o prêmio multiplica. Simplificação: (calculo exato é complexo, aproximamos)
                # Combinações de acertos em N numeros.
                multiplicador = math.comb(len(jogo['numeros_set']) - qtd_acertos, 7 - qtd_acertos) if len(jogo['numeros_set']) > 7 else 1
                # Mas para calculo exato seria muito detalhado. Vamos assumir um prêmio base * multiplicacoes aproximadas.
                # Só para fins de simulação consistente, usaremos o básico:
                if len(jogo['numeros_set']) > 7:
                    # Multiplicadores Exatos Caixa Dia de Sorte
                    if qtd_acertos == 7:
                        premio_local = 50000 + (len(jogo['numeros_set']) - 7) * 1000 * math.comb(len(jogo['numeros_set']), 6) # etc
                    # simplificacao para o app:
                    premio_local *= (len(jogo['numeros_set']) - 6) # placeholder basico
                
                premio_concurso += premio_local
            
            premio_total += premio_concurso

            if premio_concurso > melhor_premio:
                melhor_premio = premio_concurso
                melhor_concurso = {
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros_sorteio': sorted(list(numeros_sorteio)),
                    'melhor_qtd_acertos': melhor_qtd_acertos_no_concurso,
                    'melhores_numeros_acertados': lista_acertos_no_concurso,
                    'premio_estimado': premio_concurso
                }
                
            resultados_finais.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros_sorteio': sorted(list(numeros_sorteio)),
                'premio_estimado': premio_concurso,
                'melhor_acertado': melhor_qtd_acertos_no_concurso
            })

        lucro_liquido = premio_total - custo_total_acumulado

        percentual_acertos = {
            k: round((v / (total_concursos_analisados * len(jogos_validos))) * 100, 2) if total_concursos_analisados else 0
            for k, v in acertos_por_quantidade.items()
        }

        return {
            'total_concursos_analisados': total_concursos_analisados,
            'custo_total_acumulado': custo_total_acumulado,
            'premio_total': premio_total,
            'lucro_liquido': lucro_liquido,
            'acertos_por_quantidade': acertos_por_quantidade,
            'percentual_acertos': percentual_acertos,
            'melhor_concurso': melhor_concurso,
            'total_acertos_mes': total_acertos_mes,
            'resultados_recentes': resultados_finais[-10:], # ultimos 10 simulados
        }

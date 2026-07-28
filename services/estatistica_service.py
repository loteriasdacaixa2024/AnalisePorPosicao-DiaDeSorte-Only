# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from models.sorteio import Sorteio, db
from sqlalchemy import func, case
from collections import Counter, defaultdict
from itertools import combinations
from math import comb
import random

class EstatisticaService:
    """
    Serviço para cálculos estatísticos dos sorteios
    Analisa frequências, atrasos e lacunas
    """
    
    @staticmethod
    def frequencia_geral():
        """
        Calcula a frequência de cada número (1-31) em todos os sorteios
        Retorna: lista de dicionários com {numero, frequencia, percentual}
        """
        try:
            todos_sorteios = Sorteio.query.all()
            
            if not todos_sorteios:
                return []
            
            total_sorteios = len(todos_sorteios)
            contador = Counter()
            
            # Contar todas as aparições
            for sorteio in todos_sorteios:
                posicoes = sorteio.get_posicoes_lista()
                contador.update(posicoes)
            
            # Montar resultado
            resultado = []
            for numero in range(1, 32):
                frequencia = contador.get(numero, 0)
                percentual = (frequencia / total_sorteios * 100) if total_sorteios > 0 else 0
                
                resultado.append({
                    'numero': numero,
                    'frequencia': frequencia,
                    'percentual': round(percentual, 2)
                })
            
            # Ordenar por frequência (decrescente)
            resultado.sort(key=lambda x: x['frequencia'], reverse=True)
            
            return resultado
            
        except Exception as e:
            print(f" [ERRO] Erro ao calcular Frequency: {str(e)}")
            return []
    
    @staticmethod
    def frequencia_por_posicao(posicao=None):
        """
        Calcula a frequência de cada número por posição específica
        Se posicao=None, retorna frequências de todas as posições
        """
        try:
            if posicao and (posicao < 1 or posicao > 7):
                return {'erro': 'Posição inválida. Deve estar entre 1 e 7'}
            
            todos_sorteios = Sorteio.query.all()
            
            if not todos_sorteios:
                return {}
            
            total_sorteios = len(todos_sorteios)
            
            # Se posição específica
            if posicao:
                coluna = f'posicao_{posicao}'
                contador = Counter()
                
                for sorteio in todos_sorteios:
                    numero = getattr(sorteio, coluna)
                    contador[numero] += 1
                
                resultado = []
                for numero in range(1, 32):
                    frequencia = contador.get(numero, 0)
                    percentual = (frequencia / total_sorteios * 100) if total_sorteios > 0 else 0
                    
                    resultado.append({
                        'numero': numero,
                        'frequencia': frequencia,
                        'percentual': round(percentual, 2)
                    })
                
                resultado.sort(key=lambda x: x['frequencia'], reverse=True)
                
                return {
                    'posicao': posicao,
                    'total_sorteios': total_sorteios,
                    'numeros': resultado
                }
            
            # Todas as posições
            resultado_completo = {}
            
            for pos in range(1, 8):
                coluna = f'posicao_{pos}'
                contador = Counter()
                
                for sorteio in todos_sorteios:
                    numero = getattr(sorteio, coluna)
                    contador[numero] += 1
                
                numeros = []
                for numero in range(1, 32):
                    frequencia = contador.get(numero, 0)
                    percentual = (frequencia / total_sorteios * 100) if total_sorteios > 0 else 0
                    
                    numeros.append({
                        'numero': numero,
                        'frequencia': frequencia,
                        'percentual': round(percentual, 2)
                    })
                
                numeros.sort(key=lambda x: x['frequencia'], reverse=True)
                
                resultado_completo[f'posicao_{pos}'] = {
                    'numeros': numeros,
                    'mais_frequente': numeros[0] if numeros else None
                }
            
            resultado_completo['total_sorteios'] = total_sorteios
            
            return resultado_completo
            
        except Exception as e:
            print(f"❌ Erro ao calcular frequência por posição: {str(e)}")
            return {}
    
    @staticmethod
    def numeros_atrasados(posicao=None, limite=10):
        """
        Calcula os números mais atrasados (que não saem há mais tempo)
        Se posicao=None, analisa todas as posições
        """
        try:
            # Buscar último concurso
            ultimo_sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
            
            if not ultimo_sorteio:
                return []
            
            ultimo_concurso = ultimo_sorteio.concurso
            
            # Se posição específica
            if posicao:
                if posicao < 1 or posicao > 7:
                    return {'erro': 'Posição inválida'}
                
                coluna = f'posicao_{posicao}'
                atrasos = {}
                
                # Para cada número, buscar última aparição
                for numero in range(1, 32):
                    ultima_aparicao = Sorteio.query.filter(
                        getattr(Sorteio, coluna) == numero
                    ).order_by(Sorteio.concurso.desc()).first()
                    
                    if ultima_aparicao:
                        atraso = ultimo_concurso - ultima_aparicao.concurso
                    else:
                        atraso = ultimo_concurso  # Nunca saiu
                    
                    atrasos[numero] = {
                        'numero': numero,
                        'atraso': atraso,
                        'ultimo_concurso': ultima_aparicao.concurso if ultima_aparicao else None,
                        'ultima_data': ultima_aparicao.data_sorteio.strftime('%d/%m/%Y') if ultima_aparicao else 'Nunca'
                    }
                
                # Ordenar por atraso
                resultado = sorted(atrasos.values(), key=lambda x: x['atraso'], reverse=True)
                
                return {
                    'posicao': posicao,
                    'ultimo_concurso': ultimo_concurso,
                    'numeros_atrasados': resultado[:limite]
                }
            
            # Atraso geral (qualquer posição)
            atrasos = {}
            
            for numero in range(1, 32):
                ultima_aparicao = Sorteio.query.filter(
                    (Sorteio.posicao_1 == numero) |
                    (Sorteio.posicao_2 == numero) |
                    (Sorteio.posicao_3 == numero) |
                    (Sorteio.posicao_4 == numero) |
                    (Sorteio.posicao_5 == numero) |
                    (Sorteio.posicao_6 == numero) |
                    (Sorteio.posicao_7 == numero)
                ).order_by(Sorteio.concurso.desc()).first()
                
                if ultima_aparicao:
                    atraso = ultimo_concurso - ultima_aparicao.concurso
                else:
                    atraso = ultimo_concurso
                
                atrasos[numero] = {
                    'numero': numero,
                    'atraso': atraso,
                    'ultimo_concurso': ultima_aparicao.concurso if ultima_aparicao else None,
                    'ultima_data': ultima_aparicao.data_sorteio.strftime('%d/%m/%Y') if ultima_aparicao else 'Nunca'
                }
            
            resultado = sorted(atrasos.values(), key=lambda x: x['atraso'], reverse=True)
            
            return {
                'ultimo_concurso': ultimo_concurso,
                'numeros_atrasados': resultado[:limite]
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular números atrasados: {str(e)}")
            return []
    
    @staticmethod
    def lacunas_temporais(numero, posicao=None):
        """
        Calcula as lacunas (intervalos) entre aparições de um número
        Retorna: média, mínima, máxima e todas as lacunas
        """
        try:
            if numero < 1 or numero > 31:
                return {'erro': 'Número inválido'}
            
            if posicao:
                if posicao < 1 or posicao > 7:
                    return {'erro': 'Posição inválida'}
                
                coluna = f'posicao_{posicao}'
                sorteios = Sorteio.query.filter(
                    getattr(Sorteio, coluna) == numero
                ).order_by(Sorteio.concurso.asc()).all()
            else:
                sorteios = Sorteio.query.filter(
                    (Sorteio.posicao_1 == numero) |
                    (Sorteio.posicao_2 == numero) |
                    (Sorteio.posicao_3 == numero) |
                    (Sorteio.posicao_4 == numero) |
                    (Sorteio.posicao_5 == numero) |
                    (Sorteio.posicao_6 == numero) |
                    (Sorteio.posicao_7 == numero)
                ).order_by(Sorteio.concurso.asc()).all()
            
            if len(sorteios) < 2:
                return {
                    'numero': numero,
                    'posicao': posicao,
                    'total_aparicoes': len(sorteios),
                    'mensagem': 'Número apareceu menos de 2 vezes'
                }
            
            # Calcular lacunas
            lacunas = []
            for i in range(1, len(sorteios)):
                lacuna = sorteios[i].concurso - sorteios[i-1].concurso
                lacunas.append(lacuna)
            
            # Estatísticas
            media = sum(lacunas) / len(lacunas)
            minima = min(lacunas)
            maxima = max(lacunas)
            
            return {
                'numero': numero,
                'posicao': posicao,
                'total_aparicoes': len(sorteios),
                'lacunas': {
                    'media': round(media, 2),
                    'minima': minima,
                    'maxima': maxima,
                    'total_lacunas': len(lacunas),
                    'todas': lacunas[:20]  # Primeiras 20 lacunas
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular lacunas temporais: {str(e)}")
            return {}
    
    @staticmethod
    def estatisticas_mes_sorte():
        """
        Calcula estatísticas do mês da sorte
        Retorna frequência de cada mês
        """
        try:
            todos_sorteios = Sorteio.query.all()
            
            if not todos_sorteios:
                return []
            
            total_sorteios = len(todos_sorteios)
            contador = Counter()
            
            for sorteio in todos_sorteios:
                contador[sorteio.mes_sorte] += 1
            
            meses_nomes = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
                4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro',
                10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            
            resultado = []
            for mes in range(1, 13):
                frequencia = contador.get(mes, 0)
                percentual = (frequencia / total_sorteios * 100) if total_sorteios > 0 else 0
                
                resultado.append({
                    'mes': mes,
                    'nome': meses_nomes[mes],
                    'frequencia': frequencia,
                    'percentual': round(percentual, 2)
                })
            
            resultado.sort(key=lambda x: x['frequencia'], reverse=True)
            
            return {
                'total_sorteios': total_sorteios,
                'meses': resultado,
                'mais_sorteado': resultado[0] if resultado else None,
                'menos_sorteado': resultado[-1] if resultado else None
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular estatísticas do mês: {str(e)}")
            return {}
    
    @staticmethod
    def resumo_estatistico():
        """
        Retorna um resumo completo das estatísticas
        """
        try:
            return {
                'frequencia_geral': EstatisticaService.frequencia_geral()[:10],
                'numeros_atrasados': EstatisticaService.numeros_atrasados(limite=10),
                'mes_sorte': EstatisticaService.estatisticas_mes_sorte(),
                'total_sorteios': Sorteio.query.count()
            }
        except Exception as e:
            print(f"❌ Erro ao gerar resumo: {str(e)}")
            return {}

    @staticmethod
    def numeros_disponiveis_posicao(posicao):
        """
        Retorna os números que JÁ APARECERAM em uma posição específica.
        Números que nunca apareceram não são retornados.

        Args:
            posicao: Posição a verificar (1-7)

        Returns:
            Dicionário com números disponíveis e indisponíveis
        """
        try:
            if posicao < 1 or posicao > 7:
                return {'erro': 'Posição inválida. Deve estar entre 1 e 7'}

            coluna = f'posicao_{posicao}'
            todos_sorteios = Sorteio.query.all()

            if not todos_sorteios:
                return {
                    'posicao': posicao,
                    'disponiveis': [],
                    'indisponiveis': list(range(1, 32)),
                    'total_disponiveis': 0,
                    'total_indisponiveis': 31
                }

            # Contar frequência de cada número na posição
            contador = Counter()
            for sorteio in todos_sorteios:
                numero = getattr(sorteio, coluna)
                contador[numero] += 1

            # Separar disponíveis (frequência > 0) e indisponíveis (frequência = 0)
            disponiveis = []
            indisponiveis = []

            for numero in range(1, 32):
                freq = contador.get(numero, 0)
                if freq > 0:
                    disponiveis.append({
                        'numero': numero,
                        'frequencia': freq
                    })
                else:
                    indisponiveis.append(numero)

            # Ordenar disponíveis por número (para exibição no select)
            disponiveis.sort(key=lambda x: x['numero'])

            return {
                'posicao': posicao,
                'disponiveis': disponiveis,
                'indisponiveis': indisponiveis,
                'total_disponiveis': len(disponiveis),
                'total_indisponiveis': len(indisponiveis)
            }

        except Exception as e:
            print(f"❌ Erro ao buscar números disponíveis: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def analise_filtrada(posicao, numero):
        """
        Analisa a frequência de números que aparecem junto com um número específico
        em uma posição específica.

        Ex: Se filtrar posição 1 com número 1, retorna quais números mais aparecem
        nas posições 2-7 quando o 1 está na posição 1.

        Args:
            posicao: Posição do filtro (1-7)
            numero: Número a filtrar (1-31)

        Returns:
            Dicionário com frequências, insights e recomendações
        """
        try:
            if posicao < 1 or posicao > 7:
                return {'erro': 'Posição inválida. Deve estar entre 1 e 7'}

            if numero < 1 or numero > 31:
                return {'erro': 'Número inválido. Deve estar entre 1 e 31'}

            # Buscar sorteios onde o número aparece na posição especificada
            coluna_filtro = f'posicao_{posicao}'
            sorteios_filtrados = Sorteio.query.filter(
                getattr(Sorteio, coluna_filtro) == numero
            ).all()

            if not sorteios_filtrados:
                return {
                    'posicao_filtrada': posicao,
                    'numero_filtrado': numero,
                    'total_ocorrencias': 0,
                    'mensagem': f'O número {numero} nunca apareceu na posição {posicao}'
                }

            total_ocorrencias = len(sorteios_filtrados)

            # Contar frequência de todos os números nas OUTRAS posições
            contador_geral = Counter()
            contadores_por_posicao = {i: Counter() for i in range(1, 8) if i != posicao}

            for sorteio in sorteios_filtrados:
                for pos in range(1, 8):
                    if pos != posicao:  # Ignorar a posição filtrada
                        num = getattr(sorteio, f'posicao_{pos}')
                        contador_geral[num] += 1
                        contadores_por_posicao[pos][num] += 1

            # Montar ranking geral (números que mais aparecem)
            ranking_geral = []
            for num, freq in contador_geral.most_common():
                percentual = (freq / (total_ocorrencias * 6) * 100)  # 6 posições restantes
                ranking_geral.append({
                    'numero': num,
                    'frequencia': freq,
                    'percentual': round(percentual, 2)
                })

            # Montar ranking por posição
            ranking_por_posicao = {}
            for pos, contador in contadores_por_posicao.items():
                ranking_pos = []
                for num, freq in contador.most_common(10):  # Top 10 por posição
                    percentual = (freq / total_ocorrencias * 100)
                    ranking_pos.append({
                        'numero': num,
                        'frequencia': freq,
                        'percentual': round(percentual, 2)
                    })
                ranking_por_posicao[f'posicao_{pos}'] = ranking_pos

            # Gerar INSIGHTS INTELIGENTES
            insights = EstatisticaService._gerar_insights_filtro(
                numero, posicao, ranking_geral, ranking_por_posicao, total_ocorrencias
            )

            # Gerar RECOMENDAÇÕES ESTRATÉGICAS
            recomendacoes = EstatisticaService._gerar_recomendacoes(
                numero, posicao, ranking_geral, ranking_por_posicao
            )

            # Estatísticas do mês da sorte nos sorteios filtrados
            contador_mes = Counter()
            for sorteio in sorteios_filtrados:
                contador_mes[sorteio.mes_sorte] += 1

            meses_nomes = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
                4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro',
                10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }

            meses_frequentes = []
            for mes, freq in contador_mes.most_common():
                meses_frequentes.append({
                    'mes': mes,
                    'nome': meses_nomes.get(mes, 'Desconhecido'),
                    'frequencia': freq,
                    'percentual': round((freq / total_ocorrencias * 100), 2)
                })

            return {
                'posicao_filtrada': posicao,
                'numero_filtrado': numero,
                'total_ocorrencias': total_ocorrencias,
                'total_sorteios_banco': Sorteio.query.count(),
                'percentual_aparicao': round((total_ocorrencias / Sorteio.query.count() * 100), 2),
                'ranking_geral': ranking_geral[:15],  # Top 15
                'ranking_por_posicao': ranking_por_posicao,
                'meses_frequentes': meses_frequentes,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            print(f"❌ Erro ao calcular análise filtrada: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def _gerar_insights_filtro(numero, posicao, ranking_geral, ranking_por_posicao, total):
        """
        Gera insights inteligentes baseados na análise filtrada
        """
        insights = []

        # Insight 1: Número mais frequente
        if ranking_geral:
            top1 = ranking_geral[0]
            insights.append({
                'tipo': 'destaque',
                'icone': '🏆',
                'titulo': 'Número Campeão',
                'descricao': f"Quando o {numero} aparece na posição {posicao}, o número {top1['numero']} é o mais frequente nas outras posições ({top1['frequencia']}x - {top1['percentual']}%)"
            })

        # Insight 2: Top 3 companheiros
        if len(ranking_geral) >= 3:
            top3 = [str(r['numero']) for r in ranking_geral[:3]]
            insights.append({
                'tipo': 'info',
                'icone': '🎯',
                'titulo': 'Trio de Ouro',
                'descricao': f"Os 3 números que mais acompanham o {numero} são: {', '.join(top3)}"
            })

        # Insight 3: Frequência de aparição
        insights.append({
            'tipo': 'estatistica',
            'icone': '📊',
            'titulo': 'Taxa de Aparição',
            'descricao': f"O número {numero} apareceu {total} vezes na posição {posicao}"
        })

        # Insight 4: Melhor posição para cada top número
        if ranking_por_posicao:
            melhores_posicoes = []
            for pos_key, nums in ranking_por_posicao.items():
                if nums:
                    pos_num = int(pos_key.split('_')[1])
                    melhores_posicoes.append(f"P{pos_num}: {nums[0]['numero']}")

            if melhores_posicoes:
                insights.append({
                    'tipo': 'estrategia',
                    'icone': '🎲',
                    'titulo': 'Melhores por Posição',
                    'descricao': f"Top 1 em cada posição: {' | '.join(melhores_posicoes)}"
                })

        # Insight 5: Números que NUNCA aparecem junto
        numeros_ausentes = []
        numeros_presentes = set(r['numero'] for r in ranking_geral)
        for n in range(1, 32):
            if n != numero and n not in numeros_presentes:
                numeros_ausentes.append(n)

        if numeros_ausentes:
            insights.append({
                'tipo': 'alerta',
                'icone': '⚠️',
                'titulo': 'Números Ausentes',
                'descricao': f"Nunca aparecem com {numero} na P{posicao}: {', '.join(map(str, numeros_ausentes[:5]))}" + (f" (+{len(numeros_ausentes)-5} mais)" if len(numeros_ausentes) > 5 else "")
            })

        return insights

    @staticmethod
    def _gerar_recomendacoes(numero, posicao, ranking_geral, ranking_por_posicao):
        """
        Gera recomendações estratégicas para palpites
        """
        recomendacoes = []

        # Recomendação 1: Jogo sugerido baseado em frequência
        if ranking_por_posicao:
            jogo_sugerido = [numero]  # Começar com o número filtrado

            for pos in range(1, 8):
                if pos != posicao:
                    pos_key = f'posicao_{pos}'
                    if pos_key in ranking_por_posicao and ranking_por_posicao[pos_key]:
                        # Pegar o mais frequente que ainda não está no jogo
                        for candidato in ranking_por_posicao[pos_key]:
                            if candidato['numero'] not in jogo_sugerido:
                                jogo_sugerido.append(candidato['numero'])
                                break

            jogo_sugerido.sort()
            if len(jogo_sugerido) == 7:
                recomendacoes.append({
                    'tipo': 'jogo_principal',
                    'icone': '⭐',
                    'titulo': 'Jogo Recomendado (Frequência)',
                    'numeros': jogo_sugerido,
                    'descricao': 'Baseado nos números mais frequentes em cada posição'
                })

        # Recomendação 2: Top 7 geral
        if len(ranking_geral) >= 6:
            top7_geral = [numero] + [r['numero'] for r in ranking_geral[:6] if r['numero'] != numero]
            top7_geral = list(set(top7_geral))[:7]
            top7_geral.sort()

            if len(top7_geral) >= 7:
                recomendacoes.append({
                    'tipo': 'jogo_alternativo',
                    'icone': '🎯',
                    'titulo': 'Jogo Alternativo (Top Frequência)',
                    'numeros': top7_geral[:7],
                    'descricao': 'Os 7 números mais frequentes quando filtrado'
                })

        # Recomendação 3: Mix estratégico (frequentes + menos frequentes)
        if len(ranking_geral) >= 10:
            # 4 mais frequentes + 3 intermediários
            mix = [numero]
            frequentes = [r['numero'] for r in ranking_geral[:4] if r['numero'] != numero]
            intermediarios = [r['numero'] for r in ranking_geral[5:10] if r['numero'] != numero]

            mix.extend(frequentes[:3])
            mix.extend(intermediarios[:3])
            mix = list(set(mix))[:7]
            mix.sort()

            if len(mix) >= 7:
                recomendacoes.append({
                    'tipo': 'jogo_mix',
                    'icone': '🔀',
                    'titulo': 'Jogo Mix Estratégico',
                    'numeros': mix[:7],
                    'descricao': 'Combinação de frequentes e intermediários'
                })

        # Recomendação 4: Dicas gerais
        recomendacoes.append({
            'tipo': 'dica',
            'icone': '💡',
            'titulo': 'Dica Estratégica',
            'descricao': f'Considere usar o {numero} na posição {posicao} como base do seu jogo, combinando com os números do ranking'
        })

        return recomendacoes

    # ============================================
    # GERADOR DE PALPITES - Combinações Válidas
    # ============================================

    @staticmethod
    def _obter_numeros_disponiveis_por_posicao():
        """
        Obtém os conjuntos de números disponíveis para cada posição
        baseado no histórico de sorteios.
        """
        todos_sorteios = Sorteio.query.all()

        if not todos_sorteios:
            return None

        posicoes_disponiveis = {}

        for pos in range(1, 8):
            coluna = f'posicao_{pos}'
            numeros = set()

            for sorteio in todos_sorteios:
                numero = getattr(sorteio, coluna)
                numeros.add(numero)

            posicoes_disponiveis[pos] = numeros

        return posicoes_disponiveis

    @staticmethod
    def _obter_sorteios_realizados():
        """
        Retorna um set com todas as combinações já sorteadas
        (como tuplas ordenadas para comparação)
        """
        todos_sorteios = Sorteio.query.all()
        sorteados = set()

        for sorteio in todos_sorteios:
            combo = tuple(sorted([
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]))
            sorteados.add(combo)

        return sorteados

    @staticmethod
    def _tem_ordem_valida(combo, posicoes_disponiveis):
        """
        Verifica se existe pelo menos uma permutação da combinação
        onde cada número está em uma posição válida.
        Usa backtracking para eficiência.
        """
        numeros = list(combo)
        n = len(numeros)
        usado = [False] * n

        def backtrack(pos):
            if pos == 7:
                return True  # Encontrou uma ordem válida!

            for i in range(n):
                if not usado[i] and numeros[i] in posicoes_disponiveis[pos + 1]:
                    usado[i] = True
                    if backtrack(pos + 1):
                        return True
                    usado[i] = False

            return False

        return backtrack(0)

    @staticmethod
    def calcular_combinacoes_validas():
        """
        Calcula estatísticas de combinações válidas vs impossíveis.
        Considera combinações que têm pelo menos uma ordem de sorteio válida.
        Desconta as combinações já sorteadas.
        """
        try:
            posicoes_disponiveis = EstatisticaService._obter_numeros_disponiveis_por_posicao()

            if not posicoes_disponiveis:
                return {'erro': 'Nenhum sorteio encontrado no banco'}

            sorteados = EstatisticaService._obter_sorteios_realizados()
            total_sorteados = len(sorteados)

            # Total de combinações possíveis
            total_combinacoes = comb(31, 7)

            # Contar combinações válidas e impossíveis
            combinacoes_validas = 0
            combinacoes_impossiveis = 0

            # Lista para guardar algumas impossíveis como exemplo
            exemplos_impossiveis = []

            for combo in combinations(range(1, 32), 7):
                if EstatisticaService._tem_ordem_valida(combo, posicoes_disponiveis):
                    combinacoes_validas += 1
                else:
                    combinacoes_impossiveis += 1
                    if len(exemplos_impossiveis) < 50:
                        exemplos_impossiveis.append(list(combo))

            # Descontar as já sorteadas
            combinacoes_disponiveis = combinacoes_validas - total_sorteados

            # Calcular percentuais
            percentual_validas = (combinacoes_validas / total_combinacoes) * 100
            percentual_impossiveis = (combinacoes_impossiveis / total_combinacoes) * 100

            # Informações sobre números por posição
            info_posicoes = []
            for pos in range(1, 8):
                disponiveis = sorted(posicoes_disponiveis[pos])
                indisponiveis = sorted(set(range(1, 32)) - posicoes_disponiveis[pos])
                info_posicoes.append({
                    'posicao': pos,
                    'total_disponiveis': len(disponiveis),
                    'total_indisponiveis': len(indisponiveis),
                    'disponiveis': disponiveis,
                    'indisponiveis': indisponiveis
                })

            return {
                'total_combinacoes': total_combinacoes,
                'combinacoes_validas': combinacoes_validas,
                'combinacoes_impossiveis': combinacoes_impossiveis,
                'ja_sorteadas': total_sorteados,
                'combinacoes_disponiveis': combinacoes_disponiveis,
                'percentual_validas': round(percentual_validas, 2),
                'percentual_impossiveis': round(percentual_impossiveis, 2),
                'reducao': round(percentual_impossiveis, 2),
                'info_posicoes': info_posicoes,
                'exemplos_impossiveis': exemplos_impossiveis[:20]
            }

        except Exception as e:
            print(f"❌ Erro ao calcular combinações válidas: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def listar_combinacoes_impossiveis(pagina=1, por_pagina=100):
        """
        Lista todas as combinações impossíveis com paginação.
        """
        try:
            posicoes_disponiveis = EstatisticaService._obter_numeros_disponiveis_por_posicao()

            if not posicoes_disponiveis:
                return {'erro': 'Nenhum sorteio encontrado no banco'}

            # Coletar todas as impossíveis
            impossiveis = []

            for combo in combinations(range(1, 32), 7):
                if not EstatisticaService._tem_ordem_valida(combo, posicoes_disponiveis):
                    impossiveis.append(list(combo))

            # Paginação
            total = len(impossiveis)
            inicio = (pagina - 1) * por_pagina
            fim = inicio + por_pagina

            return {
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total_paginas': (total + por_pagina - 1) // por_pagina,
                'combinacoes': impossiveis[inicio:fim]
            }

        except Exception as e:
            print(f"❌ Erro ao listar combinações impossíveis: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def gerar_palpites(quantidade=10):
        """
        Gera palpites válidos aleatórios.
        - Usa apenas combinações válidas (com pelo menos uma ordem de sorteio possível)
        - Exclui combinações já sorteadas
        - Garante que não há palpites repetidos
        """
        try:
            posicoes_disponiveis = EstatisticaService._obter_numeros_disponiveis_por_posicao()

            if not posicoes_disponiveis:
                return {'erro': 'Nenhum sorteio encontrado no banco'}

            sorteados = EstatisticaService._obter_sorteios_realizados()

            # Coletar todas as combinações válidas que não foram sorteadas
            combinacoes_validas = []

            for combo in combinations(range(1, 32), 7):
                combo_ordenada = tuple(sorted(combo))

                # Verificar se não foi sorteada
                if combo_ordenada in sorteados:
                    continue

                # Verificar se tem ordem válida
                if EstatisticaService._tem_ordem_valida(combo, posicoes_disponiveis):
                    combinacoes_validas.append(list(combo))

            # Limitar quantidade ao disponível
            quantidade = min(quantidade, len(combinacoes_validas))

            # Selecionar aleatoriamente
            palpites = random.sample(combinacoes_validas, quantidade)

            # Ordenar cada palpite
            palpites = [sorted(p) for p in palpites]

            return {
                'quantidade_solicitada': quantidade,
                'quantidade_gerada': len(palpites),
                'total_disponiveis': len(combinacoes_validas),
                'palpites': palpites
            }

        except Exception as e:
            print(f"❌ Erro ao gerar palpites: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def ultimo_sorteio():
        """
        Retorna os dados do último sorteio registrado.
        Útil para referência ao gerar palpites (números que se repetem).
        """
        try:
            ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

            if not ultimo:
                return {'erro': 'Nenhum sorteio encontrado'}

            meses_nomes = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
                4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro',
                10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }

            return {
                'concurso': ultimo.concurso,
                'data_sorteio': ultimo.data_sorteio.strftime('%d/%m/%Y') if ultimo.data_sorteio else None,
                'posicao_1': ultimo.posicao_1,
                'posicao_2': ultimo.posicao_2,
                'posicao_3': ultimo.posicao_3,
                'posicao_4': ultimo.posicao_4,
                'posicao_5': ultimo.posicao_5,
                'posicao_6': ultimo.posicao_6,
                'posicao_7': ultimo.posicao_7,
                'mes_sorte': meses_nomes.get(ultimo.mes_sorte, str(ultimo.mes_sorte)),
                'numeros_ordenados': sorted([
                    ultimo.posicao_1, ultimo.posicao_2, ultimo.posicao_3,
                    ultimo.posicao_4, ultimo.posicao_5, ultimo.posicao_6,
                    ultimo.posicao_7
                ])
            }

        except Exception as e:
            print(f"❌ Erro ao buscar último sorteio: {str(e)}")
            return {'erro': str(e)}

    # ============================================
    # NOVAS ANÁLISES POR POSIÇÃO
    # ============================================

    @staticmethod
    def atraso_por_posicao():
        """
        Calcula o atraso de cada número em CADA posição específica.
        Diferente do atraso geral, mostra há quantos concursos cada número
        não aparece em cada posição.
        """
        try:
            ultimo_sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

            if not ultimo_sorteio:
                return {'erro': 'Nenhum sorteio encontrado'}

            ultimo_concurso = ultimo_sorteio.concurso
            resultado = {}

            for pos in range(1, 8):
                coluna = f'posicao_{pos}'
                atrasos = []

                for numero in range(1, 32):
                    # Buscar última aparição deste número NESTA posição
                    ultima_aparicao = Sorteio.query.filter(
                        getattr(Sorteio, coluna) == numero
                    ).order_by(Sorteio.concurso.desc()).first()

                    if ultima_aparicao:
                        atraso = ultimo_concurso - ultima_aparicao.concurso
                        ultimo_conc = ultima_aparicao.concurso
                        ultima_data = ultima_aparicao.data_sorteio.strftime('%d/%m/%Y') if ultima_aparicao.data_sorteio else 'N/A'
                    else:
                        atraso = 9999  # Nunca apareceu nesta posição
                        ultimo_conc = None
                        ultima_data = 'Nunca'

                    atrasos.append({
                        'numero': numero,
                        'atraso': atraso,
                        'ultimo_concurso': ultimo_conc,
                        'ultima_data': ultima_data,
                        'nunca_apareceu': ultimo_conc is None
                    })

                # Ordenar por atraso (decrescente) - os mais atrasados primeiro
                atrasos.sort(key=lambda x: x['atraso'], reverse=True)

                # Separar: nunca apareceram vs já apareceram
                nunca_apareceram = [a for a in atrasos if a['nunca_apareceu']]
                ja_apareceram = [a for a in atrasos if not a['nunca_apareceu']]

                resultado[f'posicao_{pos}'] = {
                    'top_atrasados': ja_apareceram[:10],
                    'nunca_apareceram': [a['numero'] for a in nunca_apareceram],
                    'total_nunca': len(nunca_apareceram),
                    'total_ja_apareceram': len(ja_apareceram)
                }

            resultado['ultimo_concurso'] = ultimo_concurso

            return resultado

        except Exception as e:
            print(f"❌ Erro ao calcular atraso por posição: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def faixas_por_posicao():
        """
        Analisa a distribuição de faixas (baixos/médios/altos) em cada posição.
        - Baixos: 1-10
        - Médios: 11-20
        - Altos: 21-31
        """
        try:
            todos_sorteios = Sorteio.query.all()

            if not todos_sorteios:
                return {'erro': 'Nenhum sorteio encontrado'}

            total_sorteios = len(todos_sorteios)
            resultado = {}

            for pos in range(1, 8):
                coluna = f'posicao_{pos}'
                baixos = 0
                medios = 0
                altos = 0

                for sorteio in todos_sorteios:
                    numero = getattr(sorteio, coluna)
                    if numero <= 10:
                        baixos += 1
                    elif numero <= 20:
                        medios += 1
                    else:
                        altos += 1

                resultado[f'posicao_{pos}'] = {
                    'baixos': {
                        'quantidade': baixos,
                        'percentual': round((baixos / total_sorteios) * 100, 1),
                        'faixa': '01-10'
                    },
                    'medios': {
                        'quantidade': medios,
                        'percentual': round((medios / total_sorteios) * 100, 1),
                        'faixa': '11-20'
                    },
                    'altos': {
                        'quantidade': altos,
                        'percentual': round((altos / total_sorteios) * 100, 1),
                        'faixa': '21-31'
                    },
                    'dominante': 'baixos' if baixos >= medios and baixos >= altos else ('medios' if medios >= altos else 'altos')
                }

            resultado['total_sorteios'] = total_sorteios

            # Resumo geral: qual faixa domina cada posição
            resumo = []
            for pos in range(1, 8):
                dados = resultado[f'posicao_{pos}']
                resumo.append({
                    'posicao': pos,
                    'dominante': dados['dominante'],
                    'percentual': dados[dados['dominante']]['percentual']
                })

            resultado['resumo'] = resumo

            return resultado

        except Exception as e:
            print(f"❌ Erro ao calcular faixas por posição: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def frequencia_relativa_por_posicao():
        """
        Calcula a frequência relativa de cada número em cada posição.
        Mostra em qual posição cada número "prefere" aparecer.
        Ex: Número 15 aparece 35% das vezes na P5, 25% na P4, etc.
        """
        try:
            todos_sorteios = Sorteio.query.all()

            if not todos_sorteios:
                return {'erro': 'Nenhum sorteio encontrado'}

            total_sorteios = len(todos_sorteios)

            # Contar aparições de cada número em cada posição
            contagem = {}
            for numero in range(1, 32):
                contagem[numero] = {pos: 0 for pos in range(1, 8)}

            for sorteio in todos_sorteios:
                for pos in range(1, 8):
                    numero = getattr(sorteio, f'posicao_{pos}')
                    contagem[numero][pos] += 1

            # Calcular frequência relativa (por número)
            resultado_por_numero = {}
            for numero in range(1, 32):
                total_aparicoes = sum(contagem[numero].values())

                posicoes = []
                melhor_posicao = None
                melhor_percentual = 0

                for pos in range(1, 8):
                    freq = contagem[numero][pos]
                    if total_aparicoes > 0:
                        percentual = round((freq / total_aparicoes) * 100, 1)
                    else:
                        percentual = 0

                    posicoes.append({
                        'posicao': pos,
                        'frequencia': freq,
                        'percentual': percentual
                    })

                    if percentual > melhor_percentual:
                        melhor_percentual = percentual
                        melhor_posicao = pos

                resultado_por_numero[numero] = {
                    'total_aparicoes': total_aparicoes,
                    'melhor_posicao': melhor_posicao,
                    'melhor_percentual': melhor_percentual,
                    'distribuicao': posicoes
                }

            # Calcular frequência relativa (por posição) - visão invertida
            resultado_por_posicao = {}
            for pos in range(1, 8):
                numeros = []
                for numero in range(1, 32):
                    freq = contagem[numero][pos]
                    percentual = round((freq / total_sorteios) * 100, 1)
                    numeros.append({
                        'numero': numero,
                        'frequencia': freq,
                        'percentual': percentual
                    })

                # Ordenar por frequência
                numeros.sort(key=lambda x: x['frequencia'], reverse=True)

                resultado_por_posicao[f'posicao_{pos}'] = {
                    'top_5': numeros[:5],
                    'todos': numeros
                }

            return {
                'por_numero': resultado_por_numero,
                'por_posicao': resultado_por_posicao,
                'total_sorteios': total_sorteios
            }

        except Exception as e:
            print(f"❌ Erro ao calcular frequência relativa: {str(e)}")
            return {'erro': str(e)}

    # ============================================
    # FILTROS DE ORDENAÇÃO (para validar palpites)
    # ============================================

    @staticmethod
    def analisar_estatisticas_ordenacao():
        """
        Analisa estatísticas de ORDENAÇÃO do histórico:
        - Distribuição de soma
        - Distribuição pares/ímpares
        - Distribuição por faixas (baixos/médios/altos)
        - Padrões de sequências
        """
        try:
            todos_sorteios = Sorteio.query.all()

            if not todos_sorteios:
                return {'erro': 'Nenhum sorteio encontrado'}

            total = len(todos_sorteios)

            # 1. Análise de SOMA
            somas = []
            for sorteio in todos_sorteios:
                nums = sorteio.get_posicoes_lista()
                somas.append(sum(nums))

            soma_min = min(somas)
            soma_max = max(somas)
            soma_media = sum(somas) / len(somas)

            # Distribuição de somas em faixas
            faixas_soma = {
                '70-90': 0, '91-110': 0, '111-130': 0,
                '131-150': 0, '151-170': 0, '171+': 0
            }
            for s in somas:
                if s <= 90:
                    faixas_soma['70-90'] += 1
                elif s <= 110:
                    faixas_soma['91-110'] += 1
                elif s <= 130:
                    faixas_soma['111-130'] += 1
                elif s <= 150:
                    faixas_soma['131-150'] += 1
                elif s <= 170:
                    faixas_soma['151-170'] += 1
                else:
                    faixas_soma['171+'] += 1

            # 2. Análise de PARES x ÍMPARES
            distribuicao_paridade = Counter()
            for sorteio in todos_sorteios:
                nums = sorteio.get_posicoes_lista()
                pares = sum(1 for n in nums if n % 2 == 0)
                impares = 7 - pares
                distribuicao_paridade[f'{pares}P/{impares}I'] += 1

            paridade_ordenada = sorted(
                [{'padrao': k, 'quantidade': v, 'percentual': round((v/total)*100, 1)}
                 for k, v in distribuicao_paridade.items()],
                key=lambda x: x['quantidade'], reverse=True
            )

            # 3. Análise de DISTRIBUIÇÃO (baixos/médios/altos)
            distribuicao_faixas = Counter()
            for sorteio in todos_sorteios:
                nums = sorteio.get_posicoes_lista()
                baixos = sum(1 for n in nums if n <= 10)
                medios = sum(1 for n in nums if 11 <= n <= 20)
                altos = sum(1 for n in nums if n >= 21)
                distribuicao_faixas[f'{baixos}B/{medios}M/{altos}A'] += 1

            faixas_ordenadas = sorted(
                [{'padrao': k, 'quantidade': v, 'percentual': round((v/total)*100, 1)}
                 for k, v in distribuicao_faixas.items()],
                key=lambda x: x['quantidade'], reverse=True
            )

            # 4. Análise de SEQUÊNCIAS (números consecutivos)
            distribuicao_sequencias = Counter()
            for sorteio in todos_sorteios:
                nums = sorted(sorteio.get_posicoes_lista())
                max_seq = 1
                seq_atual = 1

                for i in range(1, len(nums)):
                    if nums[i] == nums[i-1] + 1:
                        seq_atual += 1
                        max_seq = max(max_seq, seq_atual)
                    else:
                        seq_atual = 1

                distribuicao_sequencias[f'max_{max_seq}'] += 1

            sequencias_ordenadas = sorted(
                [{'max_sequencia': int(k.split('_')[1]), 'quantidade': v, 'percentual': round((v/total)*100, 1)}
                 for k, v in distribuicao_sequencias.items()],
                key=lambda x: x['max_sequencia']
            )

            return {
                'total_sorteios': total,
                'soma': {
                    'minima': soma_min,
                    'maxima': soma_max,
                    'media': round(soma_media, 1),
                    'faixas': {k: {'quantidade': v, 'percentual': round((v/total)*100, 1)} for k, v in faixas_soma.items()},
                    'recomendado': {'min': 95, 'max': 155}
                },
                'paridade': {
                    'distribuicao': paridade_ordenada,
                    'mais_comum': paridade_ordenada[0] if paridade_ordenada else None,
                    'recomendado': ['3P/4I', '4P/3I', '2P/5I', '5P/2I']
                },
                'faixas': {
                    'distribuicao': faixas_ordenadas[:10],
                    'mais_comum': faixas_ordenadas[0] if faixas_ordenadas else None,
                    'recomendado': ['2B/3M/2A', '2B/2M/3A', '3B/2M/2A', '1B/3M/3A']
                },
                'sequencias': {
                    'distribuicao': sequencias_ordenadas,
                    'recomendado': {'max': 3}
                }
            }

        except Exception as e:
            print(f"❌ Erro ao analisar estatísticas de ordenação: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def validar_palpite_ordenacao(numeros, filtros=None):
        """
        Valida um palpite usando critérios de ORDENAÇÃO.
        Retorna se passou ou não em cada filtro.
        """
        if len(numeros) != 7:
            return {'erro': 'Palpite deve ter 7 números'}

        if filtros is None:
            filtros = {
                'soma_min': 95,
                'soma_max': 155,
                'paridade': ['2P/5I', '3P/4I', '4P/3I', '5P/2I'],
                'max_sequencia': 3
            }

        resultado = {'valido': True, 'detalhes': {}}

        # 1. Verificar SOMA
        soma = sum(numeros)
        soma_ok = filtros.get('soma_min', 0) <= soma <= filtros.get('soma_max', 999)
        resultado['detalhes']['soma'] = {
            'valor': soma,
            'passou': soma_ok,
            'limite': f"{filtros.get('soma_min')}-{filtros.get('soma_max')}"
        }
        if not soma_ok:
            resultado['valido'] = False

        # 2. Verificar PARIDADE
        pares = sum(1 for n in numeros if n % 2 == 0)
        impares = 7 - pares
        padrao_paridade = f'{pares}P/{impares}I'
        paridade_ok = padrao_paridade in filtros.get('paridade', [])
        resultado['detalhes']['paridade'] = {
            'valor': padrao_paridade,
            'passou': paridade_ok,
            'aceitos': filtros.get('paridade')
        }
        if not paridade_ok:
            resultado['valido'] = False

        # 3. Verificar DISTRIBUIÇÃO (baixos/médios/altos)
        baixos = sum(1 for n in numeros if n <= 10)
        medios = sum(1 for n in numeros if 11 <= n <= 20)
        altos = sum(1 for n in numeros if n >= 21)
        padrao_faixa = f'{baixos}B/{medios}M/{altos}A'
        resultado['detalhes']['distribuicao'] = {
            'valor': padrao_faixa,
            'baixos': baixos,
            'medios': medios,
            'altos': altos
        }

        # 4. Verificar SEQUÊNCIAS
        nums_ord = sorted(numeros)
        max_seq = 1
        seq_atual = 1
        for i in range(1, len(nums_ord)):
            if nums_ord[i] == nums_ord[i-1] + 1:
                seq_atual += 1
                max_seq = max(max_seq, seq_atual)
            else:
                seq_atual = 1

        seq_ok = max_seq <= filtros.get('max_sequencia', 3)
        resultado['detalhes']['sequencias'] = {
            'max_encontrada': max_seq,
            'passou': seq_ok,
            'limite': filtros.get('max_sequencia')
        }
        if not seq_ok:
            resultado['valido'] = False

        return resultado

    @staticmethod
    def gerar_palpites_com_filtros(quantidade=10, filtros=None):
        """
        Gera palpites válidos aplicando filtros de POSIÇÃO e ORDENAÇÃO.
        """
        try:
            posicoes_disponiveis = EstatisticaService._obter_numeros_disponiveis_por_posicao()

            if not posicoes_disponiveis:
                return {'erro': 'Nenhum sorteio encontrado no banco'}

            sorteados = EstatisticaService._obter_sorteios_realizados()

            if filtros is None:
                filtros = {
                    'soma_min': 95,
                    'soma_max': 155,
                    'paridade': ['2P/5I', '3P/4I', '4P/3I', '5P/2I'],
                    'max_sequencia': 3
                }

            palpites_validos = []
            tentativas = 0
            max_tentativas = 100000

            while len(palpites_validos) < quantidade and tentativas < max_tentativas:
                tentativas += 1

                # Gerar combinação aleatória
                combo = tuple(sorted(random.sample(range(1, 32), 7)))

                # Verificar se não foi sorteada
                if combo in sorteados:
                    continue

                # Verificar se tem ordem válida (POSIÇÃO)
                if not EstatisticaService._tem_ordem_valida(combo, posicoes_disponiveis):
                    continue

                # Verificar filtros de ORDENAÇÃO
                validacao = EstatisticaService.validar_palpite_ordenacao(list(combo), filtros)
                if not validacao['valido']:
                    continue

                # Passou em tudo!
                palpites_validos.append({
                    'numeros': list(combo),
                    'validacao': validacao['detalhes']
                })

            return {
                'quantidade_solicitada': quantidade,
                'quantidade_gerada': len(palpites_validos),
                'tentativas': tentativas,
                'filtros_aplicados': filtros,
                'palpites': palpites_validos
            }

        except Exception as e:
            print(f"❌ Erro ao gerar palpites com filtros: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def calcular_dados_nucleos():
        """
        Calcula dados reais para geração de núcleos estratégicos.
        Retorna frequência, atraso, padrões e score ponderado para cada dezena.
        """
        try:
            todos_sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            
            if not todos_sorteios:
                return {'erro': 'Nenhum sorteio encontrado'}
            
            ultimo_concurso = todos_sorteios[-1].concurso
            total_sorteios = len(todos_sorteios)
            
            # Contador de frequência
            contador_freq = Counter()
            ultimo_concurso_dezena = {}
            
            for sorteio in todos_sorteios:
                dezenas = sorteio.get_posicoes_lista()
                for dezena in dezenas:
                    contador_freq[dezena] += 1
                    ultimo_concurso_dezena[dezena] = sorteio.concurso
            
            # Calcular dados por dezena
            resultado = []
            for dezena in range(1, 32):
                frequencia = contador_freq.get(dezena, 0)
                percentual_freq = (frequencia / total_sorteios * 100) if total_sorteios > 0 else 0
                
                # Atraso
                ultimo_aparecimento = ultimo_concurso_dezena.get(dezena, 0)
                atraso = ultimo_concurso - ultimo_aparecimento if ultimo_aparecimento > 0 else ultimo_concurso
                
                # Padrões
                par_impar = 'par' if dezena % 2 == 0 else 'ímpar'
                
                # Faixas
                if dezena <= 10:
                    faixa = 'baixa'
                    faixa_id = 1
                elif dezena <= 20:
                    faixa = 'média'
                    faixa_id = 2
                else:
                    faixa = 'alta'
                    faixa_id = 3
                
                # Quadrante
                if dezena <= 8:
                    quadrante = 1
                elif dezena <= 16:
                    quadrante = 2
                elif dezena <= 24:
                    quadrante = 3
                else:
                    quadrante = 4
                
                # Score ponderado (normalizado)
                # Frequência: peso 25% (normalizado 0-100)
                max_freq = max(contador_freq.values()) if contador_freq else 1
                score_freq = (frequencia / max_freq) * 25
                
                # Atraso: peso 30% (inverso normalizado)
                max_atraso = max(ultimo_concurso - ultimo_concurso_dezena.get(d, 0) for d in range(1, 32))
                score_atraso = (atraso / max_atraso) * 30 if max_atraso > 0 else 0
                
                # Distribuição equilibrada: peso 25%
                score_distrib = 25 - abs(faixa_id - 2) * 8  # Favorece faixa média
                
                # Padrão par/ímpar: peso 20% (leve preferência ímpar no Dia de Sorte)
                score_padrao = 22 if par_impar == 'ímpar' else 18
                
                score_total = round(score_freq + score_atraso + score_distrib + score_padrao, 2)
                
                resultado.append({
                    'dezena': dezena,
                    'frequencia': frequencia,
                    'percentual_frequencia': round(percentual_freq, 2),
                    'atraso': atraso,
                    'ultimo_concurso': ultimo_aparecimento,
                    'par_impar': par_impar,
                    'faixa': faixa,
                    'faixa_id': faixa_id,
                    'quadrante': quadrante,
                    'score': score_total,
                    'score_detalhes': {
                        'frequencia': round(score_freq, 2),
                        'atraso': round(score_atraso, 2),
                        'distribuicao': round(score_distrib, 2),
                        'padrao': round(score_padrao, 2)
                    }
                })
            
            # Ordenar por score
            resultado.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'total_sorteios': total_sorteios,
                'ultimo_concurso': ultimo_concurso,
                'dezenas': resultado,
                'top_10': resultado[:10],
                'metadados': {
                    'max_frequencia': max(contador_freq.values()) if contador_freq else 0,
                    'max_atraso': max(ultimo_concurso - ultimo_concurso_dezena.get(d, 0) for d in range(1, 32)),
                    'criterios': {
                        'frequencia': '25%',
                        'atraso': '30%',
                        'distribuicao': '25%',
                        'padrao': '20%'
                    }
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular dados de núcleos: {str(e)}")
            return {'erro': str(e)}
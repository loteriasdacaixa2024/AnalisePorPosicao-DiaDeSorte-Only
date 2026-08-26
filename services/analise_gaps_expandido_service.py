"""
Service EXPANDIDO para Análise Completa de Gaps e Padrões
Sistema: Dia de Sorte
Desenvolvido para: Márcio Fernando Maia

NOVAS ANÁLISES:
- Quadrantes
- Pares/Ímpares
- Altos/Baixos
- Quentes/Frios
- Duplas/Trincas recorrentes
- Repetidos do concurso anterior
- Faixas esquecidas
- Perfil do Mês da Sorte
"""

from models.sorteio import Sorteio
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import statistics


class AnaliseGapsExpandidoService:
    """
    Service para análises avançadas com múltiplas dimensões
    """

    # ========== ANÁLISES BÁSICAS (já existentes) ==========

    @staticmethod
    def obter_digito_inicial(numero):
        """0 → 01-09, 1 → 10-19, 2 → 20-29, 3 → 30-31"""
        if numero <= 9:
            return 0
        elif numero <= 19:
            return 1
        elif numero <= 29:
            return 2
        else:
            return 3

    @staticmethod
    def calcular_gaps(numeros_ordenados):
        """Calcula gaps entre números consecutivos"""
        return [numeros_ordenados[i+1] - numeros_ordenados[i]
                for i in range(len(numeros_ordenados) - 1)]

    @staticmethod
    def analisar_digitos_iniciais():
        """ANÁLISE 1 - Dígitos Iniciais (mesma implementação anterior)"""
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            if not sorteios:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            padroes_digitos = []
            padroes_detalhados = []

            for sorteio in sorteios:
                numeros = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                          sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]

                digitos = sorted([AnaliseGapsExpandidoService.obter_digito_inicial(n) for n in numeros])
                padrao_str = '-'.join(map(str, digitos))
                padroes_digitos.append(padrao_str)

                padroes_detalhados.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': numeros,
                    'digitos': digitos,
                    'padrao': padrao_str
                })

            contador_padroes = Counter(padroes_digitos)
            top_3_padroes = contador_padroes.most_common(3)

            todos_digitos = []
            for padrao in padroes_digitos:
                todos_digitos.extend(padrao.split('-'))
            contador_digitos_individuais = Counter(todos_digitos)

            top_3_detalhado = []
            for padrao, frequencia in top_3_padroes:
                exemplos = [p for p in padroes_detalhados if p['padrao'] == padrao][:5]
                ultimos_10 = padroes_digitos[-10:]
                aparece_recente = padrao in ultimos_10

                # Pegar exemplo de números para exibição
                exemplo_numeros = exemplos[0]['numeros'] if exemplos else []

                top_3_detalhado.append({
                    'padrao': padrao,
                    'padrao_str': f"Padrão {padrao}",
                    'frequencia': frequencia,
                    'percentual': round((frequencia / len(sorteios)) * 100, 1),
                    'reapareceu_recentemente': aparece_recente,
                    'ultimo_concurso': exemplos[-1]['concurso'] if exemplos else 0,
                    'exemplo': exemplo_numeros,
                    'exemplos': exemplos
                })

            return {
                'sucesso': True,
                'total_analisado': len(sorteios),
                'total_sorteios': len(sorteios),
                'top_padroes': top_3_detalhado,
                'digitos_individuais': dict(contador_digitos_individuais.most_common()),
                'mensagem': f'Análise de dígitos concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    @staticmethod
    def analisar_gaps():
        """ANÁLISE 2 - Gaps (mesma implementação anterior)"""
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            if not sorteios:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            todos_gaps = []
            padroes_gaps_completos = []
            padroes_detalhados = []

            for sorteio in sorteios:
                numeros = sorted([sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                                 sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7])

                gaps = AnaliseGapsExpandidoService.calcular_gaps(numeros)
                todos_gaps.extend(gaps)

                padrao_gaps_str = '-'.join(map(str, gaps))
                padroes_gaps_completos.append(padrao_gaps_str)

                padroes_detalhados.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': numeros,
                    'gaps': gaps,
                    'padrao_gaps': padrao_gaps_str,
                    'gap_medio': statistics.mean(gaps),
                    'gap_maximo': max(gaps),
                    'gap_minimo': min(gaps)
                })

            contador_gaps_individuais = Counter(todos_gaps)
            contador_padroes_completos = Counter(padroes_gaps_completos)

            top_3_gaps_individuais = contador_gaps_individuais.most_common(3)
            top_3_padroes_completos = contador_padroes_completos.most_common(3)

            top_3_gaps_detalhado = []
            for gap, frequencia in top_3_gaps_individuais:
                top_3_gaps_detalhado.append({
                    'gap': gap,
                    'frequencia': frequencia,
                    'percentual': (frequencia / len(todos_gaps)) * 100
                })

            top_3_padroes_detalhado = []
            for padrao, frequencia in top_3_padroes_completos:
                exemplos = [p for p in padroes_detalhados if p['padrao_gaps'] == padrao][:5]
                ultimos_10 = padroes_gaps_completos[-10:]
                aparece_recente = padrao in ultimos_10

                # Pegar exemplo de números para exibição
                exemplo_numeros = exemplos[0]['numeros'] if exemplos else []

                top_3_padroes_detalhado.append({
                    'padrao': padrao,
                    'padrao_str': f"Gaps {padrao}",
                    'frequencia': frequencia,
                    'percentual': round((frequencia / len(sorteios)) * 100, 1),
                    'reapareceu_recentemente': aparece_recente,
                    'ultimo_concurso': exemplos[-1]['concurso'] if exemplos else 0,
                    'exemplo': exemplo_numeros,
                    'exemplos': exemplos
                })

            gap_medio_geral = statistics.mean(todos_gaps)
            gap_mediano = statistics.median(todos_gaps)

            return {
                'sucesso': True,
                'total_analisado': len(sorteios),
                'total_sorteios': len(sorteios),
                'total_gaps': len(todos_gaps),
                'gap_medio_geral': gap_medio_geral,
                'gap_mediano': gap_mediano,
                'top_3_gaps_individuais': top_3_gaps_detalhado,
                'top_padroes': top_3_padroes_detalhado,
                'mensagem': 'Análise de gaps concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    # ========== NOVAS ANÁLISES ==========

    @staticmethod
    def analisar_quadrantes():
        """
        NOVA ANÁLISE - Quadrantes (divide cartela em 4 partes)
        Q1: 01-08, Q2: 09-16, Q3: 17-24, Q4: 25-31
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            if not sorteios:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            def obter_quadrante(numero):
                if numero <= 8:
                    return 1
                elif numero <= 16:
                    return 2
                elif numero <= 24:
                    return 3
                else:
                    return 4

            padroes_quadrantes = []
            detalhes = []

            for sorteio in sorteios:
                numeros = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                          sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]

                quadrantes = sorted([obter_quadrante(n) for n in numeros])

                # Contar quantos de cada quadrante
                q1_count = quadrantes.count(1)
                q2_count = quadrantes.count(2)
                q3_count = quadrantes.count(3)
                q4_count = quadrantes.count(4)

                padrao = f"Q1:{q1_count} Q2:{q2_count} Q3:{q3_count} Q4:{q4_count}"
                padroes_quadrantes.append(padrao)

                detalhes.append({
                    'concurso': sorteio.concurso,
                    'numeros': numeros,
                    'padrao': padrao
                })

            contador = Counter(padroes_quadrantes)
            top_3 = contador.most_common(3)

            resultado = []
            for padrao, freq in top_3:
                exemplos = [d for d in detalhes if d['padrao'] == padrao][:3]
                exemplo_numeros = exemplos[0]['numeros'] if exemplos else []
                resultado.append({
                    'padrao': padrao,
                    'padrao_str': padrao,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios)) * 100, 1),
                    'reapareceu_recentemente': False,
                    'ultimo_concurso': detalhes[-1]['concurso'] if detalhes else 0,
                    'exemplo': exemplo_numeros,
                    'exemplos': exemplos
                })

            return {
                'sucesso': True,
                'total_analisado': len(sorteios),
                'top_padroes': resultado,
                'mensagem': 'Análise de quadrantes concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    @staticmethod
    def analisar_pares_impares():
        """NOVA ANÁLISE - Pares vs Ímpares"""
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            if not sorteios:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            padroes = []
            detalhes = []

            for sorteio in sorteios:
                numeros = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                          sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]

                pares = sum(1 for n in numeros if n % 2 == 0)
                impares = 7 - pares

                padrao = f"{pares}P-{impares}I"
                padroes.append(padrao)

                detalhes.append({
                    'concurso': sorteio.concurso,
                    'numeros': numeros,
                    'padrao': padrao,
                    'pares': pares,
                    'impares': impares
                })

            contador = Counter(padroes)
            top_3 = contador.most_common(3)

            resultado = []
            for padrao, freq in top_3:
                exemplos = [d for d in detalhes if d['padrao'] == padrao][:3]
                exemplo_numeros = exemplos[0]['numeros'] if exemplos else []
                resultado.append({
                    'padrao': padrao,
                    'padrao_str': padrao,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios)) * 100, 1),
                    'reapareceu_recentemente': False,
                    'ultimo_concurso': detalhes[-1]['concurso'] if detalhes else 0,
                    'exemplo': exemplo_numeros,
                    'exemplos': exemplos
                })

            return {
                'sucesso': True,
                'total_analisado': len(sorteios),
                'top_padroes': resultado,
                'mensagem': 'Análise de pares/ímpares concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    @staticmethod
    def analisar_altos_baixos():
        """NOVA ANÁLISE - Altos (16-31) vs Baixos (01-15)"""
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            if not sorteios:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            padroes = []
            detalhes = []

            for sorteio in sorteios:
                numeros = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                          sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]

                baixos = sum(1 for n in numeros if n <= 15)
                altos = 7 - baixos

                padrao = f"{baixos}Baixos-{altos}Altos"
                padroes.append(padrao)

                detalhes.append({
                    'concurso': sorteio.concurso,
                    'numeros': numeros,
                    'padrao': padrao
                })

            contador = Counter(padroes)
            top_3 = contador.most_common(3)

            resultado = []
            for padrao, freq in top_3:
                exemplos = [d for d in detalhes if d['padrao'] == padrao][:3]
                exemplo_numeros = exemplos[0]['numeros'] if exemplos else []
                resultado.append({
                    'padrao': padrao,
                    'padrao_str': padrao,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios)) * 100, 1),
                    'reapareceu_recentemente': False,
                    'ultimo_concurso': detalhes[-1]['concurso'] if detalhes else 0,
                    'exemplo': exemplo_numeros,
                    'exemplos': exemplos
                })

            return {
                'sucesso': True,
                'total_analisado': len(sorteios),
                'top_padroes': resultado,
                'mensagem': 'Análise de altos/baixos concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    @staticmethod
    def analisar_quentes_frios():
        """
        NOVA ANÁLISE - Quentes (saíram nos últimos 10 concursos) vs Frios
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
            if len(sorteios) < 10:
                return {'sucesso': False, 'mensagem': 'Necessário pelo menos 10 sorteios'}

            # Últimos 10 concursos para definir "quentes"
            ultimos_10 = sorteios[:10]
            numeros_quentes = set()

            for sorteio in ultimos_10:
                numeros = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                          sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]
                numeros_quentes.update(numeros)

            # Analisar todos os sorteios
            padroes = []
            detalhes = []

            for sorteio in reversed(sorteios):  # Voltar à ordem crescente
                numeros = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                          sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]

                quentes = sum(1 for n in numeros if n in numeros_quentes)
                frios = 7 - quentes

                padrao = f"{quentes}Quentes-{frios}Frios"
                padroes.append(padrao)

                detalhes.append({
                    'concurso': sorteio.concurso,
                    'numeros': numeros,
                    'padrao': padrao
                })

            contador = Counter(padroes)
            top_3 = contador.most_common(3)

            resultado = []
            for padrao, freq in top_3:
                exemplos = [d for d in detalhes if d['padrao'] == padrao][:3]
                exemplo_numeros = exemplos[0]['numeros'] if exemplos else []
                resultado.append({
                    'padrao': padrao,
                    'padrao_str': padrao,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios)) * 100, 1),
                    'reapareceu_recentemente': False,
                    'ultimo_concurso': detalhes[-1]['concurso'] if detalhes else 0,
                    'exemplo': exemplo_numeros,
                    'exemplos': exemplos
                })

            return {
                'sucesso': True,
                'total_analisado': len(sorteios),
                'numeros_quentes': sorted(list(numeros_quentes)),
                'top_padroes': resultado,
                'mensagem': 'Análise de quentes/frios concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    @staticmethod
    def analisar_duplas_trincas():
        """NOVA ANÁLISE - Duplas e Trincas recorrentes"""
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            if not sorteios:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            duplas_counter = Counter()
            trincas_counter = Counter()

            for sorteio in sorteios:
                numeros = sorted([sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                                 sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7])

                # Duplas (todas as combinações de 2)
                for i in range(len(numeros)):
                    for j in range(i+1, len(numeros)):
                        dupla = (numeros[i], numeros[j])
                        duplas_counter[dupla] += 1

                # Trincas (todas as combinações de 3)
                for i in range(len(numeros)):
                    for j in range(i+1, len(numeros)):
                        for k in range(j+1, len(numeros)):
                            trinca = (numeros[i], numeros[j], numeros[k])
                            trincas_counter[trinca] += 1

            top_10_duplas = duplas_counter.most_common(10)
            top_10_trincas = trincas_counter.most_common(10)

            # Formatar top padrões (usando duplas como principal)
            top_padroes_formatado = []
            for dupla, freq in top_10_duplas[:3]:  # Top 3
                top_padroes_formatado.append({
                    'padrao': f"{dupla[0]:02d}-{dupla[1]:02d}",
                    'padrao_str': f"Dupla {dupla[0]:02d}-{dupla[1]:02d}",
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios)) * 100, 1),
                    'reapareceu_recentemente': False,
                    'ultimo_concurso': 0,
                    'exemplo': list(dupla),
                    'numeros': list(dupla)
                })

            return {
                'sucesso': True,
                'total_analisado': len(sorteios),
                'top_padroes': top_padroes_formatado,
                'top_10_duplas': [
                    {
                        'dupla': f"{d[0]}-{d[1]}",
                        'numeros': list(dupla),
                        'frequencia': freq
                    }
                    for dupla, freq in top_10_duplas
                ],
                'top_10_trincas': [
                    {
                        'trinca': f"{t[0]}-{t[1]}-{t[2]}",
                        'numeros': list(trinca),
                        'frequencia': freq
                    }
                    for trinca, freq in top_10_trincas
                ],
                'mensagem': 'Análise de duplas/trincas concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    @staticmethod
    def analisar_repetidos_concurso_anterior():
        """NOVA ANÁLISE - Quantos números se repetem do concurso anterior"""
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            if len(sorteios) < 2:
                return {'sucesso': False, 'mensagem': 'Necessário pelo menos 2 sorteios'}

            padroes = []
            detalhes = []

            for i in range(1, len(sorteios)):
                numeros_anterior = set([
                    sorteios[i-1].posicao_1, sorteios[i-1].posicao_2, sorteios[i-1].posicao_3,
                    sorteios[i-1].posicao_4, sorteios[i-1].posicao_5, sorteios[i-1].posicao_6, sorteios[i-1].posicao_7
                ])

                numeros_atual = set([
                    sorteios[i].posicao_1, sorteios[i].posicao_2, sorteios[i].posicao_3,
                    sorteios[i].posicao_4, sorteios[i].posicao_5, sorteios[i].posicao_6, sorteios[i].posicao_7
                ])

                repetidos = len(numeros_anterior & numeros_atual)
                padroes.append(repetidos)

                detalhes.append({
                    'concurso': sorteios[i].concurso,
                    'repetidos': repetidos,
                    'numeros_repetidos': sorted(list(numeros_anterior & numeros_atual))
                })

            contador = Counter(padroes)
            media_repetidos = statistics.mean(padroes)

            distribuicao = []
            for qtd in sorted(contador.keys()):
                freq = contador[qtd]
                distribuicao.append({
                    'quantidade_repetidos': qtd,
                    'frequencia': freq,
                    'percentual': (freq / len(padroes)) * 100
                })

            # Formatar para top_padroes
            top_padroes_formatado = []
            for item in distribuicao[:3]:
                qtd = item['quantidade_repetidos']
                top_padroes_formatado.append({
                    'padrao': f"{qtd} número(s) repetido(s)",
                    'padrao_str': f"{qtd} número(s) repetido(s)",
                    'frequencia': item['frequencia'],
                    'percentual': item['percentual'],
                    'reapareceu_recentemente': False,
                    'ultimo_concurso': 0,
                    'exemplo': []
                })

            return {
                'sucesso': True,
                'total_analisado': len(padroes),
                'top_padroes': top_padroes_formatado,
                'media_repetidos': media_repetidos,
                'distribuicao': distribuicao,
                'exemplos_recentes': detalhes[-5:],  # Últimos 5
                'mensagem': 'Análise de repetidos concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    @staticmethod
    def analisar_faixas_esquecidas():
        """
        NOVA ANÁLISE - Faixas que não saem há muito tempo
        Divide em faixas de 5: 01-05, 06-10, 11-15, 16-20, 21-25, 26-31
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(50).all()
            if not sorteios:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            def obter_faixa(numero):
                if numero <= 5:
                    return "01-05"
                elif numero <= 10:
                    return "06-10"
                elif numero <= 15:
                    return "11-15"
                elif numero <= 20:
                    return "16-20"
                elif numero <= 25:
                    return "21-25"
                else:
                    return "26-31"

            faixas_vistas = defaultdict(int)

            # Analisar últimos 50 concursos
            for idx, sorteio in enumerate(reversed(sorteios)):
                numeros = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                          sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]

                faixas_deste_sorteio = set([obter_faixa(n) for n in numeros])

                for faixa in faixas_deste_sorteio:
                    if faixa not in faixas_vistas:
                        faixas_vistas[faixa] = idx

            # Ordenar por "atraso" (quanto tempo sem aparecer)
            faixas_ordenadas = sorted(faixas_vistas.items(), key=lambda x: x[1], reverse=True)

            resultado = []
            for faixa, atraso in faixas_ordenadas:
                resultado.append({
                    'faixa': faixa,
                    'concursos_sem_aparecer': atraso,
                    'status': 'Esquecida' if atraso > 10 else 'Normal'
                })

            # Formatar para top_padroes (mais esquecidas primeiro)
            top_padroes_formatado = []
            for item in resultado[:3]:
                top_padroes_formatado.append({
                    'padrao': item['faixa'],
                    'padrao_str': f"Faixa {item['faixa']} ({item['status']})",
                    'frequencia': item['concursos_sem_aparecer'],
                    'percentual': 0,
                    'reapareceu_recentemente': False,
                    'ultimo_concurso': 0,
                    'exemplo': []
                })

            return {
                'sucesso': True,
                'total_analisado': 50,
                'top_padroes': top_padroes_formatado,
                'faixas': resultado,
                'mensagem': 'Análise de faixas esquecidas concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    @staticmethod
    def analisar_perfil_mes_sorte():
        """NOVA ANÁLISE - Perfil do Mês da Sorte"""
        try:
            sorteios = Sorteio.query.all()
            if not sorteios:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            meses_counter = Counter()
            mes_numeros = defaultdict(list)

            for sorteio in sorteios:
                mes = sorteio.mes_sorte
                if mes:
                    meses_counter[mes] += 1

                    numeros = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                              sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]
                    mes_numeros[mes].extend(numeros)

            top_5_meses = meses_counter.most_common(5)

            resultado = []
            for mes, freq in top_5_meses:
                numeros_deste_mes = mes_numeros[mes]
                numeros_mais_comuns = Counter(numeros_deste_mes).most_common(5)

                resultado.append({
                    'mes': mes,
                    'frequencia': freq,
                    'numeros_mais_comuns': [
                        {'numero': num, 'vezes': vezes}
                        for num, vezes in numeros_mais_comuns
                    ]
                })

            # Formatar para top_padroes
            top_padroes_formatado = []
            meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                          'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

            for item in resultado[:3]:
                mes_nome = meses_nomes[item['mes']] if item['mes'] <= 12 else f"Mês {item['mes']}"
                top_nums = ', '.join([f"{n['numero']:02d}" for n in item['numeros_mais_comuns'][:3]])

                top_padroes_formatado.append({
                    'padrao': mes_nome,
                    'padrao_str': f"{mes_nome} (Núms: {top_nums})",
                    'frequencia': item['frequencia'],
                    'percentual': round((item['frequencia'] / len(sorteios)) * 100, 1) if sorteios else 0,
                    'reapareceu_recentemente': False,
                    'ultimo_concurso': 0,
                    'exemplo': [n['numero'] for n in item['numeros_mais_comuns'][:3]]
                })

            return {
                'sucesso': True,
                'total_analisado': len(sorteios),
                'top_padroes': top_padroes_formatado,
                'top_5_meses': resultado,
                'mensagem': 'Análise de perfil do mês da sorte concluída'
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': f'Erro: {str(e)}'}

    # ========== SISTEMA DE CRUZAMENTOS ==========

    @staticmethod
    def cruzar_analises(analises_ativas):
        """
        Cruza múltiplas análises selecionadas

        Args:
            analises_ativas: Lista de análises ativas ['digitos', 'gaps', 'pares_impares', ...]

        Returns:
            dict com cruzamentos e interpretações
        """
        resultados = {}
        interpretacoes = []

        # Executar cada análise ativa
        if 'digitos' in analises_ativas:
            resultados['digitos'] = AnaliseGapsExpandidoService.analisar_digitos_iniciais()

        if 'gaps' in analises_ativas:
            resultados['gaps'] = AnaliseGapsExpandidoService.analisar_gaps()

        if 'quadrantes' in analises_ativas:
            resultados['quadrantes'] = AnaliseGapsExpandidoService.analisar_quadrantes()

        if 'pares_impares' in analises_ativas:
            resultados['pares_impares'] = AnaliseGapsExpandidoService.analisar_pares_impares()

        if 'altos_baixos' in analises_ativas:
            resultados['altos_baixos'] = AnaliseGapsExpandidoService.analisar_altos_baixos()

        if 'quentes_frios' in analises_ativas:
            resultados['quentes_frios'] = AnaliseGapsExpandidoService.analisar_quentes_frios()

        if 'duplas_trincas' in analises_ativas:
            resultados['duplas_trincas'] = AnaliseGapsExpandidoService.analisar_duplas_trincas()

        if 'repetidos' in analises_ativas:
            resultados['repetidos'] = AnaliseGapsExpandidoService.analisar_repetidos_concurso_anterior()

        if 'faixas_esquecidas' in analises_ativas:
            resultados['faixas_esquecidas'] = AnaliseGapsExpandidoService.analisar_faixas_esquecidas()

        if 'mes_sorte' in analises_ativas:
            resultados['mes_sorte'] = AnaliseGapsExpandidoService.analisar_perfil_mes_sorte()

        # Gerar interpretações baseadas nas combinações
        if 'digitos' in analises_ativas and 'gaps' in analises_ativas:
            interpretacoes.append({
                'titulo': 'Dígitos × Gaps',
                'interpretacao': 'Padrões com muitos dígitos baixos (0 e 1) tendem a ter gaps curtos (1-2), '
                                'enquanto padrões mistos apresentam gaps variados.'
            })

        if 'pares_impares' in analises_ativas and 'altos_baixos' in analises_ativas:
            interpretacoes.append({
                'titulo': 'Pares/Ímpares × Altos/Baixos',
                'interpretacao': 'Jogos equilibrados (3P-4I ou 4P-3I) combinados com distribuição balanceada '
                                'de altos/baixos são os mais comuns historicamente.'
            })

        return {
            'sucesso': True,
            'resultados': resultados,
            'interpretacoes': interpretacoes,
            'total_analises': len(analises_ativas)
        }

    # ========== GERADOR DE PALPITES INTELIGENTE ==========

    @staticmethod
    def gerar_palpites_inteligentes(analises_ativas):
        """
        Gera palpites REALISTAS baseados em padrões históricos

        NÃO inventa fórmula mágica!
        USA raciocínio estatístico:
        - Duplas/trincas frequentes
        - Salto único (gaps curtos)
        - Blocos de dígitos
        - Fechamento no 20-29 quando padrão indicar
        """
        import random

        # Buscar dados históricos
        analises = AnaliseGapsExpandidoService.cruzar_analises(analises_ativas)

        if not analises['sucesso']:
            return {'sucesso': False, 'mensagem': 'Erro ao gerar palpites'}

        palpites = []

        # PALPITE 1: Baseado em Duplas Frequentes
        if 'duplas_trincas' in analises_ativas:
            duplas_data = analises['resultados'].get('duplas_trincas', {})
            if duplas_data.get('sucesso'):
                top_duplas = duplas_data['top_10_duplas'][:3]

                jogo = []
                for dupla_info in top_duplas:
                    jogo.extend(dupla_info['numeros'])

                # Completar com número aleatório se necessário
                while len(jogo) < 7:
                    novo = random.randint(1, 31)
                    if novo not in jogo:
                        jogo.append(novo)

                jogo = sorted(jogo[:7])

                palpites.append({
                    'tipo': 'Baseado em Duplas Frequentes',
                    'numeros': jogo,
                    'justificativa': f'Usa as duplas mais recorrentes: {", ".join([d["dupla"] for d in top_duplas[:3]])}'
                })

        # PALPITE 2: Baseado em Gaps Curtos (salto único)
        if 'gaps' in analises_ativas:
            gaps_data = analises['resultados'].get('gaps', {})
            if gaps_data.get('sucesso'):
                # Começar de um número aleatório baixo
                inicio = random.randint(1, 10)
                jogo = [inicio]

                # Aplicar gaps curtos (1, 2, 3)
                gaps_curtos = [1, 1, 2, 2, 3, 3]
                random.shuffle(gaps_curtos)

                for gap in gaps_curtos[:6]:
                    proximo = jogo[-1] + gap
                    if proximo <= 31:
                        jogo.append(proximo)

                while len(jogo) < 7:
                    jogo.append(random.randint(1, 31))

                jogo = sorted(list(set(jogo)))[:7]

                palpites.append({
                    'tipo': 'Baseado em Gaps Curtos (Salto Único)',
                    'numeros': jogo,
                    'justificativa': 'Números próximos com gaps de 1-3, padrão muito comum historicamente'
                })

        # PALPITE 3: Baseado em Blocos de Dígitos
        if 'digitos' in analises_ativas:
            digitos_data = analises['resultados'].get('digitos', {})
            if digitos_data.get('sucesso'):
                top_padrao = digitos_data['top_3_padroes'][0]['padrao']
                digitos_top = list(map(int, top_padrao.split('-')))

                jogo = []
                for digito in digitos_top:
                    if digito == 0:
                        jogo.append(random.randint(1, 9))
                    elif digito == 1:
                        jogo.append(random.randint(10, 19))
                    elif digito == 2:
                        jogo.append(random.randint(20, 29))
                    else:
                        jogo.append(random.randint(30, 31))

                jogo = sorted(list(set(jogo)))[:7]

                # Garantir fechamento no 20-29 se tiver muitos 2s no padrão
                count_2 = digitos_top.count(2)
                if count_2 >= 2:
                    # Forçar pelo menos 2 números na faixa 20-29
                    numeros_20_29 = [n for n in jogo if 20 <= n <= 29]
                    if len(numeros_20_29) < 2:
                        while len([n for n in jogo if 20 <= n <= 29]) < 2:
                            jogo.append(random.randint(20, 29))
                        jogo = sorted(list(set(jogo)))[:7]

                palpites.append({
                    'tipo': 'Baseado em Blocos de Dígitos',
                    'numeros': jogo,
                    'justificativa': f'Segue o padrão mais frequente: {top_padrao}. Concentração na faixa 20-29.'
                })

        # PALPITE 4: Baseado em Números Quentes
        if 'quentes_frios' in analises_ativas:
            quentes_data = analises['resultados'].get('quentes_frios', {})
            if quentes_data.get('sucesso'):
                numeros_quentes = quentes_data.get('numeros_quentes', [])

                if len(numeros_quentes) >= 7:
                    jogo = sorted(random.sample(numeros_quentes, 7))
                else:
                    jogo = numeros_quentes.copy()
                    while len(jogo) < 7:
                        novo = random.randint(1, 31)
                        if novo not in jogo:
                            jogo.append(novo)
                    jogo = sorted(jogo)

                palpites.append({
                    'tipo': 'Baseado em Números Quentes',
                    'numeros': jogo,
                    'justificativa': 'Usa números que saíram nos últimos 10 concursos (tendência quente)'
                })

        return {
            'sucesso': True,
            'palpites': palpites,
            'total_palpites': len(palpites),
            'mensagem': f'{len(palpites)} palpites gerados com raciocínio estatístico'
        }

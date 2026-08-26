from collections import defaultdict
from models import Sorteio


class DesdobramentoService:
    """
    Serviço para desdobramento Modelo A (5 Fixas + 2 Variáveis)
    Sistema de conjunto fixo + grupos variáveis para Dia de Sorte
    """

    @staticmethod
    def gerar_sugestao_automatica():
        """
        Gera sugestão automática de dezenas baseada em análise dos concursos
        Retorna: dict com grupoA (5 fixas), grupoB (8 variáveis) e explicações
        """
        # Analisar TODOS os concursos do banco de dados
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {
                'erro': 'Nenhum sorteio encontrado para análise',
                'grupoA': [],
                'grupoB': [],
                'explicacoes': {}
            }

        # Análise estatística
        analise = DesdobramentoService._analisar_frequencias(sorteios)

        # Selecionar Grupo A (5 fixas)
        grupo_a = DesdobramentoService._selecionar_grupo_a(analise)

        # Selecionar Grupo B (8 variáveis)
        grupo_b = DesdobramentoService._selecionar_grupo_b(analise, grupo_a)

        # Gerar explicações
        explicacoes = DesdobramentoService._gerar_explicacoes(grupo_a, analise)

        return {
            'grupoA': sorted(grupo_a),
            'grupoB': sorted(grupo_b),
            'explicacoes': explicacoes,
            'total_concursos_analisados': len(sorteios)
        }

    @staticmethod
    def _analisar_frequencias(sorteios):
        """Analisa frequências e padrões dos números"""
        frequencias = defaultdict(int)
        ultimas_aparicoes = {}
        sequencias_historicas = set()

        for idx, sorteio in enumerate(sorteios):
            # Obter números do sorteio (já vem ordenado por posição)
            numeros = sorted(sorteio.get_posicoes_lista())

            # Frequência
            for num in numeros:
                frequencias[num] += 1
                ultimas_aparicoes[num] = idx

            # Detectar sequências
            for i in range(len(numeros) - 1):
                if numeros[i + 1] - numeros[i] == 1:
                    sequencias_historicas.add(numeros[i])
                    sequencias_historicas.add(numeros[i + 1])

        # Classificar números
        total_sorteios = len(sorteios)
        todos_numeros = list(range(1, 32))

        # Quentes (>40% de frequência)
        quentes = []
        # Frios (atrasados, não apareceram nos últimos 15)
        frios = []
        # Médios
        medios = []

        for num in todos_numeros:
            freq = frequencias.get(num, 0)
            percentual = (freq / total_sorteios * 100) if total_sorteios > 0 else 0
            ultima_vez = ultimas_aparicoes.get(num, 999)

            if percentual >= 40:
                quentes.append((num, freq, percentual))
            elif ultima_vez > 15:
                frios.append((num, freq, ultima_vez))
            else:
                medios.append((num, freq, percentual))

        # Ordenar
        quentes.sort(key=lambda x: x[1], reverse=True)
        frios.sort(key=lambda x: x[2], reverse=True)

        return {
            'frequencias': dict(frequencias),
            'quentes': [x[0] for x in quentes],
            'frios': [x[0] for x in frios],
            'medios': [x[0] for x in medios],
            'sequencias': list(sequencias_historicas),
            'total_sorteios': total_sorteios
        }

    @staticmethod
    def _selecionar_grupo_a(analise):
        """Seleciona 5 dezenas fixas estratégicas"""
        grupo_a = []

        # 2 quentes
        if len(analise['quentes']) >= 2:
            grupo_a.extend(analise['quentes'][:2])

        # 1 frio (atrasado)
        if len(analise['frios']) >= 1:
            grupo_a.append(analise['frios'][0])

        # 1 de sequência
        if len(analise['sequencias']) >= 1:
            seq_disponiveis = [x for x in analise['sequencias'] if x not in grupo_a]
            if seq_disponiveis:
                grupo_a.append(seq_disponiveis[0])

        # 1 alto (estratégico, 26-31)
        altos = [x for x in range(26, 32) if x not in grupo_a]
        if altos:
            # Escolher o mais frequente entre os altos
            altos_com_freq = [(n, analise['frequencias'].get(n, 0)) for n in altos]
            altos_com_freq.sort(key=lambda x: x[1], reverse=True)
            grupo_a.append(altos_com_freq[0][0])

        # Garantir 5 elementos
        while len(grupo_a) < 5:
            todos = list(range(1, 32))
            disponiveis = [x for x in todos if x not in grupo_a]
            if disponiveis:
                # Pegar o mais frequente disponível
                freq_disp = [(n, analise['frequencias'].get(n, 0)) for n in disponiveis]
                freq_disp.sort(key=lambda x: x[1], reverse=True)
                grupo_a.append(freq_disp[0][0])
            else:
                break

        return grupo_a[:5]

    @staticmethod
    def _selecionar_grupo_b(analise, grupo_a):
        """Seleciona 8 dezenas para pool de variáveis"""
        grupo_b = []

        # Números disponíveis (não estão no grupo A)
        disponiveis = [x for x in range(1, 32) if x not in grupo_a]

        # 4 quentes disponíveis
        quentes_disp = [x for x in analise['quentes'] if x not in grupo_a]
        grupo_b.extend(quentes_disp[:4])

        # 4 frios disponíveis
        frios_disp = [x for x in analise['frios'] if x not in grupo_a and x not in grupo_b]
        grupo_b.extend(frios_disp[:4])

        # Completar até 8 com médios ou qualquer disponível
        while len(grupo_b) < 8 and len(disponiveis) > len(grupo_b):
            for num in disponiveis:
                if num not in grupo_b:
                    grupo_b.append(num)
                    if len(grupo_b) >= 8:
                        break

        return grupo_b[:8]

    @staticmethod
    def _gerar_explicacoes(grupo_a, analise):
        """Gera explicações para cada número do Grupo A"""
        explicacoes = {}

        for num in grupo_a:
            freq = analise['frequencias'].get(num, 0)
            total = analise['total_sorteios']
            percentual = (freq / total * 100) if total > 0 else 0

            if num in analise['quentes']:
                emoji = '🔥'
                motivo = f'Número QUENTE - Saiu em {percentual:.0f}% dos últimos {total} concursos'
            elif num in analise['frios']:
                emoji = '❄️'
                motivo = f'Número FRIO - Atrasado, deve sair em breve (freq: {freq}x)'
            elif num in analise['sequencias']:
                emoji = '🔗'
                motivo = f'Faz parte de sequências históricas (freq: {freq}x)'
            elif num >= 26:
                emoji = '⬆️'
                motivo = f'Número ALTO - Equilíbrio estratégico (freq: {freq}x)'
            else:
                emoji = '🎯'
                motivo = f'Seleção estratégica baseada em padrões (freq: {freq}x)'

            explicacoes[num] = {
                'emoji': emoji,
                'motivo': motivo,
                'frequencia': freq,
                'percentual': round(percentual, 2)
            }

        return explicacoes

    @staticmethod
    def calcular_combinacoes(n, k):
        """Calcula C(n, k) - Combinação simples"""
        if k > n or k < 0:
            return 0
        if k == 0 or k == n:
            return 1

        # C(n, k) = n! / (k! * (n-k)!)
        result = 1
        for i in range(1, k + 1):
            result *= (n - k + i)
            result //= i

        return result

    @staticmethod
    def gerar_jogos(grupo_a, grupo_b, mes='Jan'):
        """
        Gera todas as combinações de jogos
        5 fixas (grupo_a) + 2 variáveis (grupo_b em combinações de 2)
        """
        if len(grupo_a) != 5:
            return {'erro': 'Grupo A deve ter exatamente 5 dezenas'}

        if len(grupo_b) < 2:
            return {'erro': 'Grupo B deve ter pelo menos 2 dezenas'}

        # Gerar combinações C(n, 2) do grupo B
        combinacoes = DesdobramentoService._gerar_combinacoes_2(grupo_b)

        jogos = []
        for idx, comb in enumerate(combinacoes, 1):
            numeros_completos = sorted(grupo_a + list(comb))
            jogos.append({
                'numero': idx,
                'fixas': grupo_a,
                'variaveis': list(comb),
                'numeros_completos': numeros_completos,
                'mes': mes
            })

        total_jogos = len(jogos)
        custo_unitario = 2.50
        custo_total = total_jogos * custo_unitario

        return {
            'jogos': jogos,
            'total_jogos': total_jogos,
            'custo_unitario': custo_unitario,
            'custo_total': custo_total,
            'modelo': '5+2',
            'grupo_a': sorted(grupo_a),
            'grupo_b': sorted(grupo_b),
            'mes': mes
        }

    @staticmethod
    def _gerar_combinacoes_2(lista):
        """Gera todas as combinações de 2 elementos de uma lista"""
        combinacoes = []
        n = len(lista)

        for i in range(n):
            for j in range(i + 1, n):
                combinacoes.append((lista[i], lista[j]))

        return combinacoes

    @staticmethod
    def validar_grupos(grupo_a, grupo_b):
        """Valida se os grupos estão corretos"""
        erros = []

        # Validar Grupo A
        if len(grupo_a) != 5:
            erros.append('Grupo A deve ter exatamente 5 dezenas')

        if len(set(grupo_a)) != len(grupo_a):
            erros.append('Grupo A não pode ter dezenas duplicadas')

        for num in grupo_a:
            if not (1 <= num <= 31):
                erros.append(f'Dezena {num} inválida no Grupo A (deve ser entre 1 e 31)')

        # Validar Grupo B
        if len(grupo_b) < 2:
            erros.append('Grupo B deve ter pelo menos 2 dezenas')

        if len(set(grupo_b)) != len(grupo_b):
            erros.append('Grupo B não pode ter dezenas duplicadas')

        for num in grupo_b:
            if not (1 <= num <= 31):
                erros.append(f'Dezena {num} inválida no Grupo B (deve ser entre 1 e 31)')

        # Validar interseção (não pode ter números iguais em A e B)
        intersecao = set(grupo_a) & set(grupo_b)
        if intersecao:
            erros.append(f'Dezenas {sorted(intersecao)} estão em ambos os grupos (deve estar apenas em um)')

        return {
            'valido': len(erros) == 0,
            'erros': erros
        }

    @staticmethod
    def gerar_sugestao_modelo_b():
        """
        Gera sugestão automática para Modelo B: 2 grupos de 5 dezenas cada
        Retorna: dict com grupoA (5 dezenas) e grupoB (5 dezenas)
        """
        # Analisar TODOS os concursos do banco de dados
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {
                'erro': 'Nenhum sorteio encontrado para análise',
                'grupoA': [],
                'grupoB': []
            }

        # Análise estatística
        analise = DesdobramentoService._analisar_frequencias(sorteios)

        # Estratégia: dividir dezenas em 2 grupos balanceados
        # Grupo A: números baixos e médios (1-20) mais frequentes
        # Grupo B: números médios e altos (11-31) mais frequentes

        todos_numeros = list(range(1, 32))
        numeros_com_freq = [(n, analise['frequencias'].get(n, 0)) for n in todos_numeros]
        numeros_com_freq.sort(key=lambda x: x[1], reverse=True)

        # Pegar os 10 números mais frequentes
        top_10 = [n for n, f in numeros_com_freq[:10]]

        # Dividir em 2 grupos de 5
        grupo_a = sorted(top_10[:5])
        grupo_b = sorted(top_10[5:10])

        return {
            'grupoA': grupo_a,
            'grupoB': grupo_b,
            'total_concursos_analisados': len(sorteios)
        }

    @staticmethod
    def gerar_jogos_modelo_b(grupo_a, grupo_b, mes='Jan'):
        """
        Gera jogos do Modelo B: Dois grupos fixos (5+5) com variações cruzadas

        Lógica:
        - BLOCO A: Grupo A (fixo) + combinações de 2 dezenas do Grupo B = 10 jogos
        - BLOCO B: Grupo B (fixo) + combinações de 2 dezenas do Grupo A = 10 jogos
        - TOTAL: 20 jogos

        Exemplo:
        Grupo A: [3, 4, 10, 12, 19]
        Grupo B: [22, 23, 26, 30, 31]

        Bloco A:
        Jogo 1: 03 04 10 12 19 + 22 23 = 7 dezenas
        Jogo 2: 03 04 10 12 19 + 22 26 = 7 dezenas
        ...
        Jogo 10: 03 04 10 12 19 + 30 31 = 7 dezenas

        Bloco B:
        Jogo 11: 22 23 26 30 31 + 03 04 = 7 dezenas
        Jogo 12: 22 23 26 30 31 + 03 10 = 7 dezenas
        ...
        Jogo 20: 22 23 26 30 31 + 12 19 = 7 dezenas
        """
        from itertools import combinations

        # Validações
        if len(grupo_a) != 5:
            return {'erro': 'Grupo A deve ter exatamente 5 dezenas'}

        if len(grupo_b) != 5:
            return {'erro': 'Grupo B deve ter exatamente 5 dezenas'}

        # Verificar se não há dezenas em comum
        if set(grupo_a) & set(grupo_b):
            return {'erro': 'Os grupos A e B não podem ter dezenas em comum'}

        jogos = []
        contador = 1

        # BLOCO A: Grupo A fixo + C(Grupo B, 2)
        for combo_b in combinations(sorted(grupo_b), 2):
            numeros_completos = sorted(grupo_a + list(combo_b))
            jogos.append({
                'numero': contador,
                'bloco': 'A',
                'fixas': sorted(grupo_a),
                'variaveis': list(combo_b),
                'numeros_completos': numeros_completos,
                'mes': mes
            })
            contador += 1

        # BLOCO B: Grupo B fixo + C(Grupo A, 2)
        for combo_a in combinations(sorted(grupo_a), 2):
            numeros_completos = sorted(grupo_b + list(combo_a))
            jogos.append({
                'numero': contador,
                'bloco': 'B',
                'fixas': sorted(grupo_b),
                'variaveis': list(combo_a),
                'numeros_completos': numeros_completos,
                'mes': mes
            })
            contador += 1

        total_jogos = len(jogos)
        custo_unitario = 2.50
        custo_total = total_jogos * custo_unitario

        # Contar jogos por bloco
        total_bloco_a = len([j for j in jogos if j['bloco'] == 'A'])
        total_bloco_b = len([j for j in jogos if j['bloco'] == 'B'])

        return {
            'jogos': jogos,
            'total_jogos': total_jogos,
            'total_bloco_a': total_bloco_a,
            'total_bloco_b': total_bloco_b,
            'custo_unitario': custo_unitario,
            'custo_total': custo_total,
            'modelo': 'B',
            'grupo_a': sorted(grupo_a),
            'grupo_b': sorted(grupo_b),
            'mes': mes
        }

    @staticmethod
    def gerar_sugestao_modelo_c():
        """
        Gera sugestão automática para Modelo C: 5 fixas + pool de 8 variáveis
        Retorna: dict com grupoA (5 dezenas) e grupoC (8 dezenas para trios)
        """
        # Analisar TODOS os concursos do banco de dados
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {
                'erro': 'Nenhum sorteio encontrado para análise',
                'grupoA': [],
                'grupoC': []
            }

        # Análise estatística
        analise = DesdobramentoService._analisar_frequencias(sorteios)

        # Selecionar Grupo A (5 fixas) - mesma estratégia do Modelo A
        grupo_a = DesdobramentoService._selecionar_grupo_a(analise)

        # Selecionar Grupo C (8 variáveis) - mesma estratégia do Modelo A para Grupo B
        grupo_c = DesdobramentoService._selecionar_grupo_b(analise, grupo_a)

        # Gerar explicações
        explicacoes = DesdobramentoService._gerar_explicacoes(grupo_a, analise)

        return {
            'grupoA': sorted(grupo_a),
            'grupoC': sorted(grupo_c),
            'explicacoes': explicacoes,
            'total_concursos_analisados': len(sorteios)
        }

    @staticmethod
    def gerar_jogos_modelo_c(grupo_a, grupo_c, mes='Jan'):
        """
        Gera jogos do Modelo C: 5 fixas + combinações de 3 variáveis

        Lógica:
        - Grupo A (5 dezenas fixas) aparece em TODOS os jogos
        - Grupo C (6-15 dezenas) gera combinações de 3
        - Cada jogo = 5 fixas + 3 variáveis = 7 dezenas totais

        Exemplo:
        Grupo A: [3, 7, 11, 18, 25]
        Grupo C: [2, 4, 6, 15, 17, 19, 23, 31] (8 dezenas)

        Total: C(8, 3) = 56 jogos

        Jogo 1: 03 07 11 18 25 + 02 04 06 = 7 dezenas
        Jogo 2: 03 07 11 18 25 + 02 04 15 = 7 dezenas
        ...
        Jogo 56: 03 07 11 18 25 + 19 23 31 = 7 dezenas
        """
        from itertools import combinations

        # Validações
        if len(grupo_a) != 5:
            return {'erro': 'Grupo A deve ter exatamente 5 dezenas'}

        if len(grupo_c) < 6:
            return {'erro': 'Grupo C deve ter pelo menos 6 dezenas'}

        if len(grupo_c) > 15:
            return {'erro': 'Grupo C pode ter no máximo 15 dezenas'}

        # Verificar se não há dezenas em comum
        if set(grupo_a) & set(grupo_c):
            return {'erro': 'Os grupos A e C não podem ter dezenas em comum'}

        jogos = []
        contador = 1

        # Gerar todas as combinações de 3 dezenas do Grupo C
        for trio in combinations(sorted(grupo_c), 3):
            numeros_completos = sorted(grupo_a + list(trio))
            jogos.append({
                'numero': contador,
                'fixas': sorted(grupo_a),
                'variaveis': list(trio),
                'numeros_completos': numeros_completos,
                'mes': mes
            })
            contador += 1

        total_jogos = len(jogos)
        custo_unitario = 2.50
        custo_total = total_jogos * custo_unitario

        return {
            'jogos': jogos,
            'total_jogos': total_jogos,
            'custo_unitario': custo_unitario,
            'custo_total': custo_total,
            'modelo': 'C',
            'grupo_a': sorted(grupo_a),
            'grupo_c': sorted(grupo_c),
            'mes': mes
        }

    @staticmethod
    def gerar_sugestao_modelo_d():
        """
        Gera sugestão automática para Modelo D: 4 fixas + 3 blocos de 5 dezenas
        Retorna: dict com fixas (4), blocoA (5), blocoB (5), blocoC (5)
        """
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {
                'erro': 'Nenhum sorteio encontrado para análise',
                'fixas': [],
                'blocoA': [],
                'blocoB': [],
                'blocoC': []
            }

        analise = DesdobramentoService._analisar_frequencias(sorteios)

        # Selecionar 4 fixas (os números mais quentes)
        todos_numeros = list(range(1, 32))
        numeros_com_freq = [(n, analise['frequencias'].get(n, 0)) for n in todos_numeros]
        numeros_com_freq.sort(key=lambda x: x[1], reverse=True)

        fixas = sorted([n for n, f in numeros_com_freq[:4]])

        # Números disponíveis para os blocos
        disponiveis = [n for n in todos_numeros if n not in fixas]

        # Bloco A: 5 mais quentes dos disponíveis
        quentes_disp = [n for n in numeros_com_freq if n[0] in disponiveis]
        bloco_a = sorted([n for n, f in quentes_disp[:5]])

        # Bloco B: próximos 5
        bloco_b = sorted([n for n, f in quentes_disp[5:10]])

        # Bloco C: próximos 5
        bloco_c = sorted([n for n, f in quentes_disp[10:15]])

        # Gerar explicações para as fixas
        explicacoes = {}
        for num in fixas:
            freq = analise['frequencias'].get(num, 0)
            total = analise['total_sorteios']
            percentual = (freq / total * 100) if total > 0 else 0

            explicacoes[num] = {
                'emoji': '🔥',
                'motivo': f'Número MUITO QUENTE - Saiu em {percentual:.0f}% dos concursos (freq: {freq}x)',
                'frequencia': freq,
                'percentual': round(percentual, 2)
            }

        return {
            'fixas': fixas,
            'blocoA': bloco_a,
            'blocoB': bloco_b,
            'blocoC': bloco_c,
            'explicacoes': explicacoes,
            'total_concursos_analisados': len(sorteios)
        }

    @staticmethod
    def gerar_jogos_modelo_d(fixas, bloco_a, bloco_b, bloco_c, mes='Jan'):
        """
        Gera jogos do Modelo D: Blocos rotativos com garantia progressiva

        Lógica:
        - 4 dezenas fixas (aparecem em TODOS os jogos)
        - 3 blocos de 5 dezenas cada
        - Para cada bloco: gera C(5,3) = 10 jogos com as 4 fixas + 3 do bloco
        - Total: 30 jogos (10 por bloco)
        - Cada jogo tem 7 dezenas (4 fixas + 3 do bloco)

        Exemplo:
        Fixas: [3, 12, 18, 25]
        Bloco A: [1, 2, 5, 8, 9]
        Bloco B: [7, 11, 14, 19, 23]
        Bloco C: [4, 6, 13, 20, 27]

        Bloco A gera 10 jogos: (1,2,3,5,12,18,25), (1,2,3,8,12,18,25), etc.
        Bloco B gera 10 jogos: (3,7,11,12,14,18,25), (3,7,11,12,18,19,25), etc.
        Bloco C gera 10 jogos: (3,4,6,12,13,18,25), (3,4,6,12,18,20,25), etc.
        """
        from itertools import combinations

        # Validações
        if len(fixas) != 4:
            return {'erro': 'Fixas devem ter exatamente 4 dezenas'}

        if len(bloco_a) != 5:
            return {'erro': 'Bloco A deve ter exatamente 5 dezenas'}

        if len(bloco_b) != 5:
            return {'erro': 'Bloco B deve ter exatamente 5 dezenas'}

        if len(bloco_c) != 5:
            return {'erro': 'Bloco C deve ter exatamente 5 dezenas'}

        # Verificar se fixas não aparecem nos blocos
        fixas_set = set(fixas)
        if fixas_set & set(bloco_a):
            return {'erro': 'Fixas não podem aparecer no Bloco A'}
        if fixas_set & set(bloco_b):
            return {'erro': 'Fixas não podem aparecer no Bloco B'}
        if fixas_set & set(bloco_c):
            return {'erro': 'Fixas não podem aparecer no Bloco C'}

        jogos = []
        contador = 1

        # BLOCO A: Fixas + C(Bloco A, 3)
        for trio in combinations(sorted(bloco_a), 3):
            numeros_completos = sorted(fixas + list(trio))
            jogos.append({
                'numero': contador,
                'bloco': 'A',
                'fixas': sorted(fixas),
                'variaveis': list(trio),
                'numeros_completos': numeros_completos,
                'mes': mes
            })
            contador += 1

        # BLOCO B: Fixas + C(Bloco B, 3)
        for trio in combinations(sorted(bloco_b), 3):
            numeros_completos = sorted(fixas + list(trio))
            jogos.append({
                'numero': contador,
                'bloco': 'B',
                'fixas': sorted(fixas),
                'variaveis': list(trio),
                'numeros_completos': numeros_completos,
                'mes': mes
            })
            contador += 1

        # BLOCO C: Fixas + C(Bloco C, 3)
        for trio in combinations(sorted(bloco_c), 3):
            numeros_completos = sorted(fixas + list(trio))
            jogos.append({
                'numero': contador,
                'bloco': 'C',
                'fixas': sorted(fixas),
                'variaveis': list(trio),
                'numeros_completos': numeros_completos,
                'mes': mes
            })
            contador += 1

        total_jogos = len(jogos)
        custo_unitario = 2.50
        custo_total = total_jogos * custo_unitario

        # Contar jogos por bloco
        total_bloco_a = len([j for j in jogos if j['bloco'] == 'A'])
        total_bloco_b = len([j for j in jogos if j['bloco'] == 'B'])
        total_bloco_c = len([j for j in jogos if j['bloco'] == 'C'])

        return {
            'jogos': jogos,
            'total_jogos': total_jogos,
            'total_bloco_a': total_bloco_a,
            'total_bloco_b': total_bloco_b,
            'total_bloco_c': total_bloco_c,
            'custo_unitario': custo_unitario,
            'custo_total': custo_total,
            'modelo': 'D',
            'fixas': sorted(fixas),
            'bloco_a': sorted(bloco_a),
            'bloco_b': sorted(bloco_b),
            'bloco_c': sorted(bloco_c),
            'mes': mes
        }

    @staticmethod
    def obter_nome_mes(numero_ou_sigla):
        """Converte número ou sigla para nome completo do mês"""
        meses_numero = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        meses_sigla = {
            'Jan': 'Janeiro', 'Fev': 'Fevereiro', 'Mar': 'Março', 'Abr': 'Abril',
            'Mai': 'Maio', 'Jun': 'Junho', 'Jul': 'Julho', 'Ago': 'Agosto',
            'Set': 'Setembro', 'Out': 'Outubro', 'Nov': 'Novembro', 'Dez': 'Dezembro'
        }

        if isinstance(numero_ou_sigla, int):
            return meses_numero.get(numero_ou_sigla, 'Desconhecido')
        else:
            return meses_sigla.get(numero_ou_sigla, numero_ou_sigla)

    # ========================================================================
    # MODELO E: REDUÇÃO INTELIGENTE DO ÚLTIMO SORTEIO
    # ========================================================================

    @staticmethod
    def gerar_sugestao_modelo_e(nivel=2):
        """
        Gera sugestão automática para Modelo E: Redução do último sorteio
        Retorna: dict com sorteio_base (7 números), complementares (24 números), nivel

        Args:
            nivel: Nível de redução (1-6)
                   - Nível 1: C(7,1) = 7 jogos (1 do sorteio + 6 complementares)
                   - Nível 2: C(7,2) = 21 jogos (2 do sorteio + 5 complementares)
                   - Nível 3: C(7,3) = 35 jogos (3 do sorteio + 4 complementares)
                   - Nível 4: C(7,4) = 35 jogos (4 do sorteio + 3 complementares)
                   - Nível 5: C(7,5) = 21 jogos (5 do sorteio + 2 complementares)
                   - Nível 6: C(7,6) = 7 jogos (6 do sorteio + 1 complementar)
        """
        # Buscar último sorteio
        ultimo_sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

        if not ultimo_sorteio:
            return {
                'erro': 'Nenhum sorteio encontrado',
                'sorteio_base': [],
                'complementares': [],
                'nivel': nivel
            }

        # Obter números do último sorteio
        sorteio_base = sorted(ultimo_sorteio.get_posicoes_lista())

        # Calcular complementares (1-31 menos os 7 sorteados)
        complementares = sorted([n for n in range(1, 32) if n not in sorteio_base])

        # Calcular total de jogos para o nível
        total_jogos = DesdobramentoService.calcular_combinacoes(7, nivel)
        complemento_por_jogo = 7 - nivel

        return {
            'sorteio_base': sorteio_base,
            'complementares': complementares,
            'nivel': nivel,
            'total_jogos': total_jogos,
            'complemento_por_jogo': complemento_por_jogo,
            'concurso': ultimo_sorteio.concurso,
            'mes_sorteio': ultimo_sorteio.mes_sorte
        }

    @staticmethod
    def gerar_jogos_modelo_e(sorteio_base, complementares, nivel=2, mes='Jan', dezenas_por_jogo=7):
        """
        Gera jogos do Modelo E: Redução Inteligente do Último Sorteio

        Lógica:
        - Pega os 7 números do último sorteio
        - Gera C(7, nivel) combinações desses números
        - Completa cada jogo com números complementares (que NÃO saíram)
        - Cada jogo tem dezenas_por_jogo dezenas: nivel do sorteio + (dezenas_por_jogo-nivel) complementares

        Args:
            sorteio_base: Lista com os 7 números do último sorteio
            complementares: Lista com os números disponíveis para complemento (1-31 menos sorteio)
            nivel: Nível de redução (1-6)
            mes: Mês da sorte
            dezenas_por_jogo: Quantidade de dezenas por jogo (7 a 15)

        Exemplo (Nível 2, 15 dezenas por jogo):
        Sorteio: [03, 07, 12, 18, 22, 28, 31]
        Complementares: [01, 02, 04, 05, 06, 08, 09, 10, 11, 13, ...]

        C(7,2) = 21 pares:
        Par [03, 07] + 13 complementares balanceados = 15 dezenas
        Par [03, 12] + 13 complementares balanceados = 15 dezenas
        ...
        """
        from itertools import combinations
        import random

        # Validações
        if len(sorteio_base) != 7:
            return {'erro': 'Sorteio base deve ter exatamente 7 dezenas'}

        if nivel < 1 or nivel > 6:
            return {'erro': 'Nível deve estar entre 1 e 6'}

        if dezenas_por_jogo < 7 or dezenas_por_jogo > 15:
            return {'erro': 'Dezenas por jogo deve estar entre 7 e 15'}

        if dezenas_por_jogo < nivel:
            return {'erro': f'Dezenas por jogo ({dezenas_por_jogo}) não pode ser menor que o nível ({nivel})'}

        complemento_necessario = dezenas_por_jogo - nivel

        if len(complementares) < complemento_necessario:
            return {'erro': f'Necessário pelo menos {complemento_necessario} números complementares para {dezenas_por_jogo} dezenas por jogo'}

        # Classificar complementares por faixas para balanceamento
        baixas = sorted([n for n in complementares if 1 <= n <= 10])
        medias = sorted([n for n in complementares if 11 <= n <= 20])
        altas = sorted([n for n in complementares if 21 <= n <= 31])

        jogos = []
        contador = 1

        # Gerar todas as combinações C(7, nivel) do sorteio base
        for combo_sorteio in combinations(sorted(sorteio_base), nivel):
            # Selecionar complementares de forma balanceada
            complemento = DesdobramentoService._selecionar_complementares_balanceados(
                list(combo_sorteio),
                complementares,
                complemento_necessario,
                baixas,
                medias,
                altas,
                contador  # usar como seed para variar
            )

            numeros_completos = sorted(list(combo_sorteio) + complemento)

            jogos.append({
                'numero': contador,
                'do_sorteio': sorted(list(combo_sorteio)),
                'complementares': sorted(complemento),
                'numeros_completos': numeros_completos,
                'mes': mes
            })
            contador += 1

        total_jogos = len(jogos)
        custo_unitario = 2.50
        custo_total = total_jogos * custo_unitario

        return {
            'jogos': jogos,
            'total_jogos': total_jogos,
            'custo_unitario': custo_unitario,
            'custo_total': custo_total,
            'modelo': 'E',
            'nivel': nivel,
            'dezenas_por_jogo': dezenas_por_jogo,
            'sorteio_base': sorted(sorteio_base),
            'complementares_disponiveis': sorted(complementares),
            'mes': mes
        }

    @staticmethod
    def _selecionar_complementares_balanceados(combo_sorteio, complementares, quantidade, baixas, medias, altas, seed=0):
        """
        Seleciona números complementares de forma balanceada entre as faixas

        Distribuição ideal para Dia de Sorte (7 números de 1-31):
        - Baixas (01-10): ~2-3 números
        - Médias (11-20): ~2-3 números
        - Altas (21-31): ~2-3 números

        Ajusta conforme quantos números do sorteio já estão em cada faixa
        """
        import random
        random.seed(seed)

        # Contar quantos do sorteio estão em cada faixa
        sorteio_baixas = len([n for n in combo_sorteio if 1 <= n <= 10])
        sorteio_medias = len([n for n in combo_sorteio if 11 <= n <= 20])
        sorteio_altas = len([n for n in combo_sorteio if 21 <= n <= 31])

        # Calcular quantos complementares precisamos de cada faixa
        # Meta: ~2-3 de cada faixa no jogo final (7 números)
        meta_baixas = max(0, 2 - sorteio_baixas)
        meta_medias = max(0, 2 - sorteio_medias)
        meta_altas = max(0, 2 - sorteio_altas)

        # Ajustar para a quantidade necessária
        total_meta = meta_baixas + meta_medias + meta_altas

        if total_meta > quantidade:
            # Reduzir proporcionalmente
            fator = quantidade / total_meta
            meta_baixas = int(meta_baixas * fator)
            meta_medias = int(meta_medias * fator)
            meta_altas = quantidade - meta_baixas - meta_medias
        elif total_meta < quantidade:
            # Distribuir o excesso
            excesso = quantidade - total_meta
            # Adicionar ao grupo com mais disponíveis
            if len(baixas) > meta_baixas:
                meta_baixas += min(excesso, len(baixas) - meta_baixas)
                excesso = quantidade - (meta_baixas + meta_medias + meta_altas)
            if excesso > 0 and len(medias) > meta_medias:
                meta_medias += min(excesso, len(medias) - meta_medias)
                excesso = quantidade - (meta_baixas + meta_medias + meta_altas)
            if excesso > 0 and len(altas) > meta_altas:
                meta_altas += min(excesso, len(altas) - meta_altas)

        resultado = []

        # Selecionar de cada faixa
        if baixas and meta_baixas > 0:
            escolhidos = random.sample(baixas, min(meta_baixas, len(baixas)))
            resultado.extend(escolhidos)

        if medias and meta_medias > 0:
            escolhidos = random.sample(medias, min(meta_medias, len(medias)))
            resultado.extend(escolhidos)

        if altas and meta_altas > 0:
            escolhidos = random.sample(altas, min(meta_altas, len(altas)))
            resultado.extend(escolhidos)

        # Se ainda faltam, pegar de qualquer faixa disponível
        while len(resultado) < quantidade:
            disponiveis = [n for n in complementares if n not in resultado]
            if not disponiveis:
                break
            resultado.append(random.choice(disponiveis))

        return sorted(resultado[:quantidade])

# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Atualizado: Com seletor de mês (mes_override) e 4 novos métodos de padrões

from models.sorteio import Sorteio
from services.estatistica_service import EstatisticaService
from services.mes_sorte_score_service import MesSorteScoreService
import random
from datetime import datetime


class PalpiteService:
    """
    Serviço para geração de palpites inteligentes
    Baseado em: frequência, atrasos, lacunas, regressão à média, padrões de dezenas

    MÉTODOS DISPONÍVEIS:
    - simples: Aleatório (Surpresinha)
    - frequencia: Baseado em frequência
    - atraso: Baseado em atraso
    - misto: 4 frequentes + 3 atrasados
    - posicao: Por posição
    - inteligente: 50% freq + 50% atraso

    🆕 NOVOS MÉTODOS (Padrões de Dezenas):
    - padroes_faltantes: Padrões que nunca saíram
    - padroes_frequentes: Top 10 padrões mais frequentes
    - padroes_atrasados: Top 10 padrões mais atrasados
    - digitos_iniciais_top3: Top 3 dígitos iniciais
    """

    # =========================================================================
    # HELPER: OBTER MÊS DA SORTE
    # =========================================================================

    @staticmethod
    def _obter_mes_sorte(mes_override=None):
        """
        Obtém o mês da sorte a ser usado.

        Args:
            mes_override: Se fornecido (1-12), usa este mês.
                          Se None, usa o mês mais frequente.

        Returns:
            int: Número do mês (1-12)
        """
        if mes_override and 1 <= mes_override <= 12:
            return mes_override

        # Fallback: mês mais frequente
        stats_mes = EstatisticaService.estatisticas_mes_sorte()
        if stats_mes and stats_mes.get('mais_sorteado'):
            return stats_mes['mais_sorteado']['mes']

        # Fallback final: aleatório
        return random.randint(1, 12)

    # =========================================================================
    # MÉTODOS ORIGINAIS
    # =========================================================================

    @staticmethod
    def gerar_palpite_simples(mes_override=None):
        """
        Gera um palpite simples (7 números aleatórios únicos)
        """
        numeros = random.sample(range(1, 32), 7)
        numeros.sort()

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'simples',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': 'Aleatório (Surpresinha)'
        }

    @staticmethod
    def gerar_palpite_por_frequencia(top=15, mes_override=None):
        """
        Gera palpite baseado nos números mais frequentes
        """
        frequencias = EstatisticaService.frequencia_geral()

        if not frequencias:
            return PalpiteService.gerar_palpite_simples(mes_override)

        # Pegar os 'top' números mais frequentes
        mais_frequentes = [f['numero'] for f in frequencias[:top]]

        # Escolher 7 aleatoriamente entre os mais frequentes
        numeros = random.sample(mais_frequentes, min(7, len(mais_frequentes)))

        # Completar se necessário
        while len(numeros) < 7:
            novo = random.randint(1, 31)
            if novo not in numeros:
                numeros.append(novo)

        numeros.sort()

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'frequencia',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': 'Baseado nos números mais frequentes'
        }

    @staticmethod
    def gerar_palpite_por_atraso(top=15, mes_override=None):
        """
        Gera palpite baseado nos números mais atrasados
        """
        atrasados = EstatisticaService.numeros_atrasados(limite=top)

        if not atrasados or 'numeros_atrasados' not in atrasados:
            return PalpiteService.gerar_palpite_simples(mes_override)

        # Pegar os números mais atrasados
        mais_atrasados = [a['numero'] for a in atrasados['numeros_atrasados'][:top]]

        # Escolher 7 aleatoriamente
        numeros = random.sample(mais_atrasados, min(7, len(mais_atrasados)))

        # Completar se necessário
        while len(numeros) < 7:
            novo = random.randint(1, 31)
            if novo not in numeros:
                numeros.append(novo)

        numeros.sort()

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'atraso',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': 'Baseado nos números mais atrasados'
        }

    @staticmethod
    def gerar_palpite_misto(mes_override=None):
        """
        Gera palpite misto: combina frequência + atraso
        """
        frequencias = EstatisticaService.frequencia_geral()
        atrasados = EstatisticaService.numeros_atrasados(limite=10)

        if not frequencias or not atrasados or 'numeros_atrasados' not in atrasados:
            return PalpiteService.gerar_palpite_simples(mes_override)

        # 4 dos mais frequentes
        mais_frequentes = [f['numero'] for f in frequencias[:10]]
        escolhidos_freq = random.sample(mais_frequentes, min(4, len(mais_frequentes)))

        # 3 dos mais atrasados
        mais_atrasados = [a['numero'] for a in atrasados['numeros_atrasados'][:10]]
        # Remover os já escolhidos
        mais_atrasados = [n for n in mais_atrasados if n not in escolhidos_freq]
        escolhidos_atraso = random.sample(mais_atrasados, min(3, len(mais_atrasados)))

        numeros = escolhidos_freq + escolhidos_atraso

        # Completar se necessário
        while len(numeros) < 7:
            novo = random.randint(1, 31)
            if novo not in numeros:
                numeros.append(novo)

        numeros.sort()

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'misto',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': 'Combinação: 4 mais frequentes + 3 mais atrasados'
        }

    @staticmethod
    def gerar_palpite_por_posicao(mes_override=None):
        """
        Gera palpite baseado na frequência de cada posição
        Escolhe o número mais frequente de cada posição (1 a 7)
        """
        freq_por_pos = EstatisticaService.frequencia_por_posicao()

        if not freq_por_pos or 'total_sorteios' not in freq_por_pos:
            return PalpiteService.gerar_palpite_simples(mes_override)

        numeros = []

        for pos in range(1, 8):
            key = f'posicao_{pos}'
            if key in freq_por_pos and freq_por_pos[key].get('mais_frequente'):
                numero = freq_por_pos[key]['mais_frequente']['numero']

                # Evitar duplicatas
                if numero in numeros:
                    # Pegar o segundo mais frequente
                    todos_numeros = freq_por_pos[key]['numeros']
                    for item in todos_numeros:
                        if item['numero'] not in numeros:
                            numero = item['numero']
                            break

                numeros.append(numero)

        # Completar se necessário
        while len(numeros) < 7:
            novo = random.randint(1, 31)
            if novo not in numeros:
                numeros.append(novo)

        numeros.sort()

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'posicao',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': 'Baseado nos números mais frequentes por posição'
        }

    @staticmethod
    def gerar_palpite_inteligente(mes_override=None):
        """
        Gera palpite inteligente usando múltiplos critérios
        Pontuação baseada em: frequência, atraso, lacunas
        """
        frequencias = EstatisticaService.frequencia_geral()
        atrasados_dados = EstatisticaService.numeros_atrasados(limite=31)

        if not frequencias or not atrasados_dados or 'numeros_atrasados' not in atrasados_dados:
            return PalpiteService.gerar_palpite_misto(mes_override)

        # Criar dicionário de atrasos
        atrasos = {a['numero']: a['atraso'] for a in atrasados_dados['numeros_atrasados']}

        # Calcular pontuação para cada número
        pontuacoes = {}

        for freq in frequencias:
            numero = freq['numero']

            # Pontos por frequência (normalizado 0-100)
            pts_freq = freq['percentual']

            # Pontos por atraso (quanto maior o atraso, mais pontos)
            atraso = atrasos.get(numero, 0)
            pts_atraso = min(atraso * 2, 100)  # Máximo 100 pontos

            # Pontuação balanceada (50% freq + 50% atraso)
            pontuacao_total = (pts_freq * 0.5) + (pts_atraso * 0.5)

            pontuacoes[numero] = pontuacao_total

        # Ordenar por pontuação
        numeros_ordenados = sorted(pontuacoes.items(), key=lambda x: x[1], reverse=True)

        # Escolher os 7 melhores
        top_15 = [n[0] for n in numeros_ordenados[:15]]
        numeros = random.sample(top_15, min(7, len(top_15)))

        # Completar se necessário
        while len(numeros) < 7:
            novo = random.randint(1, 31)
            if novo not in numeros:
                numeros.append(novo)

        numeros.sort()

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'inteligente',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': 'Algoritmo inteligente: 50% frequência + 50% atraso'
        }

    # =========================================================================
    # 🆕 NOVOS MÉTODOS DE GERAÇÃO POR PADRÕES DE DEZENAS
    # =========================================================================

    @staticmethod
    def _obter_dados_padroes_dezenas():
        """
        Obtém dados de padrões por dezenas da API interna
        Retorna: dict com padroes_faltantes, top_10_frequentes, top_10_atrasados
        """
        try:
            from services.analise_digito_padrao_inicial_final_service import AnaliseDigitoPadraoInicialFinalService
            dados = AnaliseDigitoPadraoInicialFinalService.analisar_padroes_dezenas()

            if dados.get('error'):
                print(f"[WARN] Erro ao obter padrões de dezenas: {dados.get('error')}")
                return None

            return dados
        except Exception as e:
            print(f"[ERROR] Erro ao obter padrões de dezenas: {e}")
            return None

    @staticmethod
    def _obter_top3_digitos_iniciais():
        """
        Obtém os Top 3 padrões de dígitos iniciais
        Retorna: lista dos 3 padrões mais frequentes
        """
        try:
            from services.analise_digito_padrao_inicial_final_service import AnaliseDigitoPadraoInicialFinalService
            dados = AnaliseDigitoPadraoInicialFinalService.analisar_padroes()

            if dados.get('error'):
                return None

            # Extrair top 3 padrões simples
            top_padroes = dados.get('top_padroes_digitos_iniciais_simples', [])[:3]
            return top_padroes
        except Exception as e:
            print(f"[ERROR] Erro ao obter top 3 dígitos iniciais: {e}")
            return None

    @staticmethod
    def _gerar_numeros_por_padrao(padrao_str):
        """
        Gera 7 números seguindo um padrão de dezenas

        Padrão: "0 0 1 1 2 2 3" significa:
        - 2 números na faixa 0 (01-09)
        - 2 números na faixa 1 (10-19)
        - 2 números na faixa 2 (20-29)
        - 1 número na faixa 3 (30-31)

        Args:
            padrao_str: String como "0 0 1 1 2 2 3"

        Returns:
            Lista de 7 números ordenados
        """
        # Faixas de números
        faixas = {
            '0': list(range(1, 10)),    # 01-09
            '1': list(range(10, 20)),   # 10-19
            '2': list(range(20, 30)),   # 20-29
            '3': [30, 31]               # 30-31
        }

        # Contar quantos de cada faixa
        partes = padrao_str.split()
        contagem = {'0': 0, '1': 0, '2': 0, '3': 0}

        for p in partes:
            if p in contagem:
                contagem[p] += 1

        # Gerar números respeitando as faixas
        numeros = []

        for faixa, qtd in contagem.items():
            if qtd > 0:
                disponiveis = faixas[faixa]
                # Garantir que não pedimos mais do que existe na faixa
                qtd_real = min(qtd, len(disponiveis))
                escolhidos = random.sample(disponiveis, qtd_real)
                numeros.extend(escolhidos)

        # Completar se necessário (caso o padrão não tenha 7)
        while len(numeros) < 7:
            novo = random.randint(1, 31)
            if novo not in numeros:
                numeros.append(novo)

        # Garantir apenas 7
        numeros = numeros[:7]
        numeros.sort()

        return numeros

    @staticmethod
    def gerar_palpite_padroes_faltantes(mes_override=None):
        """
        🆕 NOVO MÉTODO: Gera palpite baseado em padrões que NUNCA saíram
        Escolhe aleatoriamente um dos padrões faltantes e gera números nesse formato
        """
        dados = PalpiteService._obter_dados_padroes_dezenas()

        if not dados or not dados.get('padroes_faltantes'):
            # Fallback para método inteligente
            resultado = PalpiteService.gerar_palpite_inteligente(mes_override)
            resultado['fallback'] = True
            resultado['fallback_motivo'] = 'Não foi possível obter padrões faltantes'
            return resultado

        # Escolher um padrão faltante aleatório (prioriza os com mais jogos possíveis)
        faltantes = dados['padroes_faltantes']

        # Pegar apenas os viáveis (com mais de 100 jogos possíveis)
        faltantes_viaveis = [p for p in faltantes if p.get('jogos_possiveis', 0) > 100]

        if not faltantes_viaveis:
            faltantes_viaveis = faltantes[:5]  # Pegar os 5 primeiros

        if not faltantes_viaveis:
            resultado = PalpiteService.gerar_palpite_inteligente(mes_override)
            resultado['fallback'] = True
            return resultado

        # Escolher um aleatório
        padrao_escolhido = random.choice(faltantes_viaveis)
        padrao_str = padrao_escolhido['padrao']

        # Gerar números seguindo o padrão
        numeros = PalpiteService._gerar_numeros_por_padrao(padrao_str)

        # NÃO aplicar validações que alteram números - manter o padrão!
        numeros = PalpiteService._aplicar_validacoes(numeros, manter_padrao=True)

        # Calcular o padrão REAL dos números gerados
        padrao_real = PalpiteService._calcular_padrao_real(numeros)

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'padroes_faltantes',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': f'Padrão Faltante: {padrao_real} (nunca saiu!)',
            'padrao_utilizado': padrao_real,
            'padrao_solicitado': padrao_str,
            'jogos_possiveis': padrao_escolhido.get('jogos_possiveis', 0),
            'validado': True
        }

    @staticmethod
    def gerar_palpite_padroes_frequentes(mes_override=None):
        """
        🆕 NOVO MÉTODO: Gera palpite baseado nos Top 10 padrões mais frequentes
        """
        dados = PalpiteService._obter_dados_padroes_dezenas()

        if not dados or not dados.get('top_10_frequentes'):
            resultado = PalpiteService.gerar_palpite_inteligente(mes_override)
            resultado['fallback'] = True
            resultado['fallback_motivo'] = 'Não foi possível obter padrões frequentes'
            return resultado

        # Escolher um dos top 10 mais frequentes (com peso para os mais frequentes)
        frequentes = dados['top_10_frequentes']

        if not frequentes:
            resultado = PalpiteService.gerar_palpite_inteligente(mes_override)
            resultado['fallback'] = True
            return resultado

        # Ponderar por frequência
        pesos = [p.get('frequencia', 1) for p in frequentes]
        padrao_escolhido = random.choices(frequentes, weights=pesos, k=1)[0]
        padrao_str = padrao_escolhido['padrao']

        # Gerar números seguindo o padrão
        numeros = PalpiteService._gerar_numeros_por_padrao(padrao_str)

        # NÃO aplicar validações que alteram números - manter o padrão!
        numeros = PalpiteService._aplicar_validacoes(numeros, manter_padrao=True)

        # Calcular o padrão REAL dos números gerados
        padrao_real = PalpiteService._calcular_padrao_real(numeros)

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'padroes_frequentes',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': f'Padrão Frequente: {padrao_real} ({padrao_escolhido.get("frequencia", 0)}x)',
            'padrao_utilizado': padrao_real,
            'padrao_solicitado': padrao_str,
            'frequencia_historica': padrao_escolhido.get('frequencia', 0),
            'validado': True
        }

    @staticmethod
    def gerar_palpite_padroes_atrasados(mes_override=None):
        """
        🆕 NOVO MÉTODO: Gera palpite baseado nos Top 10 padrões mais atrasados
        """
        dados = PalpiteService._obter_dados_padroes_dezenas()

        if not dados or not dados.get('top_10_atrasados'):
            resultado = PalpiteService.gerar_palpite_inteligente(mes_override)
            resultado['fallback'] = True
            resultado['fallback_motivo'] = 'Não foi possível obter padrões atrasados'
            return resultado

        # Escolher um dos top 10 mais atrasados (com peso para os mais atrasados)
        atrasados = dados['top_10_atrasados']

        if not atrasados:
            resultado = PalpiteService.gerar_palpite_inteligente(mes_override)
            resultado['fallback'] = True
            return resultado

        # Ponderar por atraso
        pesos = [p.get('atraso', 1) for p in atrasados]
        padrao_escolhido = random.choices(atrasados, weights=pesos, k=1)[0]
        padrao_str = padrao_escolhido['padrao']

        # Gerar números seguindo o padrão
        numeros = PalpiteService._gerar_numeros_por_padrao(padrao_str)

        # NÃO aplicar validações que alteram números - manter o padrão!
        numeros = PalpiteService._aplicar_validacoes(numeros, manter_padrao=True)

        # Calcular o padrão REAL dos números gerados
        padrao_real = PalpiteService._calcular_padrao_real(numeros)

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'padroes_atrasados',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': f'Padrão Atrasado: {padrao_real} ({padrao_escolhido.get("atraso", 0)} conc. sem sair)',
            'padrao_utilizado': padrao_real,
            'padrao_solicitado': padrao_str,
            'atraso': padrao_escolhido.get('atraso', 0),
            'validado': True
        }

    @staticmethod
    def gerar_palpite_digitos_iniciais_top3(mes_override=None):
        """
        🆕 NOVO MÉTODO: Gera palpite baseado nos Top 3 padrões de dígitos iniciais
        """
        top3 = PalpiteService._obter_top3_digitos_iniciais()

        if not top3:
            resultado = PalpiteService.gerar_palpite_inteligente(mes_override)
            resultado['fallback'] = True
            resultado['fallback_motivo'] = 'Não foi possível obter top 3 dígitos iniciais'
            return resultado

        # Escolher um dos top 3 (com peso para os mais frequentes)
        pesos = [p.get('frequencia', 1) for p in top3]
        padrao_escolhido = random.choices(top3, weights=pesos, k=1)[0]
        padrao_str = padrao_escolhido['padrao']

        # Gerar números seguindo o padrão
        numeros = PalpiteService._gerar_numeros_por_padrao(padrao_str)

        # NÃO aplicar validações que alteram números - manter o padrão!
        numeros = PalpiteService._aplicar_validacoes(numeros, manter_padrao=True)

        # Calcular o padrão REAL dos números gerados
        padrao_real = PalpiteService._calcular_padrao_real(numeros)

        mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

        return {
            'tipo': 'digitos_iniciais_top3',
            'numeros': numeros,
            'mes_sorte': mes_sorte,
            'metodo': f'Padrão Top 3 Dígitos Iniciais: {padrao_real} ({padrao_escolhido.get("frequencia", 0)}x)',
            'padrao_utilizado': padrao_real,
            'padrao_solicitado': padrao_str,
            'frequencia_historica': padrao_escolhido.get('frequencia', 0),
            'validado': True
        }

    # =========================================================================
    # 🆕 VALIDAÇÕES EXTRAS (APIs RECOMENDADAS)
    # =========================================================================

    @staticmethod
    def _calcular_padrao_real(numeros):
        """
        Calcula o padrão REAL de dezenas de uma lista de números

        Mapeamento:
        - 01-09 → faixa 0
        - 10-19 → faixa 1
        - 20-29 → faixa 2
        - 30-31 → faixa 3

        Args:
            numeros: Lista de números (ordenados)

        Returns:
            String do padrão como "0 1 1 2 2 2 3"
        """
        faixas = []
        for num in sorted(numeros):
            if num <= 9:
                faixas.append('0')
            elif num <= 19:
                faixas.append('1')
            elif num <= 29:
                faixas.append('2')
            else:
                faixas.append('3')
        return ' '.join(faixas)

    @staticmethod
    def _aplicar_validacoes(numeros, manter_padrao=False):
        """
        Aplica validações extras nos números gerados.

        IMPORTANTE: Para métodos de padrões (manter_padrao=True),
        NÃO altera os números para preservar o padrão original!

        Args:
            numeros: Lista de 7 números
            manter_padrao: Se True, não altera os números (apenas valida)

        Returns:
            Lista de 7 números (validados ou inalterados)
        """
        numeros_validados = list(numeros)

        # Se precisamos manter o padrão, apenas garantir 7 números únicos e ordenar
        if manter_padrao:
            numeros_validados = list(set(numeros_validados))
            while len(numeros_validados) < 7:
                # Completar mantendo a distribuição original se possível
                novo = random.randint(1, 31)
                if novo not in numeros_validados:
                    numeros_validados.append(novo)
            numeros_validados = numeros_validados[:7]
            numeros_validados.sort()
            return numeros_validados

        # =====================================================================
        # VALIDAÇÕES PARA MÉTODOS ESTATÍSTICOS (não de padrões)
        # =====================================================================

        # VALIDAÇÃO 1: Soma das dezenas (ideal: 90-140)
        soma = sum(numeros_validados)
        tentativas = 0
        max_tentativas = 20

        while (soma < 90 or soma > 140) and tentativas < max_tentativas:
            tentativas += 1

            if soma < 90:
                menor = min(numeros_validados)
                numeros_validados.remove(menor)
                novo = random.randint(20, 31)
                while novo in numeros_validados:
                    novo = random.randint(15, 31)
                numeros_validados.append(novo)
            elif soma > 140:
                maior = max(numeros_validados)
                numeros_validados.remove(maior)
                novo = random.randint(1, 15)
                while novo in numeros_validados:
                    novo = random.randint(1, 20)
                numeros_validados.append(novo)

            soma = sum(numeros_validados)

        # VALIDAÇÃO 2: Incluir pares frequentes (opcional)
        try:
            from services.analise_numeros_juntos_service import AnaliseNumerosJuntosService
            dados_juntos = AnaliseNumerosJuntosService.analisar_numeros_juntos()

            if dados_juntos and dados_juntos.get('top_pares'):
                for par_info in dados_juntos['top_pares'][:3]:
                    par = par_info.get('par', [])
                    if len(par) == 2:
                        num1, num2 = par[0], par[1]
                        if num1 not in numeros_validados and num2 not in numeros_validados:
                            if len(numeros_validados) >= 7:
                                for _ in range(2):
                                    if len(numeros_validados) > 5:
                                        numeros_validados.remove(random.choice(numeros_validados))
                                numeros_validados.extend([num1, num2])
                                break
        except Exception:
            pass

        # VALIDAÇÃO 3: Distribuição equilibrada
        faixas = {'baixa': 0, 'media': 0, 'alta': 0}
        for n in numeros_validados:
            if n <= 10:
                faixas['baixa'] += 1
            elif n <= 20:
                faixas['media'] += 1
            else:
                faixas['alta'] += 1

        tentativas = 0
        while max(faixas.values()) > 5 and tentativas < 10:
            tentativas += 1
            faixa_max = max(faixas, key=faixas.get)

            if faixa_max == 'baixa':
                candidatos = [n for n in numeros_validados if n <= 10]
            elif faixa_max == 'media':
                candidatos = [n for n in numeros_validados if 10 < n <= 20]
            else:
                candidatos = [n for n in numeros_validados if n > 20]

            if candidatos:
                numeros_validados.remove(random.choice(candidatos))
                faixa_min = min(faixas, key=faixas.get)
                if faixa_min == 'baixa':
                    novo = random.randint(1, 10)
                elif faixa_min == 'media':
                    novo = random.randint(11, 20)
                else:
                    novo = random.randint(21, 31)

                while novo in numeros_validados:
                    novo = random.randint(1, 31)
                numeros_validados.append(novo)

            faixas = {'baixa': 0, 'media': 0, 'alta': 0}
            for n in numeros_validados:
                if n <= 10:
                    faixas['baixa'] += 1
                elif n <= 20:
                    faixas['media'] += 1
                else:
                    faixas['alta'] += 1

        # Garantir exatamente 7 números únicos
        numeros_validados = list(set(numeros_validados))
        while len(numeros_validados) < 7:
            novo = random.randint(1, 31)
            if novo not in numeros_validados:
                numeros_validados.append(novo)

        numeros_validados = numeros_validados[:7]
        numeros_validados.sort()

        return numeros_validados

    @staticmethod
    def _aplicar_correlacao_mes_nos_numeros(numeros, mes_ref, max_trocas=2):
        """
        Inclui dezenas que historicamente mais saem com o Mês da Sorte escolhido,
        substituindo dezenas menos alinhadas ao top do mês (poucas trocas para não distorcer o método).
        """
        if not mes_ref or not numeros:
            return sorted(numeros)[:7]
        try:
            prioritarias = MesSorteScoreService.dezenas_prioridade_mes(mes_ref, top=12) or []
        except Exception:
            return sorted(numeros)[:7]
        if not prioritarias:
            return sorted(numeros)[:7]
        out = sorted(numeros)[:7]
        trocas = 0
        for d in prioritarias:
            if trocas >= max_trocas:
                break
            if d in out:
                continue
            removiveis = [n for n in out if n not in prioritarias[:8]]
            if not removiveis:
                removiveis = list(out)
            out.remove(removiveis[-1])
            out.append(d)
            trocas += 1
        return sorted(out[:7])

    # =========================================================================
    # GERADOR DE MÚLTIPLOS PALPITES (ATUALIZADO COM mes_override)
    # =========================================================================

    @staticmethod
    def gerar_multiplos_palpites(quantidade=5, tipo='inteligente', mes_override=None):
        """
        Gera múltiplos palpites de uma vez

        Args:
            quantidade: Número de apostas a gerar
            tipo: Método de geração
            mes_override: Mês fixo a usar (1-12) ou None para automático

        Tipos disponíveis:
        - simples: Aleatório (Surpresinha)
        - frequencia: Baseado em frequência
        - atraso: Baseado em atraso
        - misto: 4 frequentes + 3 atrasados
        - posicao: Por posição
        - inteligente: 50% freq + 50% atraso

        🆕 NOVOS:
        - padroes_faltantes: Padrões que nunca saíram (COBERTURA COMPLETA SEM REPETIÇÃO)
        - padroes_frequentes: Top 10 padrões mais frequentes
        - padroes_atrasados: Top 10 padrões mais atrasados
        - digitos_iniciais_top3: Top 3 dígitos iniciais
        """
        metodos = {
            'simples': lambda: PalpiteService.gerar_palpite_simples(mes_override),
            'frequencia': lambda: PalpiteService.gerar_palpite_por_frequencia(15, mes_override),
            'atraso': lambda: PalpiteService.gerar_palpite_por_atraso(15, mes_override),
            'misto': lambda: PalpiteService.gerar_palpite_misto(mes_override),
            'posicao': lambda: PalpiteService.gerar_palpite_por_posicao(mes_override),
            'inteligente': lambda: PalpiteService.gerar_palpite_inteligente(mes_override),
            # 🆕 NOVOS MÉTODOS
            'padroes_faltantes': lambda: PalpiteService.gerar_palpite_padroes_faltantes(mes_override),
            'padroes_frequentes': lambda: PalpiteService.gerar_palpite_padroes_frequentes(mes_override),
            'padroes_atrasados': lambda: PalpiteService.gerar_palpite_padroes_atrasados(mes_override),
            'digitos_iniciais_top3': lambda: PalpiteService.gerar_palpite_digitos_iniciais_top3(mes_override)
        }

        # VALIDAÇÃO: Verificar se o método existe
        if tipo not in metodos:
            return {
                'erro': f'Método "{tipo}" não encontrado',
                'metodos_disponiveis': list(metodos.keys()),
                'quantidade': 0,
                'palpites': []
            }

        # =====================================================================
        # 🆕 TRATAMENTO ESPECIAL: PADRÕES COM COBERTURA COMPLETA SEM REPETIÇÃO
        # =====================================================================
        tipos_com_cobertura = ['padroes_faltantes', 'padroes_frequentes', 'padroes_atrasados', 'digitos_iniciais_top3']

        if tipo in tipos_com_cobertura:
            return PalpiteService._gerar_multiplos_por_padrao_sem_repeticao(quantidade, tipo, mes_override)

        # =====================================================================
        # GERAÇÃO PADRÃO (métodos estatísticos)
        # =====================================================================
        metodo = metodos[tipo]

        palpites = []
        jogos_unicos = set()  # Para evitar duplicatas

        tentativas = 0
        max_tentativas = quantidade * 10

        while len(palpites) < quantidade and tentativas < max_tentativas:
            tentativas += 1
            palpite = metodo()
            if mes_override and isinstance(mes_override, int) and 1 <= mes_override <= 12:
                palpite['numeros'] = PalpiteService._aplicar_correlacao_mes_nos_numeros(
                    palpite['numeros'], mes_override, max_trocas=2
                )

            # Verificar duplicatas
            chave = tuple(palpite['numeros'])
            if chave not in jogos_unicos:
                jogos_unicos.add(chave)
                palpite['numero_jogo'] = len(palpites) + 1
                palpites.append(palpite)

        return {
            'sucesso': True,
            'quantidade': len(palpites),
            'tipo': tipo,
            'metodo_validado': True,
            'gerado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'palpites': palpites
        }

    @staticmethod
    def _gerar_multiplos_por_padrao_sem_repeticao(quantidade, tipo, mes_override=None):
        """
        🆕 Gera múltiplos palpites garantindo que cada PADRÃO seja usado apenas UMA vez
        Isso garante cobertura completa dos padrões disponíveis sem repetição.

        Args:
            quantidade: Número de apostas a gerar
            tipo: Tipo de padrão (padroes_faltantes, padroes_frequentes, padroes_atrasados, digitos_iniciais_top3)
            mes_override: Mês fixo a usar (1-12) ou None para automático

        Returns:
            Dict com palpites gerados
        """
        palpites = []
        padroes_usados = set()  # Controle de padrões já utilizados

        # Obter lista de padrões disponíveis
        if tipo == 'padroes_faltantes':
            dados = PalpiteService._obter_dados_padroes_dezenas()
            if not dados or not dados.get('padroes_faltantes'):
                return {'sucesso': False, 'erro': 'Não foi possível obter padrões faltantes', 'palpites': []}
            padroes_disponiveis = [p for p in dados['padroes_faltantes'] if p.get('jogos_possiveis', 0) > 0]
            info_extra = 'nunca saiu!'

        elif tipo == 'padroes_frequentes':
            dados = PalpiteService._obter_dados_padroes_dezenas()
            if not dados or not dados.get('top_10_frequentes'):
                return {'sucesso': False, 'erro': 'Não foi possível obter padrões frequentes', 'palpites': []}
            padroes_disponiveis = dados['top_10_frequentes']
            info_extra = 'frequente'

        elif tipo == 'padroes_atrasados':
            dados = PalpiteService._obter_dados_padroes_dezenas()
            if not dados or not dados.get('top_10_atrasados'):
                return {'sucesso': False, 'erro': 'Não foi possível obter padrões atrasados', 'palpites': []}
            padroes_disponiveis = dados['top_10_atrasados']
            info_extra = 'atrasado'

        elif tipo == 'digitos_iniciais_top3':
            padroes_disponiveis = PalpiteService._obter_top3_digitos_iniciais()
            if not padroes_disponiveis:
                return {'sucesso': False, 'erro': 'Não foi possível obter top 3 dígitos iniciais', 'palpites': []}
            info_extra = 'top 3'

        else:
            return {'sucesso': False, 'erro': f'Tipo {tipo} não suportado para cobertura', 'palpites': []}

        # Embaralhar para variar a ordem
        padroes_para_usar = list(padroes_disponiveis)
        random.shuffle(padroes_para_usar)

        # Gerar uma aposta para cada padrão (sem repetição)
        for padrao_info in padroes_para_usar:
            if len(palpites) >= quantidade:
                break

            padrao_str = padrao_info.get('padrao', '')
            if not padrao_str or padrao_str in padroes_usados:
                continue

            # Marcar padrão como usado
            padroes_usados.add(padrao_str)

            # Gerar números seguindo o padrão
            numeros = PalpiteService._gerar_numeros_por_padrao(padrao_str)
            numeros = PalpiteService._aplicar_validacoes(numeros, manter_padrao=True)

            # Calcular o padrão REAL
            padrao_real = PalpiteService._calcular_padrao_real(numeros)

            # Mês
            mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

            # Construir descrição do método
            if tipo == 'padroes_faltantes':
                metodo_desc = f'Padrão Faltante: {padrao_real} ({info_extra})'
                jogos_possiveis = padrao_info.get('jogos_possiveis', 0)
            elif tipo == 'padroes_frequentes':
                freq = padrao_info.get('frequencia', 0)
                metodo_desc = f'Padrão Frequente: {padrao_real} ({freq}x)'
                jogos_possiveis = None
            elif tipo == 'padroes_atrasados':
                atraso = padrao_info.get('atraso', 0)
                metodo_desc = f'Padrão Atrasado: {padrao_real} ({atraso} conc. sem sair)'
                jogos_possiveis = None
            else:
                freq = padrao_info.get('frequencia', 0)
                metodo_desc = f'Padrão Top 3: {padrao_real} ({freq}x)'
                jogos_possiveis = None

            palpite = {
                'tipo': tipo,
                'numeros': numeros,
                'mes_sorte': mes_sorte,
                'metodo': metodo_desc,
                'padrao_utilizado': padrao_real,
                'padrao_solicitado': padrao_str,
                'numero_jogo': len(palpites) + 1,
                'validado': True
            }

            if jogos_possiveis is not None:
                palpite['jogos_possiveis'] = jogos_possiveis
            if tipo == 'padroes_frequentes' or tipo == 'digitos_iniciais_top3':
                palpite['frequencia_historica'] = padrao_info.get('frequencia', 0)
            if tipo == 'padroes_atrasados':
                palpite['atraso'] = padrao_info.get('atraso', 0)

            palpites.append(palpite)

        # Se quantidade pedida for maior que padrões disponíveis, gerar mais com repetição
        if len(palpites) < quantidade:
            padroes_usados.clear()  # Permitir reutilização
            tentativas = 0
            max_tentativas = (quantidade - len(palpites)) * 5

            while len(palpites) < quantidade and tentativas < max_tentativas:
                tentativas += 1

                # Escolher padrão aleatório
                padrao_info = random.choice(padroes_disponiveis)
                padrao_str = padrao_info.get('padrao', '')

                if not padrao_str:
                    continue

                # Gerar números
                numeros = PalpiteService._gerar_numeros_por_padrao(padrao_str)
                numeros = PalpiteService._aplicar_validacoes(numeros, manter_padrao=True)

                # Verificar se jogo já existe
                chave = tuple(numeros)
                jogos_existentes = {tuple(p['numeros']) for p in palpites}
                if chave in jogos_existentes:
                    continue

                padrao_real = PalpiteService._calcular_padrao_real(numeros)

                mes_sorte = PalpiteService._obter_mes_sorte(mes_override)

                palpite = {
                    'tipo': tipo,
                    'numeros': numeros,
                    'mes_sorte': mes_sorte,
                    'metodo': f'Padrão: {padrao_real}',
                    'padrao_utilizado': padrao_real,
                    'numero_jogo': len(palpites) + 1,
                    'validado': True,
                    'repeticao': True  # Indicar que é repetição de padrão
                }

                palpites.append(palpite)

        return {
            'sucesso': True,
            'quantidade': len(palpites),
            'tipo': tipo,
            'metodo_validado': True,
            'cobertura_completa': len(padroes_usados) == min(quantidade, len(padroes_disponiveis)),
            'total_padroes_disponiveis': len(padroes_disponiveis),
            'padroes_utilizados': len(padroes_usados),
            'gerado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'palpites': palpites
        }

    @staticmethod
    def gerar_surpresinha(mes_override=None):
        """
        Gera um palpite totalmente aleatório (como a surpresinha da lotérica)
        """
        return PalpiteService.gerar_palpite_simples(mes_override)

    # =========================================================================
    # INFORMAÇÕES SOBRE MÉTODOS
    # =========================================================================

    @staticmethod
    def obter_info_metodos():
        """
        Retorna informações detalhadas sobre cada método de geração
        """
        return {
            'inteligente': {
                'nome': 'Inteligente (50% freq + 50% atraso)',
                'descricao': 'Algoritmo balanceado que considera frequência histórica e atraso dos números',
                'icone': '🧠',
                'grupo': 'estatisticos'
            },
            'frequencia': {
                'nome': 'Por Frequência',
                'descricao': 'Prioriza os números que mais saíram no histórico',
                'icone': '📊',
                'grupo': 'estatisticos'
            },
            'atraso': {
                'nome': 'Por Atraso',
                'descricao': 'Prioriza os números que estão há mais tempo sem sair',
                'icone': '⏰',
                'grupo': 'estatisticos'
            },
            'misto': {
                'nome': 'Misto (4 freq + 3 atraso)',
                'descricao': 'Combina 4 números frequentes com 3 atrasados',
                'icone': '🔀',
                'grupo': 'estatisticos'
            },
            'posicao': {
                'nome': 'Por Posição',
                'descricao': 'Usa os números mais frequentes em cada posição (1ª a 7ª bola)',
                'icone': '📍',
                'grupo': 'estatisticos'
            },
            'simples': {
                'nome': 'Aleatório (Surpresinha)',
                'descricao': 'Gera números completamente aleatórios',
                'icone': '🎲',
                'grupo': 'estatisticos'
            },
            'padroes_faltantes': {
                'nome': 'Padrões Faltantes (nunca saíram!)',
                'descricao': 'Usa padrões de dezenas que NUNCA apareceram nos sorteios - potencial de ineditismo',
                'icone': '🎯',
                'grupo': 'padroes'
            },
            'padroes_frequentes': {
                'nome': 'Top 10 Padrões Frequentes',
                'descricao': 'Usa os 10 padrões de dezenas que mais aparecem nos sorteios',
                'icone': '🏆',
                'grupo': 'padroes'
            },
            'padroes_atrasados': {
                'nome': 'Top 10 Padrões Atrasados',
                'descricao': 'Usa os 10 padrões de dezenas que estão há mais tempo sem sair',
                'icone': '⌛',
                'grupo': 'padroes'
            },
            'digitos_iniciais_top3': {
                'nome': 'Top 3 Dígitos Iniciais',
                'descricao': 'Usa os 3 padrões de dígitos iniciais campeões (mais frequentes)',
                'icone': '🥇',
                'grupo': 'padroes'
            }
        }

    @staticmethod
    def listar_metodos_disponiveis():
        """
        Lista todos os métodos disponíveis para geração
        """
        return list(PalpiteService.obter_info_metodos().keys())

from itertools import combinations
from typing import List, Dict, Any, Set
from models.configuracao import Configuracao

class FechamentoFaltantesService:
    @staticmethod
    def gerar_fechamento(apostas: List[List[int]]) -> Dict[str, Any]:
        """
        Gera combinações de fechamento baseadas na união das dezenas das apostas fornecidas.
        Aplica os 'Filtros de Ouro': Paridade, Sequência, Soma e Primos.
        """
        if not apostas:
            return {'sucesso': False, 'mensagem': 'Nenhuma aposta fornecida.'}

        # 1. Extrair universo de dezenas (União)
        universo_dezenas: Set[int] = set()
        for aposta in apostas:
            universo_dezenas.update(aposta)
        
        lista_dezenas = sorted(list(universo_dezenas))
        total_dezenas = len(lista_dezenas)

        # Se houver menos de 7 dezenas, não dá para formar jogo
        if total_dezenas < 7:
             return {
                'sucesso': False, 
                'mensagem': f'Universo de dezenas insuficiente ({total_dezenas}). Necessário pelo menos 7.'
            }

        # Limite de segurança
        if total_dezenas > 25:
             return {
                'sucesso': False, 
                'mensagem': f'Muitas dezenas únicas ({total_dezenas}). O limite para simulação web é 25 para garantir performance.'
            }

        todas_combinacoes = combinations(lista_dezenas, 7)
        
        jogos_validos = []
        total_gerados = 0
        
        # Primos do Dia de Sorte (até 31)
        PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31}

        # 3. Filtragem "Golden Filters"
        # Sequências: Max 4
        # Paridade: 3P/4I ou 4P/3I
        # Soma: 100 a 150
        # Primos: 2 a 5
        
        for comb in todas_combinacoes:
            total_gerados += 1
            numeros = sorted(list(comb))
            
            # Filtro 1: Paridade (Equilíbrio) - Somente 3P/4I ou 4P/3I
            pares = sum(1 for n in numeros if n % 2 == 0)
            if pares != 3 and pares != 4:
                continue
                
            # Filtro 2: Soma (100 a 150)
            soma = sum(numeros)
            if not (100 <= soma <= 150):
                continue
                
            # Filtro 3: Primos (2 a 5)
            qtd_primos = sum(1 for n in numeros if n in PRIMOS)
            if not (2 <= qtd_primos <= 5):
                continue

            # Filtro 4: Sequencias (Max 4)
            max_seq = 1
            atual_seq = 1
            for i in range(1, len(numeros)):
                if numeros[i] == numeros[i-1] + 1:
                    atual_seq += 1
                    max_seq = max(max_seq, atual_seq)
                else:
                    atual_seq = 1
            
            if max_seq > 4:
                continue

            jogos_validos.append(numeros)

        # 4. Análise Financeira
        try:
            config_valor = Configuracao.query.filter_by(chave='valor_aposta_minima').first()
            preco_aposta = float(config_valor.valor) if config_valor else 2.50
        except:
            preco_aposta = 2.50

        qtd_jogos = len(jogos_validos)
        custo_total = qtd_jogos * preco_aposta
        jogos_eliminados = total_gerados - qtd_jogos

        # 5. Insights e Estatísticas
        insights = []
        insights.append(f"Universo de {total_dezenas} dezenas. Total de combinações possíveis: {total_gerados.toLocaleString('pt-BR') if hasattr(total_gerados, 'toLocaleString') else total_gerados}")
        insights.append(f"Filtros aplicados eliminaram {jogos_eliminados} jogos 'improváveis'.")
        
        if qtd_jogos > 0:
            economia = (jogos_eliminados * preco_aposta)
            insights.append(f"Economia estimada com filtros: R$ {economia:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

        if qtd_jogos > 300:
            insights.append("Alto volume de jogos gerados. Considere fixar algumas dezenas.")

        return {
            'sucesso': True,
            'universo_dezenas': lista_dezenas,
            'total_dezenas_unicas': total_dezenas,
            'jogos_gerados': jogos_validos,
            'quantidade_jogos': qtd_jogos,
            'total_bruto': total_gerados,
            'jogos_eliminados': jogos_eliminados,
            'custo_unitario': preco_aposta,
            'custo_total': custo_total,
            'insights': insights
        }

    @staticmethod
    def _validar_paridade(comb: tuple) -> bool:
        """
        Retorna True se a paridade for aceitável (evita 7 pares ou 7 ímpares).
        Aceitável: 6p/1i, 5p/2i, 4p/3i, 3p/4i, 2p/5i, 1p/6i
        """
        pares = sum(1 for n in comb if n % 2 == 0)
        # Ímpares = 7 - pares
        # Bloquear se pares == 7 (0 ímpares) ou pares == 0 (7 ímpares)
        return 0 < pares < 7

    @staticmethod
    def _validar_sequencia(comb: tuple) -> bool:
        """
        Retorna True se a maior sequência consecutiva for <= 4.
        """
        max_seq = 1
        atual_seq = 1
        sorted_comb = sorted(comb) # Já vem sortido do combinations, mas garantia
        
        for i in range(1, len(sorted_comb)):
            if sorted_comb[i] == sorted_comb[i-1] + 1:
                atual_seq += 1
                max_seq = max(max_seq, atual_seq)
            else:
                atual_seq = 1
        
        return max_seq <= 4

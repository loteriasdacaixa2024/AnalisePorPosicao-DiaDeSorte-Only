from services.configuracao_service import ConfiguracaoService


class ValoresProbabilidadesService:
    """
    Service para cálculo de valores de apostas e probabilidades
    Baseado nas regras oficiais da Caixa Econômica Federal
    """

    @staticmethod
    def calcular_valores_apostas(valor_base=None):
        """
        Calcula todos os valores de apostas baseado no valor da aposta mínima (7 números)

        Args:
            valor_base: Valor da aposta de 7 números (busca da configuração se None)

        Returns:
            dict com valores para cada quantidade de números
        """

        # Se valor_base não fornecido, buscar da configuração
        if valor_base is None:
            valor_base = ConfiguracaoService.obter_valor_aposta()

        valores = {
            7: valor_base,
            8: valor_base * 8,
            9: valor_base * 36,
            10: valor_base * 120,
            11: valor_base * 330,
            12: valor_base * 792,
            13: valor_base * 1716,
            14: valor_base * 3432,
            15: valor_base * 6435
        }

        return {
            'valor_base': valor_base,
            'valores': valores,
            'combinacoes': {
                7: 1,
                8: 8,
                9: 36,
                10: 120,
                11: 330,
                12: 792,
                13: 1716,
                14: 3432,
                15: 6435
            }
        }

    @staticmethod
    def obter_probabilidades():
        """
        Retorna as probabilidades oficiais para cada faixa de premiação
        Baseado na tabela oficial da Caixa

        Returns:
            dict com probabilidades para cada quantidade de números
        """

        return {
            7: {
                '7_acertos': 2629575,
                '6_acertos': 15652,
                '5_acertos': 453,
                '4_acertos': 37,
                'mes_sorte': 12
            },
            8: {
                '7_acertos': 328696,
                '6_acertos': 4083,
                '5_acertos': 185,
                '4_acertos': 21,
                'mes_sorte': 12
            },
            9: {
                '7_acertos': 73043,
                '6_acertos': 1422,
                '5_acertos': 90,
                '4_acertos': 13,
                'mes_sorte': 12
            },
            10: {
                '7_acertos': 21913,
                '6_acertos': 596,
                '5_acertos': 49,
                '4_acertos': 9,
                'mes_sorte': 12
            },
            11: {
                '7_acertos': 7968,
                '6_acertos': 284,
                '5_acertos': 29,
                '4_acertos': 6,
                'mes_sorte': 12
            },
            12: {
                '7_acertos': 3320,
                '6_acertos': 149,
                '5_acertos': 19,
                '4_acertos': 5,
                'mes_sorte': 12
            },
            13: {
                '7_acertos': 1532,
                '6_acertos': 85,
                '5_acertos': 13,
                '4_acertos': 4,
                'mes_sorte': 12
            },
            14: {
                '7_acertos': 766,
                '6_acertos': 51,
                '5_acertos': 9,
                '4_acertos': 3,
                'mes_sorte': 12
            },
            15: {
                '7_acertos': 408,
                '6_acertos': 32,
                '5_acertos': 7,
                '4_acertos': 3,
                'mes_sorte': 12
            }
        }

    @staticmethod
    def obter_premios_fixos():
        """
        Retorna os valores dos prêmios fixos

        Returns:
            dict com valores dos prêmios fixos
        """

        return {
            'mes_sorte': 2.50,
            '4_acertos': 5.00,
            '5_acertos': 25.00
        }

    @staticmethod
    def calcular_quantidade_premios(quantidade_numeros):
        """
        Calcula quantos prêmios de cada faixa são ganhos ao acertar
        Baseado na tabela oficial da Caixa

        Args:
            quantidade_numeros: Quantidade de números jogados (7-15)

        Returns:
            dict com quantidade de prêmios por faixa ao acertar
        """

        tabela_premios = {
            7: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 0, '5_acertos': 0, '4_acertos': 0},
                'acertando_6': {'6_acertos': 1, '5_acertos': 0, '4_acertos': 0},
                'acertando_5': {'5_acertos': 1, '4_acertos': 0},
                'acertando_4': {'4_acertos': 1},
                'mes_sorte': 1
            },
            8: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 7, '5_acertos': 0, '4_acertos': 0},
                'acertando_6': {'6_acertos': 2, '5_acertos': 6, '4_acertos': 0},
                'acertando_5': {'5_acertos': 3, '4_acertos': 5},
                'acertando_4': {'4_acertos': 4},
                'mes_sorte': 8
            },
            9: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 14, '5_acertos': 21, '4_acertos': 0},
                'acertando_6': {'6_acertos': 3, '5_acertos': 18, '4_acertos': 15},
                'acertando_5': {'5_acertos': 6, '4_acertos': 20},
                'acertando_4': {'4_acertos': 10},
                'mes_sorte': 36
            },
            10: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 21, '5_acertos': 63, '4_acertos': 35},
                'acertando_6': {'6_acertos': 4, '5_acertos': 36, '4_acertos': 60},
                'acertando_5': {'5_acertos': 10, '4_acertos': 50},
                'acertando_4': {'4_acertos': 20},
                'mes_sorte': 120
            },
            11: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 28, '5_acertos': 126, '4_acertos': 140},
                'acertando_6': {'6_acertos': 5, '5_acertos': 60, '4_acertos': 150},
                'acertando_5': {'5_acertos': 15, '4_acertos': 100},
                'acertando_4': {'4_acertos': 35},
                'mes_sorte': 330
            },
            12: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 35, '5_acertos': 210, '4_acertos': 350},
                'acertando_6': {'6_acertos': 6, '5_acertos': 90, '4_acertos': 300},
                'acertando_5': {'5_acertos': 21, '4_acertos': 175},
                'acertando_4': {'4_acertos': 56},
                'mes_sorte': 792
            },
            13: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 42, '5_acertos': 315, '4_acertos': 700},
                'acertando_6': {'6_acertos': 7, '5_acertos': 126, '4_acertos': 525},
                'acertando_5': {'5_acertos': 28, '4_acertos': 280},
                'acertando_4': {'4_acertos': 84},
                'mes_sorte': 1716
            },
            14: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 49, '5_acertos': 441, '4_acertos': 1225},
                'acertando_6': {'6_acertos': 8, '5_acertos': 168, '4_acertos': 840},
                'acertando_5': {'5_acertos': 36, '4_acertos': 420},
                'acertando_4': {'4_acertos': 120},
                'mes_sorte': 3432
            },
            15: {
                'acertando_7': {'7_acertos': 1, '6_acertos': 56, '5_acertos': 588, '4_acertos': 1960},
                'acertando_6': {'6_acertos': 9, '5_acertos': 216, '4_acertos': 1260},
                'acertando_5': {'5_acertos': 45, '4_acertos': 600},
                'acertando_4': {'4_acertos': 165},
                'mes_sorte': 6435
            }
        }

        return tabela_premios.get(quantidade_numeros, {})

    @staticmethod
    def formatar_probabilidade(probabilidade):
        """
        Formata probabilidade como "1 em X"

        Args:
            probabilidade: Número representando a probabilidade

        Returns:
            str formatada
        """
        return f"1 em {probabilidade:,}".replace(',', '.')

    @staticmethod
    def calcular_valor_estimado_premio(quantidade_acertos, quantidade_numeros, valor_arrecadado=0):
        """
        Calcula valor estimado de prêmio baseado na arrecadação

        Args:
            quantidade_acertos: 4, 5, 6 ou 7
            quantidade_numeros: 7-15
            valor_arrecadado: Valor total arrecadado no concurso

        Returns:
            dict com valores estimados
        """

        premios_fixos = ValoresProbabilidadesService.obter_premios_fixos()

        if quantidade_acertos == 4:
            return {'valor_fixo': premios_fixos['4_acertos'], 'tipo': 'fixo'}
        elif quantidade_acertos == 5:
            return {'valor_fixo': premios_fixos['5_acertos'], 'tipo': 'fixo'}

        if valor_arrecadado == 0:
            return {'tipo': 'variavel', 'msg': 'Depende da arrecadação'}

        percentual_premios = 0.4379
        valor_premios = valor_arrecadado * percentual_premios

        if quantidade_acertos == 7:
            valor_estimado = valor_premios * 0.70
        elif quantidade_acertos == 6:
            valor_estimado = valor_premios * 0.30
        else:
            valor_estimado = 0

        return {
            'tipo': 'variavel',
            'valor_estimado': valor_estimado,
            'msg': f'Estimativa baseada em arrecadação de R$ {valor_arrecadado:,.2f}'
        }

    @staticmethod
    def obter_tabela_completa(valor_base=None):
        """
        Retorna tabela completa com valores, probabilidades e prêmios

        Args:
            valor_base: Valor da aposta mínima (busca da configuração se None)

        Returns:
            dict completo com todas as informações
        """

        # Se valor_base não fornecido, buscar da configuração
        if valor_base is None:
            valor_base = ConfiguracaoService.obter_valor_aposta()

        valores_apostas = ValoresProbabilidadesService.calcular_valores_apostas(valor_base)
        probabilidades = ValoresProbabilidadesService.obter_probabilidades()
        premios_fixos = ValoresProbabilidadesService.obter_premios_fixos()

        tabela = []

        for qtd_numeros in range(7, 16):
            item = {
                'quantidade_numeros': qtd_numeros,
                'valor_aposta': valores_apostas['valores'][qtd_numeros],
                'quantidade_jogos': valores_apostas['combinacoes'][qtd_numeros],
                'probabilidades': probabilidades[qtd_numeros],
                'quantidade_premios': ValoresProbabilidadesService.calcular_quantidade_premios(qtd_numeros),
                'premios_fixos': premios_fixos
            }
            tabela.append(item)

        return {
            'valor_base': valor_base,
            'tabela': tabela,
            'premios_fixos': premios_fixos,
            'percentuais': {
                'premio_bruto': 43.79,
                'faixa_7_acertos': 70.0,
                'faixa_6_acertos': 30.0
            }
        }

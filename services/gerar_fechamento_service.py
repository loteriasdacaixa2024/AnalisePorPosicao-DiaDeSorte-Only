# -*- coding: utf-8 -*-
"""
Serviço para gerar fechamentos (jogos) do Dia de Sorte
🔥🔥🔥 VERSÃO ABSOLUTAMENTE RIGOROSA: GARANTIA 100% - NUNCA DESISTE!
"""

import random
from itertools import combinations
from collections import Counter


class GerarFechamentoService:
    """Serviço para gerar jogos com regras específicas"""

    TOTAL_DEZENAS = 31  # Dia de Sorte: 01 a 31
    DEZENAS_POR_JOGO = 7
    MESES = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    @staticmethod
    def obter_ultimo_sorteio():
        """Obtém os números do último sorteio"""
        from models.sorteio import Sorteio

        try:
            ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
            if not ultimo:
                return None

            return {
                'concurso': ultimo.concurso,
                'numeros': [
                    ultimo.posicao_1, ultimo.posicao_2, ultimo.posicao_3,
                    ultimo.posicao_4, ultimo.posicao_5, ultimo.posicao_6,
                    ultimo.posicao_7
                ],
                'mes': ultimo.get_nome_mes()
            }
        except Exception as e:
            print(f"Erro ao obter último sorteio: {e}")
            return None

    @staticmethod
    def calcular_soma_digitos_unicos(numeros):
        """Calcula a soma dos números e conta quantos dígitos únicos tem"""
        soma = sum(numeros)
        digitos_str = str(soma)
        digitos_unicos = len(set(digitos_str))
        return soma, digitos_unicos

    @staticmethod
    def verificar_finais_iguais(numeros):
        """Verifica quantos conjuntos de finais iguais existem"""
        finais = {}
        for num in numeros:
            final = num % 10
            if final not in finais:
                finais[final] = []
            finais[final].append(num)

        conjuntos = [nums for nums in finais.values() if len(nums) >= 2]
        return len(conjuntos), conjuntos

    @staticmethod
    def verificar_sequencias(numeros):
        """Verifica quantos conjuntos de sequências existem"""
        numeros_ordenados = sorted(numeros)
        sequencias = []
        seq_atual = [numeros_ordenados[0]]

        for i in range(1, len(numeros_ordenados)):
            if numeros_ordenados[i] == seq_atual[-1] + 1:
                seq_atual.append(numeros_ordenados[i])
            else:
                if len(seq_atual) >= 2:
                    sequencias.append(seq_atual)
                seq_atual = [numeros_ordenados[i]]

        if len(seq_atual) >= 2:
            sequencias.append(seq_atual)

        return len(sequencias), sequencias

    @staticmethod
    def contar_repeticoes_sorteio_anterior(numeros, numeros_sorteio_anterior):
        """Conta quantos números se repetem do sorteio anterior"""
        if not numeros_sorteio_anterior:
            return 0, []

        repetidos = [n for n in numeros if n in numeros_sorteio_anterior]
        return len(repetidos), repetidos

    @staticmethod
    def tem_duplicata_ou_tripla(numeros):
        """
        🔥 VERIFICAÇÃO RIGOROSA: Retorna True se tem 11 ou 22
        """
        for num in numeros:
            if num == 11 or num == 22:
                return True
        return False

    @staticmethod
    def validar_analises_configuradas(numeros, analises_ativas):
        """
        🔥🔥🔥 VALIDAÇÃO ABSOLUTAMENTE RIGOROSA
        NUNCA retorna True se análise ativa não for atendida
        """
        if not analises_ativas:
            return True, "Nenhuma análise ativa"

        # ===== DUPLICATAS/TRIPLAS - SUPER RIGOROSO =====
        if analises_ativas.get('duplicatas_triplas'):
            # 🔥 VERIFICAÇÃO EXPLÍCITA
            tem_11 = 11 in numeros
            tem_22 = 22 in numeros

            if not tem_11 and not tem_22:
                # 🚨 REJEITA IMEDIATAMENTE - SEM EXCEÇÕES!
                return False, f"❌ BLOQUEADO: duplicatas_triplas ativo mas {numeros} NÃO tem 11 nem 22"

        # Outras análises...
        if analises_ativas.get('pares_impares'):
            pares = sum(1 for n in numeros if n % 2 == 0)
            impares = 7 - pares
            if pares < 2 or impares < 2:
                return False, f"❌ BLOQUEADO: pares_impares - {pares}P/{impares}I"

        if analises_ativas.get('consecutivos'):
            qtd_seq, _ = GerarFechamentoService.verificar_sequencias(numeros)
            if qtd_seq < 1:
                return False, f"❌ BLOQUEADO: consecutivos - sem sequências"

        if analises_ativas.get('primos_compostos'):
            primos = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
            qtd_primos = sum(1 for n in numeros if n in primos)
            if qtd_primos < 1:
                return False, f"❌ BLOQUEADO: primos_compostos - sem primos"

        if analises_ativas.get('extremos'):
            extremos = sum(1 for n in numeros if n <= 5 or n >= 27)
            if extremos < 1:
                return False, f"❌ BLOQUEADO: extremos - sem extremos"

        if analises_ativas.get('numeros_juntos'):
            qtd_finais, _ = GerarFechamentoService.verificar_finais_iguais(numeros)
            if qtd_finais < 1:
                return False, f"❌ BLOQUEADO: numeros_juntos - sem finais iguais"

        return True, "✅ Passou"

    @staticmethod
    def validar_jogo(numeros, config, numeros_sorteio_anterior=None):
        """Valida se um jogo atende às regras configuradas"""
        detalhes = {}

        qtd_finais, conjuntos_finais = GerarFechamentoService.verificar_finais_iguais(numeros)
        detalhes['finais_iguais'] = {
            'quantidade': qtd_finais,
            'conjuntos': conjuntos_finais,
            'minimo': config.get('min_finais_iguais', 2)
        }

        qtd_seq, conjuntos_seq = GerarFechamentoService.verificar_sequencias(numeros)
        detalhes['sequencias'] = {
            'quantidade': qtd_seq,
            'conjuntos': conjuntos_seq,
            'minimo': config.get('min_sequencias', 2)
        }

        qtd_rep, nums_rep = GerarFechamentoService.contar_repeticoes_sorteio_anterior(
            numeros, numeros_sorteio_anterior
        )
        detalhes['repeticoes_anterior'] = {
            'quantidade': qtd_rep,
            'numeros': nums_rep,
            'minimo': config.get('min_repeticoes_anterior', 2)
        }

        soma, digitos_unicos = GerarFechamentoService.calcular_soma_digitos_unicos(numeros)
        detalhes['soma'] = {
            'valor': soma,
            'digitos_unicos': digitos_unicos,
            'minimo': config.get('min_digitos_unicos', 6),
            'maximo': config.get('max_digitos_unicos', 8)
        }

        valido = (
            qtd_finais >= config.get('min_finais_iguais', 2) and
            qtd_seq >= config.get('min_sequencias', 2) and
            qtd_rep >= config.get('min_repeticoes_anterior', 2) and
            config.get('min_digitos_unicos', 6) <= digitos_unicos <= config.get('max_digitos_unicos', 8)
        )

        return valido, detalhes

    @staticmethod
    def gerar_jogo_aleatorio(numeros_sorteio_anterior, config, analises_ativas=None, max_tentativas=100000):
        """
        🔥🔥🔥 ABSOLUTAMENTE RIGOROSO: NUNCA retorna jogo inválido
        AUMENTADO: max_tentativas = 100.000 (era 50.000)
        """
        tentativas_total = 0
        tentativas_falhas_analises = 0
        tentativas_falhas_regras = 0

        # 🔥 LOOP INFINITO ATÉ ENCONTRAR UM JOGO VÁLIDO
        while tentativas_total < max_tentativas:
            tentativas_total += 1

            # Gera números aleatórios
            numeros = sorted(random.sample(range(1, 32), 7))

            # 🔥🔥 VALIDAÇÃO 1: ANÁLISES CONFIGURADAS (bloqueio rigoroso)
            if analises_ativas:
                passou_analises, motivo = GerarFechamentoService.validar_analises_configuradas(
                    numeros, analises_ativas
                )
                if not passou_analises:
                    tentativas_falhas_analises += 1
                    if tentativas_falhas_analises % 5000 == 0:
                        print(f"   ⚠️  {tentativas_falhas_analises} tentativas bloqueadas por análises")
                    continue  # 🚨 CONTINUA TENTANDO

            # 🔥🔥 VALIDAÇÃO 2: REGRAS ANTIGAS
            valido, detalhes = GerarFechamentoService.validar_jogo(
                numeros, config, numeros_sorteio_anterior
            )

            if not valido:
                tentativas_falhas_regras += 1
                continue  # 🚨 CONTINUA TENTANDO

            # ✅ ENCONTROU UM JOGO VÁLIDO!
            mes = random.choice(GerarFechamentoService.MESES)

            if tentativas_total > 1000:
                print(f"      ✅ Jogo válido após {tentativas_total} tentativas ({tentativas_falhas_analises} bloqueios)")

            return numeros, mes, detalhes

        # ❌ FALHA CRÍTICA (só chega aqui após 100.000 tentativas)
        print(f"❌ FALHA APÓS {max_tentativas} TENTATIVAS!")
        print(f"   Bloqueios por análises: {tentativas_falhas_analises}")
        print(f"   Bloqueios por regras: {tentativas_falhas_regras}")
        raise Exception(f"Impossível gerar jogo válido após {max_tentativas} tentativas. Relaxe as regras ou desative análises.")

    @staticmethod
    def calcular_valor_aposta(quantidade_dezenas):
        """Calcula o valor da aposta"""
        from services.configuracao_service import ConfiguracaoService
        from services.valores_probabilidades_service import ValoresProbabilidadesService

        valor_base = ConfiguracaoService.obter_valor_aposta()
        dados_valores = ValoresProbabilidadesService.calcular_valores_apostas(valor_base)

        return dados_valores['valores'].get(quantidade_dezenas, valor_base)

    @staticmethod
    def gerar_multiplos_jogos(quantidade, config=None, dezenas_por_jogo=7):
        """
        🔥🔥🔥 ABSOLUTAMENTE RIGOROSO: NUNCA retorna jogos inválidos
        GARANTIA: Cada jogo passou em TODAS as validações
        """
        from services.configuracao_service import ConfiguracaoService

        try:
            analises_ativas = ConfiguracaoService.obter_analises_ativas()
            qtd_ativas = sum(1 for v in analises_ativas.values() if v)

            print(f"🔥🔥🔥 MODO ABSOLUTAMENTE RIGOROSO")
            print(f"✅ {qtd_ativas} análises ativas de {len(analises_ativas)}")

            if qtd_ativas > 0:
                print(f"   Ativas: {[k for k, v in analises_ativas.items() if v]}")
                print(f"   🚨 GARANTIA 100%: NENHUM jogo inválido será gerado!")
        except Exception as e:
            print(f"⚠️  Erro ao carregar análises: {e}")
            analises_ativas = {}

        config_padrao = {
            'min_finais_iguais': 2,
            'min_sequencias': 2,
            'min_repeticoes_anterior': 2,
            'min_digitos_unicos': 7,
            'max_digitos_unicos': 7
        }

        if config:
            config_padrao.update(config)

        ultimo_sorteio = GerarFechamentoService.obter_ultimo_sorteio()
        if not ultimo_sorteio:
            return {
                'sucesso': False,
                'mensagem': 'Não foi possível obter o último sorteio do banco de dados'
            }

        numeros_sorteio_anterior = ultimo_sorteio['numeros']

        jogos = []
        jogos_duplicados = set()

        print(f"🎯 Gerando {quantidade} jogos (max 100.000 tentativas por jogo)")
        print()

        for i in range(quantidade):
            # 🔥 GERA JOGO (nunca retorna inválido - lança exceção se impossível)
            try:
                numeros, mes, detalhes = GerarFechamentoService.gerar_jogo_aleatorio(
                    numeros_sorteio_anterior, config_padrao, analises_ativas
                )
            except Exception as e:
                print(f"❌ Erro ao gerar jogo {i+1}: {e}")
                return {
                    'sucesso': False,
                    'mensagem': str(e)
                }

            # 🔥🔥 VERIFICAÇÃO TRIPLA (paranoia máxima!)
            if analises_ativas:
                passou, motivo = GerarFechamentoService.validar_analises_configuradas(numeros, analises_ativas)
                if not passou:
                    print(f"🚨 BUG CRÍTICO DETECTADO!")
                    print(f"   Jogo {numeros} passou mas validação tripla REJEITOU!")
                    print(f"   Motivo: {motivo}")
                    # 🚨 LANÇA EXCEÇÃO AO INVÉS DE ADICIONAR JOGO INVÁLIDO
                    raise Exception(f"BUG: Jogo inválido passou pelas validações! {motivo}")

            # Verifica duplicados
            chave = tuple(numeros)
            if chave not in jogos_duplicados:
                jogos_duplicados.add(chave)
                jogos.append({
                    'numero': len(jogos) + 1,
                    'numeros': numeros,
                    'mes': mes,
                    'detalhes': detalhes
                })

                if (i + 1) % 5 == 0:
                    print(f"   ✅ {len(jogos)}/{quantidade} jogos gerados")

        valor_unitario = GerarFechamentoService.calcular_valor_aposta(dezenas_por_jogo)
        valor_total = valor_unitario * len(jogos)

        print()
        print(f"✅✅✅ {len(jogos)} jogos gerados - TODOS 100% VALIDADOS!")
        print()

        return {
            'sucesso': True,
            'jogos': jogos,
            'total': len(jogos),
            'configuracao': config_padrao,
            'analises_ativas': analises_ativas,
            'ultimo_sorteio': ultimo_sorteio,
            'dezenas_por_jogo': dezenas_por_jogo,
            'valor_unitario': valor_unitario,
            'valor_total': valor_total
        }

    @staticmethod
    def analisar_jogo(numeros, mes=None):
        """Analisa um jogo e retorna informações visuais"""
        ultimo_sorteio = GerarFechamentoService.obter_ultimo_sorteio()
        numeros_anterior = ultimo_sorteio['numeros'] if ultimo_sorteio else []

        _, sequencias = GerarFechamentoService.verificar_sequencias(numeros)
        _, finais_iguais = GerarFechamentoService.verificar_finais_iguais(numeros)
        _, repeticoes = GerarFechamentoService.contar_repeticoes_sorteio_anterior(
            numeros, numeros_anterior
        )
        soma, digitos_unicos = GerarFechamentoService.calcular_soma_digitos_unicos(numeros)

        cores = {}
        for num in numeros:
            classes = []
            for seq in sequencias:
                if num in seq:
                    if len(seq) == 2:
                        classes.append('seq-2')
                    elif len(seq) == 3:
                        classes.append('seq-3')
                    elif len(seq) >= 4:
                        classes.append('seq-4')
                    break
            if num in repeticoes:
                classes.append('repetition')
            cores[num] = ' '.join(classes) if classes else ''

        return {
            'numeros': numeros,
            'mes': mes,
            'cores': cores,
            'sequencias': sequencias,
            'finais_iguais': finais_iguais,
            'repeticoes': repeticoes,
            'soma': soma,
            'digitos_unicos': digitos_unicos,
            'ultimo_sorteio': ultimo_sorteio
        }

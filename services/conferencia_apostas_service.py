"""
Service para conferência de apostas pós-sorteio
Compara jogos apostados com resultados e calcula ganhos/perdas
"""

import json
import os
import re
from datetime import datetime
from collections import Counter
from models import Sorteio, db


class ConferenciaApostasService:
    """Service para conferir apostas e calcular resultados"""

    COLUNAS_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'colunas_adicionais.json')

    MESES_DICT = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    MESES_ABREV = {
        'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
        'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12,
        'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
        'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
        'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
    }

    MESES_ABREV_SHORT = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    @staticmethod
    def _garantir_arquivo_colunas():
        """Garante que o arquivo de colunas existe com colunas padrão"""
        diretorio = os.path.dirname(ConferenciaApostasService.COLUNAS_JSON_PATH)
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

        if not os.path.exists(ConferenciaApostasService.COLUNAS_JSON_PATH):
            colunas_padrao = [
                {'id': 'col_seq', 'nome': 'SEQ', 'tipo': 'text', 'descricao': 'Sequências detectadas'},
                {'id': 'col_finais', 'nome': 'FINAIS', 'tipo': 'number', 'descricao': 'Finais iguais'},
                {'id': 'col_rept', 'nome': 'REPT', 'tipo': 'number', 'descricao': 'Repetições do concurso anterior'},
                {'id': 'col_soma', 'nome': 'SOMA', 'tipo': 'number', 'descricao': 'Soma dos números'},
                {'id': 'col_pares_impares', 'nome': 'P/I', 'tipo': 'text', 'descricao': 'Pares e Ímpares'},
                {'id': 'col_padroes', 'nome': 'PADRÕES', 'tipo': 'text', 'descricao': 'Inicial/Final'},
                {'id': 'col_mes', 'nome': 'MÊS', 'tipo': 'text', 'descricao': 'Mês da sorte'},
                {'id': 'col_digitos_unicos', 'nome': 'DIG.ÚNICOS', 'tipo': 'text', 'descricao': 'Dígitos únicos'},
                {'id': 'col_mais_menos', 'nome': '+/-', 'tipo': 'text', 'descricao': 'Mais/Menos/Média'}
            ]
            with open(ConferenciaApostasService.COLUNAS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(colunas_padrao, f, ensure_ascii=False, indent=2)

    @staticmethod
    def listar_colunas_adicionais():
        """Lista colunas adicionais do JSON"""
        ConferenciaApostasService._garantir_arquivo_colunas()

        try:
            with open(ConferenciaApostasService.COLUNAS_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    @staticmethod
    def adicionar_coluna(nome, tipo='text', descricao=''):
        """Adiciona nova coluna adicional"""
        colunas = ConferenciaApostasService.listar_colunas_adicionais()

        novo_id = f"col_custom_{len(colunas) + 1}"
        nova_coluna = {
            'id': novo_id,
            'nome': nome,
            'tipo': tipo,
            'descricao': descricao
        }

        colunas.append(nova_coluna)

        with open(ConferenciaApostasService.COLUNAS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(colunas, f, ensure_ascii=False, indent=2)

        return nova_coluna

    @staticmethod
    def remover_coluna(coluna_id):
        """Remove coluna adicional"""
        colunas = ConferenciaApostasService.listar_colunas_adicionais()
        colunas_filtradas = [c for c in colunas if c['id'] != coluna_id]

        with open(ConferenciaApostasService.COLUNAS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(colunas_filtradas, f, ensure_ascii=False, indent=2)

        return {'sucesso': True}

    @staticmethod
    def normalizar_combinacao(texto):
        """
        Normaliza entrada de jogo com vários formatos possíveis
        Aceita separadores: espaço, vírgula, ponto, hífen, barra, pipe, +
        Aceita mês: Jan, Janeiro, jan, janeiro, etc

        Returns:
            dict: {'numeros': [1,2,3,4,5,6,7], 'mes': 1} ou None
        """
        padrao = re.compile(
            r'(\d{1,2})[\s,.\-+/|]*'
            r'(\d{1,2})[\s,.\-+/|]*'
            r'(\d{1,2})[\s,.\-+/|]*'
            r'(\d{1,2})[\s,.\-+/|]*'
            r'(\d{1,2})[\s,.\-+/|]*'
            r'(\d{1,2})[\s,.\-+/|]*'
            r'(\d{1,2})[\s,.\-+/|]*'
            r'(Jan(?:eiro)?|Fev(?:ereiro)?|Mar(?:ço)?|Abr(?:il)?|Mai(?:o)?|Jun(?:ho)?|Jul(?:ho)?|Ago(?:sto)?|Set(?:embro)?|Out(?:ubro)?|Nov(?:embro)?|Dez(?:embro)?)?',
            re.IGNORECASE
        )

        m = padrao.search(texto)
        if not m:
            return None

        numeros = [int(n) for n in m.groups()[:7]]
        mes_texto = m.groups()[7]

        mes_numero = None
        if mes_texto:
            mes_cap = mes_texto.capitalize()
            for mes_nome, mes_num in ConferenciaApostasService.MESES_ABREV.items():
                if mes_cap.startswith(mes_nome[:3]):
                    mes_numero = mes_num
                    break

        return {'numeros': numeros, 'mes': mes_numero}

    @staticmethod
    def validar_jogo(numeros, mes=None):
        """
        Valida um jogo (7 números de 1 a 31, sem repetição, opcionalmente com mês 1-12)

        Args:
            numeros: Lista de números
            mes: Mês da sorte (1-12) opcional

        Returns:
            dict: {valido: bool, erro: str}
        """
        if not numeros or len(numeros) != 7:
            return {'valido': False, 'erro': 'Jogo deve ter exatamente 7 números'}

        if len(set(numeros)) != 7:
            return {'valido': False, 'erro': 'Números não podem se repetir'}

        for num in numeros:
            if not isinstance(num, int) or num < 1 or num > 31:
                return {'valido': False, 'erro': 'Números devem estar entre 1 e 31'}

        if mes is not None:
            if not isinstance(mes, int) or mes < 1 or mes > 12:
                return {'valido': False, 'erro': 'Mês deve estar entre 1 e 12'}

        return {'valido': True}

    @staticmethod
    def detectar_sequencias(numeros):
        """
        Detecta sequências de números consecutivos

        Returns:
            dict: {'max_seq': int, 'sequencias': [[1,2,3], [5,6]], 'classe': 'seq-2'}
        """
        numeros_sorted = sorted(numeros)
        sequencias = []
        seq_atual = [numeros_sorted[0]]

        for i in range(1, len(numeros_sorted)):
            if numeros_sorted[i] - numeros_sorted[i-1] == 1:
                seq_atual.append(numeros_sorted[i])
            else:
                if len(seq_atual) >= 2:
                    sequencias.append(seq_atual)
                seq_atual = [numeros_sorted[i]]

        if len(seq_atual) >= 2:
            sequencias.append(seq_atual)

        max_seq = max([len(s) for s in sequencias]) if sequencias else 0

        classe = ''
        if max_seq == 2:
            classe = 'seq-2'
        elif max_seq == 3:
            classe = 'seq-3'
        elif max_seq >= 4:
            classe = 'seq-4'

        return {
            'max_seq': max_seq,
            'sequencias': sequencias,
            'classe': classe,
            'quantidade': len(sequencias)
        }

    @staticmethod
    def formatar_repeticoes_emoji(repeticoes):
        """
        Formata repetições com emoji

        Args:
            repeticoes: Número de repetições (0-7)

        Returns:
            str: Emoji + número (ex: '❌0', '✅1', '🔥3')
        """
        if repeticoes == 0:
            return f'❌{repeticoes}'
        elif repeticoes <= 2:
            return f'✅{repeticoes}'
        else:
            return f'🔥{repeticoes}'

    @staticmethod
    def formatar_com_emoji(valor):
        """
        Formata valor com emoji conforme as regras:
        - 0 → ❌0
        - 1-2 → ✅1 ou ✅2
        - 3+ → 🔥3 ou 🔥4+

        Args:
            valor: Número a ser formatado

        Returns:
            str: Emoji + número
        """
        if valor == 0:
            return f'❌{valor}'
        elif valor <= 2:
            return f'✅{valor}'
        else:
            return f'🔥{valor}'

    @staticmethod
    def obter_mes_classe(mes):
        """
        Retorna classe CSS para o mês

        Args:
            mes: Número do mês (1-12)

        Returns:
            str: Nome da classe CSS (ex: 'mes-cor-0' para Janeiro)
        """
        if mes is None or mes < 1 or mes > 12:
            return ''
        return f'mes-cor-{mes - 1}'

    @staticmethod
    def analisar_jogo(numeros, mes=None, concurso_numero=None):
        """
        Analisa características de um jogo

        Args:
            numeros: Lista de 7 números
            mes: Mês da sorte (opcional)
            concurso_numero: Número do concurso para comparar com anterior

        Returns:
            dict: Análise completa do jogo
        """
        numeros_sorted = sorted(numeros)

        pares = sum(1 for n in numeros if n % 2 == 0)
        impares = 7 - pares

        seq_info = ConferenciaApostasService.detectar_sequencias(numeros)

        print("=" * 80)
        print(f"🔥 ANALISANDO JOGO: {numeros}")
        print("=" * 80)

        finais = Counter([n % 10 for n in numeros])
        print(f"📊 Counter finais: {finais}")

        # Identificar números com finais iguais E contar GRUPOS
        numeros_finais_iguais = []
        grupos_finais = 0  # ← CONTAR GRUPOS
        maior_grupo = 0   # ← MAIOR QUANTIDADE DE NÚMEROS EM UM GRUPO (para emoji)

        for final, count in finais.items():
            if count > 1:
                grupos_finais += 1  # ← INCREMENTA CONTADOR DE GRUPOS
                if count > maior_grupo:
                    maior_grupo = count  # ← ATUALIZA MAIOR GRUPO
                numeros_no_grupo = [n for n in numeros if n % 10 == final]
                print(f"   Final {final}: {count} números → {numeros_no_grupo} [GRUPO {grupos_finais}]")
                numeros_finais_iguais.extend(numeros_no_grupo)

        # QUANTIDADE DE GRUPOS (coluna FINAIS)
        finais_iguais = grupos_finais

        print(f"🔍 RESULTADO: finais_iguais={finais_iguais} GRUPOS, maior_grupo={maior_grupo}, array={numeros_finais_iguais}")
        print("=" * 80)

        repeticoes = 0
        repeticoes_numeros = []

        # ✅ SEMPRE comparar com o ÚLTIMO concurso disponível no banco
        # NÃO usar concurso_numero - 1, mas sim o último sorteio realizado
        ultimo_concurso = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

        if ultimo_concurso:
            print(f"🔍 Comparando com ÚLTIMO concurso: {ultimo_concurso.concurso}")
            numeros_anteriores = ultimo_concurso.get_posicoes_lista()
            repeticoes_numeros = [n for n in numeros if n in numeros_anteriores]
            repeticoes = len(repeticoes_numeros)
            print(f"   Números do último concurso: {numeros_anteriores}")
            print(f"   Repetições encontradas: {repeticoes_numeros} (Total: {repeticoes})")

        soma = sum(numeros)

        # Padrões: Todos os dígitos iniciais e finais (com espaço)
        iniciais = [str(n).zfill(2)[0] for n in numeros_sorted]
        finais_digitos = [str(n).zfill(2)[1] for n in numeros_sorted]
        padroes_iniciais = ' '.join(iniciais)
        padroes_finais = ' '.join(finais_digitos)

        # Extract all digits from all numbers (with zero-padding)
        todos_digitos = []
        for num in numeros:
            todos_digitos.extend([int(d) for d in str(num).zfill(2)])
        digitos_unicos_set = sorted(set(todos_digitos))
        digitos_unicos_qtde = len(digitos_unicos_set)
        digitos_unicos_str = ','.join(map(str, digitos_unicos_set))

        menos = sum(1 for n in numeros if n <= 15)
        media_count = sum(1 for n in numeros if n == 16)
        mais = sum(1 for n in numeros if n >= 17)

        mes_nome_completo = ConferenciaApostasService.MESES_DICT.get(mes, '') if mes else ''
        mes_nome_abrev = ConferenciaApostasService.MESES_ABREV_SHORT.get(mes, '') if mes else ''
        mes_classe = ConferenciaApostasService.obter_mes_classe(mes)
        repeticoes_emoji = ConferenciaApostasService.formatar_repeticoes_emoji(repeticoes)

        # Criar versões emoji para SEQ, FINAIS e REPT
        sequencias_emoji = ConferenciaApostasService.formatar_com_emoji(seq_info['max_seq'])
        # ✅ EMOJI usa GRUPOS_FINAIS (quantidade de grupos)
        # ✅ COLUNA usa FINAIS_IGUAIS (quantidade de grupos)
        # Ambos mostram a MESMA coisa: quantidade de GRUPOS!
        finais_emoji = ConferenciaApostasService.formatar_com_emoji(grupos_finais)

        # Identificar todos os números em sequências
        numeros_em_sequencias = []
        for seq in seq_info['sequencias']:
            numeros_em_sequencias.extend(seq)

        return {
            'numeros': numeros_sorted,
            'pares': pares,
            'impares': impares,
            'sequencias': seq_info['max_seq'],
            'sequencias_emoji': sequencias_emoji,
            'sequencias_detalhes': seq_info,
            'sequencias_classe': seq_info['classe'],
            'numeros_em_sequencias': numeros_em_sequencias,
            'finais_iguais': finais_iguais,
            'finais_emoji': finais_emoji,
            'numeros_finais_iguais': numeros_finais_iguais,
            'repeticoes': repeticoes,
            'repeticoes_numeros': repeticoes_numeros,
            'repeticoes_emoji': repeticoes_emoji,
            'soma': soma,
            'padroes_iniciais': padroes_iniciais,
            'padroes_finais': padroes_finais,
            'digitos_unicos_qtde': digitos_unicos_qtde,
            'digitos_unicos_str': digitos_unicos_str,
            'mes': mes,
            'mes_nome': mes_nome_completo,
            'mes_nome_abrev': mes_nome_abrev,
            'mes_classe': mes_classe,
            'mais': mais,
            'menos': menos,
            'media': media_count
        }

    @staticmethod
    def conferir_jogo_com_resultado(jogo_numeros, jogo_mes, concurso_numero):
        """
        Confere um jogo com o resultado de um concurso

        Args:
            jogo_numeros: Lista de 7 números do jogo
            jogo_mes: Mês apostado (1-12) ou None
            concurso_numero: Número do concurso para conferir

        Returns:
            dict: Resultado da conferência
        """
        concurso = Sorteio.query.filter_by(concurso=concurso_numero).first()

        if not concurso:
            return {'erro': 'Concurso não encontrado'}

        numeros_sorteados = concurso.get_posicoes_lista()
        mes_sorteado = concurso.mes_sorte

        numeros_acertados = [n for n in jogo_numeros if n in numeros_sorteados]
        quantidade_acertos_numeros = len(numeros_acertados)

        acertou_mes = False
        if jogo_mes is not None and mes_sorteado is not None:
            acertou_mes = (jogo_mes == mes_sorteado)

        premio = ConferenciaApostasService._calcular_premio(
            quantidade_acertos_numeros,
            acertou_mes,
            concurso
        )

        analise = ConferenciaApostasService.analisar_jogo(jogo_numeros, jogo_mes, concurso_numero)

        return {
            'concurso': concurso_numero,
            'data_sorteio': concurso.data_sorteio.strftime('%d/%m/%Y'),
            'numeros_sorteados': numeros_sorteados,
            'mes_sorteado': mes_sorteado,
            'mes_sorteado_nome': ConferenciaApostasService.MESES_DICT.get(mes_sorteado, ''),
            'jogo': jogo_numeros,
            'jogo_mes': jogo_mes,
            'jogo_mes_nome': ConferenciaApostasService.MESES_DICT.get(jogo_mes, '') if jogo_mes else '',
            'acertos_numeros': numeros_acertados,
            'quantidade_acertos_numeros': quantidade_acertos_numeros,
            'acertou_mes': acertou_mes,
            'premio': premio,
            'analise': analise
        }

    @staticmethod
    def _calcular_premio(quantidade_acertos_numeros, acertou_mes, concurso):
        """
        Calcula prêmio baseado na quantidade de acertos de números e mês

        Regras Dia de Sorte:
        - 7 acertos: Prêmio variável (acumulado)
        - 6 acertos: Prêmio variável
        - 5 acertos: Prêmio variável
        - 4 acertos: Prêmio fixo (R$ 4,00 ou valor_premio_4_acertos do DB)
        - Mês da sorte: Prêmio fixo (R$ 2,00 ou valor_premio_mes_sorte do DB)
        """
        premios = []
        valor_total = 0.0
        valor_7_acertos_real = 0.0

        if quantidade_acertos_numeros == 7:
            # ✅ SEMPRE exibir 7 acertos, mesmo se valor for 0 ou NULL (ACUMULOU!)
            valor = concurso.valor_premio_7_acertos if concurso.valor_premio_7_acertos else 0.0
            valor_7_acertos_real = valor

            # Se valor é 0, significa ACUMULOU!
            faixa_descricao = '7 acertos - ACUMULOU!' if valor == 0.0 else '7 acertos'

            premios.append({
                'faixa': faixa_descricao,
                'valor': valor,
                'ganhadores': concurso.ganhadores_7_acertos,
                'acumulou': (valor == 0.0)  # ← Flag indicando acúmulo
            })
            valor_total += valor

            print(f"🎰 7 ACERTOS! Valor: R$ {valor:.2f} {'(ACUMULOU!)' if valor == 0.0 else ''}")

        elif quantidade_acertos_numeros == 6:
            valor = concurso.valor_premio_6_acertos if concurso.valor_premio_6_acertos else 0.0
            premios.append({
                'faixa': '6 acertos',
                'valor': valor,
                'ganhadores': concurso.ganhadores_6_acertos
            })
            valor_total += valor

        elif quantidade_acertos_numeros == 5:
            valor = concurso.valor_premio_5_acertos if concurso.valor_premio_5_acertos else 0.0
            premios.append({
                'faixa': '5 acertos',
                'valor': valor,
                'ganhadores': concurso.ganhadores_5_acertos
            })
            valor_total += valor

        elif quantidade_acertos_numeros == 4:
            # Get from database or use default
            valor = concurso.valor_premio_4_acertos if concurso.valor_premio_4_acertos else 4.00
            premios.append({
                'faixa': '4 acertos',
                'valor': valor,
                'ganhadores': concurso.ganhadores_4_acertos
            })
            valor_total += valor

        if acertou_mes:
            # Get Mês da Sorte value from database
            valor_mes = concurso.valor_premio_mes_sorte if concurso.valor_premio_mes_sorte else 2.00
            premios.append({
                'faixa': 'Mês da Sorte',
                'valor': valor_mes,
                'ganhadores': concurso.ganhadores_mes_sorte if hasattr(concurso, 'ganhadores_mes_sorte') else 0
            })
            valor_total += valor_mes

        return {
            'faixas': premios,
            'valor': valor_total,
            'valor_7_acertos_real': valor_7_acertos_real,
            'descricao': ' + '.join([f['faixa'] for f in premios]) if premios else 'Sem prêmio'
        }

    @staticmethod
    def conferir_multiplos_jogos(jogos, concurso_numero, valor_aposta=2.50):
        """
        Confere múltiplos jogos de uma vez

        Args:
            jogos: Lista de dicts {'numeros': [1,2,3,4,5,6,7], 'mes': 1}
            concurso_numero: Número do concurso
            valor_aposta: Valor de cada aposta

        Returns:
            dict: Resumo da conferência
        """
        resultados = []
        total_gasto = len(jogos) * valor_aposta
        total_ganho = 0.0

        for idx, jogo in enumerate(jogos):
            numeros = jogo.get('numeros', jogo) if isinstance(jogo, dict) else jogo
            mes = jogo.get('mes') if isinstance(jogo, dict) else None

            resultado = ConferenciaApostasService.conferir_jogo_com_resultado(
                numeros,
                mes,
                concurso_numero
            )

            if 'erro' not in resultado:
                total_ganho += resultado['premio']['valor']
                resultado['numero_jogo'] = idx + 1
                resultados.append(resultado)

        lucro = total_ganho - total_gasto

        acertos_por_faixa = Counter([r['quantidade_acertos_numeros'] for r in resultados])
        acertos_mes_total = sum(1 for r in resultados if r.get('acertou_mes'))

        return {
            'concurso': concurso_numero,
            'total_jogos': len(jogos),
            'total_gasto': total_gasto,
            'total_ganho': total_ganho,
            'lucro': lucro,
            'valor_aposta': valor_aposta,
            'acertos_por_faixa': dict(acertos_por_faixa),
            'acertos_mes_total': acertos_mes_total,
            'jogos_premiados': len([r for r in resultados if r['premio']['valor'] > 0]),
            'resultados': resultados
        }

    @staticmethod
    def listar_concursos_disponiveis():
        """Lista TODOS os concursos disponíveis (do primeiro ao último) com dezenas sorteadas"""
        concursos = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        return [
            {
                'numero': c.concurso,
                'data': c.data_sorteio.strftime('%d/%m/%Y'),
                'mes_nome': c.get_nome_mes(),
                'numeros': [c.posicao_1, c.posicao_2, c.posicao_3, c.posicao_4, c.posicao_5, c.posicao_6, c.posicao_7]
            }
            for c in concursos
        ]

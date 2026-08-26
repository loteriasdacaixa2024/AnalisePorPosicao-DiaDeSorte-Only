"""
SERVIÇO DE ANÁLISE PROFUNDA EXPANDIDO - 150+ TÉCNICAS
Sistema de Detetive Automático para descoberta de origens de dezenas
Versão: 2.0 EXPANDIDO

CATEGORIAS:
- A: Básicas (10)
- B: Matemáticas (15)
- C: Combinações (10)
- D: Avançadas (20)
- E: Data (10)
- J: Partes do Ano (20) ← NOVA
- K: Dígitos do Prêmio (30) ← NOVA
- L: Espelhamento Universal 6↔️9 (automático) ← NOVA
"""

import sqlite3
import re
import math
from datetime import datetime
from collections import defaultdict


# ========== UTILITÁRIOS MATEMÁTICOS ==========

def raiz_digital(n):
    """Calcula raiz digital (soma recursiva até 1 dígito)"""
    n = abs(int(n))
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n


def eh_primo(n):
    """Verifica se número é primo"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def primo_anterior(n):
    """Encontra o primo anterior a n"""
    n = int(n) - 1
    while n > 1:
        if eh_primo(n):
            return n
        n -= 1
    return 2


def primo_posterior(n):
    """Encontra o primo posterior a n"""
    n = int(n) + 1
    while n < 1000:
        if eh_primo(n):
            return n
        n += 1
    return None


def fibonacci(n):
    """Retorna o n-ésimo número de Fibonacci"""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def indice_fibonacci(n):
    """Retorna o índice na sequência Fibonacci se n está nela"""
    n = int(n)
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    idx = 1
    while b < n:
        a, b = b, a + b
        idx += 1
    return idx if b == n else None


def triangular(n):
    """Retorna o n-ésimo número triangular"""
    return n * (n + 1) // 2


def indice_triangular(n):
    """Retorna o índice se n é triangular"""
    n = int(n)
    idx = 1
    while True:
        tri = triangular(idx)
        if tri == n:
            return idx
        if tri > n:
            return None
        idx += 1


# ========== CLASSE PRINCIPAL ==========

class AnalisadorProfundo:
    """
    Sistema de Detetive Automático para análise de técnicas
    Aplica ~150 técnicas matemáticas automaticamente
    """

    def __init__(self, db_path='analise_por_posicao.db'):
        self.db_path = db_path
        self.tecnicas_cache = {}

        # Mapeamento de espelhamento visual
        self.espelhamento_69 = {6: 9, 9: 6}

    # ========== MÉTODOS DE EXTRAÇÃO ==========

    def extrair_partes_ano(self, ano):
        """
        Extrai TODAS as partes possíveis do ano
        Exemplo: 2025 → {
            'ano_completo': 2025,
            'primeiros_2': 20,
            'ultimos_2': 25,
            'digito_1': 2,
            'digito_2': 0,
            'digito_3': 2,
            'digito_4': 5,
            'digitos': [2, 0, 2, 5]
        }
        """
        ano_str = str(ano).zfill(4)  # Garante 4 dígitos

        return {
            'ano_completo': ano,
            'primeiros_2': int(ano_str[:2]),
            'ultimos_2': int(ano_str[2:]),
            'digito_1': int(ano_str[0]),
            'digito_2': int(ano_str[1]),
            'digito_3': int(ano_str[2]),
            'digito_4': int(ano_str[3]),
            'digitos': [int(d) for d in ano_str]
        }

    def extrair_digitos_premio(self, valor_premio):
        """
        Extrai TODOS os dígitos individuais do prêmio
        Exemplo: 1.500.000,00 → [1, 5, 0, 0, 0, 0, 0]
        """
        # Remove separadores e casas decimais
        valor_str = str(int(valor_premio))
        return [int(d) for d in valor_str]

    def aplicar_espelhamento_69(self, valor):
        """
        Aplica espelhamento visual 6 ↔️ 9
        Retorna None se valor não for 6 ou 9
        """
        if valor in self.espelhamento_69:
            return self.espelhamento_69[valor]
        return None

    # ========== CATEGORIA J: PARTES DO ANO (20 TÉCNICAS) ==========

    def aplicar_tecnicas_partes_ano(self, data_str):
        """
        20 técnicas usando partes específicas do ano
        Usa primeiros 2 dígitos, últimos 2 dígitos, dígitos individuais
        """
        tecnicas = []

        # Parsear data
        match_br = re.match(r'(\d{2})/(\d{2})/(\d{4})', data_str)
        match_iso = re.match(r'(\d{4})-(\d{2})-(\d{2})', data_str)

        if match_br:
            dia, mes, ano = int(match_br.group(1)), int(match_br.group(2)), int(match_br.group(3))
        elif match_iso:
            ano, mes, dia = int(match_iso.group(1)), int(match_iso.group(2)), int(match_iso.group(3))
        else:
            return tecnicas

        partes = self.extrair_partes_ano(ano)

        # TEC-J-01: Primeiros 2 dígitos do ano
        tecnicas.append({
            'id': 'TEC-J-01',
            'nome': 'Primeiros 2 Dígitos do Ano',
            'categoria': 'Partes do Ano',
            'campo': 'DATA',
            'formula': f'primeiros_2_digitos({ano})',
            'calculo': f'{ano} → primeiros 2 dígitos = {partes["primeiros_2"]}',
            'resultado': partes['primeiros_2']
        })

        # TEC-J-02: Últimos 2 dígitos do ano
        tecnicas.append({
            'id': 'TEC-J-02',
            'nome': 'Últimos 2 Dígitos do Ano',
            'categoria': 'Partes do Ano',
            'campo': 'DATA',
            'formula': f'ultimos_2_digitos({ano})',
            'calculo': f'{ano} → últimos 2 dígitos = {partes["ultimos_2"]}',
            'resultado': partes['ultimos_2']
        })

        # TEC-J-03: Primeiros 2 dígitos + Mês
        soma = partes['primeiros_2'] + mes
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-J-03',
                'nome': 'Primeiros 2 Dígitos Ano + Mês',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{partes["primeiros_2"]} + {mes}',
                'calculo': f'{partes["primeiros_2"]} + {mes} = {soma}',
                'resultado': soma
            })

        # TEC-J-04: Últimos 2 dígitos + Dia
        soma = partes['ultimos_2'] + dia
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-J-04',
                'nome': 'Últimos 2 Dígitos Ano + Dia',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{partes["ultimos_2"]} + {dia}',
                'calculo': f'{partes["ultimos_2"]} + {dia} = {soma}',
                'resultado': soma
            })

        # TEC-J-05: Primeiros 2 dígitos - Mês
        diff = partes['primeiros_2'] - mes
        if 1 <= diff <= 31:
            tecnicas.append({
                'id': 'TEC-J-05',
                'nome': 'Primeiros 2 Dígitos Ano - Mês',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{partes["primeiros_2"]} - {mes}',
                'calculo': f'{partes["primeiros_2"]} - {mes} = {diff}',
                'resultado': diff
            })

        # TEC-J-06: Últimos 2 dígitos - Dia
        diff = partes['ultimos_2'] - dia
        if 1 <= diff <= 31:
            tecnicas.append({
                'id': 'TEC-J-06',
                'nome': 'Últimos 2 Dígitos Ano - Dia',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{partes["ultimos_2"]} - {dia}',
                'calculo': f'{partes["ultimos_2"]} - {dia} = {diff}',
                'resultado': diff
            })

        # TEC-J-07: 1º dígito do ano
        if 1 <= partes['digito_1'] <= 31:
            tecnicas.append({
                'id': 'TEC-J-07',
                'nome': '1º Dígito do Ano',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'1º_digito({ano})',
                'calculo': f'{ano} → 1º dígito = {partes["digito_1"]}',
                'resultado': partes['digito_1']
            })

        # TEC-J-08: 2º dígito do ano
        if 1 <= partes['digito_2'] <= 31:
            tecnicas.append({
                'id': 'TEC-J-08',
                'nome': '2º Dígito do Ano',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'2º_digito({ano})',
                'calculo': f'{ano} → 2º dígito = {partes["digito_2"]}',
                'resultado': partes['digito_2']
            })

        # TEC-J-09: 3º dígito do ano
        if 1 <= partes['digito_3'] <= 31:
            tecnicas.append({
                'id': 'TEC-J-09',
                'nome': '3º Dígito do Ano',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'3º_digito({ano})',
                'calculo': f'{ano} → 3º dígito = {partes["digito_3"]}',
                'resultado': partes['digito_3']
            })

        # TEC-J-10: 4º dígito do ano
        if 1 <= partes['digito_4'] <= 31:
            tecnicas.append({
                'id': 'TEC-J-10',
                'nome': '4º Dígito do Ano',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'4º_digito({ano})',
                'calculo': f'{ano} → 4º dígito = {partes["digito_4"]}',
                'resultado': partes['digito_4']
            })

        # TEC-J-11: Soma primeiros 2 dígitos ano
        soma = partes['digito_1'] + partes['digito_2']
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-J-11',
                'nome': 'Soma Primeiros 2 Dígitos Ano',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{partes["digito_1"]} + {partes["digito_2"]}',
                'calculo': f'{partes["digito_1"]} + {partes["digito_2"]} = {soma}',
                'resultado': soma
            })

        # TEC-J-12: Soma últimos 2 dígitos ano
        soma = partes['digito_3'] + partes['digito_4']
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-J-12',
                'nome': 'Soma Últimos 2 Dígitos Ano',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{partes["digito_3"]} + {partes["digito_4"]}',
                'calculo': f'{partes["digito_3"]} + {partes["digito_4"]} = {soma}',
                'resultado': soma
            })

        # TEC-J-13: Soma todos dígitos do ano
        soma = sum(partes['digitos'])
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-J-13',
                'nome': 'Soma Todos Dígitos Ano',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'soma({partes["digitos"]})',
                'calculo': f'{" + ".join(map(str, partes["digitos"]))} = {soma}',
                'resultado': soma
            })

        # TEC-J-14: Primeiros 2 + Últimos 2
        soma = partes['primeiros_2'] + partes['ultimos_2']
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-J-14',
                'nome': 'Primeiros 2 + Últimos 2',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{partes["primeiros_2"]} + {partes["ultimos_2"]}',
                'calculo': f'{partes["primeiros_2"]} + {partes["ultimos_2"]} = {soma}',
                'resultado': soma
            })

        # TEC-J-15: Primeiros 2 - Últimos 2 (absoluto)
        diff = abs(partes['primeiros_2'] - partes['ultimos_2'])
        if 1 <= diff <= 31:
            tecnicas.append({
                'id': 'TEC-J-15',
                'nome': 'Primeiros 2 - Últimos 2',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'abs({partes["primeiros_2"]} - {partes["ultimos_2"]})',
                'calculo': f'|{partes["primeiros_2"]} - {partes["ultimos_2"]}| = {diff}',
                'resultado': diff
            })

        # TEC-J-16: Primeiros 2 × 2
        resultado = partes['primeiros_2'] * 2
        if 1 <= resultado <= 31:
            tecnicas.append({
                'id': 'TEC-J-16',
                'nome': 'Primeiros 2 Dígitos × 2',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{partes["primeiros_2"]} × 2',
                'calculo': f'{partes["primeiros_2"]} × 2 = {resultado}',
                'resultado': resultado
            })

        # TEC-J-17: Últimos 2 ÷ 2
        if partes['ultimos_2'] % 2 == 0:
            resultado = partes['ultimos_2'] // 2
            if 1 <= resultado <= 31:
                tecnicas.append({
                    'id': 'TEC-J-17',
                    'nome': 'Últimos 2 Dígitos ÷ 2',
                    'categoria': 'Partes do Ano',
                    'campo': 'DATA',
                    'formula': f'{partes["ultimos_2"]} ÷ 2',
                    'calculo': f'{partes["ultimos_2"]} ÷ 2 = {resultado}',
                    'resultado': resultado
                })

        # TEC-J-18: Raiz digital ano completo
        rd = raiz_digital(ano)
        if 1 <= rd <= 31:
            tecnicas.append({
                'id': 'TEC-J-18',
                'nome': 'Raiz Digital Ano Completo',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'raiz_digital({ano})',
                'calculo': f'raiz_digital({ano}) = {rd}',
                'resultado': rd
            })

        # TEC-J-19: Ano mod 31
        resultado = ano % 31
        if 1 <= resultado <= 31:
            tecnicas.append({
                'id': 'TEC-J-19',
                'nome': 'Ano mod 31',
                'categoria': 'Partes do Ano',
                'campo': 'DATA',
                'formula': f'{ano} % 31',
                'calculo': f'{ano} mod 31 = {resultado}',
                'resultado': resultado
            })

        # TEC-J-20: Primeiros 2 mod 31
        resultado = partes['primeiros_2'] % 31
        if resultado == 0:
            resultado = 31
        tecnicas.append({
            'id': 'TEC-J-20',
            'nome': 'Primeiros 2 Dígitos mod 31',
            'categoria': 'Partes do Ano',
            'campo': 'DATA',
            'formula': f'{partes["primeiros_2"]} % 31',
            'calculo': f'{partes["primeiros_2"]} mod 31 = {resultado}',
            'resultado': resultado
        })

        return tecnicas

    # ========== CATEGORIA K: DÍGITOS DO PRÊMIO (30 TÉCNICAS) ==========

    def aplicar_tecnicas_digitos_premio(self, valor_premio):
        """
        30 técnicas usando dígitos individuais do prêmio
        Extrai cada dígito e faz combinações
        """
        tecnicas = []

        digitos = self.extrair_digitos_premio(valor_premio)

        if not digitos:
            return tecnicas

        # TEC-K-01 a K-10: Cada dígito individual (até 10 dígitos)
        for i, digito in enumerate(digitos[:10], 1):
            if 1 <= digito <= 31:
                tecnicas.append({
                    'id': f'TEC-K-{i:02d}',
                    'nome': f'{i}º Dígito do Prêmio',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'{i}º_digito({int(valor_premio)})',
                    'calculo': f'{int(valor_premio)} → {i}º dígito = {digito}',
                    'resultado': digito
                })

        # TEC-K-11: Soma 1º e 2º dígitos
        if len(digitos) >= 2:
            soma = digitos[0] + digitos[1]
            if 1 <= soma <= 31:
                tecnicas.append({
                    'id': 'TEC-K-11',
                    'nome': 'Soma 1º + 2º Dígitos Prêmio',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'{digitos[0]} + {digitos[1]}',
                    'calculo': f'{digitos[0]} + {digitos[1]} = {soma}',
                    'resultado': soma
                })

        # TEC-K-12: Produto 1º × 2º dígitos
        if len(digitos) >= 2 and digitos[0] != 0 and digitos[1] != 0:
            produto = digitos[0] * digitos[1]
            if 1 <= produto <= 31:
                tecnicas.append({
                    'id': 'TEC-K-12',
                    'nome': 'Produto 1º × 2º Dígitos',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'{digitos[0]} × {digitos[1]}',
                    'calculo': f'{digitos[0]} × {digitos[1]} = {produto}',
                    'resultado': produto
                })

        # TEC-K-13: Soma de TODOS os dígitos
        soma_total = sum(digitos)
        if 1 <= soma_total <= 31:
            tecnicas.append({
                'id': 'TEC-K-13',
                'nome': 'Soma Todos Dígitos Prêmio',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'soma({digitos})',
                'calculo': f'{" + ".join(map(str, digitos))} = {soma_total}',
                'resultado': soma_total
            })

        # TEC-K-14: Soma dígitos + Espelhamento 6↔️9
        # Esta técnica será expandida em TEC-L (espelhamento universal)
        soma_total = sum(digitos)
        espelhado = self.aplicar_espelhamento_69(soma_total)
        if espelhado and 1 <= espelhado <= 31:
            tecnicas.append({
                'id': 'TEC-K-14',
                'nome': 'Soma Dígitos Espelhada',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'espelhar(soma({digitos}))',
                'calculo': f'soma = {soma_total} → espelhado = {espelhado}',
                'resultado': espelhado
            })

        # TEC-K-15: Raiz digital do prêmio
        rd = raiz_digital(valor_premio)
        if 1 <= rd <= 31:
            tecnicas.append({
                'id': 'TEC-K-15',
                'nome': 'Raiz Digital Prêmio',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'raiz_digital({int(valor_premio)})',
                'calculo': f'raiz_digital({int(valor_premio)}) = {rd}',
                'resultado': rd
            })

        # TEC-K-16: Primeiros 2 dígitos do prêmio
        if len(digitos) >= 2:
            primeiros_2 = int(str(digitos[0]) + str(digitos[1]))
            if 1 <= primeiros_2 <= 31:
                tecnicas.append({
                    'id': 'TEC-K-16',
                    'nome': 'Primeiros 2 Dígitos Prêmio',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'primeiros_2({int(valor_premio)})',
                    'calculo': f'{int(valor_premio)} → primeiros 2 = {primeiros_2}',
                    'resultado': primeiros_2
                })

        # TEC-K-17: Últimos 2 dígitos do prêmio
        if len(digitos) >= 2:
            ultimos_2 = int(str(digitos[-2]) + str(digitos[-1]))
            if 1 <= ultimos_2 <= 31:
                tecnicas.append({
                    'id': 'TEC-K-17',
                    'nome': 'Últimos 2 Dígitos Prêmio',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'ultimos_2({int(valor_premio)})',
                    'calculo': f'{int(valor_premio)} → últimos 2 = {ultimos_2}',
                    'resultado': ultimos_2
                })

        # TEC-K-18: Soma dígitos ímpares
        impares = [d for d in digitos if d % 2 == 1]
        if impares:
            soma_impares = sum(impares)
            if 1 <= soma_impares <= 31:
                tecnicas.append({
                    'id': 'TEC-K-18',
                    'nome': 'Soma Dígitos Ímpares',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'soma_impares({digitos})',
                    'calculo': f'ímpares: {impares} → soma = {soma_impares}',
                    'resultado': soma_impares
                })

        # TEC-K-19: Soma dígitos pares
        pares = [d for d in digitos if d % 2 == 0]
        if pares:
            soma_pares = sum(pares)
            if 1 <= soma_pares <= 31:
                tecnicas.append({
                    'id': 'TEC-K-19',
                    'nome': 'Soma Dígitos Pares',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'soma_pares({digitos})',
                    'calculo': f'pares: {pares} → soma = {soma_pares}',
                    'resultado': soma_pares
                })

        # TEC-K-20: Quantidade de dígitos não-zero
        nao_zero = [d for d in digitos if d != 0]
        qtd = len(nao_zero)
        if 1 <= qtd <= 31:
            tecnicas.append({
                'id': 'TEC-K-20',
                'nome': 'Quantidade Dígitos Não-Zero',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'count_nonzero({digitos})',
                'calculo': f'não-zero: {nao_zero} → count = {qtd}',
                'resultado': qtd
            })

        # TEC-K-21: Maior dígito
        maior = max(digitos)
        if 1 <= maior <= 31:
            tecnicas.append({
                'id': 'TEC-K-21',
                'nome': 'Maior Dígito Prêmio',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'max({digitos})',
                'calculo': f'max({digitos}) = {maior}',
                'resultado': maior
            })

        # TEC-K-22: Menor dígito (não-zero)
        nao_zero = [d for d in digitos if d != 0]
        if nao_zero:
            menor = min(nao_zero)
            if 1 <= menor <= 31:
                tecnicas.append({
                    'id': 'TEC-K-22',
                    'nome': 'Menor Dígito Não-Zero',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'min_nonzero({digitos})',
                    'calculo': f'não-zero: {nao_zero} → min = {menor}',
                    'resultado': menor
                })

        # TEC-K-23: Amplitude (maior - menor)
        if len(digitos) > 0:
            amplitude = max(digitos) - min(digitos)
            if 1 <= amplitude <= 31:
                tecnicas.append({
                    'id': 'TEC-K-23',
                    'nome': 'Amplitude Dígitos',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'max - min',
                    'calculo': f'{max(digitos)} - {min(digitos)} = {amplitude}',
                    'resultado': amplitude
                })

        # TEC-K-24: Dígito do meio (se quantidade ímpar)
        if len(digitos) % 2 == 1:
            idx_meio = len(digitos) // 2
            digito_meio = digitos[idx_meio]
            if 1 <= digito_meio <= 31:
                tecnicas.append({
                    'id': 'TEC-K-24',
                    'nome': 'Dígito Central Prêmio',
                    'categoria': 'Dígitos do Prêmio',
                    'campo': 'PRÊMIO',
                    'formula': f'digito_central({digitos})',
                    'calculo': f'posição {idx_meio+1} = {digito_meio}',
                    'resultado': digito_meio
                })

        # TEC-K-25: XOR de todos os dígitos
        xor_result = 0
        for d in digitos:
            xor_result ^= d
        if 1 <= xor_result <= 31:
            tecnicas.append({
                'id': 'TEC-K-25',
                'nome': 'XOR Todos Dígitos',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'XOR({digitos})',
                'calculo': f'{" XOR ".join(map(str, digitos))} = {xor_result}',
                'resultado': xor_result
            })

        # TEC-K-26: Produto dígitos não-zero mod 31
        nao_zero = [d for d in digitos if d != 0]
        if nao_zero:
            produto = 1
            for d in nao_zero:
                produto *= d
            resultado = produto % 31
            if resultado == 0:
                resultado = 31
            tecnicas.append({
                'id': 'TEC-K-26',
                'nome': 'Produto Dígitos mod 31',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'produto({nao_zero}) % 31',
                'calculo': f'{" × ".join(map(str, nao_zero))} mod 31 = {resultado}',
                'resultado': resultado
            })

        # TEC-K-27: Soma alternada (+ - + - ...)
        soma_alt = 0
        for i, d in enumerate(digitos):
            if i % 2 == 0:
                soma_alt += d
            else:
                soma_alt -= d
        soma_alt = abs(soma_alt)
        if 1 <= soma_alt <= 31:
            tecnicas.append({
                'id': 'TEC-K-27',
                'nome': 'Soma Alternada Dígitos',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'{digitos[0]} - {digitos[1] if len(digitos) > 1 else 0} + ...',
                'calculo': f'soma_alternada = {soma_alt}',
                'resultado': soma_alt
            })

        # TEC-K-28: Reverso dos dígitos
        reverso = int(''.join(map(str, reversed(digitos))))
        primeiro_dig_reverso = int(str(reverso)[0])
        if 1 <= primeiro_dig_reverso <= 31:
            tecnicas.append({
                'id': 'TEC-K-28',
                'nome': '1º Dígito do Reverso',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'reverso({int(valor_premio)})[0]',
                'calculo': f'reverso = {reverso} → 1º = {primeiro_dig_reverso}',
                'resultado': primeiro_dig_reverso
            })

        # TEC-K-29: Quantidade de zeros
        qtd_zeros = digitos.count(0)
        if 1 <= qtd_zeros <= 31:
            tecnicas.append({
                'id': 'TEC-K-29',
                'nome': 'Quantidade de Zeros',
                'categoria': 'Dígitos do Prêmio',
                'campo': 'PRÊMIO',
                'formula': f'count_zeros({digitos})',
                'calculo': f'zeros em {digitos} = {qtd_zeros}',
                'resultado': qtd_zeros
            })

        # TEC-K-30: Prêmio mod 31
        resultado = int(valor_premio) % 31
        if resultado == 0:
            resultado = 31
        tecnicas.append({
            'id': 'TEC-K-30',
            'nome': 'Prêmio mod 31',
            'categoria': 'Dígitos do Prêmio',
            'campo': 'PRÊMIO',
            'formula': f'{int(valor_premio)} % 31',
            'calculo': f'{int(valor_premio)} mod 31 = {resultado}',
            'resultado': resultado
        })

        return tecnicas

    # ========== CATEGORIA A: BÁSICAS (10 TÉCNICAS ORIGINAIS) ==========

    def aplicar_tecnicas_basicas(self, valor, campo_nome):
        """10 técnicas básicas de extração de dígitos"""
        tecnicas = []
        valor = int(valor)
        valor_str = str(valor)

        # TEC-A-01: Primeiro dígito
        primeiro = int(valor_str[0])
        if 1 <= primeiro <= 31:
            tecnicas.append({
                'id': 'TEC-A-01',
                'nome': 'Primeiro Dígito',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'primeiro_digito({valor})',
                'calculo': f'{valor} → primeiro dígito = {primeiro}',
                'resultado': primeiro
            })

        # TEC-A-02: Último dígito
        ultimo = int(valor_str[-1])
        if 1 <= ultimo <= 31:
            tecnicas.append({
                'id': 'TEC-A-02',
                'nome': 'Último Dígito',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'ultimo_digito({valor})',
                'calculo': f'{valor} → último dígito = {ultimo}',
                'resultado': ultimo
            })

        # TEC-A-03: Soma dos dígitos
        soma = sum(int(d) for d in valor_str)
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-A-03',
                'nome': 'Soma dos Dígitos',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'soma_digitos({valor})',
                'calculo': f'{" + ".join(valor_str)} = {soma}',
                'resultado': soma
            })

        # TEC-A-04: Produto dos dígitos
        produto = 1
        for d in valor_str:
            produto *= int(d)
        if 1 <= produto <= 31:
            tecnicas.append({
                'id': 'TEC-A-04',
                'nome': 'Produto dos Dígitos',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'produto_digitos({valor})',
                'calculo': f'{" × ".join(valor_str)} = {produto}',
                'resultado': produto
            })

        # TEC-A-05: Primeiros 2 dígitos
        if len(valor_str) >= 2:
            primeiros2 = int(valor_str[:2])
            if 1 <= primeiros2 <= 31:
                tecnicas.append({
                    'id': 'TEC-A-05',
                    'nome': 'Primeiros 2 Dígitos',
                    'categoria': 'Básica',
                    'campo': campo_nome,
                    'formula': f'primeiros_2({valor})',
                    'calculo': f'{valor} → primeiros 2 = {primeiros2}',
                    'resultado': primeiros2
                })

        # TEC-A-06: Últimos 2 dígitos
        if len(valor_str) >= 2:
            ultimos2 = int(valor_str[-2:])
            if 1 <= ultimos2 <= 31:
                tecnicas.append({
                    'id': 'TEC-A-06',
                    'nome': 'Últimos 2 Dígitos',
                    'categoria': 'Básica',
                    'campo': campo_nome,
                    'formula': f'ultimos_2({valor})',
                    'calculo': f'{valor} → últimos 2 = {ultimos2}',
                    'resultado': ultimos2
                })

        # TEC-A-07: Dígito central
        if len(valor_str) % 2 == 1:
            idx_central = len(valor_str) // 2
            central = int(valor_str[idx_central])
            if 1 <= central <= 31:
                tecnicas.append({
                    'id': 'TEC-A-07',
                    'nome': 'Dígito Central',
                    'categoria': 'Básica',
                    'campo': campo_nome,
                    'formula': f'digito_central({valor})',
                    'calculo': f'{valor} → posição {idx_central+1} = {central}',
                    'resultado': central
                })

        # TEC-A-08: Inversão de dígitos
        invertido = int(valor_str[::-1])
        if 1 <= invertido <= 31:
            tecnicas.append({
                'id': 'TEC-A-08',
                'nome': 'Inversão de Dígitos',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'inverter({valor})',
                'calculo': f'{valor} invertido = {invertido}',
                'resultado': invertido
            })

        # TEC-A-09: Módulo 31
        mod31 = valor % 31
        if mod31 == 0:
            mod31 = 31
        tecnicas.append({
            'id': 'TEC-A-09',
            'nome': 'Módulo 31',
            'categoria': 'Básica',
            'campo': campo_nome,
            'formula': f'{valor} % 31',
            'calculo': f'{valor} mod 31 = {mod31}',
            'resultado': mod31
        })

        # TEC-A-10: Raiz digital
        rd = raiz_digital(valor)
        if 1 <= rd <= 31:
            tecnicas.append({
                'id': 'TEC-A-10',
                'nome': 'Raiz Digital',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'raiz_digital({valor})',
                'calculo': f'raiz_digital({valor}) = {rd}',
                'resultado': rd
            })

        return tecnicas

    # ========== CATEGORIA B: MATEMÁTICAS (15 TÉCNICAS) ==========

    def aplicar_tecnicas_matematicas(self, valor, campo_nome):
        """15 técnicas matemáticas avançadas"""
        tecnicas = []
        valor = int(valor)
        valor_str = str(valor)

        # TEC-B-01: Divisão por 2
        if valor % 2 == 0:
            resultado = valor // 2
            if 1 <= resultado <= 31:
                tecnicas.append({
                    'id': 'TEC-B-01',
                    'nome': 'Divisão por 2',
                    'categoria': 'Matemática',
                    'campo': campo_nome,
                    'formula': f'{valor} ÷ 2',
                    'calculo': f'{valor} ÷ 2 = {resultado}',
                    'resultado': resultado
                })

        # TEC-B-02: Divisão por 3
        if valor % 3 == 0:
            resultado = valor // 3
            if 1 <= resultado <= 31:
                tecnicas.append({
                    'id': 'TEC-B-02',
                    'nome': 'Divisão por 3',
                    'categoria': 'Matemática',
                    'campo': campo_nome,
                    'formula': f'{valor} ÷ 3',
                    'calculo': f'{valor} ÷ 3 = {resultado}',
                    'resultado': resultado
                })

        # TEC-B-03: Multiplicação por 2
        resultado = valor * 2
        if 1 <= resultado <= 31:
            tecnicas.append({
                'id': 'TEC-B-03',
                'nome': 'Multiplicação por 2',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'{valor} × 2',
                'calculo': f'{valor} × 2 = {resultado}',
                'resultado': resultado
            })

        # TEC-B-04: Multiplicação por 3
        resultado = valor * 3
        if 1 <= resultado <= 31:
            tecnicas.append({
                'id': 'TEC-B-04',
                'nome': 'Multiplicação por 3',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'{valor} × 3',
                'calculo': f'{valor} × 3 = {resultado}',
                'resultado': resultado
            })

        # TEC-B-05: Raiz quadrada (se perfeito)
        raiz = int(math.sqrt(valor))
        if raiz * raiz == valor and 1 <= raiz <= 31:
            tecnicas.append({
                'id': 'TEC-B-05',
                'nome': 'Raiz Quadrada',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'√{valor}',
                'calculo': f'√{valor} = {raiz}',
                'resultado': raiz
            })

        # TEC-B-06: Quadrado do primeiro dígito
        primeiro = int(valor_str[0])
        quadrado = primeiro ** 2
        if 1 <= quadrado <= 31:
            tecnicas.append({
                'id': 'TEC-B-06',
                'nome': 'Quadrado 1º Dígito',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'{primeiro}²',
                'calculo': f'{primeiro}² = {quadrado}',
                'resultado': quadrado
            })

        # TEC-B-07: Módulo 10
        mod10 = valor % 10
        if 1 <= mod10 <= 31:
            tecnicas.append({
                'id': 'TEC-B-07',
                'nome': 'Módulo 10',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'{valor} % 10',
                'calculo': f'{valor} mod 10 = {mod10}',
                'resultado': mod10
            })

        # TEC-B-08: Módulo 7
        mod7 = valor % 7
        if mod7 == 0:
            mod7 = 7
        tecnicas.append({
            'id': 'TEC-B-08',
            'nome': 'Módulo 7',
            'categoria': 'Matemática',
            'campo': campo_nome,
            'formula': f'{valor} % 7',
            'calculo': f'{valor} mod 7 = {mod7}',
            'resultado': mod7
        })

        # TEC-B-09: Complemento 31
        comp = 31 - (valor % 31)
        if comp == 31:
            comp = 0
        if 1 <= comp <= 31:
            tecnicas.append({
                'id': 'TEC-B-09',
                'nome': 'Complemento 31',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'31 - ({valor} % 31)',
                'calculo': f'31 - {valor % 31} = {comp}',
                'resultado': comp
            })

        # TEC-B-10: Soma alternada (+/-)
        digitos = [int(d) for d in valor_str]
        soma_alt = 0
        for i, d in enumerate(digitos):
            if i % 2 == 0:
                soma_alt += d
            else:
                soma_alt -= d
        soma_alt = abs(soma_alt)
        if 1 <= soma_alt <= 31:
            tecnicas.append({
                'id': 'TEC-B-10',
                'nome': 'Soma Alternada',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'{digitos[0]} - {digitos[1] if len(digitos) > 1 else 0} + ...',
                'calculo': f'resultado = {soma_alt}',
                'resultado': soma_alt
            })

        # TEC-B-11: XOR de dígitos
        xor_result = 0
        for d in valor_str:
            xor_result ^= int(d)
        if 1 <= xor_result <= 31:
            tecnicas.append({
                'id': 'TEC-B-11',
                'nome': 'XOR dos Dígitos',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'XOR({valor_str})',
                'calculo': f'{" XOR ".join(valor_str)} = {xor_result}',
                'resultado': xor_result
            })

        # TEC-B-12: Maior dígito
        maior = max(int(d) for d in valor_str)
        if 1 <= maior <= 31:
            tecnicas.append({
                'id': 'TEC-B-12',
                'nome': 'Maior Dígito',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'max({valor_str})',
                'calculo': f'max = {maior}',
                'resultado': maior
            })

        # TEC-B-13: Menor dígito
        menor = min(int(d) for d in valor_str)
        if 1 <= menor <= 31:
            tecnicas.append({
                'id': 'TEC-B-13',
                'nome': 'Menor Dígito',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'min({valor_str})',
                'calculo': f'min = {menor}',
                'resultado': menor
            })

        # TEC-B-14: Amplitude (max - min)
        amplitude = max(int(d) for d in valor_str) - min(int(d) for d in valor_str)
        if 1 <= amplitude <= 31:
            tecnicas.append({
                'id': 'TEC-B-14',
                'nome': 'Amplitude',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': 'max - min',
                'calculo': f'{max(int(d) for d in valor_str)} - {min(int(d) for d in valor_str)} = {amplitude}',
                'resultado': amplitude
            })

        # TEC-B-15: Quantidade de dígitos
        qtd = len(valor_str)
        if 1 <= qtd <= 31:
            tecnicas.append({
                'id': 'TEC-B-15',
                'nome': 'Quantidade Dígitos',
                'categoria': 'Matemática',
                'campo': campo_nome,
                'formula': f'len({valor})',
                'calculo': f'{valor} tem {qtd} dígitos',
                'resultado': qtd
            })

        return tecnicas

    # ========== CATEGORIA C: COMBINAÇÕES (10 TÉCNICAS) ==========

    def aplicar_tecnicas_combinacoes(self, valor1, nome1, valor2, nome2):
        """10 técnicas combinando dois campos"""
        tecnicas = []
        v1 = int(valor1)
        v2 = int(valor2)

        # TEC-C-01: Soma 1º dígitos
        dig1_v1 = int(str(v1)[0])
        dig1_v2 = int(str(v2)[0])
        soma = dig1_v1 + dig1_v2
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-C-01',
                'nome': 'Soma 1º Dígitos',
                'categoria': 'Combinação',
                'campo': f'{nome1}+{nome2}',
                'formula': f'{dig1_v1} + {dig1_v2}',
                'calculo': f'{dig1_v1} ({nome1}) + {dig1_v2} ({nome2}) = {soma}',
                'resultado': soma
            })

        # TEC-C-02: Diferença 1º dígitos
        diff = abs(dig1_v1 - dig1_v2)
        if 1 <= diff <= 31:
            tecnicas.append({
                'id': 'TEC-C-02',
                'nome': 'Diferença 1º Dígitos',
                'categoria': 'Combinação',
                'campo': f'{nome1}+{nome2}',
                'formula': f'|{dig1_v1} - {dig1_v2}|',
                'calculo': f'|{dig1_v1} - {dig1_v2}| = {diff}',
                'resultado': diff
            })

        # TEC-C-03: Produto 1º dígitos
        produto = dig1_v1 * dig1_v2
        if 1 <= produto <= 31:
            tecnicas.append({
                'id': 'TEC-C-03',
                'nome': 'Produto 1º Dígitos',
                'categoria': 'Combinação',
                'campo': f'{nome1}+{nome2}',
                'formula': f'{dig1_v1} × {dig1_v2}',
                'calculo': f'{dig1_v1} × {dig1_v2} = {produto}',
                'resultado': produto
            })

        # TEC-C-04: Soma raízes digitais
        rd1 = raiz_digital(v1)
        rd2 = raiz_digital(v2)
        soma_rd = rd1 + rd2
        if 1 <= soma_rd <= 31:
            tecnicas.append({
                'id': 'TEC-C-04',
                'nome': 'Soma Raízes Digitais',
                'categoria': 'Combinação',
                'campo': f'{nome1}+{nome2}',
                'formula': f'rd({v1}) + rd({v2})',
                'calculo': f'{rd1} + {rd2} = {soma_rd}',
                'resultado': soma_rd
            })

        # TEC-C-05: XOR 1º dígitos
        xor_dig = dig1_v1 ^ dig1_v2
        if 1 <= xor_dig <= 31:
            tecnicas.append({
                'id': 'TEC-C-05',
                'nome': 'XOR 1º Dígitos',
                'categoria': 'Combinação',
                'campo': f'{nome1}+{nome2}',
                'formula': f'{dig1_v1} XOR {dig1_v2}',
                'calculo': f'{dig1_v1} XOR {dig1_v2} = {xor_dig}',
                'resultado': xor_dig
            })

        # TEC-C-06: Módulo da soma total
        soma_total = v1 + v2
        mod31 = soma_total % 31
        if mod31 == 0:
            mod31 = 31
        tecnicas.append({
            'id': 'TEC-C-06',
            'nome': 'Soma Total mod 31',
            'categoria': 'Combinação',
            'campo': f'{nome1}+{nome2}',
            'formula': f'({v1} + {v2}) % 31',
            'calculo': f'{soma_total} mod 31 = {mod31}',
            'resultado': mod31
        })

        # TEC-C-07: Concatenação primeiros dígitos
        concat = int(str(dig1_v1) + str(dig1_v2))
        if 1 <= concat <= 31:
            tecnicas.append({
                'id': 'TEC-C-07',
                'nome': 'Concatenação 1º Dígitos',
                'categoria': 'Combinação',
                'campo': f'{nome1}+{nome2}',
                'formula': f'concat({dig1_v1}, {dig1_v2})',
                'calculo': f'"{dig1_v1}" + "{dig1_v2}" = {concat}',
                'resultado': concat
            })

        # TEC-C-08: Média aritmética
        media = (v1 + v2) // 2
        if 1 <= media <= 31:
            tecnicas.append({
                'id': 'TEC-C-08',
                'nome': 'Média Aritmética',
                'categoria': 'Combinação',
                'campo': f'{nome1}+{nome2}',
                'formula': f'({v1} + {v2}) ÷ 2',
                'calculo': f'({v1} + {v2}) ÷ 2 = {media}',
                'resultado': media
            })

        # TEC-C-09: v1 ÷ v2 (se divisível)
        if v2 != 0 and v1 % v2 == 0:
            div = v1 // v2
            if 1 <= div <= 31:
                tecnicas.append({
                    'id': 'TEC-C-09',
                    'nome': f'{nome1} ÷ {nome2}',
                    'categoria': 'Combinação',
                    'campo': f'{nome1}+{nome2}',
                    'formula': f'{v1} ÷ {v2}',
                    'calculo': f'{v1} ÷ {v2} = {div}',
                    'resultado': div
                })

        # TEC-C-10: v2 ÷ v1 (se divisível)
        if v1 != 0 and v2 % v1 == 0:
            div = v2 // v1
            if 1 <= div <= 31:
                tecnicas.append({
                    'id': 'TEC-C-10',
                    'nome': f'{nome2} ÷ {nome1}',
                    'categoria': 'Combinação',
                    'campo': f'{nome1}+{nome2}',
                    'formula': f'{v2} ÷ {v1}',
                    'calculo': f'{v2} ÷ {v1} = {div}',
                    'resultado': div
                })

        return tecnicas

    # ========== CATEGORIA D: AVANÇADAS (20 TÉCNICAS) ==========

    def aplicar_tecnicas_avancadas(self, valor, campo_nome):
        """20 técnicas matemáticas avançadas"""
        tecnicas = []
        valor = int(valor)

        # TEC-D-01: Índice Fibonacci
        idx_fib = indice_fibonacci(valor)
        if idx_fib and 1 <= idx_fib <= 31:
            tecnicas.append({
                'id': 'TEC-D-01',
                'nome': 'Índice Fibonacci',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'indice_fib({valor})',
                'calculo': f'{valor} é o {idx_fib}º Fibonacci',
                'resultado': idx_fib
            })

        # TEC-D-02: N-ésimo Fibonacci (se valor pequeno)
        if valor <= 15:
            fib = fibonacci(valor)
            if 1 <= fib <= 31:
                tecnicas.append({
                    'id': 'TEC-D-02',
                    'nome': 'N-ésimo Fibonacci',
                    'categoria': 'Avançada',
                    'campo': campo_nome,
                    'formula': f'fib({valor})',
                    'calculo': f'{valor}º Fibonacci = {fib}',
                    'resultado': fib
                })

        # TEC-D-03: Primo anterior
        primo_ant = primo_anterior(valor)
        if primo_ant and 1 <= primo_ant <= 31:
            tecnicas.append({
                'id': 'TEC-D-03',
                'nome': 'Primo Anterior',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'primo_anterior({valor})',
                'calculo': f'primo < {valor} = {primo_ant}',
                'resultado': primo_ant
            })

        # TEC-D-04: Primo posterior
        primo_post = primo_posterior(valor)
        if primo_post and 1 <= primo_post <= 31:
            tecnicas.append({
                'id': 'TEC-D-04',
                'nome': 'Primo Posterior',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'primo_posterior({valor})',
                'calculo': f'primo > {valor} = {primo_post}',
                'resultado': primo_post
            })

        # TEC-D-05: Índice primo (se é primo)
        if eh_primo(valor):
            primos = [n for n in range(2, 200) if eh_primo(n)]
            if valor in primos:
                idx = primos.index(valor) + 1
                if 1 <= idx <= 31:
                    tecnicas.append({
                        'id': 'TEC-D-05',
                        'nome': 'Índice Primo',
                        'categoria': 'Avançada',
                        'campo': campo_nome,
                        'formula': f'indice_primo({valor})',
                        'calculo': f'{valor} é o {idx}º primo',
                        'resultado': idx
                    })

        # TEC-D-06: Índice triangular
        idx_tri = indice_triangular(valor)
        if idx_tri and 1 <= idx_tri <= 31:
            tecnicas.append({
                'id': 'TEC-D-06',
                'nome': 'Índice Triangular',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'indice_triangular({valor})',
                'calculo': f'{valor} é o {idx_tri}º triangular',
                'resultado': idx_tri
            })

        # TEC-D-07: N-ésimo triangular
        if valor <= 15:
            tri = triangular(valor)
            if 1 <= tri <= 31:
                tecnicas.append({
                    'id': 'TEC-D-07',
                    'nome': 'N-ésimo Triangular',
                    'categoria': 'Avançada',
                    'campo': campo_nome,
                    'formula': f'triangular({valor})',
                    'calculo': f'{valor}º triangular = {tri}',
                    'resultado': tri
                })

        # TEC-D-08: Fatorial mod 31
        if valor <= 10:
            fat = math.factorial(valor)
            fat_mod = fat % 31
            if fat_mod == 0:
                fat_mod = 31
            tecnicas.append({
                'id': 'TEC-D-08',
                'nome': 'Fatorial mod 31',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'{valor}! % 31',
                'calculo': f'{fat} mod 31 = {fat_mod}',
                'resultado': fat_mod
            })

        # TEC-D-09: Potência de 2 mod 31
        if valor <= 20:
            pot = 2 ** valor
            pot_mod = pot % 31
            if pot_mod == 0:
                pot_mod = 31
            tecnicas.append({
                'id': 'TEC-D-09',
                'nome': 'Potência 2 mod 31',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'2^{valor} % 31',
                'calculo': f'{pot} mod 31 = {pot_mod}',
                'resultado': pot_mod
            })

        # TEC-D-10: Checksum (soma mod 9)
        valor_str = str(valor)
        checksum = sum(int(d) for d in valor_str) % 9
        if checksum == 0:
            checksum = 9
        if 1 <= checksum <= 31:
            tecnicas.append({
                'id': 'TEC-D-10',
                'nome': 'Checksum mod 9',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'soma_digitos({valor}) % 9',
                'calculo': f'checksum = {checksum}',
                'resultado': checksum
            })

        # TEC-D-11: Espelhamento base 31
        espelho = 31 - (valor % 31)
        if espelho == 31:
            espelho = 0
        if 1 <= espelho <= 31:
            tecnicas.append({
                'id': 'TEC-D-11',
                'nome': 'Espelhamento 31',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'31 - ({valor} % 31)',
                'calculo': f'espelho = {espelho}',
                'resultado': espelho
            })

        # TEC-D-12: Rotação esquerda (1º vai pro fim)
        valor_str = str(valor)
        if len(valor_str) > 1:
            rotacao = int(valor_str[1:] + valor_str[0])
            if 1 <= rotacao <= 31:
                tecnicas.append({
                    'id': 'TEC-D-12',
                    'nome': 'Rotação Esquerda',
                    'categoria': 'Avançada',
                    'campo': campo_nome,
                    'formula': f'rotate_left({valor})',
                    'calculo': f'{valor} → {rotacao}',
                    'resultado': rotacao
                })

        # TEC-D-13: Rotação direita (último vai pro início)
        if len(valor_str) > 1:
            rotacao = int(valor_str[-1] + valor_str[:-1])
            if 1 <= rotacao <= 31:
                tecnicas.append({
                    'id': 'TEC-D-13',
                    'nome': 'Rotação Direita',
                    'categoria': 'Avançada',
                    'campo': campo_nome,
                    'formula': f'rotate_right({valor})',
                    'calculo': f'{valor} → {rotacao}',
                    'resultado': rotacao
                })

        # TEC-D-14: Ordenação crescente dígitos
        digitos_ordenados = ''.join(sorted(valor_str))
        ordenado = int(digitos_ordenados)
        if 1 <= ordenado <= 31:
            tecnicas.append({
                'id': 'TEC-D-14',
                'nome': 'Dígitos Ordenados Crescente',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'sort_asc({valor})',
                'calculo': f'{valor} → {ordenado}',
                'resultado': ordenado
            })

        # TEC-D-15: Ordenação decrescente dígitos
        digitos_ordenados_desc = ''.join(sorted(valor_str, reverse=True))
        ordenado_desc = int(digitos_ordenados_desc)
        if 1 <= ordenado_desc <= 31:
            tecnicas.append({
                'id': 'TEC-D-15',
                'nome': 'Dígitos Ordenados Decrescente',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'sort_desc({valor})',
                'calculo': f'{valor} → {ordenado_desc}',
                'resultado': ordenado_desc
            })

        # TEC-D-16: Persistência multiplicativa
        temp = valor
        steps = 0
        while temp >= 10 and steps < 10:
            produto = 1
            for d in str(temp):
                produto *= int(d)
            temp = produto
            steps += 1
        if 1 <= steps <= 31:
            tecnicas.append({
                'id': 'TEC-D-16',
                'nome': 'Persistência Multiplicativa',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'persist_mult({valor})',
                'calculo': f'{steps} iterações',
                'resultado': steps
            })

        # TEC-D-17: Soma de quadrados dos dígitos
        soma_quad = sum(int(d)**2 for d in valor_str)
        if 1 <= soma_quad <= 31:
            tecnicas.append({
                'id': 'TEC-D-17',
                'nome': 'Soma Quadrados Dígitos',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'Σ(d²)',
                'calculo': f'{soma_quad}',
                'resultado': soma_quad
            })

        # TEC-D-18: Diferença max-min consecutivos
        if len(valor_str) > 1:
            diffs = []
            for i in range(len(valor_str) - 1):
                diff = abs(int(valor_str[i]) - int(valor_str[i+1]))
                diffs.append(diff)
            max_diff = max(diffs)
            if 1 <= max_diff <= 31:
                tecnicas.append({
                    'id': 'TEC-D-18',
                    'nome': 'Max Diferença Consecutivos',
                    'categoria': 'Avançada',
                    'campo': campo_nome,
                    'formula': 'max(|d[i] - d[i+1]|)',
                    'calculo': f'max_diff = {max_diff}',
                    'resultado': max_diff
                })

        # TEC-D-19: Contagem dígitos pares
        pares = sum(1 for d in valor_str if int(d) % 2 == 0)
        if 1 <= pares <= 31:
            tecnicas.append({
                'id': 'TEC-D-19',
                'nome': 'Quantidade Dígitos Pares',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'count_pares({valor})',
                'calculo': f'{pares} dígitos pares',
                'resultado': pares
            })

        # TEC-D-20: Contagem dígitos ímpares
        impares = sum(1 for d in valor_str if int(d) % 2 == 1)
        if 1 <= impares <= 31:
            tecnicas.append({
                'id': 'TEC-D-20',
                'nome': 'Quantidade Dígitos Ímpares',
                'categoria': 'Avançada',
                'campo': campo_nome,
                'formula': f'count_impares({valor})',
                'calculo': f'{impares} dígitos ímpares',
                'resultado': impares
            })

        return tecnicas

    # ========== CATEGORIA E: DATA (10 TÉCNICAS) ==========

    def aplicar_tecnicas_data(self, data_str):
        """10 técnicas específicas para datas"""
        tecnicas = []

        # Parsear data (aceita DD/MM/YYYY ou YYYY-MM-DD)
        match_br = re.match(r'(\d{2})/(\d{2})/(\d{4})', data_str)
        match_iso = re.match(r'(\d{4})-(\d{2})-(\d{2})', data_str)

        if match_br:
            dia, mes, ano = int(match_br.group(1)), int(match_br.group(2)), int(match_br.group(3))
        elif match_iso:
            ano, mes, dia = int(match_iso.group(1)), int(match_iso.group(2)), int(match_iso.group(3))
        else:
            return tecnicas

        # TEC-E-01: Dia do mês
        if 1 <= dia <= 31:
            tecnicas.append({
                'id': 'TEC-E-01',
                'nome': 'Dia do Mês',
                'categoria': 'Data',
                'campo': 'DATA',
                'formula': f'extrair_dia({data_str})',
                'calculo': f'{data_str} → dia {dia}',
                'resultado': dia
            })

        # TEC-E-02: Mês
        if 1 <= mes <= 31:
            tecnicas.append({
                'id': 'TEC-E-02',
                'nome': 'Mês',
                'categoria': 'Data',
                'campo': 'DATA',
                'formula': f'extrair_mes({data_str})',
                'calculo': f'{data_str} → mês {mes}',
                'resultado': mes
            })

        # TEC-E-03: Ano (2 dígitos)
        ano_2dig = ano % 100
        if 1 <= ano_2dig <= 31:
            tecnicas.append({
                'id': 'TEC-E-03',
                'nome': 'Ano (2 dígitos)',
                'categoria': 'Data',
                'campo': 'DATA',
                'formula': f'{ano} % 100',
                'calculo': f'{ano} → {ano_2dig}',
                'resultado': ano_2dig
            })

        # TEC-E-04: Dia + Mês
        soma = dia + mes
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-E-04',
                'nome': 'Dia + Mês',
                'categoria': 'Data',
                'campo': 'DATA',
                'formula': f'{dia} + {mes}',
                'calculo': f'{dia} + {mes} = {soma}',
                'resultado': soma
            })

        # TEC-E-05: Dia - Mês (absoluto)
        diff = abs(dia - mes)
        if 1 <= diff <= 31:
            tecnicas.append({
                'id': 'TEC-E-05',
                'nome': 'Dia - Mês',
                'categoria': 'Data',
                'campo': 'DATA',
                'formula': f'|{dia} - {mes}|',
                'calculo': f'|{dia} - {mes}| = {diff}',
                'resultado': diff
            })

        # TEC-E-06: Dia × 2
        resultado = dia * 2
        if 1 <= resultado <= 31:
            tecnicas.append({
                'id': 'TEC-E-06',
                'nome': 'Dia × 2',
                'categoria': 'Data',
                'campo': 'DATA',
                'formula': f'{dia} × 2',
                'calculo': f'{dia} × 2 = {resultado}',
                'resultado': resultado
            })

        # TEC-E-07: Dia ÷ 2
        if dia % 2 == 0:
            resultado = dia // 2
            if 1 <= resultado <= 31:
                tecnicas.append({
                    'id': 'TEC-E-07',
                    'nome': 'Dia ÷ 2',
                    'categoria': 'Data',
                    'campo': 'DATA',
                    'formula': f'{dia} ÷ 2',
                    'calculo': f'{dia} ÷ 2 = {resultado}',
                    'resultado': resultado
                })

        # TEC-E-08: Mês × 2
        resultado = mes * 2
        if 1 <= resultado <= 31:
            tecnicas.append({
                'id': 'TEC-E-08',
                'nome': 'Mês × 2',
                'categoria': 'Data',
                'campo': 'DATA',
                'formula': f'{mes} × 2',
                'calculo': f'{mes} × 2 = {resultado}',
                'resultado': resultado
            })

        # TEC-E-09: Dia mod 31
        mod = dia % 31
        if mod == 0:
            mod = 31
        tecnicas.append({
            'id': 'TEC-E-09',
            'nome': 'Dia mod 31',
            'categoria': 'Data',
            'campo': 'DATA',
            'formula': f'{dia} % 31',
            'calculo': f'{dia} mod 31 = {mod}',
            'resultado': mod
        })

        # TEC-E-10: Raiz digital da data completa (DDMMYYYY)
        data_num = int(f'{dia:02d}{mes:02d}{ano}')
        rd = raiz_digital(data_num)
        if 1 <= rd <= 31:
            tecnicas.append({
                'id': 'TEC-E-10',
                'nome': 'Raiz Digital Data',
                'categoria': 'Data',
                'campo': 'DATA',
                'formula': f'raiz_digital({data_num})',
                'calculo': f'raiz_digital({data_num}) = {rd}',
                'resultado': rd
            })

        return tecnicas

    # ========== CATEGORIA L: ESPELHAMENTO UNIVERSAL 6↔️9 ==========

    def aplicar_espelhamento_universal(self, tecnicas_existentes):
        """
        Aplica espelhamento 6 ↔️ 9 em TODAS as técnicas
        Para cada técnica que retornou 6 ou 9, cria versão espelhada
        """
        tecnicas_espelhadas = []

        for tec in tecnicas_existentes:
            resultado = tec['resultado']
            espelhado = self.aplicar_espelhamento_69(resultado)

            if espelhado:
                # Cria nova técnica com resultado espelhado
                tec_espelhada = {
                    'id': f"{tec['id']}-L",  # Ex: TEC-A-01-L
                    'nome': f"{tec['nome']} (Espelhado 6↔️9)",
                    'categoria': 'Espelhamento Universal',
                    'campo': tec['campo'],
                    'formula': f"espelhar({tec['formula']})",
                    'calculo': f"{tec['calculo']} → espelhado {resultado}↔️{espelhado}",
                    'resultado': espelhado
                }
                tecnicas_espelhadas.append(tec_espelhada)

        return tecnicas_espelhadas

    # ========== MÉTODO PRINCIPAL DE ANÁLISE ==========

    def analisar_concurso(self, numero_concurso):
        """
        MÉTODO PRINCIPAL - Detetive Automático
        Aplica TODAS as ~150 técnicas e retorna resultados
        """
        import time
        inicio = time.time()

        # Buscar dados do banco
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT concurso,
                   posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7,
                   numero_concurso_proximo, data_proximo_concurso, valor_estimado_proximo_concurso
            FROM sorteios
            WHERE concurso = ?
        ''', (numero_concurso,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {
                'sucesso': False,
                'erro': f'Concurso {numero_concurso} não encontrado no banco de dados'
            }

        # Extrair dados
        concurso = row[0]
        dezenas_sorteadas = [row[i] for i in range(1, 8)]
        numero_proximo = row[8]
        data_proxima = row[9]
        premio_estimado = row[10]

        # Validar campos gatilho
        if not all([numero_proximo, data_proxima, premio_estimado]):
            return {
                'sucesso': False,
                'erro': 'Campos gatilho (número_concurso_proximo, data_proximo_concurso, valor_estimado_proximo_concurso) não disponíveis'
            }

        # ========== APLICAR TODAS AS TÉCNICAS ==========

        todas_tecnicas = []

        # CONCURSO PRÓXIMO
        todas_tecnicas.extend(self.aplicar_tecnicas_basicas(numero_proximo, 'CONCURSO'))
        todas_tecnicas.extend(self.aplicar_tecnicas_matematicas(numero_proximo, 'CONCURSO'))
        todas_tecnicas.extend(self.aplicar_tecnicas_avancadas(numero_proximo, 'CONCURSO'))

        # PRÊMIO ESTIMADO
        todas_tecnicas.extend(self.aplicar_tecnicas_basicas(premio_estimado, 'PRÊMIO'))
        todas_tecnicas.extend(self.aplicar_tecnicas_matematicas(premio_estimado, 'PRÊMIO'))
        todas_tecnicas.extend(self.aplicar_tecnicas_avancadas(premio_estimado, 'PRÊMIO'))

        # DÍGITOS DO PRÊMIO (NOVA CATEGORIA K)
        todas_tecnicas.extend(self.aplicar_tecnicas_digitos_premio(premio_estimado))

        # DATA
        todas_tecnicas.extend(self.aplicar_tecnicas_data(data_proxima))

        # PARTES DO ANO (NOVA CATEGORIA J)
        todas_tecnicas.extend(self.aplicar_tecnicas_partes_ano(data_proxima))

        # COMBINAÇÕES (CONCURSO + PRÊMIO)
        todas_tecnicas.extend(self.aplicar_tecnicas_combinacoes(
            numero_proximo, 'CONCURSO', premio_estimado, 'PRÊMIO'
        ))

        # ESPELHAMENTO UNIVERSAL 6↔️9 (NOVA CATEGORIA L)
        tecnicas_espelhadas = self.aplicar_espelhamento_universal(todas_tecnicas)
        todas_tecnicas.extend(tecnicas_espelhadas)

        # ========== ANALISAR CADA DEZENA ==========

        analise_por_dezena = []
        estatisticas_categorias = defaultdict(int)
        estatisticas_campos = defaultdict(int)
        total_acertos = 0
        dezenas_com_tecnica = 0
        dezenas_sem_tecnica = []

        for posicao, dezena in enumerate(dezenas_sorteadas, 1):
            # Filtrar técnicas que acertaram esta dezena
            tecnicas_acertaram = [t for t in todas_tecnicas if t['resultado'] == dezena]

            # Estatísticas
            if tecnicas_acertaram:
                dezenas_com_tecnica += 1
                for tec in tecnicas_acertaram:
                    estatisticas_categorias[tec['categoria']] += 1
                    estatisticas_campos[tec['campo']] += 1
                    total_acertos += 1
            else:
                dezenas_sem_tecnica.append(dezena)

            analise_por_dezena.append({
                'posicao': posicao,
                'dezena': dezena,
                'total_tecnicas_encontradas': len(tecnicas_acertaram),
                'tecnicas': tecnicas_acertaram
            })

        # Categoria e campo mais usados
        categoria_mais_usada = max(estatisticas_categorias.items(), key=lambda x: x[1])[0] if estatisticas_categorias else 'N/A'
        campo_mais_usado = max(estatisticas_campos.items(), key=lambda x: x[1])[0] if estatisticas_campos else 'N/A'

        # Tempo de processamento
        tempo_ms = int((time.time() - inicio) * 1000)

        # ========== RETORNAR RESULTADO COMPLETO ==========

        return {
            'sucesso': True,
            'concurso_analisado': concurso,
            'dados_gatilho': {
                'numero_concurso_proximo': numero_proximo,
                'data_proximo_concurso': data_proxima,
                'valor_estimado_proximo_concurso': premio_estimado
            },
            'dezenas_sorteadas': dezenas_sorteadas,
            'resumo': {
                'total_dezenas': 7,
                'dezenas_com_tecnica': dezenas_com_tecnica,
                'dezenas_sem_tecnica': 7 - dezenas_com_tecnica,
                'lista_dezenas_sem_tecnica': dezenas_sem_tecnica,
                'total_tecnicas_testadas': len(todas_tecnicas),
                'total_tecnicas_acertaram': total_acertos,
                'percentual_cobertura': round((dezenas_com_tecnica / 7) * 100, 2),
                'percentual_eficacia': round((total_acertos / len(todas_tecnicas)) * 100, 2) if todas_tecnicas else 0,
                'categoria_mais_usada': categoria_mais_usada,
                'campo_mais_usado': campo_mais_usado,
                'tempo_processamento_ms': tempo_ms
            },
            'analise_por_dezena': analise_por_dezena,
            'estatisticas_categorias': dict(estatisticas_categorias),
            'estatisticas_campos': dict(estatisticas_campos)
        }


# ========== FUNÇÃO PÚBLICA ==========

def analisar_concurso_profundo(numero_concurso):
    """
    FUNÇÃO PÚBLICA para uso nas rotas Flask

    Uso:
        from services.analise_profunda_service_EXPANDIDO import analisar_concurso_profundo
        resultado = analisar_concurso_profundo(1138)
    """
    analisador = AnalisadorProfundo()
    return analisador.analisar_concurso(numero_concurso)


# ========== TESTE STANDALONE ==========

if __name__ == '__main__':
    print("🔍 Testando Sistema de Análise Profunda EXPANDIDO (~150 técnicas)")
    print("=" * 80)

    # Testar com concurso 1138
    resultado = analisar_concurso_profundo(1138)

    if resultado['sucesso']:
        print(f"\n✅ Concurso {resultado['concurso_analisado']} analisado com sucesso!")
        print(f"\n📊 RESUMO:")
        print(f"   Total de técnicas testadas: {resultado['resumo']['total_tecnicas_testadas']}")
        print(f"   Técnicas que acertaram: {resultado['resumo']['total_tecnicas_acertaram']}")
        print(f"   Cobertura: {resultado['resumo']['percentual_cobertura']}%")
        print(f"   Tempo: {resultado['resumo']['tempo_processamento_ms']}ms")

        print(f"\n🎯 DEZENAS COM TÉCNICAS:")
        for analise in resultado['analise_por_dezena']:
            if analise['total_tecnicas_encontradas'] > 0:
                print(f"   Dezena {analise['dezena']}: {analise['total_tecnicas_encontradas']} técnica(s)")
    else:
        print(f"\n❌ Erro: {resultado['erro']}")

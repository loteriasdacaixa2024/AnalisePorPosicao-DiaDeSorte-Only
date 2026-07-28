"""
Serviço de Análise Profunda de Técnicas
Implementa 50+ técnicas matemáticas para descobrir padrões em concursos da loteria
"""

import sqlite3
import math
import re
from datetime import datetime
from collections import defaultdict


class AnalisadorProfundo:
    """Analisador profundo com 50+ técnicas matemáticas"""
   
   # CAMINHO CORRETO PARA O  BANCO
    def __init__(self, db_path='analise_por_posicao.db'):
        """
        Inicializa o analisador profundo

        Args:
            db_path: Caminho para o banco de dados SQLite (padrão: analise_por_posicao.db na raiz)
        """
        self.db_path = db_path
        self.tecnicas_cache = {}

    # ========================================================================
    # UTILITÁRIOS MATEMÁTICOS
    # ========================================================================

    def extrair_digitos(self, numero):
        """Extrai lista de dígitos de um número"""
        return [int(d) for d in str(abs(int(numero)))]

    def eh_primo(self, n):
        """Verifica se número é primo"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

    def proximo_primo(self, n):
        """Encontra o próximo número primo"""
        n += 1
        while not self.eh_primo(n):
            n += 1
        return n

    def fibonacci(self, n):
        """Calcula n-ésimo número de Fibonacci"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def numero_triangular(self, n):
        """Calcula número triangular: T(n) = n*(n+1)/2"""
        return n * (n + 1) // 2

    def digital_root(self, n):
        """Redução iterativa: soma dígitos até ficar 1 dígito"""
        while n >= 10:
            n = sum(self.extrair_digitos(n))
        return n

    def inverter_numero(self, n):
        """Inverte os dígitos do número"""
        return int(str(abs(int(n)))[::-1])

    # ========================================================================
    # CATEGORIA A: TÉCNICAS BÁSICAS (ID: TEC-A-XX)
    # ========================================================================

    def aplicar_tecnicas_basicas(self, valor, campo_nome):
        """10 técnicas básicas de extração"""
        tecnicas = []
        digitos = self.extrair_digitos(valor)

        if not digitos:
            return tecnicas

        # A01: Primeiro dígito
        if 1 <= digitos[0] <= 31:
            tecnicas.append({
                'id': 'TEC-A-01',
                'nome': 'Primeiro Dígito',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'primeiro_digito({valor})',
                'calculo': f'{valor} → {digitos[0]}',
                'resultado': digitos[0]
            })

        # A02: Último dígito
        if len(digitos) > 0 and 1 <= digitos[-1] <= 31:
            tecnicas.append({
                'id': 'TEC-A-02',
                'nome': 'Último Dígito',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'ultimo_digito({valor})',
                'calculo': f'{valor} → {digitos[-1]}',
                'resultado': digitos[-1]
            })

        # A03: Soma de dígitos
        soma = sum(digitos)
        if 1 <= soma <= 31:
            tecnicas.append({
                'id': 'TEC-A-03',
                'nome': 'Soma dos Dígitos',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'soma_digitos({valor})',
                'calculo': f'{"+".join(map(str, digitos))} = {soma}',
                'resultado': soma
            })

        # A04: Produto de dígitos (se não zero)
        if 0 not in digitos:
            produto = 1
            for d in digitos:
                produto *= d
            if 1 <= produto <= 31:
                tecnicas.append({
                    'id': 'TEC-A-04',
                    'nome': 'Produto dos Dígitos',
                    'categoria': 'Básica',
                    'campo': campo_nome,
                    'formula': f'produto_digitos({valor})',
                    'calculo': f'{"×".join(map(str, digitos))} = {produto}',
                    'resultado': produto
                })

        # A05: Primeiros 2 dígitos
        if len(digitos) >= 2:
            dois_dig = int(str(digitos[0]) + str(digitos[1]))
            if 1 <= dois_dig <= 31:
                tecnicas.append({
                    'id': 'TEC-A-05',
                    'nome': 'Primeiros 2 Dígitos',
                    'categoria': 'Básica',
                    'campo': campo_nome,
                    'formula': f'primeiros_2_digitos({valor})',
                    'calculo': f'{valor} → {dois_dig}',
                    'resultado': dois_dig
                })

        # A06: Últimos 2 dígitos
        if len(digitos) >= 2:
            dois_dig = int(str(digitos[-2]) + str(digitos[-1]))
            if 1 <= dois_dig <= 31:
                tecnicas.append({
                    'id': 'TEC-A-06',
                    'nome': 'Últimos 2 Dígitos',
                    'categoria': 'Básica',
                    'campo': campo_nome,
                    'formula': f'ultimos_2_digitos({valor})',
                    'calculo': f'{valor} → {dois_dig}',
                    'resultado': dois_dig
                })

        # A07: Dígito do meio (se ímpar quantidade)
        if len(digitos) % 2 == 1:
            meio = digitos[len(digitos) // 2]
            if 1 <= meio <= 31:
                tecnicas.append({
                    'id': 'TEC-A-07',
                    'nome': 'Dígito Central',
                    'categoria': 'Básica',
                    'campo': campo_nome,
                    'formula': f'digito_central({valor})',
                    'calculo': f'{valor} → posição {len(digitos)//2} → {meio}',
                    'resultado': meio
                })

        # A08: Inversão simples
        invertido = self.inverter_numero(valor)
        if 1 <= invertido <= 31:
            tecnicas.append({
                'id': 'TEC-A-08',
                'nome': 'Inversão de Dígitos',
                'categoria': 'Inversão',
                'campo': campo_nome,
                'formula': f'inverter({valor})',
                'calculo': f'{valor} → invertido = {invertido}',
                'resultado': invertido
            })

        # A09: Módulo 31
        mod = valor % 31
        if 1 <= mod <= 31:
            tecnicas.append({
                'id': 'TEC-A-09',
                'nome': 'Módulo 31',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'{valor} % 31',
                'calculo': f'{valor} mod 31 = {mod}',
                'resultado': mod
            })

        # A10: Digital Root
        root = self.digital_root(valor)
        if 1 <= root <= 31:
            tecnicas.append({
                'id': 'TEC-A-10',
                'nome': 'Raiz Digital',
                'categoria': 'Básica',
                'campo': campo_nome,
                'formula': f'digital_root({valor})',
                'calculo': f'Redução iterativa de {valor} = {root}',
                'resultado': root
            })

        return tecnicas

    # Continua no próximo bloco devido ao limite de espaço...

    def analisar_concurso(self, numero_concurso):
        """
        Analisa um concurso específico e retorna todas as técnicas encontradas

        Args:
            numero_concurso: Número do concurso a analisar

        Returns:
            dict com análise completa dezena por dezena
        """
        # Buscar dados do banco
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                concurso,
                posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7,
                numero_concurso_proximo,
                data_proximo_concurso,
                valor_estimado_proximo_concurso
            FROM sorteios
            WHERE concurso = ?
        ''', (numero_concurso,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {'sucesso': False, 'erro': f'Concurso {numero_concurso} não encontrado'}

        # Extrair dados
        dezenas_sorteadas = [
            row['posicao_1'], row['posicao_2'], row['posicao_3'], row['posicao_4'],
            row['posicao_5'], row['posicao_6'], row['posicao_7']
        ]

        num_prox = row['numero_concurso_proximo']
        data_prox = row['data_proximo_concurso']
        valor_prox = row['valor_estimado_proximo_concurso']

        # Analisar cada dezena
        analise_dezenas = {}

        for idx, dezena in enumerate(dezenas_sorteadas, 1):
            tecnicas_encontradas = []

            # Aplicar técnicas básicas em todos os campos
            if num_prox:
                tecnicas_encontradas.extend(self.aplicar_tecnicas_basicas(num_prox, 'CONCURSO'))

            if valor_prox:
                tecnicas_encontradas.extend(self.aplicar_tecnicas_basicas(int(valor_prox), 'PRÊMIO'))

            # Filtrar apenas técnicas que geraram a dezena correta
            tecnicas_corretas = [t for t in tecnicas_encontradas if t['resultado'] == dezena]

            analise_dezenas[f'dezena_{dezena}'] = {
                'dezena': dezena,
                'posicao': idx,
                'tecnicas_encontradas': len(tecnicas_corretas),
                'tecnicas': tecnicas_corretas
            }

        return {
            'sucesso': True,
            'concurso': numero_concurso,
            'dados_gatilho': {
                'numero_concurso_proximo': num_prox,
                'data_proximo_concurso': data_prox,
                'valor_estimado_proximo_concurso': valor_prox
            },
            'dezenas_sorteadas': dezenas_sorteadas,
            'analise_por_dezena': analise_dezenas
        }

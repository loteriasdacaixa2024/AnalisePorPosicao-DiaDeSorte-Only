"""
Serviço de Descoberta de Técnicas - Engenharia Reversa
Analisa concursos passados e descobre técnicas/padrões que conectam
os 3 campos do banco (número, data, prêmio) com as dezenas sorteadas.
"""

import sqlite3
from datetime import datetime
import re
import json
from collections import defaultdict
import os


class DescobridorTecnicas:
    """Descobre técnicas analisando resultados passados da loteria Dia de Sorte"""

    # CAMINHO CORRETO PARA O  BANCO
    def __init__(self, db_path='analise_por_posicao.db'):
        """
        Inicializa o descobridor de técnicas

        Args:
            db_path: Caminho para o banco de dados SQLite (padrão: analise_por_posicao.db na raiz)
        """
        self.db_path = db_path
        self.tecnicas_descobertas = []

    def buscar_dados_concurso(self, numero_concurso):
        """
        Busca dados de um concurso específico no banco de dados

        Args:
            numero_concurso: Número do concurso a buscar

        Returns:
            dict com dados do concurso ou None se não encontrado
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Buscar dados do concurso na tabela SORTEIOS
            cursor.execute('''
                SELECT
                    concurso,
                    data_sorteio,
                    posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7,
                    numero_concurso_proximo,
                    data_proximo_concurso,
                    valor_estimado_proximo_concurso,
                    mes_sorte
                FROM sorteios
                WHERE concurso = ?
            ''', (numero_concurso,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            # Converter para dict compatível com o formato esperado
            return {
                'numero': row['concurso'],
                'dataSorteio': row['data_sorteio'],
                'listaDezenas': [
                    str(row['posicao_1']).zfill(2),
                    str(row['posicao_2']).zfill(2),
                    str(row['posicao_3']).zfill(2),
                    str(row['posicao_4']).zfill(2),
                    str(row['posicao_5']).zfill(2),
                    str(row['posicao_6']).zfill(2),
                    str(row['posicao_7']).zfill(2)
                ],
                'numeroConcursoProximo': row['numero_concurso_proximo'],
                'dataProximoConcurso': row['data_proximo_concurso'],
                'valorEstimadoProximoConcurso': row['valor_estimado_proximo_concurso'],
                'mesSorte': row['mes_sorte']
            }

        except Exception as e:
            print(f"Erro ao buscar concurso {numero_concurso} no banco: {e}")
            return None

    def extrair_numero_concurso_proximo(self, dados):
        """Extrai numeroConcursoProximo dos dados"""
        return dados.get('numeroConcursoProximo', None)

    def extrair_data_proximo_concurso(self, dados):
        """Extrai dataProximoConcurso dos dados"""
        return dados.get('dataProximoConcurso', None)

    def extrair_valor_estimado_proximo(self, dados):
        """Extrai valorEstimadoProximoConcurso dos dados"""
        return dados.get('valorEstimadoProximoConcurso', None)

    def extrair_dezenas_sorteadas(self, dados):
        """Extrai as dezenas sorteadas do concurso"""
        dezenas_str = dados.get('listaDezenas', [])
        return [int(d) for d in dezenas_str]

    def gerar_id_tecnica(self, index):
        """Gera ID único para a técnica"""
        return f"TEC-{str(index).zfill(3)}"

    def aplicar_tecnicas_numero_concurso(self, numero_concurso):
        """Aplica todas as técnicas possíveis ao número do concurso"""
        tecnicas = []

        if not numero_concurso:
            return tecnicas

        num_str = str(numero_concurso)

        # TEC: Primeiros 2 dígitos
        if len(num_str) >= 2:
            valor = int(num_str[:2])
            if 1 <= valor <= 31:
                tecnicas.append({
                    'apelido': 'Primeiros 2 Dígitos do Concurso',
                    'campo': 'numeroConcursoProximo',
                    'formula': 'primeiros_2_digitos(numero)',
                    'valor_gerado': valor
                })

        # TEC: Últimos 2 dígitos
        if len(num_str) >= 2:
            valor = int(num_str[-2:])
            if 1 <= valor <= 31:
                tecnicas.append({
                    'apelido': 'Últimos 2 Dígitos do Concurso',
                    'campo': 'numeroConcursoProximo',
                    'formula': 'ultimos_2_digitos(numero)',
                    'valor_gerado': valor
                })

        # TEC: Soma dos dígitos
        soma = sum(int(d) for d in num_str)
        if 1 <= soma <= 31:
            tecnicas.append({
                'apelido': 'Soma dos Dígitos do Concurso',
                'campo': 'numeroConcursoProximo',
                'formula': 'soma_digitos(numero)',
                'valor_gerado': soma
            })

        # TEC: Produto dos dígitos
        produto = 1
        for d in num_str:
            produto *= int(d)
        if 1 <= produto <= 31:
            tecnicas.append({
                'apelido': 'Produto dos Dígitos do Concurso',
                'campo': 'numeroConcursoProximo',
                'formula': 'produto_digitos(numero)',
                'valor_gerado': produto
            })

        # TEC: Cada dígito individualmente
        for i, digito in enumerate(num_str):
            valor = int(digito)
            if 1 <= valor <= 31:
                tecnicas.append({
                    'apelido': f'Dígito {i+1} do Concurso',
                    'campo': 'numeroConcursoProximo',
                    'formula': f'digito_{i+1}(numero)',
                    'valor_gerado': valor
                })

        return tecnicas

    def aplicar_tecnicas_data(self, data_str):
        """Aplica todas as técnicas possíveis à data do concurso"""
        tecnicas = []

        if not data_str:
            return tecnicas

        try:
            # Formato: DD/MM/YYYY
            match = re.match(r'(\d{2})/(\d{2})/(\d{4})', data_str)
            if not match:
                return tecnicas

            dia = int(match.group(1))
            mes = int(match.group(2))
            ano = int(match.group(3))
            ano_2dig = ano % 100

            # TEC: Dia do mês
            if 1 <= dia <= 31:
                tecnicas.append({
                    'apelido': 'Dia do Mês',
                    'campo': 'dataProximoConcurso',
                    'formula': 'extrair_dia(data)',
                    'valor_gerado': dia
                })

            # TEC: Mês
            if 1 <= mes <= 31:
                tecnicas.append({
                    'apelido': 'Mês do Sorteio',
                    'campo': 'dataProximoConcurso',
                    'formula': 'extrair_mes(data)',
                    'valor_gerado': mes
                })

            # TEC: Ano (últimos 2 dígitos)
            if 1 <= ano_2dig <= 31:
                tecnicas.append({
                    'apelido': 'Ano (2 últimos dígitos)',
                    'campo': 'dataProximoConcurso',
                    'formula': 'ano_2_digitos(data)',
                    'valor_gerado': ano_2dig
                })

            # TEC: Dia + Mês
            soma_dia_mes = dia + mes
            if 1 <= soma_dia_mes <= 31:
                tecnicas.append({
                    'apelido': 'Dia + Mês',
                    'campo': 'dataProximoConcurso',
                    'formula': 'dia + mes',
                    'valor_gerado': soma_dia_mes
                })

            # TEC: Dia - Mês (se positivo)
            if dia > mes:
                diff = dia - mes
                if 1 <= diff <= 31:
                    tecnicas.append({
                        'apelido': 'Dia - Mês',
                        'campo': 'dataProximoConcurso',
                        'formula': 'dia - mes',
                        'valor_gerado': diff
                    })

            # TEC: Dia ÷ 2
            if dia % 2 == 0:
                metade = dia // 2
                if 1 <= metade <= 31:
                    tecnicas.append({
                        'apelido': 'Dia Dividido por 2',
                        'campo': 'dataProximoConcurso',
                        'formula': 'dia / 2',
                        'valor_gerado': metade
                    })

            # TEC: Dia × 2
            dobro = dia * 2
            if 1 <= dobro <= 31:
                tecnicas.append({
                    'apelido': 'Dia Multiplicado por 2',
                    'campo': 'dataProximoConcurso',
                    'formula': 'dia * 2',
                    'valor_gerado': dobro
                })

        except Exception as e:
            print(f"Erro ao processar data {data_str}: {e}")

        return tecnicas

    def aplicar_tecnicas_premio(self, valor_premio):
        """Aplica todas as técnicas possíveis ao valor do prêmio"""
        tecnicas = []

        if not valor_premio:
            return tecnicas

        # Remove formatação monetária e extrai número
        valor_str = str(valor_premio).replace('R$', '').replace('.', '').replace(',', '').strip()

        if not valor_str or not valor_str.isdigit():
            return tecnicas

        # TEC: Primeiro dígito
        primeiro_dig = int(valor_str[0])
        if 1 <= primeiro_dig <= 31:
            tecnicas.append({
                'apelido': 'Primeiro Dígito do Prêmio',
                'campo': 'valorEstimadoProximoConcurso',
                'formula': 'primeiro_digito(premio)',
                'valor_gerado': primeiro_dig
            })

        # TEC: Primeiro dígito ÷ 2
        if primeiro_dig >= 2:
            metade = primeiro_dig // 2
            if 1 <= metade <= 31:
                tecnicas.append({
                    'apelido': 'Primeiro Dígito do Prêmio ÷ 2',
                    'campo': 'valorEstimadoProximoConcurso',
                    'formula': 'primeiro_digito(premio) / 2',
                    'valor_gerado': metade
                })

        # TEC: Primeiro dígito ÷ 3
        if primeiro_dig >= 3:
            terco = primeiro_dig // 3
            if 1 <= terco <= 31:
                tecnicas.append({
                    'apelido': 'Primeiro Dígito do Prêmio ÷ 3',
                    'campo': 'valorEstimadoProximoConcurso',
                    'formula': 'primeiro_digito(premio) / 3',
                    'valor_gerado': terco
                })

        # TEC: Primeiro dígito × 2
        dobro = primeiro_dig * 2
        if 1 <= dobro <= 31:
            tecnicas.append({
                'apelido': 'Primeiro Dígito do Prêmio × 2',
                'campo': 'valorEstimadoProximoConcurso',
                'formula': 'primeiro_digito(premio) * 2',
                'valor_gerado': dobro
            })

        # TEC: Primeiro dígito × 3
        triplo = primeiro_dig * 3
        if 1 <= triplo <= 31:
            tecnicas.append({
                'apelido': 'Primeiro Dígito do Prêmio × 3',
                'campo': 'valorEstimadoProximoConcurso',
                'formula': 'primeiro_digito(premio) * 3',
                'valor_gerado': triplo
            })

        # TEC: Quantidade de zeros
        qtd_zeros = valor_str.count('0')
        if 1 <= qtd_zeros <= 31:
            tecnicas.append({
                'apelido': 'Quantidade de Zeros no Prêmio',
                'campo': 'valorEstimadoProximoConcurso',
                'formula': 'contar_zeros(premio)',
                'valor_gerado': qtd_zeros
            })

        # TEC: Soma de todos os dígitos
        soma = sum(int(d) for d in valor_str if d.isdigit())
        if 1 <= soma <= 31:
            tecnicas.append({
                'apelido': 'Soma dos Dígitos do Prêmio',
                'campo': 'valorEstimadoProximoConcurso',
                'formula': 'soma_digitos(premio)',
                'valor_gerado': soma
            })

        # TEC: Primeiros 2 dígitos
        if len(valor_str) >= 2:
            dois_dig = int(valor_str[:2])
            if 1 <= dois_dig <= 31:
                tecnicas.append({
                    'apelido': 'Primeiros 2 Dígitos do Prêmio',
                    'campo': 'valorEstimadoProximoConcurso',
                    'formula': 'primeiros_2_digitos(premio)',
                    'valor_gerado': dois_dig
                })

        return tecnicas

    def descobrir_tecnicas_concurso(self, numero_concurso):
        """
        Descobre técnicas analisando um concurso específico

        Args:
            numero_concurso: Número do concurso a analisar

        Returns:
            dict com técnicas descobertas e estatísticas
        """
        # Buscar dados do concurso
        dados = self.buscar_dados_concurso(numero_concurso)

        if not dados:
            return {
                'sucesso': False,
                'erro': f'Não foi possível buscar dados do concurso {numero_concurso}'
            }

        # Extrair os 3 campos gatilho
        num_concurso_prox = self.extrair_numero_concurso_proximo(dados)
        data_prox = self.extrair_data_proximo_concurso(dados)
        valor_prox = self.extrair_valor_estimado_proximo(dados)

        # Extrair dezenas sorteadas
        dezenas_sorteadas = self.extrair_dezenas_sorteadas(dados)

        # Aplicar todas as técnicas possíveis
        tecnicas_numero = self.aplicar_tecnicas_numero_concurso(num_concurso_prox)
        tecnicas_data = self.aplicar_tecnicas_data(data_prox)
        tecnicas_premio = self.aplicar_tecnicas_premio(valor_prox)

        # Juntar todas as técnicas
        todas_tecnicas = tecnicas_numero + tecnicas_data + tecnicas_premio

        # Verificar quais técnicas acertaram
        tecnicas_acertadas = []
        index = 1

        for tecnica in todas_tecnicas:
            if tecnica['valor_gerado'] in dezenas_sorteadas:
                tecnicas_acertadas.append({
                    'id': self.gerar_id_tecnica(index),
                    'apelido': tecnica['apelido'],
                    'campo_usado': tecnica['campo'],
                    'formula': tecnica['formula'],
                    'valor_entrada': {
                        'numeroConcursoProximo': num_concurso_prox,
                        'dataProximoConcurso': data_prox,
                        'valorEstimadoProximoConcurso': valor_prox
                    },
                    'dezena_gerada': tecnica['valor_gerado'],
                    'acertou': True,
                    'descoberta_em_concurso': numero_concurso
                })
                index += 1

        return {
            'sucesso': True,
            'concurso_analisado': numero_concurso,
            'dados_entrada': {
                'numeroConcursoProximo': num_concurso_prox,
                'dataProximoConcurso': data_prox,
                'valorEstimadoProximoConcurso': valor_prox
            },
            'dezenas_sorteadas': dezenas_sorteadas,
            'total_tecnicas_testadas': len(todas_tecnicas),
            'total_tecnicas_acertadas': len(tecnicas_acertadas),
            'tecnicas_descobertas': tecnicas_acertadas,
            'taxa_acerto': round((len(tecnicas_acertadas) / len(todas_tecnicas)) * 100, 2) if todas_tecnicas else 0
        }

    def descobrir_tecnicas_multiplos_concursos(self, concurso_inicial, concurso_final):
        """
        Descobre técnicas analisando múltiplos concursos

        Args:
            concurso_inicial: Número do primeiro concurso
            concurso_final: Número do último concurso

        Returns:
            dict com análise consolidada de todos os concursos
        """
        resultados = []
        tecnicas_consolidadas = defaultdict(lambda: {
            'id': '',
            'apelido': '',
            'campo_usado': '',
            'formula': '',
            'total_acertos': 0,
            'concursos_acertou': [],
            'dezenas_geradas': []
        })

        for numero_concurso in range(concurso_inicial, concurso_final + 1):
            resultado = self.descobrir_tecnicas_concurso(numero_concurso)

            if resultado['sucesso']:
                resultados.append(resultado)

                # Consolidar técnicas
                for tecnica in resultado['tecnicas_descobertas']:
                    chave = f"{tecnica['campo_usado']}_{tecnica['formula']}"

                    if not tecnicas_consolidadas[chave]['id']:
                        tecnicas_consolidadas[chave]['id'] = tecnica['id']
                        tecnicas_consolidadas[chave]['apelido'] = tecnica['apelido']
                        tecnicas_consolidadas[chave]['campo_usado'] = tecnica['campo_usado']
                        tecnicas_consolidadas[chave]['formula'] = tecnica['formula']

                    tecnicas_consolidadas[chave]['total_acertos'] += 1
                    tecnicas_consolidadas[chave]['concursos_acertou'].append(numero_concurso)
                    tecnicas_consolidadas[chave]['dezenas_geradas'].append(tecnica['dezena_gerada'])

        # Calcular taxa de acerto de cada técnica
        total_concursos_analisados = len(resultados)
        tecnicas_lista = []

        for chave, dados in tecnicas_consolidadas.items():
            taxa_acerto = (dados['total_acertos'] / total_concursos_analisados) * 100 if total_concursos_analisados > 0 else 0

            tecnicas_lista.append({
                'id': dados['id'],
                'apelido': dados['apelido'],
                'campo_usado': dados['campo_usado'],
                'formula': dados['formula'],
                'total_acertos': dados['total_acertos'],
                'taxa_acerto': round(taxa_acerto, 2),
                'concursos_acertou': dados['concursos_acertou'],
                'frequencia_dezenas': list(set(dados['dezenas_geradas']))
            })

        # Ordenar por taxa de acerto (maior primeiro)
        tecnicas_lista.sort(key=lambda x: x['taxa_acerto'], reverse=True)

        return {
            'sucesso': True,
            'concurso_inicial': concurso_inicial,
            'concurso_final': concurso_final,
            'total_concursos_analisados': total_concursos_analisados,
            'total_tecnicas_descobertas': len(tecnicas_lista),
            'tecnicas': tecnicas_lista,
            'detalhes_por_concurso': resultados
        }


def descobrir_tecnicas(concurso_inicial, concurso_final=None):
    """
    Função principal para descobrir técnicas

    Args:
        concurso_inicial: Concurso inicial
        concurso_final: Concurso final (se None, analisa apenas o inicial)

    Returns:
        dict com resultados da descoberta
    """
    descobridor = DescobridorTecnicas()

    if concurso_final is None or concurso_inicial == concurso_final:
        return descobridor.descobrir_tecnicas_concurso(concurso_inicial)
    else:
        return descobridor.descobrir_tecnicas_multiplos_concursos(concurso_inicial, concurso_final)

"""
SERVICE: Análise de Colunas - CONEXÃO DIRETA SQLITE (SEM SQLALCHEMY!)
Destino: services/analise_colunas_service.py

Esta versão usa conexão DIRETA com sqlite3 do Python
NÃO passa pelo SQLAlchemy session - ZERO cache!
"""

import sqlite3
from config import Config
import json


class AnaliseColunasService:

    @staticmethod
    def _get_db_path():
        """Retorna caminho do banco"""
        import os
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analise_por_posicao.db")

    @staticmethod
    def mapear_numeros_para_colunas(numeros):
        """Mapeia 7 números para colunas (1-10)"""
        colunas = set()
        for num in numeros:
            coluna = Config.obter_coluna(num)
            if coluna:
                colunas.add(coluna)
        return sorted(colunas)

    @staticmethod
    def importar_historico():
        """Importa histórico - CONEXÃO DIRETA SQLITE"""
        db_path = AnaliseColunasService._get_db_path()

        try:
            # CONEXÃO DIRETA - SEM SQLALCHEMY!
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Buscar sorteios (ainda precisa do Model para isso)
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.order_by(Sorteio.concurso).all()

            if not sorteios:
                conn.close()
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio no banco'}

            # Limpar tabelas - DIRETO NO SQLITE
            cursor.execute("DELETE FROM estatisticas_colunas")
            cursor.execute("DELETE FROM historico_colunas")
            cursor.execute("DELETE FROM coocorrencias_colunas")
            conn.commit()

            # Contadores
            contagens = {i: 0 for i in range(1, 11)}
            coocorrencias = {}

            # Processar sorteios
            for sorteio in sorteios:
                numeros = sorteio.get_posicoes_lista()
                colunas = AnaliseColunasService.mapear_numeros_para_colunas(numeros)

                # Contar
                for col in colunas:
                    contagens[col] += 1

                # Salvar histórico - DIRETO NO SQLITE
                cursor.execute("""
                    INSERT INTO historico_colunas (concurso, data_sorteio, colunas_json)
                    VALUES (?, ?, ?)
                """, (sorteio.concurso, str(sorteio.data_sorteio), json.dumps(colunas)))

                # Co-ocorrências
                for i, col1 in enumerate(colunas):
                    for col2 in colunas[i+1:]:
                        if col1 > col2:
                            col1, col2 = col2, col1
                        key = (col1, col2)
                        coocorrencias[key] = coocorrencias.get(key, 0) + 1

            total = len(sorteios)

            # Preparar ranking
            stats = []
            for coluna, qtd in contagens.items():
                freq = (qtd / total * 100) if total > 0 else 0
                stats.append({'coluna': coluna, 'qtd': qtd, 'freq': freq})

            stats.sort(key=lambda x: x['qtd'], reverse=True)

            # Inserir estatísticas - DIRETO NO SQLITE
            for idx, st in enumerate(stats, 1):
                cursor.execute("""
                    INSERT INTO estatisticas_colunas
                    (coluna, total_aparicoes, frequencia_relativa, ranking, total_concursos)
                    VALUES (?, ?, ?, ?, ?)
                """, (st['coluna'], st['qtd'], st['freq'], idx, total))

            # Inserir co-ocorrências - DIRETO NO SQLITE
            for (col1, col2), qtd in coocorrencias.items():
                perc = (qtd / total * 100) if total > 0 else 0
                cursor.execute("""
                    INSERT INTO coocorrencias_colunas
                    (coluna_1, coluna_2, total_juntas, percentual)
                    VALUES (?, ?, ?, ?)
                """, (col1, col2, qtd, perc))

            conn.commit()
            conn.close()

            return {
                'sucesso': True,
                'total_sorteios': total,
                'concurso_inicial': sorteios[0].concurso,
                'concurso_final': sorteios[-1].concurso,
                'mensagem': f'{total} sorteios processados!'
            }

        except Exception as e:
            try:
                conn.rollback()
                conn.close()
            except:
                pass

            return {
                'sucesso': False,
                'mensagem': f'Erro: {str(e)}'
            }

    @staticmethod
    def obter_ranking():
        """Busca ranking - CONEXÃO DIRETA SQLITE"""
        db_path = AnaliseColunasService._get_db_path()

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT coluna, total_aparicoes, frequencia_relativa, ranking, total_concursos
                FROM estatisticas_colunas
                ORDER BY ranking
            """)

            rows = cursor.fetchall()

            # Obter top números de cada coluna
            top_numeros = AnaliseColunasService._obter_top_numeros_por_coluna(cursor)

            conn.close()

            ranking = []
            for row in rows:
                coluna_num = row[0]
                ranking.append({
                    'coluna': coluna_num,
                    'total_aparicoes': row[1],
                    'frequencia_relativa': round(row[2], 2),
                    'ranking': row[3],
                    'total_concursos': row[4],
                    'numeros': Config.obter_numeros_da_coluna(coluna_num),
                    'cor_heatmap': Config.obter_cor_heatmap(row[2]),
                    'top_numero': top_numeros.get(coluna_num, None)
                })

            total = ranking[0]['total_concursos'] if ranking else 0
            return {'ranking': ranking, 'total_concursos': total}

        except:
            return {'ranking': [], 'total_concursos': 0}

    @staticmethod
    def _obter_top_numeros_por_coluna(cursor):
        """Identifica o número mais frequente de cada coluna"""
        top_numeros = {}

        try:
            # Buscar todos os sorteios do histórico
            cursor.execute("SELECT colunas_json FROM historico_colunas")
            rows = cursor.fetchall()

            # Contador de números por coluna
            contadores = {}
            for coluna in range(1, 11):
                numeros_coluna = Config.obter_numeros_da_coluna(coluna)
                contadores[coluna] = {num: 0 for num in numeros_coluna}

            # Contar aparições de cada número
            for row in rows:
                colunas_json = json.loads(row[0])
                for coluna_num in colunas_json:
                    # Para cada coluna que apareceu, precisamos verificar QUAL número específico apareceu
                    # Mas o JSON só guarda quais colunas, não os números exatos!
                    pass

            # Como não temos os números individuais no histórico,
            # vamos buscar direto dos sorteios originais
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.all()

            for sorteio in sorteios:
                numeros = sorteio.get_posicoes_lista()
                for num in numeros:
                    coluna = Config.obter_coluna(num)
                    if coluna and coluna in contadores and num in contadores[coluna]:
                        contadores[coluna][num] += 1

            # Identificar o top de cada coluna
            for coluna, nums_count in contadores.items():
                if nums_count:
                    top_num = max(nums_count.items(), key=lambda x: x[1])[0]
                    top_numeros[coluna] = top_num

        except Exception as e:
            print(f"Erro ao obter top números: {e}")

        return top_numeros

    @staticmethod
    def obter_coocorrencias(top_n=20):
        """Busca co-ocorrências - CONEXÃO DIRETA SQLITE"""
        db_path = AnaliseColunasService._get_db_path()

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT coluna_1, coluna_2, total_juntas, percentual
                FROM coocorrencias_colunas
                ORDER BY total_juntas DESC
                LIMIT ?
            """, (top_n,))

            rows = cursor.fetchall()
            conn.close()

            coocs = []
            for row in rows:
                coocs.append({
                    'coluna_1': row[0],
                    'coluna_2': row[1],
                    'total_juntas': row[2],
                    'percentual': round(row[3], 2)
                })

            return {'coocorrencias': coocs}

        except:
            return {'coocorrencias': []}

    @staticmethod
    def verificar_atualizacao_necessaria():
        """Verifica se há novos sorteios que precisam ser processados"""
        db_path = AnaliseColunasService._get_db_path()

        try:
            # Buscar total de sorteios no banco
            from models.sorteio import Sorteio
            total_sorteios_banco = Sorteio.query.count()

            # Buscar total processado na análise de colunas
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT total_concursos
                FROM estatisticas_colunas
                LIMIT 1
            """)

            row = cursor.fetchone()
            conn.close()

            total_processado = row[0] if row else 0

            precisa_atualizar = total_sorteios_banco > total_processado

            return {
                'precisa_atualizar': precisa_atualizar,
                'total_banco': total_sorteios_banco,
                'total_processado': total_processado,
                'diferenca': total_sorteios_banco - total_processado
            }

        except Exception as e:
            return {
                'precisa_atualizar': True,
                'total_banco': 0,
                'total_processado': 0,
                'diferenca': 0,
                'erro': str(e)
            }

    @staticmethod
    def obter_status():
        """Retorna status atual da análise"""
        db_path = AnaliseColunasService._get_db_path()

        try:
            # Total de sorteios no banco
            from models.sorteio import Sorteio
            total_banco = Sorteio.query.count()

            # Total processado
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT total_concursos, MAX(ranking) as total_colunas
                FROM estatisticas_colunas
            """)

            row = cursor.fetchone()
            conn.close()

            if row and row[0]:
                return {
                    'status': 'ok',
                    'total_banco': total_banco,
                    'total_processado': row[0],
                    'total_colunas': row[1] or 0,
                    'atualizado': total_banco == row[0]
                }
            else:
                return {
                    'status': 'vazio',
                    'total_banco': total_banco,
                    'total_processado': 0,
                    'total_colunas': 0,
                    'atualizado': False
                }

        except Exception as e:
            return {
                'status': 'erro',
                'total_banco': 0,
                'total_processado': 0,
                'total_colunas': 0,
                'atualizado': False,
                'erro': str(e)
            }

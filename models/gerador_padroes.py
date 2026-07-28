"""
Modelos do Banco de Dados para o Gerador de Padrões Completo.

Este arquivo NÃO usa SQLAlchemy ORM para evitar conflitos de registro.
Em vez disso, usa SQL raw com o objeto db.session.

Tabelas:
- padroes_gerados: Padrões estatísticos calculados
- combinacoes_geradas: Combinações/apostas geradas
- sorteios_reais: Resultados de sorteios reais
- analise_sorteios: Análises de correspondência
- estatisticas_padroes: Estatísticas detalhadas
"""

from datetime import datetime

# Tentar importar o db do app
try:
    from app import db
except ImportError:
    try:
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy()
    except ImportError:
        db = None


# =========================================================================
# FUNÇÕES AUXILIARES PARA OPERAÇÕES NO BANCO (SEM ORM)
# =========================================================================

def gerar_hash_dezenas(dezenas):
    """Gera hash único para uma combinação de dezenas."""
    ordenadas = sorted(dezenas)
    return '-'.join([str(d).zfill(2) for d in ordenadas])


# =========================================================================
# OPERAÇÕES COM PADRÕES
# =========================================================================

class PadroesRepository:
    """Repositório para operações com a tabela padroes_gerados."""

    @staticmethod
    def buscar_por_padrao(padrao_str):
        """Busca um padrão pelo string."""
        if db is None:
            return None
        try:
            result = db.session.execute(
                db.text("SELECT * FROM padroes_gerados WHERE padrao = :padrao"),
                {'padrao': padrao_str}
            )
            row = result.fetchone()
            return PadroesRepository._row_to_dict(row) if row else None
        except Exception:
            return None

    @staticmethod
    def inserir(padrao_str, descricao, jogos_possiveis, frequencia=0, atraso=None, status='faltante', viavel=True):
        """Insere um novo padrão."""
        if db is None:
            return None
        try:
            db.session.execute(
                db.text("""
                    INSERT INTO padroes_gerados
                    (padrao, descricao, jogos_possiveis, frequencia, atraso, status, viavel, data_criacao, data_atualizacao)
                    VALUES (:padrao, :descricao, :jogos_possiveis, :frequencia, :atraso, :status, :viavel, :data_criacao, :data_atualizacao)
                """),
                {
                    'padrao': padrao_str,
                    'descricao': descricao,
                    'jogos_possiveis': jogos_possiveis,
                    'frequencia': frequencia,
                    'atraso': atraso,
                    'status': status,
                    'viavel': 1 if viavel else 0,
                    'data_criacao': datetime.utcnow(),
                    'data_atualizacao': datetime.utcnow()
                }
            )
            db.session.commit()
            return PadroesRepository.buscar_por_padrao(padrao_str)
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def atualizar(padrao_str, frequencia=None, atraso=None, status=None):
        """Atualiza um padrão existente."""
        if db is None:
            return False
        try:
            updates = ['data_atualizacao = :data_atualizacao']
            params = {'padrao': padrao_str, 'data_atualizacao': datetime.utcnow()}

            if frequencia is not None:
                updates.append('frequencia = :frequencia')
                params['frequencia'] = frequencia
            if atraso is not None:
                updates.append('atraso = :atraso')
                params['atraso'] = atraso
            if status is not None:
                updates.append('status = :status')
                params['status'] = status

            db.session.execute(
                db.text(f"UPDATE padroes_gerados SET {', '.join(updates)} WHERE padrao = :padrao"),
                params
            )
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def contar():
        """Conta total de padrões."""
        if db is None:
            return 0
        try:
            result = db.session.execute(db.text("SELECT COUNT(*) FROM padroes_gerados"))
            return result.scalar() or 0
        except Exception:
            return 0

    @staticmethod
    def contar_por_status(status):
        """Conta padrões por status."""
        if db is None:
            return 0
        try:
            result = db.session.execute(
                db.text("SELECT COUNT(*) FROM padroes_gerados WHERE status = :status"),
                {'status': status}
            )
            return result.scalar() or 0
        except Exception:
            return 0

    @staticmethod
    def _row_to_dict(row):
        """Converte row para dict."""
        if row is None:
            return None
        return {
            'id': row[0],
            'padrao': row[1],
            'descricao': row[2],
            'jogos_possiveis': row[3],
            'frequencia': row[4],
            'atraso': row[5],
            'status': row[6],
            'viavel': bool(row[7]),
            'data_criacao': row[8],
            'data_atualizacao': row[9]
        }


# =========================================================================
# OPERAÇÕES COM COMBINAÇÕES
# =========================================================================

class CombinacoesRepository:
    """Repositório para operações com a tabela combinacoes_geradas."""

    @staticmethod
    def buscar_por_hash(hash_dezenas):
        """Busca uma combinação pelo hash."""
        if db is None:
            return None
        try:
            result = db.session.execute(
                db.text("SELECT * FROM combinacoes_geradas WHERE hash_dezenas = :hash"),
                {'hash': hash_dezenas}
            )
            row = result.fetchone()
            return CombinacoesRepository._row_to_dict(row) if row else None
        except Exception:
            return None

    @staticmethod
    def buscar_por_padrao_id(padrao_id, offset=0, limit=100, apenas_viaveis=None):
        """Busca combinações por padrão com paginação."""
        if db is None:
            return []
        try:
            sql = "SELECT * FROM combinacoes_geradas WHERE padrao_id = :padrao_id"
            params = {'padrao_id': padrao_id, 'limit': limit, 'offset': offset}

            if apenas_viaveis is True:
                sql += " AND viavel = 1"
            elif apenas_viaveis is False:
                sql += " AND viavel = 0"

            sql += " LIMIT :limit OFFSET :offset"

            result = db.session.execute(db.text(sql), params)
            return [CombinacoesRepository._row_to_dict(row) for row in result.fetchall()]
        except Exception:
            return []

    @staticmethod
    def inserir(padrao_id, dezenas, viavel=True, motivo_inviavel=None):
        """Insere uma nova combinação."""
        if db is None:
            return None
        try:
            hash_dezenas = gerar_hash_dezenas(dezenas)
            soma = sum(dezenas)

            db.session.execute(
                db.text("""
                    INSERT INTO combinacoes_geradas
                    (padrao_id, d1, d2, d3, d4, d5, d6, d7, hash_dezenas, soma, viavel, motivo_inviavel, data_criacao)
                    VALUES (:padrao_id, :d1, :d2, :d3, :d4, :d5, :d6, :d7, :hash, :soma, :viavel, :motivo, :data)
                """),
                {
                    'padrao_id': padrao_id,
                    'd1': dezenas[0], 'd2': dezenas[1], 'd3': dezenas[2], 'd4': dezenas[3],
                    'd5': dezenas[4], 'd6': dezenas[5], 'd7': dezenas[6],
                    'hash': hash_dezenas,
                    'soma': soma,
                    'viavel': 1 if viavel else 0,
                    'motivo': motivo_inviavel,
                    'data': datetime.utcnow()
                }
            )
            return True
        except Exception:
            return False

    @staticmethod
    def inserir_lote(padrao_id, combinacoes_data):
        """
        Insere combinações em lote.

        Args:
            padrao_id: ID do padrão
            combinacoes_data: Lista de dicts com {dezenas, viavel, motivo_inviavel}

        Returns:
            int: Quantidade inserida
        """
        if db is None or not combinacoes_data:
            return 0

        inseridas = 0
        try:
            for item in combinacoes_data:
                dezenas = item['dezenas']
                hash_dezenas = gerar_hash_dezenas(dezenas)

                # Verificar se já existe
                existe = db.session.execute(
                    db.text("SELECT 1 FROM combinacoes_geradas WHERE hash_dezenas = :hash LIMIT 1"),
                    {'hash': hash_dezenas}
                ).fetchone()

                if existe:
                    continue

                db.session.execute(
                    db.text("""
                        INSERT INTO combinacoes_geradas
                        (padrao_id, d1, d2, d3, d4, d5, d6, d7, hash_dezenas, soma, viavel, motivo_inviavel, data_criacao)
                        VALUES (:padrao_id, :d1, :d2, :d3, :d4, :d5, :d6, :d7, :hash, :soma, :viavel, :motivo, :data)
                    """),
                    {
                        'padrao_id': padrao_id,
                        'd1': dezenas[0], 'd2': dezenas[1], 'd3': dezenas[2], 'd4': dezenas[3],
                        'd5': dezenas[4], 'd6': dezenas[5], 'd7': dezenas[6],
                        'hash': hash_dezenas,
                        'soma': sum(dezenas),
                        'viavel': 1 if item.get('viavel', True) else 0,
                        'motivo': item.get('motivo_inviavel'),
                        'data': datetime.utcnow()
                    }
                )
                inseridas += 1

                # Commit a cada 1000 para melhor performance
                if inseridas % 1000 == 0:
                    db.session.commit()

            db.session.commit()
            return inseridas
        except Exception:
            db.session.rollback()
            return inseridas

    @staticmethod
    def contar(padrao_id=None, apenas_viaveis=None):
        """Conta combinações."""
        if db is None:
            return 0
        try:
            sql = "SELECT COUNT(*) FROM combinacoes_geradas WHERE 1=1"
            params = {}

            if padrao_id is not None:
                sql += " AND padrao_id = :padrao_id"
                params['padrao_id'] = padrao_id

            if apenas_viaveis is True:
                sql += " AND viavel = 1"
            elif apenas_viaveis is False:
                sql += " AND viavel = 0"

            result = db.session.execute(db.text(sql), params)
            return result.scalar() or 0
        except Exception:
            return 0

    @staticmethod
    def buscar_matches_parciais(dezenas_sorteadas, min_acertos=4, limite=50):
        """Busca combinações com correspondência parcial."""
        if db is None:
            return {'total_6': 0, 'total_5': 0, 'total_4': 0, 'detalhes': []}

        resultado = {'total_6': 0, 'total_5': 0, 'total_4': 0, 'detalhes': []}
        set_sorteadas = set(dezenas_sorteadas)

        try:
            # Buscar combinações (limitando para performance)
            result = db.session.execute(
                db.text("SELECT id, d1, d2, d3, d4, d5, d6, d7, viavel FROM combinacoes_geradas LIMIT 50000")
            )

            for row in result.fetchall():
                comb_id = row[0]
                comb_dezenas = set([row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
                viavel = bool(row[8])

                acertos = len(comb_dezenas.intersection(set_sorteadas))

                if acertos >= min_acertos:
                    if acertos == 6:
                        resultado['total_6'] += 1
                    elif acertos == 5:
                        resultado['total_5'] += 1
                    elif acertos == 4:
                        resultado['total_4'] += 1

                    if len(resultado['detalhes']) < limite:
                        resultado['detalhes'].append({
                            'combinacao_id': comb_id,
                            'dezenas': list(comb_dezenas),
                            'acertos': acertos,
                            'dezenas_acertadas': list(comb_dezenas.intersection(set_sorteadas)),
                            'viavel': viavel
                        })

            # Ordenar por acertos
            resultado['detalhes'].sort(key=lambda x: x['acertos'], reverse=True)

        except Exception:
            pass

        return resultado

    @staticmethod
    def _row_to_dict(row):
        """Converte row para dict."""
        if row is None:
            return None
        return {
            'id': row[0],
            'padrao_id': row[1],
            'dezenas': [row[2], row[3], row[4], row[5], row[6], row[7], row[8]],
            'hash_dezenas': row[9],
            'soma': row[10],
            'viavel': bool(row[11]),
            'motivo_inviavel': row[12],
            'data_criacao': row[13]
        }


# =========================================================================
# OPERAÇÕES COM SORTEIOS REAIS
# =========================================================================

class SorteiosReaisRepository:
    """Repositório para operações com a tabela sorteios_reais."""

    @staticmethod
    def buscar_por_hash(hash_dezenas):
        """Busca um sorteio pelo hash."""
        if db is None:
            return None
        try:
            result = db.session.execute(
                db.text("SELECT * FROM sorteios_reais WHERE hash_dezenas = :hash"),
                {'hash': hash_dezenas}
            )
            row = result.fetchone()
            return SorteiosReaisRepository._row_to_dict(row) if row else None
        except Exception:
            return None

    @staticmethod
    def buscar_por_concurso(concurso):
        """Busca um sorteio pelo número do concurso."""
        if db is None:
            return None
        try:
            result = db.session.execute(
                db.text("SELECT * FROM sorteios_reais WHERE concurso = :concurso"),
                {'concurso': concurso}
            )
            row = result.fetchone()
            return SorteiosReaisRepository._row_to_dict(row) if row else None
        except Exception:
            return None

    @staticmethod
    def inserir(concurso, dezenas, mes_sorte=None, padrao_str=None, padrao_id=None,
                combinacao_encontrada=False, combinacao_id=None):
        """Insere um novo sorteio."""
        if db is None:
            return None
        try:
            hash_dezenas = gerar_hash_dezenas(dezenas)

            db.session.execute(
                db.text("""
                    INSERT INTO sorteios_reais
                    (concurso, d1, d2, d3, d4, d5, d6, d7, mes_sorte, hash_dezenas,
                     padrao_id, padrao_str, combinacao_encontrada, combinacao_id, data_registro)
                    VALUES (:concurso, :d1, :d2, :d3, :d4, :d5, :d6, :d7, :mes_sorte, :hash,
                            :padrao_id, :padrao_str, :comb_enc, :comb_id, :data)
                """),
                {
                    'concurso': concurso or 0,
                    'd1': dezenas[0], 'd2': dezenas[1], 'd3': dezenas[2], 'd4': dezenas[3],
                    'd5': dezenas[4], 'd6': dezenas[5], 'd7': dezenas[6],
                    'mes_sorte': mes_sorte,
                    'hash': hash_dezenas,
                    'padrao_id': padrao_id,
                    'padrao_str': padrao_str,
                    'comb_enc': 1 if combinacao_encontrada else 0,
                    'comb_id': combinacao_id,
                    'data': datetime.utcnow()
                }
            )
            db.session.commit()
            return SorteiosReaisRepository.buscar_por_hash(hash_dezenas)
        except Exception:
            db.session.rollback()
            return None

    @staticmethod
    def listar_ultimos(limite=50):
        """Lista os últimos sorteios."""
        if db is None:
            return []
        try:
            result = db.session.execute(
                db.text(f"SELECT * FROM sorteios_reais ORDER BY id DESC LIMIT :limite"),
                {'limite': limite}
            )
            return [SorteiosReaisRepository._row_to_dict(row) for row in result.fetchall()]
        except Exception:
            return []

    @staticmethod
    def contar():
        """Conta total de sorteios."""
        if db is None:
            return 0
        try:
            result = db.session.execute(db.text("SELECT COUNT(*) FROM sorteios_reais"))
            return result.scalar() or 0
        except Exception:
            return 0

    @staticmethod
    def _row_to_dict(row):
        """Converte row para dict."""
        if row is None:
            return None
        return {
            'id': row[0],
            'concurso': row[1],
            'data_sorteio': row[2],
            'dezenas': [row[3], row[4], row[5], row[6], row[7], row[8], row[9]],
            'mes_sorte': row[10],
            'hash_dezenas': row[11],
            'padrao_id': row[12],
            'padrao_str': row[13],
            'combinacao_encontrada': bool(row[14]),
            'combinacao_id': row[15],
            'data_registro': row[16]
        }


# =========================================================================
# FLAG DE DISPONIBILIDADE
# =========================================================================

def verificar_tabelas_existem():
    """Verifica se as tabelas do módulo existem."""
    if db is None:
        return False
    try:
        db.session.execute(db.text("SELECT 1 FROM padroes_gerados LIMIT 1"))
        db.session.execute(db.text("SELECT 1 FROM combinacoes_geradas LIMIT 1"))
        db.session.execute(db.text("SELECT 1 FROM sorteios_reais LIMIT 1"))
        return True
    except Exception:
        return False


# Verificar disponibilidade ao importar
MODELOS_DISPONIVEIS = False  # Será verificado no primeiro uso

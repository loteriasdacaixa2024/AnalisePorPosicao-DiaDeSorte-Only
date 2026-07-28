# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Modelo: Combinações Geradas (Cache Inteligente)

from models import db
from datetime import datetime
import json


class CombinacaoGerada(db.Model):
    """
    Armazena TODAS as 2.629.575 combinações possíveis do Dia de Sorte
    com análises pré-calculadas e controle de combinações já sorteadas
    """
    __tablename__ = 'combinacoes_geradas'

    # ========================================================================
    # IDENTIFICAÇÃO
    # ========================================================================
    id = db.Column(db.Integer, primary_key=True)

    # ========================================================================
    # NÚMEROS DA COMBINAÇÃO
    # ========================================================================
    # Formato: "01-05-11-13-23-24-26"
    numeros_crescente = db.Column(db.String(50), nullable=False, index=True, unique=True)
    numeros_original = db.Column(db.String(50), nullable=False)

    # Hash para busca rápida
    hash_combinacao = db.Column(db.String(64), nullable=False, index=True, unique=True)

    # ========================================================================
    # ANÁLISES PRÉ-CALCULADAS (JSON)
    # ========================================================================
    analises = db.Column(db.Text, nullable=False)
    """
    Estrutura do JSON:
    {
        'pares': 3,
        'impares': 4,
        'soma': 105,
        'quadrantes': [2, 2, 2, 1],
        'espelhados': 2,
        'sequencias': 1,
        'gap_medio': 3.8,
        'baixa_media_alta': [2, 3, 2],
        'atrasados': [1, 5],
        'quentes': 4,
        'frios': 3,
        'primos': 3,
        'compostos': 4,
        'multiplos_3': 2,
        'multiplos_5': 1,
        'multiplos_7': 1,
        'consecutivos': 0,
        'raiz_digital': 6,
        'digitos_unicos': 7,
        'digito_inicial_padrao': '0-1-2',
        'fibonacci': 2
    }
    """

    # ========================================================================
    # SCORE DE RECOMENDAÇÃO
    # ========================================================================
    score = db.Column(db.Float, default=0.0, index=True)
    score_detalhado = db.Column(db.Text, nullable=True)  # JSON com detalhamento

    # ========================================================================
    # FILTRO INTELIGENTE - JÁ SORTEADA
    # ========================================================================
    ja_sorteada = db.Column(db.Boolean, default=False, index=True)
    concurso_sorteio = db.Column(db.Integer, nullable=True)
    data_sorteio = db.Column(db.DateTime, nullable=True)
    mes_sorteio = db.Column(db.Integer, nullable=True)  # 1-12

    # ========================================================================
    # CONTROLE
    # ========================================================================
    data_geracao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True, index=True)

    # ========================================================================
    # ÍNDICES PARA PERFORMANCE
    # ========================================================================
    __table_args__ = (
        db.Index('idx_crescente_ativo', 'numeros_crescente', 'ativo'),
        db.Index('idx_sorteada_ativo', 'ja_sorteada', 'ativo'),
        db.Index('idx_score_desc', 'score'),
        db.Index('idx_hash', 'hash_combinacao'),
    )

    # ========================================================================
    # MÉTODOS
    # ========================================================================

    def get_analises(self):
        """Retorna análises como dicionário"""
        try:
            return json.loads(self.analises) if self.analises else {}
        except:
            return {}

    def set_analises(self, dados):
        """Define análises como JSON"""
        self.analises = json.dumps(dados, ensure_ascii=False)

    def get_numeros_crescente_list(self):
        """Retorna lista de números em ordem crescente"""
        return [int(n) for n in self.numeros_crescente.split('-')]

    def get_numeros_original_list(self):
        """Retorna lista de números em ordem original"""
        return [int(n) for n in self.numeros_original.split('-')]

    def to_dict(self, incluir_analises=False):
        """Converte para dicionário"""
        dados = {
            'id': self.id,
            'numeros_crescente': self.get_numeros_crescente_list(),
            'numeros_original': self.get_numeros_original_list(),
            'score': self.score,
            'ja_sorteada': self.ja_sorteada,
            'concurso_sorteio': self.concurso_sorteio,
            'data_sorteio': self.data_sorteio.strftime('%d/%m/%Y') if self.data_sorteio else None
        }

        if incluir_analises:
            dados['analises'] = self.get_analises()

        return dados

    @staticmethod
    def gerar_hash(numeros):
        """
        Gera hash único para combinação
        Útil para buscas rápidas
        """
        import hashlib
        nums_str = '-'.join([f"{n:02d}" for n in sorted(numeros)])
        return hashlib.sha256(nums_str.encode()).hexdigest()


class CacheGeracao(db.Model):
    """
    Controle do cache de combinações geradas
    """
    __tablename__ = 'cache_geracao'

    id = db.Column(db.Integer, primary_key=True)

    # ========================================================================
    # ESTATÍSTICAS
    # ========================================================================
    total_combinacoes = db.Column(db.Integer, default=2629575)
    total_geradas = db.Column(db.Integer, default=0)
    total_sorteadas = db.Column(db.Integer, default=0)
    total_disponiveis = db.Column(db.Integer, default=0)

    # ========================================================================
    # CONTROLE DE GERAÇÃO
    # ========================================================================
    data_geracao = db.Column(db.DateTime, nullable=True)
    data_ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ========================================================================
    # SINCRONIZAÇÃO COM HISTÓRICO
    # ========================================================================
    ultimo_concurso_sincronizado = db.Column(db.Integer, default=0)
    data_ultima_sincronizacao = db.Column(db.DateTime, nullable=True)

    # ========================================================================
    # STATUS
    # ========================================================================
    status = db.Column(db.String(50), default='aguardando')
    # Valores: aguardando, gerando, calculando_analises, completo, erro

    versao = db.Column(db.String(20), default='1.0.0')

    # ========================================================================
    # PROGRESSO (para barra de progresso)
    # ========================================================================
    progresso_atual = db.Column(db.Integer, default=0)
    progresso_total = db.Column(db.Integer, default=0)
    progresso_percentual = db.Column(db.Float, default=0.0)
    mensagem_progresso = db.Column(db.String(200), nullable=True)

    # ========================================================================
    # MÉTODOS
    # ========================================================================

    def atualizar_progresso(self, atual, total, mensagem=''):
        """Atualiza progresso da geração"""
        self.progresso_atual = atual
        self.progresso_total = total
        self.progresso_percentual = (atual / total * 100) if total > 0 else 0
        self.mensagem_progresso = mensagem
        db.session.commit()

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'total_combinacoes': self.total_combinacoes,
            'total_geradas': self.total_geradas,
            'total_sorteadas': self.total_sorteadas,
            'total_disponiveis': self.total_disponiveis,
            'data_geracao': self.data_geracao.strftime('%d/%m/%Y %H:%M:%S') if self.data_geracao else None,
            'data_ultima_atualizacao': self.data_ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S') if self.data_ultima_atualizacao else None,
            'ultimo_concurso_sincronizado': self.ultimo_concurso_sincronizado,
            'data_ultima_sincronizacao': self.data_ultima_sincronizacao.strftime('%d/%m/%Y %H:%M:%S') if self.data_ultima_sincronizacao else None,
            'status': self.status,
            'versao': self.versao,
            'progresso': {
                'atual': self.progresso_atual,
                'total': self.progresso_total,
                'percentual': self.progresso_percentual,
                'mensagem': self.mensagem_progresso
            }
        }

    @staticmethod
    def obter_ou_criar():
        """Obtém registro único do cache ou cria se não existir"""
        cache = CacheGeracao.query.first()
        if not cache:
            cache = CacheGeracao()
            db.session.add(cache)
            db.session.commit()
        return cache

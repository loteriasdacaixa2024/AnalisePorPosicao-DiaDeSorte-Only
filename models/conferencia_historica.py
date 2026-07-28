"""
Modelos para Conferência Histórica - Dia de Sorte
Processa apostas contra TODOS os resultados históricos e ranqueia por performance
"""

from datetime import datetime
from sqlalchemy import Index, Text
from models.shared import db


class SessaoConferenciaHistorica(db.Model):
    """
    Representa uma sessão de conferência histórica (upload de arquivo)
    Cada vez que o usuário faz upload de um arquivo TXT, cria uma nova sessão
    """

    __tablename__ = 'sessoes_conferencia_historica'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Identificação da sessão
    nome_arquivo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(500), nullable=True)

    # Configurações da conferência
    estrategia = db.Column(db.String(50), nullable=False, default='ordenada')  # 'ordenada' ou 'sorteio'
    filtro_acertos_min = db.Column(db.Integer, default=4)  # Mínimo de acertos para considerar vitória

    # Estatísticas gerais
    total_apostas = db.Column(db.Integer, default=0)
    total_concursos_analisados = db.Column(db.Integer, default=0)
    total_premiacoes = db.Column(db.Integer, default=0)

    # Estatísticas por faixa
    total_4_acertos = db.Column(db.Integer, default=0)
    total_5_acertos = db.Column(db.Integer, default=0)
    total_6_acertos = db.Column(db.Integer, default=0)
    total_7_acertos = db.Column(db.Integer, default=0)
    total_mes_acertado = db.Column(db.Integer, default=0)

    # Valor total estimado ganho (soma de todos os prêmios)
    valor_total_premios = db.Column(db.Float, default=0.0)

    # Status do processamento
    status = db.Column(db.String(50), default='pendente')  # 'pendente', 'processando', 'concluido', 'erro'
    progresso = db.Column(db.Integer, default=0)  # 0-100%
    erro_mensagem = db.Column(db.Text, nullable=True)

    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    processado_em = db.Column(db.DateTime, nullable=True)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    apostas = db.relationship('ApostaHistorica', backref='sessao', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_sessao_status', 'status'),
        Index('idx_sessao_criado', 'criado_em'),
    )

    def __repr__(self):
        return f'<SessaoConferenciaHistorica {self.id} - {self.nome_arquivo}>'

    @staticmethod
    def contagem_mes_premio(total_ocorrencias, total_4, total_5, total_6, total_7):
        """Prêmios só pelo mês (<4 dezenas): fecha 4+5+6+7+mes = total de ocorrências."""
        faixas = (total_4 or 0) + (total_5 or 0) + (total_6 or 0) + (total_7 or 0)
        return max(0, (total_ocorrencias or 0) - faixas)

    def to_dict(self):
        mes_premio = self.contagem_mes_premio(
            self.total_premiacoes,
            self.total_4_acertos,
            self.total_5_acertos,
            self.total_6_acertos,
            self.total_7_acertos,
        )
        return {
            'id': self.id,
            'nome_arquivo': self.nome_arquivo,
            'descricao': self.descricao,
            'estrategia': self.estrategia,
            'filtro_acertos_min': self.filtro_acertos_min,
            'total_apostas': self.total_apostas,
            'total_concursos_analisados': self.total_concursos_analisados,
            'total_premiacoes': self.total_premiacoes,
            'estatisticas': {
                '4_acertos': self.total_4_acertos,
                '5_acertos': self.total_5_acertos,
                '6_acertos': self.total_6_acertos,
                '7_acertos': self.total_7_acertos,
                'mes_acertado': self.total_mes_acertado,
                'mes_premio': mes_premio,
            },
            'valor_total_premios': self.valor_total_premios,
            'status': self.status,
            'progresso': self.progresso,
            'erro_mensagem': self.erro_mensagem,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M') if self.criado_em else None,
            'processado_em': self.processado_em.strftime('%d/%m/%Y %H:%M') if self.processado_em else None
        }


class ApostaHistorica(db.Model):
    """
    Representa uma aposta individual dentro de uma sessão
    Armazena os números, mês e estatísticas de performance histórica
    """

    __tablename__ = 'apostas_historicas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sessao_id = db.Column(db.Integer, db.ForeignKey('sessoes_conferencia_historica.id'), nullable=False, index=True)

    # Identificação da aposta
    numero_linha = db.Column(db.Integer, nullable=False)  # Linha no arquivo original

    # Números da aposta (7 a 15 números)
    # Armazenados como string separada por vírgula para flexibilidade
    numeros_apostados = db.Column(db.String(100), nullable=False)
    quantidade_numeros = db.Column(db.Integer, nullable=False)  # 7 a 15

    # Mês da sorte
    mes_apostado = db.Column(db.Integer, nullable=True)  # 1-12, null se não informado

    # Estatísticas de performance (calculadas após processamento)
    total_vitorias = db.Column(db.Integer, default=0)  # Quantas vezes ganhou (4+ acertos)
    total_4_acertos = db.Column(db.Integer, default=0)
    total_5_acertos = db.Column(db.Integer, default=0)
    total_6_acertos = db.Column(db.Integer, default=0)
    total_7_acertos = db.Column(db.Integer, default=0)
    total_mes_acertado = db.Column(db.Integer, default=0)

    # Valor total estimado ganho
    valor_total_premios = db.Column(db.Float, default=0.0)

    # Score de ranking (calculado baseado nas vitórias ponderadas)
    score_ranking = db.Column(db.Float, default=0.0)

    # Posição no ranking (1 = melhor aposta)
    posicao_ranking = db.Column(db.Integer, nullable=True)

    # Melhor resultado (concurso onde teve mais acertos)
    melhor_concurso = db.Column(db.Integer, nullable=True)
    melhor_acertos = db.Column(db.Integer, default=0)

    # Análise estatística da aposta
    soma_numeros = db.Column(db.Integer, nullable=True)
    qtd_pares = db.Column(db.Integer, nullable=True)
    qtd_impares = db.Column(db.Integer, nullable=True)

    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    processado_em = db.Column(db.DateTime, nullable=True)

    # Relacionamentos
    resultados = db.relationship('ResultadoApostaHistorica', backref='aposta', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_aposta_sessao', 'sessao_id'),
        Index('idx_aposta_ranking', 'sessao_id', 'posicao_ranking'),
        Index('idx_aposta_score', 'sessao_id', 'score_ranking'),
        Index('idx_aposta_vitorias', 'sessao_id', 'total_vitorias'),
    )

    def __repr__(self):
        return f'<ApostaHistorica {self.id} - Linha {self.numero_linha}>'

    def get_numeros_lista(self):
        """Retorna os números como lista de inteiros"""
        return [int(n) for n in self.numeros_apostados.split(',')]

    def set_numeros_lista(self, numeros):
        """Define os números a partir de uma lista"""
        self.numeros_apostados = ','.join(map(str, sorted(numeros)))
        self.quantidade_numeros = len(numeros)

    def get_mes_nome(self):
        """Retorna o nome do mês apostado"""
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(self.mes_apostado, '-')

    def to_dict(self):
        mes_premio = SessaoConferenciaHistorica.contagem_mes_premio(
            self.total_vitorias,
            self.total_4_acertos,
            self.total_5_acertos,
            self.total_6_acertos,
            self.total_7_acertos,
        )
        return {
            'id': self.id,
            'sessao_id': self.sessao_id,
            'numero_linha': self.numero_linha,
            'numeros': self.get_numeros_lista(),
            'quantidade_numeros': self.quantidade_numeros,
            'mes_apostado': self.mes_apostado,
            'mes_nome': self.get_mes_nome(),
            'estatisticas': {
                'total_vitorias': self.total_vitorias,
                '4_acertos': self.total_4_acertos,
                '5_acertos': self.total_5_acertos,
                '6_acertos': self.total_6_acertos,
                '7_acertos': self.total_7_acertos,
                'mes_acertado': self.total_mes_acertado,
                'mes_premio': mes_premio,
            },
            'valor_total_premios': self.valor_total_premios,
            'score_ranking': self.score_ranking,
            'posicao_ranking': self.posicao_ranking,
            'melhor_resultado': {
                'concurso': self.melhor_concurso,
                'acertos': self.melhor_acertos
            },
            'analise': {
                'soma': self.soma_numeros,
                'pares': self.qtd_pares,
                'impares': self.qtd_impares
            }
        }


class ResultadoApostaHistorica(db.Model):
    """
    Armazena o resultado de uma aposta em um concurso específico
    Apenas armazena quando há premiação (4+ acertos ou mês acertado)
    """

    __tablename__ = 'resultados_apostas_historicas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aposta_id = db.Column(db.Integer, db.ForeignKey('apostas_historicas.id'), nullable=False, index=True)
    concurso = db.Column(db.Integer, nullable=False, index=True)

    # Resultado
    quantidade_acertos = db.Column(db.Integer, nullable=False)
    acertou_mes = db.Column(db.Boolean, default=False)

    # Números que acertou (armazenados como string)
    numeros_acertados = db.Column(db.String(100), nullable=True)

    # Valor do prêmio neste concurso
    valor_premio = db.Column(db.Float, default=0.0)

    # Faixa de premiação
    faixa_premiacao = db.Column(db.String(20), nullable=True)  # '4_acertos', '5_acertos', etc.

    __table_args__ = (
        Index('idx_resultado_aposta', 'aposta_id'),
        Index('idx_resultado_concurso', 'concurso'),
        Index('idx_resultado_acertos', 'quantidade_acertos'),
    )

    def __repr__(self):
        return f'<ResultadoApostaHistorica Aposta {self.aposta_id} - Concurso {self.concurso}>'

    def get_numeros_acertados_lista(self):
        """Retorna os números acertados como lista"""
        if self.numeros_acertados:
            return [int(n) for n in self.numeros_acertados.split(',')]
        return []

    def to_dict(self):
        return {
            'id': self.id,
            'aposta_id': self.aposta_id,
            'concurso': self.concurso,
            'quantidade_acertos': self.quantidade_acertos,
            'acertou_mes': self.acertou_mes,
            'numeros_acertados': self.get_numeros_acertados_lista(),
            'valor_premio': self.valor_premio,
            'faixa_premiacao': self.faixa_premiacao
        }

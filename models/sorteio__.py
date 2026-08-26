# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from datetime import datetime
from sqlalchemy import Index
from flask_sqlalchemy import SQLAlchemy

# Criar instância do db aqui
db = SQLAlchemy()

class Sorteio(db.Model):
    """
    Modelo para armazenar os resultados dos sorteios do Dia de Sorte
    ATUALIZADO COM CAMPOS DA API CAIXA
    """

    __tablename__ = 'sorteios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    concurso = db.Column(db.Integer, unique=True, nullable=False, index=True)

    posicao_1 = db.Column(db.Integer, nullable=False)
    posicao_2 = db.Column(db.Integer, nullable=False)
    posicao_3 = db.Column(db.Integer, nullable=False)
    posicao_4 = db.Column(db.Integer, nullable=False)
    posicao_5 = db.Column(db.Integer, nullable=False)
    posicao_6 = db.Column(db.Integer, nullable=False)
    posicao_7 = db.Column(db.Integer, nullable=False)

    mes_sorte = db.Column(db.Integer, nullable=False)
    data_sorteio = db.Column(db.Date, nullable=False, index=True)

    # CAMPOS DE PREMIAÇÃO
    # Faixa 1 - 7 acertos
    ganhadores_7_acertos = db.Column(db.Integer, default=0)
    valor_premio_7_acertos = db.Column(db.Float, default=0.0)

    # Faixa 2 - 6 acertos
    ganhadores_6_acertos = db.Column(db.Integer, default=0)
    valor_premio_6_acertos = db.Column(db.Float, default=0.0)

    # Faixa 3 - 5 acertos (fixo R$ 25,00)
    ganhadores_5_acertos = db.Column(db.Integer, default=0)
    valor_premio_5_acertos = db.Column(db.Float, default=25.0)

    # Faixa 4 - 4 acertos (fixo R$ 5,00)
    ganhadores_4_acertos = db.Column(db.Integer, default=0)
    valor_premio_4_acertos = db.Column(db.Float, default=5.0)

    # Faixa 5 - Mês da Sorte (fixo R$ 2,50)
    ganhadores_mes_sorte = db.Column(db.Integer, default=0)
    valor_premio_mes_sorte = db.Column(db.Float, default=2.5)

    # CAMPOS ADICIONAIS DA API (já existiam)
    acumulado = db.Column(db.Boolean, default=False)
    valor_arrecadado = db.Column(db.Float, default=0.0)
    valor_acumulado_proximo_concurso = db.Column(db.Float, default=0.0)
    valor_estimado_proximo_concurso = db.Column(db.Float, default=0.0)

    # ========================================================================
    # NOVOS CAMPOS ADICIONADOS PELA MIGRATION (ADICIONAR ESTAS LINHAS!)
    # ========================================================================
    data_proximo_concurso = db.Column(db.Date)
    numero_concurso_proximo = db.Column(db.Integer)
    data_apuracao = db.Column(db.Date)
    numero_concurso_anterior = db.Column(db.Integer)
    local_sorteio = db.Column(db.String(200))
    municipio_uf_sorteio = db.Column(db.String(200))
    valor_acumulado_concurso_especial = db.Column(db.Float, default=0.0)
    ultimo_concurso = db.Column(db.Boolean, default=False)
    # ========================================================================

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_concurso_data', 'concurso', 'data_sorteio'),
        Index('idx_mes_sorte', 'mes_sorte'),
    )

    def __repr__(self):
        return f'<Sorteio {self.concurso} - {self.data_sorteio}>'

    def to_dict(self):
        return {
            'id': self.id,
            'concurso': self.concurso,
            'posicoes': {
                'posicao_1': self.posicao_1,
                'posicao_2': self.posicao_2,
                'posicao_3': self.posicao_3,
                'posicao_4': self.posicao_4,
                'posicao_5': self.posicao_5,
                'posicao_6': self.posicao_6,
                'posicao_7': self.posicao_7,
            },
            'mes_sorte': self.mes_sorte,
            'mes_sorte_nome': self.get_nome_mes(),
            'data_sorteio': self.data_sorteio.strftime('%d/%m/%Y') if self.data_sorteio else None,
            'premiacao': {
                '7_acertos': {
                    'ganhadores': self.ganhadores_7_acertos,
                    'valor_premio': self.valor_premio_7_acertos
                },
                '6_acertos': {
                    'ganhadores': self.ganhadores_6_acertos,
                    'valor_premio': self.valor_premio_6_acertos
                },
                '5_acertos': {
                    'ganhadores': self.ganhadores_5_acertos,
                    'valor_premio': self.valor_premio_5_acertos
                },
                '4_acertos': {
                    'ganhadores': self.ganhadores_4_acertos,
                    'valor_premio': self.valor_premio_4_acertos
                },
                'mes_sorte': {
                    'ganhadores': self.ganhadores_mes_sorte,
                    'valor_premio': self.valor_premio_mes_sorte
                }
            },
            'acumulado': self.acumulado,
            'valor_arrecadado': self.valor_arrecadado,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M:%S') if self.criado_em else None
        }

    def get_posicoes_lista(self):
        return [
            self.posicao_1, self.posicao_2, self.posicao_3, self.posicao_4,
            self.posicao_5, self.posicao_6, self.posicao_7
        ]

    def get_nome_mes(self):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(self.mes_sorte, 'Desconhecido')

    def tem_numero(self, numero):
        return numero in self.get_posicoes_lista()

    def tem_numero_na_posicao(self, numero, posicao):
        if posicao < 1 or posicao > 7:
            return False
        posicoes = self.get_posicoes_lista()
        return posicoes[posicao - 1] == numero

    def tem_premiacao_cadastrada(self):
        """Verifica se já tem dados de premiação cadastrados"""
        return (self.ganhadores_7_acertos is not None or
                self.ganhadores_6_acertos is not None or
                self.valor_premio_7_acertos > 0 or
                self.valor_premio_6_acertos > 0)

    @staticmethod
    def get_range_numeros():
        return range(1, 32)

    @staticmethod
    def validar_numero(numero):
        return 1 <= numero <= 31

    @staticmethod
    def validar_mes(mes):
        return 1 <= mes <= 12


# ============================================================================
# MÓDULO DE EVENTOS INTUITIVOS (Sonhos, Fatos e Sinais)
# ============================================================================

class EventoIntuitivo(db.Model):
    """
    Modelo para armazenar eventos intuitivos (sonhos, fatos, sinais)
    que podem gerar palpites para loterias
    """
    __tablename__ = 'eventos_intuitivos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Dados do evento
    tipo = db.Column(db.String(50), nullable=False)  # sonho, fato, sinal, simbolico, outro
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False, index=True)

    # Características do evento
    intensidade = db.Column(db.Integer, default=3)  # 1 a 5
    emocao = db.Column(db.String(50))  # alegria, neutro, estranho, apreensao, medo, surpresa
    tags = db.Column(db.String(500))  # palavras-chave separadas por vírgula

    # Interpretação
    interpretacao_simbolica = db.Column(db.Text)
    observacoes = db.Column(db.Text)

    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    apostas = db.relationship('ApostaIntuitiva', backref='evento', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_tipo_data', 'tipo', 'data_evento'),
    )

    def __repr__(self):
        return f'<EventoIntuitivo {self.id} - {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'data_evento': self.data_evento.strftime('%d/%m/%Y %H:%M') if self.data_evento else None,
            'intensidade': self.intensidade,
            'emocao': self.emocao,
            'tags': self.tags.split(',') if self.tags else [],
            'interpretacao_simbolica': self.interpretacao_simbolica,
            'observacoes': self.observacoes,
            'total_apostas': len(self.apostas),
            'modalidades': list(set([a.modalidade for a in self.apostas])),
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M:%S') if self.criado_em else None,
            'atualizado_em': self.atualizado_em.strftime('%d/%m/%Y %H:%M:%S') if self.atualizado_em else None
        }

    def get_status(self):
        """Retorna o status geral do evento (conferido, parcial, pendente)"""
        if not self.apostas:
            return 'sem_apostas'

        total = len(self.apostas)
        conferidas = sum(1 for a in self.apostas if a.resultado)

        if conferidas == 0:
            return 'pendente'
        elif conferidas == total:
            return 'conferido'
        else:
            return 'parcial'

    def get_total_acertos(self):
        """Retorna o total de acertos em todas as apostas"""
        return sum(r.acertos for a in self.apostas if a.resultado for r in [a.resultado])

    def get_melhor_jogo(self):
        """Retorna a aposta com mais acertos"""
        if not self.apostas:
            return None

        apostas_com_resultado = [a for a in self.apostas if a.resultado]
        if not apostas_com_resultado:
            return None

        return max(apostas_com_resultado, key=lambda a: a.resultado.acertos)

    def get_apostas_dict(self):
        """Retorna as apostas como lista de dicionários (para JSON)"""
        return [a.to_dict() for a in self.apostas]


class ApostaIntuitiva(db.Model):
    """
    Modelo para armazenar apostas geradas a partir de eventos intuitivos
    """
    __tablename__ = 'apostas_intuitivas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos_intuitivos.id'), nullable=False, index=True)

    # Dados da aposta
    modalidade = db.Column(db.String(50), nullable=False)  # mega, quina, lotofacil, etc.
    numeros = db.Column(db.Text, nullable=False)  # JSON string com array de números

    # Campos específicos por modalidade
    mes_sorte = db.Column(db.Integer)  # Dia de Sorte (1-12)
    time_coracao = db.Column(db.String(100))  # Timemania
    trevos = db.Column(db.String(20))  # +Milionária (2 trevos)

    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    resultado = db.relationship('ResultadoConferido', backref='aposta', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ApostaIntuitiva {self.id} - {self.modalidade}>'

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'evento_id': self.evento_id,
            'modalidade': self.modalidade,
            'numeros': json.loads(self.numeros) if self.numeros else [],
            'mes_sorte': self.mes_sorte,
            'time_coracao': self.time_coracao,
            'trevos': self.trevos,
            'tem_resultado': self.resultado is not None,
            'resultado': self.resultado.to_dict() if self.resultado else None,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M:%S') if self.criado_em else None
        }

    def get_numeros_lista(self):
        """Retorna os números como lista de inteiros"""
        import json
        return json.loads(self.numeros) if self.numeros else []


class ResultadoConferido(db.Model):
    """
    Modelo para armazenar resultados conferidos de apostas intuitivas
    """
    __tablename__ = 'resultados_conferidos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aposta_id = db.Column(db.Integer, db.ForeignKey('apostas_intuitivas.id'), nullable=False, unique=True, index=True)

    # Dados do concurso
    concurso = db.Column(db.Integer, nullable=False)
    data_sorteio = db.Column(db.Date)

    # Resultado oficial
    numeros_sorteados = db.Column(db.Text, nullable=False)  # JSON string
    mes_sorteado = db.Column(db.Integer)  # Dia de Sorte
    time_sorteado = db.Column(db.String(100))  # Timemania
    trevos_sorteados = db.Column(db.String(20))  # +Milionária

    # Análise
    acertos = db.Column(db.Integer, default=0, nullable=False)
    acertou_mes = db.Column(db.Boolean, default=False)  # Dia de Sorte
    acertou_time = db.Column(db.Boolean, default=False)  # Timemania
    acertos_trevos = db.Column(db.Integer, default=0)  # +Milionária

    premiacao = db.Column(db.Float)  # valor do prêmio (se houver)

    # Controle
    origem = db.Column(db.String(20), default='manual')  # manual ou api
    conferido_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ResultadoConferido {self.id} - Concurso {self.concurso}>'

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'aposta_id': self.aposta_id,
            'concurso': self.concurso,
            'data_sorteio': self.data_sorteio.strftime('%d/%m/%Y') if self.data_sorteio else None,
            'numeros_sorteados': json.loads(self.numeros_sorteados) if self.numeros_sorteados else [],
            'mes_sorteado': self.mes_sorteado,
            'time_sorteado': self.time_sorteado,
            'trevos_sorteados': self.trevos_sorteados,
            'acertos': self.acertos,
            'acertou_mes': self.acertou_mes,
            'acertou_time': self.acertou_time,
            'acertos_trevos': self.acertos_trevos,
            'premiacao': self.premiacao,
            'origem': self.origem,
            'conferido_em': self.conferido_em.strftime('%d/%m/%Y %H:%M:%S') if self.conferido_em else None
        }

    def get_numeros_sorteados_lista(self):
        """Retorna os números sorteados como lista de inteiros"""
        import json
        return json.loads(self.numeros_sorteados) if self.numeros_sorteados else []

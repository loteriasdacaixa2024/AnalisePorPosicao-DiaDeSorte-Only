# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Módulo: Eventos Intuitivos SIMPLIFICADO

"""
ESTE ARQUIVO VAI EM: models/eventos_intuitivos.py

IMPORTANTE: Adicione ao final de models/__init__.py:
    from models.eventos_intuitivos import EventoIntuitivo, ApostaIntuitiva, ConferenciaResultado
"""

from datetime import datetime
from models.shared import db
import json


class EventoIntuitivo(db.Model):
    """
    Registra eventos intuitivos (sonhos, fatos, sinais)
    """
    __tablename__ = 'eventos_intuitivos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Dados básicos
    tipo = db.Column(db.String(50), nullable=False)  # sonho, fato, sinal, outro
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)

    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    apostas = db.relationship('ApostaIntuitiva', backref='evento', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<EventoIntuitivo {self.id} - {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'data_evento': self.data_evento.strftime('%d/%m/%Y %H:%M'),
            'total_apostas': len(self.apostas),
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M')
        }


class ApostaIntuitiva(db.Model):
    """
    Aposta gerada a partir de um evento
    """
    __tablename__ = 'apostas_intuitivas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos_intuitivos.id'), nullable=False)

    # Dados da aposta
    modalidade = db.Column(db.String(50), nullable=False)  # mega, quina, lotofacil, diadesorte
    numeros = db.Column(db.Text, nullable=False)  # JSON: [1,2,3,...]
    mes_sorte = db.Column(db.Integer)  # Apenas Dia de Sorte (1-12)

    # CAMPO IMPORTANTE: Como chegou nos números
    interpretacao = db.Column(db.Text)  # "Usei as iniciais", "Contei letras", "Números gêmeos"

    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento (um-para-um)
    conferencia = db.relationship('ConferenciaResultado', backref='aposta', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ApostaIntuitiva {self.id} - {self.modalidade}>'

    def get_numeros_lista(self):
        """Retorna números como lista"""
        return json.loads(self.numeros) if self.numeros else []

    def to_dict(self):
        return {
            'id': self.id,
            'evento_id': self.evento_id,
            'modalidade': self.modalidade,
            'numeros': self.get_numeros_lista(),
            'mes_sorte': self.mes_sorte,
            'interpretacao': self.interpretacao,
            'tem_conferencia': self.conferencia is not None,
            'conferencia': self.conferencia.to_dict() if self.conferencia else None,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M')
        }


class ConferenciaResultado(db.Model):
    """
    Resultado da conferência de uma aposta
    """
    __tablename__ = 'conferencias_resultados'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aposta_id = db.Column(db.Integer, db.ForeignKey('apostas_intuitivas.id'), nullable=False, unique=True)

    # Dados do concurso
    concurso = db.Column(db.Integer, nullable=False)
    data_sorteio = db.Column(db.Date)

    # Resultado
    numeros_sorteados = db.Column(db.Text, nullable=False)  # JSON: [1,2,3,...]
    mes_sorteado = db.Column(db.Integer)  # Dia de Sorte

    # Análise
    acertos = db.Column(db.Integer, default=0, nullable=False)
    acertou_mes = db.Column(db.Boolean, default=False)

    # CAMPO IMPORTANTE: Análise retrospectiva
    analise_final = db.Column(db.Text)  # "Funcionou porque...", "Não funcionou porque..."

    # Timestamps
    conferido_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    analise_adicionada_em = db.Column(db.DateTime)

    def __repr__(self):
        return f'<ConferenciaResultado {self.id} - Concurso {self.concurso}>'

    def get_numeros_sorteados_lista(self):
        """Retorna números sorteados como lista"""
        return json.loads(self.numeros_sorteados) if self.numeros_sorteados else []

    def to_dict(self):
        return {
            'id': self.id,
            'aposta_id': self.aposta_id,
            'concurso': self.concurso,
            'data_sorteio': self.data_sorteio.strftime('%d/%m/%Y') if self.data_sorteio else None,
            'numeros_sorteados': self.get_numeros_sorteados_lista(),
            'mes_sorteado': self.mes_sorteado,
            'acertos': self.acertos,
            'acertou_mes': self.acertou_mes,
            'analise_final': self.analise_final,
            'conferido_em': self.conferido_em.strftime('%d/%m/%Y %H:%M'),
            'analise_adicionada_em': self.analise_adicionada_em.strftime('%d/%m/%Y %H:%M') if self.analise_adicionada_em else None
        }

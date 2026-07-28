# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Models: Eventos Intuitivos SIMPLIFICADO

"""
ESTE ARQUIVO VAI EM: models/eventos_intuitivos.py

SOLUÇÃO DEFINITIVA PARA IMPORTAÇÃO CIRCULAR:
- Importa SQLAlchemy e cria uma referência ao db QUE JÁ EXISTE
- NÃO importa de models nem de models.sorteio
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

# SOLUÇÃO: Criar uma instância vazia aqui que será substituída pelo db real
# Isso evita importação circular!
db = SQLAlchemy()


class EventoIntuitivo(db.Model):
    """
    Evento intuitivo (sonho, fato, sinal) que pode gerar múltiplas apostas
    """
    __tablename__ = 'eventos_intuitivos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(50), nullable=False)  # sonho, fato, sinal, outro
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento: um evento pode ter várias apostas
    apostas = db.relationship('ApostaIntuitiva', backref='evento', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<EventoIntuitivo {self.id}: {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'data_evento': self.data_evento.strftime('%d/%m/%Y %H:%M'),
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M'),
            'apostas': [aposta.to_dict() for aposta in self.apostas],
            'total_apostas': len(self.apostas)
        }


class ApostaIntuitiva(db.Model):
    """
    Aposta gerada a partir de um evento intuitivo
    Pode ser para qualquer loteria (Mega, Quina, Lotofácil, Dia de Sorte, etc.)
    """
    __tablename__ = 'apostas_intuitivas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos_intuitivos.id'), nullable=False)
    
    modalidade = db.Column(db.String(50), nullable=False)  # mega, quina, lotofacil, diadesorte
    numeros = db.Column(db.Text, nullable=False)  # JSON array
    mes_sorte = db.Column(db.Integer)  # Apenas para Dia de Sorte
    
    # NOVO: Campo para registrar COMO chegou nos números
    interpretacao = db.Column(db.Text)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento: uma aposta pode ter uma conferência
    conferencia = db.relationship('ConferenciaResultado', backref='aposta', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ApostaIntuitiva {self.id}: {self.modalidade}>'

    def get_numeros_lista(self):
        """Retorna os números como lista Python"""
        return json.loads(self.numeros)

    def to_dict(self):
        return {
            'id': self.id,
            'evento_id': self.evento_id,
            'modalidade': self.modalidade,
            'numeros': self.get_numeros_lista(),
            'mes_sorte': self.mes_sorte,
            'interpretacao': self.interpretacao,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M'),
            'conferencia': self.conferencia.to_dict() if self.conferencia else None,
            'tem_conferencia': self.conferencia is not None
        }


class ConferenciaResultado(db.Model):
    """
    Resultado da conferência de uma aposta com o sorteio real
    """
    __tablename__ = 'conferencias_resultados'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aposta_id = db.Column(db.Integer, db.ForeignKey('apostas_intuitivas.id'), nullable=False, unique=True)
    
    concurso = db.Column(db.Integer, nullable=False)
    data_sorteio = db.Column(db.Date)
    numeros_sorteados = db.Column(db.Text, nullable=False)  # JSON array
    mes_sorteado = db.Column(db.Integer)  # Para Dia de Sorte
    
    acertos = db.Column(db.Integer, default=0, nullable=False)
    acertou_mes = db.Column(db.Boolean, default=False)
    
    # NOVO: Campo para análise retrospectiva
    analise_final = db.Column(db.Text)
    
    conferido_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    analise_adicionada_em = db.Column(db.DateTime)

    def __repr__(self):
        return f'<ConferenciaResultado {self.id}: {self.acertos} acertos>'

    def get_numeros_sorteados_lista(self):
        """Retorna os números sorteados como lista Python"""
        return json.loads(self.numeros_sorteados)

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


# IMPORTANTE: Quando este módulo for importado, o db será substituído pelo db real de sorteio.py
# Isso acontece automaticamente porque Python usa a mesma instância de db para todos os modelos

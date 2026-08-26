# -*- coding: utf-8 -*-
"""Registro JSON de acertos — Laboratório de Alterações (Dia de Sorte)."""

from datetime import datetime

from models.shared import db


class LaboratorioAlteracoesRegistro(db.Model):
    """
    Persiste somente desempenho em acertos (faixas 4–7) e resumo comparativo,
    em JSON para análises futuras.
    """

    __tablename__ = 'laboratorio_alteracoes_registro'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    concurso_ref = db.Column(db.Integer, nullable=False, index=True)
    origem = db.Column(db.String(120), default='manual')
    dados_json = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'concurso_ref': self.concurso_ref,
            'origem': self.origem,
        }

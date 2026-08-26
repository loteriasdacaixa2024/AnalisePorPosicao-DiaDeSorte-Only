"""
Modelo de banco de dados para Análises de Apostas
"""

# from extensions import db
from models import db
from datetime import datetime


class AnaliseAposta(db.Model):
    """Modelo para armazenar análises de apostas realizadas"""

    __tablename__ = 'analises_apostas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Informações gerais da análise
    data_analise = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    usuario_id = db.Column(db.Integer, nullable=True, index=True)  # FK se houver sistema de usuários
    tipo_upload = db.Column(db.String(50), nullable=False)  # 'json', 'texto', 'drag_drop', etc.

    # Quantidades
    total_apostas = db.Column(db.Integer, nullable=False, default=0)
    total_concursos = db.Column(db.Integer, nullable=False, default=0)

    # Período analisado
    concurso_inicio = db.Column(db.Integer, nullable=True, index=True)
    concurso_fim = db.Column(db.Integer, nullable=True, index=True)
    data_inicio = db.Column(db.Date, nullable=True, index=True)
    data_fim = db.Column(db.Date, nullable=True, index=True)

    # Resumo de resultados
    apostas_premiadas = db.Column(db.Integer, nullable=False, default=0)
    total_premios_4 = db.Column(db.Integer, nullable=False, default=0)
    total_premios_5 = db.Column(db.Integer, nullable=False, default=0)
    total_premios_6 = db.Column(db.Integer, nullable=False, default=0)
    total_premios_7 = db.Column(db.Integer, nullable=False, default=0)

    # Dados JSON detalhados
    metricas_json = db.Column(db.Text, nullable=True)  # Estatísticas completas em JSON
    apostas_detalhadas_json = db.Column(db.Text, nullable=True)  # Apostas e resultados detalhados
    insights_json = db.Column(db.Text, nullable=True)  # Insights gerados automaticamente

    # Status e metadados
    status = db.Column(db.String(50), nullable=False, default='Concluído')  # 'Concluído', 'Erro', etc.
    observacoes = db.Column(db.Text, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<AnaliseAposta {self.id} - {self.data_analise.strftime("%Y-%m-%d %H:%M")}>'

    def to_dict(self):
        """Converte para dicionário"""
        import json

        return {
            'id': self.id,
            'data_analise': self.data_analise.strftime('%Y-%m-%d %H:%M:%S'),
            'usuario_id': self.usuario_id,
            'tipo_upload': self.tipo_upload,
            'total_apostas': self.total_apostas,
            'total_concursos': self.total_concursos,
            'concurso_inicio': self.concurso_inicio,
            'concurso_fim': self.concurso_fim,
            'data_inicio': self.data_inicio.strftime('%Y-%m-%d') if self.data_inicio else None,
            'data_fim': self.data_fim.strftime('%Y-%m-%d') if self.data_fim else None,
            'apostas_premiadas': self.apostas_premiadas,
            'total_premios_4': self.total_premios_4,
            'total_premios_5': self.total_premios_5,
            'total_premios_6': self.total_premios_6,
            'total_premios_7': self.total_premios_7,
            'metricas': json.loads(self.metricas_json) if self.metricas_json else {},
            'apostas_detalhadas': json.loads(self.apostas_detalhadas_json) if self.apostas_detalhadas_json else [],
            'insights': json.loads(self.insights_json) if self.insights_json else [],
            'status': self.status,
            'observacoes': self.observacoes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @property
    def taxa_premiacao(self):
        """Calcula taxa de premiação percentual"""
        if self.total_apostas == 0:
            return 0
        return round((self.apostas_premiadas / self.total_apostas) * 100, 2)

    @property
    def total_premios(self):
        """Total de prêmios conquistados"""
        return self.total_premios_4 + self.total_premios_5 + self.total_premios_6 + self.total_premios_7

    @property
    def resumo_curto(self):
        """Resumo em uma linha"""
        return f"{self.total_apostas} apostas × {self.total_concursos} concursos = {self.total_premios} prêmios"



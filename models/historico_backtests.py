from models.shared import db
from datetime import datetime

class HistoricoBacktest(db.Model):
    __tablename__ = 'historico_backtests'

    id = db.Column(db.Integer, primary_key=True)
    nome_lote = db.Column(db.String(150), nullable=False)
    total_jogos = db.Column(db.Integer, nullable=False, default=0)
    
    # Premiações globais varridas do histórico
    acertos_7 = db.Column(db.Integer, nullable=False, default=0)
    acertos_6 = db.Column(db.Integer, nullable=False, default=0)
    acertos_5 = db.Column(db.Integer, nullable=False, default=0)
    acertos_4 = db.Column(db.Integer, nullable=False, default=0)
    
    # Outros metadados
    concurso_alvo = db.Column(db.String(50), nullable=True) # Ex: "Global", ou "1197"
    melhor_concurso_id = db.Column(db.Integer, nullable=True) # Qual concurso teve a pontuação máxima 
    data_execucao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome_lote': self.nome_lote,
            'total_jogos': self.total_jogos,
            'acertos_7': self.acertos_7,
            'acertos_6': self.acertos_6,
            'acertos_5': self.acertos_5,
            'acertos_4': self.acertos_4,
            'concurso_alvo': self.concurso_alvo,
            'melhor_concurso_id': self.melhor_concurso_id,
            'data_execucao': self.data_execucao.strftime('%d/%m/%Y %H:%M') if self.data_execucao else ''
        }

from models.shared import db
from datetime import datetime

class LocaisSorte(db.Model):
    __tablename__ = 'locais_sorte'

    id = db.Column(db.Integer, primary_key=True)
    modalidade = db.Column(db.String(50), nullable=False, index=True)
    concurso = db.Column(db.Integer, nullable=False, index=True)
    cidade = db.Column(db.String(150), nullable=True, index=True)
    unidade_loterica = db.Column(db.String(150), nullable=True, index=True)
    razao_social = db.Column(db.String(150), nullable=True)
    faixa_acertos = db.Column(db.String(50), nullable=True, index=True)
    qtd_numeros_apostados = db.Column(db.Integer, nullable=True)
    canal_vendas = db.Column(db.String(50), nullable=True)
    teimosinha = db.Column(db.String(20), nullable=True)
    tipo_aposta = db.Column(db.String(50), nullable=True, index=True)
    cotas = db.Column(db.Integer, nullable=True)
    qtd_premios_faixa = db.Column(db.Integer, nullable=True)
    premio = db.Column(db.String(50), nullable=True)
    valor_premio = db.Column(db.Float, nullable=True, default=0.0)
    data_importacao = db.Column(db.DateTime, default=datetime.utcnow)
    arquivo_origem = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'modalidade': self.modalidade,
            'concurso': self.concurso,
            'cidade': self.cidade,
            'unidade_loterica': self.unidade_loterica,
            'razao_social': self.razao_social,
            'faixa_acertos': self.faixa_acertos,
            'qtd_numeros_apostados': self.qtd_numeros_apostados,
            'canal_vendas': self.canal_vendas,
            'teimosinha': self.teimosinha,
            'tipo_aposta': self.tipo_aposta,
            'cotas': self.cotas,
            'qtd_premios_faixa': self.qtd_premios_faixa,
            'premio': self.premio,
            'valor_premio': self.valor_premio,
            'data_importacao': self.data_importacao.strftime('%d/%m/%Y %H:%M') if self.data_importacao else '',
            'arquivo_origem': self.arquivo_origem
        }

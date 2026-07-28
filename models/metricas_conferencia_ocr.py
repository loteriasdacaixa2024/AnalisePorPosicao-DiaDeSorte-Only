from models import db
from datetime import datetime
import json

class MetricasConferenciaOCR(db.Model):
    __tablename__ = 'metricas_conferencia_ocr'

    id = db.Column(db.Integer, primary_key=True)
    concurso = db.Column(db.Integer, unique=True, nullable=False)
    data_conferencia = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Métricas Financeiras
    total_apostas = db.Column(db.Integer, default=0)
    total_investido = db.Column(db.Float, default=0.0)
    total_ganho = db.Column(db.Float, default=0.0)
    lucro_prejuizo = db.Column(db.Float, default=0.0)
    
    # Métricas de Cobertura
    dezenas_cobertas_qtd = db.Column(db.Integer, default=0)
    cobertura_percentual = db.Column(db.Float, default=0.0)
    
    # Métricas Estratégicas Avançadas
    indice_redundancia = db.Column(db.Float, default=0.0)  # Total Dezenas Marcadas / Dezenas Únicas
    custo_por_dezena_unica = db.Column(db.Float, default=0.0) # Investimento Total / Dezenas Únicas
    
    # Armazenamento detalhado (JSON)
    # Lista de números únicos que foram jogados
    dezenas_jogadas_json = db.Column(db.Text, nullable=True) 
    # Lista de números do resultado oficial que NÃO foram jogados
    dezenas_nao_cobertas_json = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'concurso': self.concurso,
            'data_conferencia': self.data_conferencia.strftime('%d/%m/%Y %H:%M'),
            'financeiro': {
                'total_apostas': self.total_apostas,
                'investido': self.total_investido,
                'ganho': self.total_ganho,
                'lucro': self.lucro_prejuizo
            },
            'cobertura': {
                'qtd_coberta': self.dezenas_cobertas_qtd,
                'percentual': self.cobertura_percentual,
                'dezenas_jogadas': json.loads(self.dezenas_jogadas_json) if self.dezenas_jogadas_json else [],
                'dezenas_nao_cobertas': json.loads(self.dezenas_nao_cobertas_json) if self.dezenas_nao_cobertas_json else []
            },
            'estrategia': {
                'redundancia': self.indice_redundancia,
                'custo_dezena_unica': self.custo_por_dezena_unica
            }
        }

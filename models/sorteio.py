# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from datetime import datetime
from sqlalchemy import Index
from flask_sqlalchemy import SQLAlchemy


# Usar instância compartilhada
from models.shared import db

class Sorteio(db.Model):
    """
    Modelo para armazenar os resultados dos sorteios do Dia de Sorte
    """

    __tablename__ = 'sorteios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    concurso = db.Column(db.Integer, unique=True, nullable=False, index=True)

    # Números em ORDEM CRESCENTE (para análise por posição)
    posicao_1 = db.Column(db.Integer, nullable=False)
    posicao_2 = db.Column(db.Integer, nullable=False)
    posicao_3 = db.Column(db.Integer, nullable=False)
    posicao_4 = db.Column(db.Integer, nullable=False)
    posicao_5 = db.Column(db.Integer, nullable=False)
    posicao_6 = db.Column(db.Integer, nullable=False)
    posicao_7 = db.Column(db.Integer, nullable=False)

    # Números em ORDEM DE SORTEIO (ordem real em que foram sorteados)
    sorteio_1 = db.Column(db.Integer, nullable=True)
    sorteio_2 = db.Column(db.Integer, nullable=True)
    sorteio_3 = db.Column(db.Integer, nullable=True)
    sorteio_4 = db.Column(db.Integer, nullable=True)
    sorteio_5 = db.Column(db.Integer, nullable=True)
    sorteio_6 = db.Column(db.Integer, nullable=True)
    sorteio_7 = db.Column(db.Integer, nullable=True)

    mes_sorte = db.Column(db.Integer, nullable=False)
    data_sorteio = db.Column(db.Date, nullable=False, index=True)

    # NOVOS CAMPOS - PREMIAÇÃO
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

    # Dados adicionais da API
    acumulado = db.Column(db.Boolean, default=False)
    valor_arrecadado = db.Column(db.Float, default=0.0)
    valor_acumulado_proximo_concurso = db.Column(db.Float, default=0.0)
    valor_estimado_proximo_concurso = db.Column(db.Float, default=0.0)

    # Campos para informações do próximo concurso
    numero_concurso_proximo = db.Column(db.Integer, nullable=True)
    data_proximo_concurso = db.Column(db.Date, nullable=True)

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
                'posicao_1': self.sorteio_1 if self.sorteio_1 is not None else self.posicao_1,
                'posicao_2': self.sorteio_2 if self.sorteio_2 is not None else self.posicao_2,
                'posicao_3': self.sorteio_3 if self.sorteio_3 is not None else self.posicao_3,
                'posicao_4': self.sorteio_4 if self.sorteio_4 is not None else self.posicao_4,
                'posicao_5': self.sorteio_5 if self.sorteio_5 is not None else self.posicao_5,
                'posicao_6': self.sorteio_6 if self.sorteio_6 is not None else self.posicao_6,
                'posicao_7': self.sorteio_7 if self.sorteio_7 is not None else self.posicao_7,
            },
            'ordem_crescente': {
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
        """Retorna números em ORDEM CRESCENTE (posicao_1 a posicao_7)"""
        return [
            self.posicao_1, self.posicao_2, self.posicao_3, self.posicao_4,
            self.posicao_5, self.posicao_6, self.posicao_7
        ]

    def get_ordem_sorteio_lista(self):
        """Retorna números em ORDEM DE SORTEIO (sorteio_1 a sorteio_7)"""
        # Se as colunas de ordem de sorteio estão preenchidas, usa elas
        if self.sorteio_1 is not None:
            return [
                self.sorteio_1, self.sorteio_2, self.sorteio_3, self.sorteio_4,
                self.sorteio_5, self.sorteio_6, self.sorteio_7
            ]
        # Fallback: retorna ordem crescente (mesma coisa que get_posicoes_lista)
        return self.get_posicoes_lista()

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


# Importar modelos de Eventos Intuitivos (no final para evitar circular import)
from models.eventos_intuitivos import EventoIntuitivo, ApostaIntuitiva, ConferenciaResultado

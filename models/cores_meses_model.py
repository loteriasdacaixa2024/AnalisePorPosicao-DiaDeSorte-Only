# -*- coding: utf-8 -*-
"""
Modelo para armazenar as cores personalizadas dos 12 meses
Sistema: Análise por Posição - Dia de Sorte
Desenvolvido para: Márcio Fernando Maia
"""

from datetime import datetime
from models.shared import db


class CoresMeses(db.Model):
    """
    Modelo para armazenar as cores dos 12 meses do Dia de Sorte.
    Permite personalização das cores usadas em todo o sistema.
    """

    __tablename__ = 'cores_meses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mes = db.Column(db.Integer, nullable=False, unique=True, index=True)  # 0-11 (Janeiro-Dezembro)
    cor_hex = db.Column(db.String(7), nullable=False)  # Formato: #RRGGBB
    nome_mes = db.Column(db.String(20), nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    @staticmethod
    def criar_cores_padrao():
        """
        Cria as cores padrão dos 12 meses se não existirem.
        Cores originais do sistema.
        """
        cores_padrao = [
            {'mes': 0, 'cor_hex': '#f0e9ee', 'nome_mes': 'Janeiro'},
            {'mes': 1, 'cor_hex': '#f0c282', 'nome_mes': 'Fevereiro'},
            {'mes': 2, 'cor_hex': '#686b69', 'nome_mes': 'Março'},
            {'mes': 3, 'cor_hex': '#ce3500', 'nome_mes': 'Abril'},
            {'mes': 4, 'cor_hex': '#457725', 'nome_mes': 'Maio'},
            {'mes': 5, 'cor_hex': '#a2a7ad', 'nome_mes': 'Junho'},
            {'mes': 6, 'cor_hex': '#98ddde', 'nome_mes': 'Julho'},
            {'mes': 7, 'cor_hex': '#2c8587', 'nome_mes': 'Agosto'},
            {'mes': 8, 'cor_hex': '#0d00f2', 'nome_mes': 'Setembro'},
            {'mes': 9, 'cor_hex': '#ffff66', 'nome_mes': 'Outubro'},
            {'mes': 10, 'cor_hex': '#cc99ff', 'nome_mes': 'Novembro'},
            {'mes': 11, 'cor_hex': '#99ff33', 'nome_mes': 'Dezembro'},
        ]

        for cor_data in cores_padrao:
            # Verifica se já existe
            cor_existente = CoresMeses.query.filter_by(mes=cor_data['mes']).first()

            if not cor_existente:
                nova_cor = CoresMeses(
                    mes=cor_data['mes'],
                    cor_hex=cor_data['cor_hex'],
                    nome_mes=cor_data['nome_mes']
                )
                db.session.add(nova_cor)

        try:
            db.session.commit()
            print(f"[OK] Cores padrão dos meses inicializadas!")
        except Exception as e:
            db.session.rollback()
            print(f"[ERRO] Erro ao inicializar cores dos meses: {str(e)}")


    @staticmethod
    def obter_todas_cores():
        """
        Retorna todas as cores dos meses ordenadas (0-11).
        """
        cores = CoresMeses.query.order_by(CoresMeses.mes).all()

        if not cores or len(cores) < 12:
            # Se não existem cores ou estão incompletas, criar as padrão
            CoresMeses.criar_cores_padrao()
            cores = CoresMeses.query.order_by(CoresMeses.mes).all()

        return cores


    @staticmethod
    def obter_cor_por_mes(mes):
        """
        Retorna a cor de um mês específico (0-11).
        """
        cor = CoresMeses.query.filter_by(mes=mes).first()

        if cor:
            return cor.cor_hex

        # Se não encontrar, retornar cor padrão
        cores_padrao = [
            '#f0e9ee', '#f0c282', '#686b69', '#ce3500',
            '#457725', '#a2a7ad', '#98ddde', '#2c8587',
            '#0d00f2', '#ffff66', '#cc99ff', '#99ff33'
        ]

        if 0 <= mes < 12:
            return cores_padrao[mes]

        return '#cccccc'  # Cor padrão cinza


    @staticmethod
    def atualizar_cor(mes, nova_cor_hex):
        """
        Atualiza a cor de um mês específico.
        """
        if not (0 <= mes < 12):
            return False, "Mês inválido. Deve estar entre 0 (Janeiro) e 11 (Dezembro)."

        # Validar formato hexadecimal
        if not nova_cor_hex.startswith('#') or len(nova_cor_hex) != 7:
            return False, "Formato de cor inválido. Use o formato #RRGGBB (ex: #ff0000)"

        try:
            # Verificar se a cor existe
            cor = CoresMeses.query.filter_by(mes=mes).first()

            if cor:
                cor.cor_hex = nova_cor_hex
                cor.atualizado_em = datetime.utcnow()
            else:
                # Criar nova
                nomes_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

                nova_cor = CoresMeses(
                    mes=mes,
                    cor_hex=nova_cor_hex,
                    nome_mes=nomes_meses[mes]
                )
                db.session.add(nova_cor)

            db.session.commit()
            return True, f"Cor do mês {mes + 1} atualizada com sucesso!"

        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao atualizar cor: {str(e)}"


    @staticmethod
    def restaurar_cores_padrao():
        """
        Restaura todas as cores para os valores padrão.
        """
        cores_padrao = [
            {'mes': 0, 'cor_hex': '#f0e9ee'},
            {'mes': 1, 'cor_hex': '#f0c282'},
            {'mes': 2, 'cor_hex': '#686b69'},
            {'mes': 3, 'cor_hex': '#ce3500'},
            {'mes': 4, 'cor_hex': '#457725'},
            {'mes': 5, 'cor_hex': '#a2a7ad'},
            {'mes': 6, 'cor_hex': '#98ddde'},
            {'mes': 7, 'cor_hex': '#2c8587'},
            {'mes': 8, 'cor_hex': '#0d00f2'},
            {'mes': 9, 'cor_hex': '#ffff66'},
            {'mes': 10, 'cor_hex': '#cc99ff'},
            {'mes': 11, 'cor_hex': '#99ff33'},
        ]

        try:
            for cor_data in cores_padrao:
                cor = CoresMeses.query.filter_by(mes=cor_data['mes']).first()
                if cor:
                    cor.cor_hex = cor_data['cor_hex']
                    cor.atualizado_em = datetime.utcnow()

            db.session.commit()
            return True, "Cores restauradas para os valores padrão!"

        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao restaurar cores: {str(e)}"


    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'mes': self.mes,
            'cor_hex': self.cor_hex,
            'nome_mes': self.nome_mes,
            'atualizado_em': self.atualizado_em.strftime('%d/%m/%Y %H:%M:%S') if self.atualizado_em else None
        }

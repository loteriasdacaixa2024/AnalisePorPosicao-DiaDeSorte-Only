# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia  
# Service: Eventos Intuitivos SIMPLIFICADO

"""
ESTE ARQUIVO VAI EM: services/eventos_intuitivos_service.py
"""

from datetime import datetime
from models.sorteio import db
from models.eventos_intuitivos import EventoIntuitivo, ApostaIntuitiva, ConferenciaResultado
import json


class EventosIntuitivosService:
    """
    Service SIMPLIFICADO para gerenciar eventos intuitivos
    """

    @staticmethod
    def listar_eventos():
        """
        Lista todos os eventos (mais recentes primeiro)
        """
        eventos = EventoIntuitivo.query.order_by(EventoIntuitivo.data_evento.desc()).all()
        return [e.to_dict() for e in eventos]

    @staticmethod
    def obter_evento(evento_id):
        """
        Obtém um evento específico com suas apostas
        """
        evento = EventoIntuitivo.query.get(evento_id)
        if not evento:
            return None

        dados = evento.to_dict()
        dados['apostas'] = [a.to_dict() for a in evento.apostas]
        return dados

    @staticmethod
    def criar_evento(dados):
        """
        Cria um novo evento
        
        Args:
            dados (dict): {
                'tipo': 'sonho',
                'titulo': 'Título',
                'descricao': 'Descrição',
                'data_evento': '2025-12-09 10:30'
            }
        """
        evento = EventoIntuitivo(
            tipo=dados['tipo'],
            titulo=dados['titulo'],
            descricao=dados['descricao'],
            data_evento=datetime.fromisoformat(dados['data_evento'])
        )

        db.session.add(evento)
        db.session.commit()

        return evento.to_dict()

    @staticmethod
    def adicionar_aposta(evento_id, dados):
        """
        Adiciona uma aposta a um evento
        
        Args:
            evento_id (int): ID do evento
            dados (dict): {
                'modalidade': 'mega',
                'numeros': [1, 2, 3, 4, 5, 6],
                'mes_sorte': 1 (opcional, só Dia de Sorte),
                'interpretacao': 'Usei as iniciais dos nomes'
            }
        """
        evento = EventoIntuitivo.query.get(evento_id)
        if not evento:
            raise ValueError(f'Evento {evento_id} não encontrado')

        aposta = ApostaIntuitiva(
            evento_id=evento_id,
            modalidade=dados['modalidade'],
            numeros=json.dumps(dados['numeros']),
            mes_sorte=dados.get('mes_sorte'),
            interpretacao=dados.get('interpretacao')
        )

        db.session.add(aposta)
        db.session.commit()

        return aposta.to_dict()

    @staticmethod
    def conferir_resultado(aposta_id, dados):
        """
        Confere o resultado de uma aposta
        
        Args:
            aposta_id (int): ID da aposta
            dados (dict): {
                'concurso': 1234,
                'data_sorteio': '2025-12-09',
                'numeros_sorteados': [5, 10, 15, 20, 25, 30],
                'mes_sorteado': 1 (opcional, só Dia de Sorte)
            }
        """
        aposta = ApostaIntuitiva.query.get(aposta_id)
        if not aposta:
            raise ValueError(f'Aposta {aposta_id} não encontrada')

        # Calcular acertos
        numeros_aposta = set(aposta.get_numeros_lista())
        numeros_sorteados = set(dados['numeros_sorteados'])
        acertos = len(numeros_aposta & numeros_sorteados)

        # Verificar mês (se Dia de Sorte)
        acertou_mes = False
        if aposta.modalidade == 'diadesorte' and aposta.mes_sorte:
            acertou_mes = (aposta.mes_sorte == dados.get('mes_sorteado'))

        # Criar ou atualizar conferência
        conferencia = aposta.conferencia
        if not conferencia:
            conferencia = ConferenciaResultado(aposta_id=aposta_id)
            db.session.add(conferencia)

        conferencia.concurso = dados['concurso']
        conferencia.data_sorteio = datetime.strptime(dados['data_sorteio'], '%Y-%m-%d').date()
        conferencia.numeros_sorteados = json.dumps(dados['numeros_sorteados'])
        conferencia.mes_sorteado = dados.get('mes_sorteado')
        conferencia.acertos = acertos
        conferencia.acertou_mes = acertou_mes
        conferencia.conferido_em = datetime.utcnow()

        db.session.commit()

        return conferencia.to_dict()

    @staticmethod
    def adicionar_analise(conferencia_id, analise_texto):
        """
        Adiciona análise retrospectiva a uma conferência
        
        Args:
            conferencia_id (int): ID da conferência
            analise_texto (str): "Funcionou porque..." ou "Não funcionou porque..."
        """
        conferencia = ConferenciaResultado.query.get(conferencia_id)
        if not conferencia:
            raise ValueError(f'Conferência {conferencia_id} não encontrada')

        conferencia.analise_final = analise_texto
        conferencia.analise_adicionada_em = datetime.utcnow()

        db.session.commit()

        return conferencia.to_dict()

    @staticmethod
    def excluir_evento(evento_id):
        """
        Exclui um evento (e todas suas apostas/conferências em cascade)
        """
        evento = EventoIntuitivo.query.get(evento_id)
        if not evento:
            raise ValueError(f'Evento {evento_id} não encontrado')

        db.session.delete(evento)
        db.session.commit()

        return True

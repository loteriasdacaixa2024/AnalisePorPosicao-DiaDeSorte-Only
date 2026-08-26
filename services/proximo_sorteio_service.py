"""
Service para buscar informações do próximo sorteio DIRETO DO BANCO DE DADOS

Este service busca o último concurso cadastrado no banco e retorna
as informações do próximo sorteio que estão armazenadas nele.
"""

from models import Sorteio


class ProximoSorteioService:

    @staticmethod
    def obter_info_proximo_sorteio():
        """
        Busca informações do próximo sorteio do banco de dados.

        Retorna as informações do próximo concurso baseado no último
        concurso cadastrado no banco.

        Returns:
            dict: Informações do próximo sorteio ou erro
        """
        try:
            # CORRIGIDO: Busca SEMPRE pelo maior número de concurso
            # Isso garante que funciona mesmo durante atualização em lote
            ultimo_sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

            if not ultimo_sorteio:
                return {
                    'erro': 'Nenhum sorteio encontrado no banco de dados',
                    'disponivel': False
                }

            # Extrai informações do próximo concurso
            proximo_concurso = {
                'disponivel': True,

                # Informações do próximo concurso
                'numero_concurso': ultimo_sorteio.numero_concurso_proximo,
                'data_concurso': ultimo_sorteio.data_proximo_concurso.strftime('%d/%m/%Y') if ultimo_sorteio.data_proximo_concurso else None,
                'dia_semana': ProximoSorteioService._obter_dia_semana(ultimo_sorteio.data_proximo_concurso) if ultimo_sorteio.data_proximo_concurso else None,
                'valor_estimado': ultimo_sorteio.valor_estimado_proximo_concurso,
                'valor_acumulado': ultimo_sorteio.valor_acumulado_proximo_concurso,

                # Informações do último concurso (para referência)
                'ultimo_concurso': {
                    'numero': ultimo_sorteio.concurso,
                    'data': ultimo_sorteio.data_apuracao.strftime('%d/%m/%Y') if ultimo_sorteio.data_apuracao else ultimo_sorteio.data_sorteio.strftime('%d/%m/%Y'),
                    'acumulou': ultimo_sorteio.acumulado,
                    'ganhadores_7_acertos': ultimo_sorteio.ganhadores_7_acertos
                }
            }

            return proximo_concurso

        except Exception as e:
            return {
                'erro': f'Erro ao buscar próximo sorteio: {str(e)}',
                'disponivel': False
            }

    @staticmethod
    def _obter_dia_semana(data):
        """Retorna o nome do dia da semana para uma data"""
        if not data:
            return None

        dias = {
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }

        return dias.get(data.weekday(), '')

    @staticmethod
    def formatar_valor(valor):
        """Formata valor em reais"""
        if not valor:
            return 'R$ 0,00'

        return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

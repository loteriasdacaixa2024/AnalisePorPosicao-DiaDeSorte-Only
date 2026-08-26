"""
Serviço de Análise Visual - Dia de Sorte
Responsável por buscar e formatar dados dos concursos para análise visual
"""

from typing import Dict, List, Optional
from datetime import datetime
from models.sorteio import Sorteio


class AnaliseVisualService:
    """
    Service para análise visual de resultados do Dia de Sorte
    """

    # Mapeamento de dias da semana
    DIAS_SEMANA = {
        0: 'Segunda-feira',
        1: 'Terça-feira',
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }

    # Mapeamento de meses
    MESES = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    @staticmethod
    def buscar_todos_concursos(limite: Optional[int] = None, ordem: str = 'desc') -> List[Dict]:
        """
        Busca todos os concursos do banco de dados

        Args:
            limite: Quantidade máxima de concursos a retornar (None = todos)
            ordem: 'desc' (mais recente primeiro) ou 'asc' (mais antigo primeiro)

        Returns:
            Lista de dicionários com dados dos concursos
        """
        try:
            # Construir query
            query = Sorteio.query

            # Ordenação
            if ordem == 'desc':
                query = query.order_by(Sorteio.concurso.desc())
            else:
                query = query.order_by(Sorteio.concurso.asc())

            # Limite
            if limite:
                query = query.limit(limite)

            # Executar query
            sorteios = query.all()

            # Formatar resultados
            resultados = []
            for sorteio in sorteios:
                resultados.append(AnaliseVisualService._formatar_sorteio(sorteio))

            return resultados

        except Exception as e:
            print(f"Erro ao buscar concursos: {str(e)}")
            return []

    @staticmethod
    def buscar_concurso(numero_concurso: int) -> Optional[Dict]:
        """
        Busca um concurso específico

        Args:
            numero_concurso: Número do concurso

        Returns:
            Dicionário com dados do concurso ou None
        """
        try:
            sorteio = Sorteio.query.filter_by(concurso=numero_concurso).first()
            if sorteio:
                return AnaliseVisualService._formatar_sorteio(sorteio)
            return None
        except Exception as e:
            print(f"Erro ao buscar concurso {numero_concurso}: {str(e)}")
            return None

    @staticmethod
    def buscar_range_concursos(inicio: int, fim: int) -> List[Dict]:
        """
        Busca concursos em um intervalo

        Args:
            inicio: Número do primeiro concurso
            fim: Número do último concurso

        Returns:
            Lista de dicionários com dados dos concursos
        """
        try:
            sorteios = Sorteio.query.filter(
                Sorteio.concurso >= inicio,
                Sorteio.concurso <= fim
            ).order_by(Sorteio.concurso.desc()).all()

            return [AnaliseVisualService._formatar_sorteio(s) for s in sorteios]

        except Exception as e:
            print(f"Erro ao buscar range {inicio}-{fim}: {str(e)}")
            return []

    @staticmethod
    def obter_estatisticas_gerais() -> Dict:
        """
        Obtém estatísticas gerais dos concursos

        Returns:
            Dicionário com estatísticas
        """
        try:
            total = Sorteio.query.count()
            primeiro = Sorteio.query.order_by(Sorteio.concurso.asc()).first()
            ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

            # Calcular frequência de cada número (1-31)
            frequencia_numeros = AnaliseVisualService._calcular_frequencia_numeros()

            # Calcular frequência de meses da sorte
            frequencia_meses = AnaliseVisualService._calcular_frequencia_meses()

            return {
                'total_concursos': total,
                'primeiro_concurso': primeiro.concurso if primeiro else None,
                'ultimo_concurso': ultimo.concurso if ultimo else None,
                'data_primeiro': primeiro.data_sorteio.strftime('%d/%m/%Y') if primeiro and primeiro.data_sorteio else None,
                'data_ultimo': ultimo.data_sorteio.strftime('%d/%m/%Y') if ultimo and ultimo.data_sorteio else None,
                'frequencia_numeros': frequencia_numeros,
                'frequencia_meses': frequencia_meses
            }

        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return {}

    @staticmethod
    def _calcular_frequencia_numeros() -> Dict[int, int]:
        """
        Calcula a frequência de cada número (1-31) em todos os sorteios

        Returns:
            Dicionário com número -> quantidade de vezes sorteado
        """
        try:
            # Inicializar contagem para todos os números
            frequencia = {n: 0 for n in range(1, 32)}

            # Buscar todos os sorteios
            sorteios = Sorteio.query.all()

            for sorteio in sorteios:
                # Contar cada posição
                numeros = [
                    sorteio.posicao_1,
                    sorteio.posicao_2,
                    sorteio.posicao_3,
                    sorteio.posicao_4,
                    sorteio.posicao_5,
                    sorteio.posicao_6,
                    sorteio.posicao_7
                ]
                for num in numeros:
                    if num and 1 <= num <= 31:
                        frequencia[num] += 1

            return frequencia

        except Exception as e:
            print(f"Erro ao calcular frequência de números: {str(e)}")
            return {}

    @staticmethod
    def _calcular_frequencia_meses() -> Dict[int, int]:
        """
        Calcula a frequência de cada mês da sorte

        Returns:
            Dicionário com mês -> quantidade de vezes sorteado
        """
        try:
            # Inicializar contagem para todos os meses
            frequencia = {m: 0 for m in range(1, 13)}

            # Buscar todos os sorteios
            sorteios = Sorteio.query.all()

            for sorteio in sorteios:
                if sorteio.mes_sorte and 1 <= sorteio.mes_sorte <= 12:
                    frequencia[sorteio.mes_sorte] += 1

            return frequencia

        except Exception as e:
            print(f"Erro ao calcular frequência de meses: {str(e)}")
            return {}

    @staticmethod
    def _formatar_sorteio(sorteio: Sorteio) -> Dict:
        """
        Formata um objeto Sorteio para dicionário

        Args:
            sorteio: Objeto Sorteio do banco

        Returns:
            Dicionário formatado
        """
        # Números em ORDEM CRESCENTE (posicao_1 a posicao_7)
        numeros_ordenados = [
            sorteio.posicao_1,
            sorteio.posicao_2,
            sorteio.posicao_3,
            sorteio.posicao_4,
            sorteio.posicao_5,
            sorteio.posicao_6,
            sorteio.posicao_7
        ]

        # Números em ORDEM DE SORTEIO (sorteio_1 a sorteio_7)
        # Se as colunas sorteio_* existem e estão preenchidas, usa elas
        if hasattr(sorteio, 'sorteio_1') and sorteio.sorteio_1 is not None:
            numeros = [
                sorteio.sorteio_1,
                sorteio.sorteio_2,
                sorteio.sorteio_3,
                sorteio.sorteio_4,
                sorteio.sorteio_5,
                sorteio.sorteio_6,
                sorteio.sorteio_7
            ]
        else:
            # Fallback: usa ordem crescente se não houver ordem de sorteio
            numeros = numeros_ordenados.copy()

        # Data formatada
        data_formatada = None
        dia_semana = None
        dia_semana_abrev = None

        if sorteio.data_sorteio:
            data_formatada = sorteio.data_sorteio.strftime('%d/%m/%Y')
            dia_semana_num = sorteio.data_sorteio.weekday()
            dia_semana = AnaliseVisualService.DIAS_SEMANA.get(dia_semana_num, '')
            dia_semana_abrev = dia_semana[:3] if dia_semana else ''

        # Mês da sorte formatado
        mes_sorte_nome = AnaliseVisualService.MESES.get(sorteio.mes_sorte, '')

        return {
            'concurso': sorteio.concurso,
            'data': data_formatada,
            'dia_semana': dia_semana,
            'dia_semana_abrev': dia_semana_abrev,
            'numeros': numeros,  # Ordem de sorteio
            'numeros_ordenados': numeros_ordenados,  # Ordem crescente
            'mes_sorte': sorteio.mes_sorte,
            'mes_sorte_nome': mes_sorte_nome,
            'acumulou': sorteio.acumulou if hasattr(sorteio, 'acumulou') else False,
            'valor_premio_7': sorteio.valor_premio_7_acertos if hasattr(sorteio, 'valor_premio_7_acertos') else 0,
            'valor_premio_6': sorteio.valor_premio_6_acertos if hasattr(sorteio, 'valor_premio_6_acertos') else 0,
            'valor_premio_5': sorteio.valor_premio_5_acertos if hasattr(sorteio, 'valor_premio_5_acertos') else 0,
            'valor_premio_4': sorteio.valor_premio_4_acertos if hasattr(sorteio, 'valor_premio_4_acertos') else 0,
            'valor_premio_mes': sorteio.valor_premio_mes_sorte if hasattr(sorteio, 'valor_premio_mes_sorte') else 0
        }

    @staticmethod
    def gerar_grade_31(numeros_sorteados: List[int]) -> List[Dict]:
        """
        Gera uma grade com os 31 números indicando quais foram sorteados

        Args:
            numeros_sorteados: Lista com os 7 números sorteados

        Returns:
            Lista de dicionários representando cada número de 1 a 31
        """
        grade = []
        for n in range(1, 32):
            grade.append({
                'numero': n,
                'numero_formatado': str(n).zfill(2),
                'sorteado': n in numeros_sorteados
            })
        return grade

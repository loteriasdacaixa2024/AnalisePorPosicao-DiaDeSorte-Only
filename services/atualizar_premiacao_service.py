import requests
from models import Sorteio, db
from datetime import datetime


class AtualizarPremiacaoService:
    """
    Service para buscar e salvar dados de premiação da API da Caixa
    """

    API_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte"

    @staticmethod
    def buscar_dados_api(numero_concurso=None):
        """
        Busca dados de um concurso na API da Caixa

        Args:
            numero_concurso: Número do concurso (None para último)

        Returns:
            dict com dados do concurso ou None em caso de erro
        """
        try:
            if numero_concurso:
                url = f"{AtualizarPremiacaoService.API_URL}/{numero_concurso}"
            else:
                url = AtualizarPremiacaoService.API_URL

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados da API: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return None

    @staticmethod
    def extrair_premiacao(dados_api):
        """
        Extrai dados de premiação do JSON da API

        Args:
            dados_api: dict com dados da API

        Returns:
            dict com dados de premiação formatados
        """
        if not dados_api or 'listaRateioPremio' not in dados_api:
            return None

        premiacao = {
            'ganhadores_7_acertos': 0,
            'valor_premio_7_acertos': 0.0,
            'ganhadores_6_acertos': 0,
            'valor_premio_6_acertos': 0.0,
            'ganhadores_5_acertos': 0,
            'valor_premio_5_acertos': 25.0,
            'ganhadores_4_acertos': 0,
            'valor_premio_4_acertos': 5.0,
            'ganhadores_mes_sorte': 0,
            'valor_premio_mes_sorte': 2.5,
            'acumulado': dados_api.get('acumulado', False),
            'valor_arrecadado': dados_api.get('valorArrecadado', 0.0),
            'valor_acumulado_proximo_concurso': dados_api.get('valorAcumuladoProximoConcurso', 0.0),
            'valor_estimado_proximo_concurso': dados_api.get('valorEstimadoProximoConcurso', 0.0)
        }

        for faixa in dados_api['listaRateioPremio']:
            numero_faixa = faixa.get('faixa')
            ganhadores = faixa.get('numeroDeGanhadores', 0)
            valor = faixa.get('valorPremio', 0.0)

            if numero_faixa == 1:
                premiacao['ganhadores_7_acertos'] = ganhadores
                premiacao['valor_premio_7_acertos'] = valor
            elif numero_faixa == 2:
                premiacao['ganhadores_6_acertos'] = ganhadores
                premiacao['valor_premio_6_acertos'] = valor
            elif numero_faixa == 3:
                premiacao['ganhadores_5_acertos'] = ganhadores
                premiacao['valor_premio_5_acertos'] = valor
            elif numero_faixa == 4:
                premiacao['ganhadores_4_acertos'] = ganhadores
                premiacao['valor_premio_4_acertos'] = valor
            elif numero_faixa == 5:
                premiacao['ganhadores_mes_sorte'] = ganhadores
                premiacao['valor_premio_mes_sorte'] = valor

        return premiacao

    @staticmethod
    def atualizar_concurso(numero_concurso):
        """
        Atualiza dados de premiação de um concurso específico

        Args:
            numero_concurso: Número do concurso

        Returns:
            dict com resultado da operação
        """
        try:
            sorteio = Sorteio.query.filter_by(concurso=numero_concurso).first()

            if not sorteio:
                return {
                    'sucesso': False,
                    'mensagem': f'Concurso {numero_concurso} não encontrado no banco de dados'
                }

            dados_api = AtualizarPremiacaoService.buscar_dados_api(numero_concurso)

            if not dados_api:
                return {
                    'sucesso': False,
                    'mensagem': f'Não foi possível buscar dados do concurso {numero_concurso} na API'
                }

            premiacao = AtualizarPremiacaoService.extrair_premiacao(dados_api)

            if not premiacao:
                return {
                    'sucesso': False,
                    'mensagem': 'Erro ao extrair dados de premiação'
                }

            sorteio.ganhadores_7_acertos = premiacao['ganhadores_7_acertos']
            sorteio.valor_premio_7_acertos = premiacao['valor_premio_7_acertos']
            sorteio.ganhadores_6_acertos = premiacao['ganhadores_6_acertos']
            sorteio.valor_premio_6_acertos = premiacao['valor_premio_6_acertos']
            sorteio.ganhadores_5_acertos = premiacao['ganhadores_5_acertos']
            sorteio.valor_premio_5_acertos = premiacao['valor_premio_5_acertos']
            sorteio.ganhadores_4_acertos = premiacao['ganhadores_4_acertos']
            sorteio.valor_premio_4_acertos = premiacao['valor_premio_4_acertos']
            sorteio.ganhadores_mes_sorte = premiacao['ganhadores_mes_sorte']
            sorteio.valor_premio_mes_sorte = premiacao['valor_premio_mes_sorte']
            sorteio.acumulado = premiacao['acumulado']
            sorteio.valor_arrecadado = premiacao['valor_arrecadado']
            sorteio.valor_acumulado_proximo_concurso = premiacao['valor_acumulado_proximo_concurso']
            sorteio.valor_estimado_proximo_concurso = premiacao['valor_estimado_proximo_concurso']
            sorteio.atualizado_em = datetime.utcnow()

            db.session.commit()

            return {
                'sucesso': True,
                'mensagem': f'Concurso {numero_concurso} atualizado com sucesso',
                'dados': {
                    'concurso': numero_concurso,
                    'ganhadores_7': premiacao['ganhadores_7_acertos'],
                    'valor_7': premiacao['valor_premio_7_acertos'],
                    'ganhadores_6': premiacao['ganhadores_6_acertos'],
                    'valor_6': premiacao['valor_premio_6_acertos']
                }
            }

        except Exception as e:
            db.session.rollback()
            return {
                'sucesso': False,
                'mensagem': f'Erro ao atualizar concurso: {str(e)}'
            }

    @staticmethod
    def atualizar_ultimo_concurso():
        """
        Atualiza o último concurso cadastrado no banco

        Returns:
            dict com resultado da operação
        """
        try:
            ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

            if not ultimo:
                return {
                    'sucesso': False,
                    'mensagem': 'Nenhum concurso encontrado no banco de dados'
                }

            return AtualizarPremiacaoService.atualizar_concurso(ultimo.concurso)

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao buscar último concurso: {str(e)}'
            }

    @staticmethod
    def atualizar_multiplos_concursos(concurso_inicial, concurso_final):
        """
        Atualiza múltiplos concursos em lote

        Args:
            concurso_inicial: Número do primeiro concurso
            concurso_final: Número do último concurso

        Returns:
            dict com resultado da operação
        """
        resultados = {
            'total': 0,
            'sucesso': 0,
            'erros': 0,
            'detalhes': []
        }

        try:
            for numero in range(concurso_inicial, concurso_final + 1):
                resultado = AtualizarPremiacaoService.atualizar_concurso(numero)

                resultados['total'] += 1

                if resultado['sucesso']:
                    resultados['sucesso'] += 1
                    resultados['detalhes'].append({
                        'concurso': numero,
                        'status': 'sucesso'
                    })
                else:
                    resultados['erros'] += 1
                    resultados['detalhes'].append({
                        'concurso': numero,
                        'status': 'erro',
                        'mensagem': resultado['mensagem']
                    })

            return {
                'sucesso': True,
                'mensagem': f'Processados {resultados["total"]} concursos. Sucesso: {resultados["sucesso"]}, Erros: {resultados["erros"]}',
                'resultados': resultados
            }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao processar lote: {str(e)}'
            }

    @staticmethod
    def atualizar_todos_sem_premiacao():
        """
        Atualiza todos os concursos que ainda não têm dados de premiação

        Returns:
            dict com resultado da operação
        """
        try:
            sorteios = Sorteio.query.filter(
                (Sorteio.ganhadores_7_acertos == None) |
                (Sorteio.ganhadores_7_acertos == 0)
            ).order_by(Sorteio.concurso.desc()).all()

            if not sorteios:
                return {
                    'sucesso': True,
                    'mensagem': 'Todos os concursos já têm dados de premiação',
                    'total': 0
                }

            resultados = {
                'total': len(sorteios),
                'sucesso': 0,
                'erros': 0,
                'detalhes': []
            }

            for sorteio in sorteios:
                resultado = AtualizarPremiacaoService.atualizar_concurso(sorteio.concurso)

                if resultado['sucesso']:
                    resultados['sucesso'] += 1
                else:
                    resultados['erros'] += 1

                resultados['detalhes'].append({
                    'concurso': sorteio.concurso,
                    'status': 'sucesso' if resultado['sucesso'] else 'erro',
                    'mensagem': resultado.get('mensagem', '')
                })

            return {
                'sucesso': True,
                'mensagem': f'Processados {resultados["total"]} concursos. Sucesso: {resultados["sucesso"]}, Erros: {resultados["erros"]}',
                'resultados': resultados
            }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao processar concursos: {str(e)}'
            }

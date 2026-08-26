# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

import sys
import os

# Add parent directory to path to import from atualizar_banco_da_api_MELHORADO
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.configuracao import Configuracao, db
from models.sorteio import Sorteio
from datetime import datetime
import requests
import time
import urllib3

# Desabilita warnings de SSL (se necessário)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ConfiguracaoService:
    """
    Service para gerenciar configurações do sistema e atualizações do banco
    """

    @staticmethod
    def obter_configuracao(chave, valor_padrao=None):
        """
        Obtém uma configuração pela chave

        Args:
            chave: Chave da configuração
            valor_padrao: Valor padrão caso não exista

        Returns:
            Valor da configuração convertido para o tipo apropriado
        """
        try:
            config = Configuracao.query.filter_by(chave=chave).first()

            if config:
                return config.get_valor_convertido()

            return valor_padrao

        except Exception as e:
            print(f"Erro ao obter configuração '{chave}': {str(e)}")
            return valor_padrao

    @staticmethod
    def obter_valor_aposta():
        """
        Obtém o valor da aposta mínima

        Returns:
            float: Valor da aposta mínima (padrão: 2.50)
        """
        return ConfiguracaoService.obter_configuracao('valor_aposta_minima', 2.50)

    @staticmethod
    def salvar_configuracao(chave, valor, tipo='string', descricao=None):
        """
        Salva ou atualiza uma configuração

        Args:
            chave: Chave da configuração
            valor: Valor a ser salvo (será convertido para string)
            tipo: Tipo do valor (string, float, int, boolean)
            descricao: Descrição da configuração

        Returns:
            dict com resultado da operação
        """
        try:
            # Busca configuração existente
            config = Configuracao.query.filter_by(chave=chave).first()

            if config:
                # Atualiza existente
                config.valor = str(valor)
                config.tipo = tipo
                if descricao:
                    config.descricao = descricao
            else:
                # Cria nova
                config = Configuracao(
                    chave=chave,
                    valor=str(valor),
                    tipo=tipo,
                    descricao=descricao
                )
                db.session.add(config)

            db.session.commit()

            return {
                'sucesso': True,
                'mensagem': f'Configuração "{chave}" salva com sucesso',
                'configuracao': config.to_dict()
            }

        except Exception as e:
            db.session.rollback()
            return {
                'sucesso': False,
                'mensagem': f'Erro ao salvar configuração: {str(e)}'
            }

    @staticmethod
    def salvar_valor_aposta(valor):
        """
        Salva o valor da aposta mínima

        Args:
            valor: Valor da aposta em reais

        Returns:
            dict com resultado da operação
        """
        try:
            valor_float = float(valor)

            if valor_float <= 0:
                return {
                    'sucesso': False,
                    'mensagem': 'O valor da aposta deve ser maior que zero'
                }

            return ConfiguracaoService.salvar_configuracao(
                chave='valor_aposta_minima',
                valor=valor_float,
                tipo='float',
                descricao='Valor da aposta mínima (7 números) em reais'
            )

        except ValueError:
            return {
                'sucesso': False,
                'mensagem': 'Valor inválido. Use apenas números (ex: 2.50)'
            }

    @staticmethod
    def listar_todas():
        """
        Lista todas as configurações

        Returns:
            list: Lista de configurações
        """
        try:
            configs = Configuracao.query.order_by(Configuracao.chave).all()
            return [config.to_dict() for config in configs]

        except Exception as e:
            print(f"Erro ao listar configurações: {str(e)}")
            return []

    @staticmethod
    def excluir_configuracao(chave):
        """
        Exclui uma configuração

        Args:
            chave: Chave da configuração a ser excluída

        Returns:
            dict com resultado da operação
        """
        try:
            config = Configuracao.query.filter_by(chave=chave).first()

            if not config:
                return {
                    'sucesso': False,
                    'mensagem': f'Configuração "{chave}" não encontrada'
                }

            db.session.delete(config)
            db.session.commit()

            return {
                'sucesso': True,
                'mensagem': f'Configuração "{chave}" excluída com sucesso'
            }

        except Exception as e:
            db.session.rollback()
            return {
                'sucesso': False,
                'mensagem': f'Erro ao excluir configuração: {str(e)}'
            }

    @staticmethod
    def inicializar_configuracoes():
        """
        Inicializa as configurações padrão do sistema

        Returns:
            bool: True se sucesso, False se erro
        """
        return Configuracao.criar_configuracoes_padrao()

    # ========================================================================
    # ANÁLISES CONFIGURATION METHODS
    # ========================================================================

    @staticmethod
    def obter_analises_ativas():
        """
        Obtém todas as análises que estão ativas (enabled)

        Returns:
            dict: Dicionário com status de cada análise (48 análises no total)
        """
        analises = {
            # ===== ESTATÍSTICAS BÁSICAS (8) =====
            'atrasados': ConfiguracaoService.obter_configuracao('analise_atrasados', True),
            'quentes_frios': ConfiguracaoService.obter_configuracao('analise_quentes_frios', True),
            'numeros_devidos': ConfiguracaoService.obter_configuracao('analise_numeros_devidos', True),
            'frequencia': ConfiguracaoService.obter_configuracao('analise_frequencia', True),
            'probabilidade': ConfiguracaoService.obter_configuracao('analise_probabilidade', True),
            'media_atrasos': ConfiguracaoService.obter_configuracao('analise_media_atrasos', True),
            'desvio_padrao': ConfiguracaoService.obter_configuracao('analise_desvio_padrao', False),
            'tendencias': ConfiguracaoService.obter_configuracao('analise_tendencias', True),

            # ===== PADRÕES NUMÉRICOS (10) =====
            'pares_impares': ConfiguracaoService.obter_configuracao('analise_pares_impares', True),
            'primos_compostos': ConfiguracaoService.obter_configuracao('analise_primos_compostos', False),
            'digito_inicial': ConfiguracaoService.obter_configuracao('analise_digito_inicial', True),
            'digito_final': ConfiguracaoService.obter_configuracao('analise_digito_final', True),
            'soma_dezenas': ConfiguracaoService.obter_configuracao('analise_soma_dezenas', True),
            'faixas_numericas': ConfiguracaoService.obter_configuracao('analise_faixas_numericas', True),
            'extremos': ConfiguracaoService.obter_configuracao('analise_extremos', True),
            'numeros_juntos': ConfiguracaoService.obter_configuracao('analise_numeros_juntos', True),
            'duplicatas_triplas': ConfiguracaoService.obter_configuracao('analise_duplicatas_triplas', False),
            'padroes_extremos': ConfiguracaoService.obter_configuracao('analise_padroes_extremos', True),

            # ===== DISTRIBUIÇÃO E ESPAÇAMENTO (8) =====
            'gaps': ConfiguracaoService.obter_configuracao('analise_gaps', True),
            'consecutivos': ConfiguracaoService.obter_configuracao('analise_consecutivos', True),
            'quadrantes': ConfiguracaoService.obter_configuracao('analise_quadrantes', False),
            'dezenas': ConfiguracaoService.obter_configuracao('analise_dezenas', True),
            'espacamento': ConfiguracaoService.obter_configuracao('analise_espacamento', True),
            'distribuicao_geral': ConfiguracaoService.obter_configuracao('analise_distribuicao_geral', True),
            'concentracao': ConfiguracaoService.obter_configuracao('analise_concentracao', True),
            'dispersao': ConfiguracaoService.obter_configuracao('analise_dispersao', False),

            # ===== RELACIONAMENTO E SEQUÊNCIAS (6) =====
            'repeticoes': ConfiguracaoService.obter_configuracao('analise_repeticoes', True),
            'sequencias': ConfiguracaoService.obter_configuracao('analise_sequencias', True),
            'persistencia': ConfiguracaoService.obter_configuracao('analise_persistencia', True),
            'alternancia': ConfiguracaoService.obter_configuracao('analise_alternancia', False),
            'correlacao_numeros': ConfiguracaoService.obter_configuracao('analise_correlacao_numeros', False),
            'grupos_frequentes': ConfiguracaoService.obter_configuracao('analise_grupos_frequentes', True),

            # ===== TEMPORAIS E SAZONAIS (8) =====
            'meses': ConfiguracaoService.obter_configuracao('analise_meses', True),
            'dias_semana': ConfiguracaoService.obter_configuracao('analise_dias_semana', False),
            'trimestres': ConfiguracaoService.obter_configuracao('analise_trimestres', False),
            'sazonal': ConfiguracaoService.obter_configuracao('analise_sazonal', True),
            'transicao_meses': ConfiguracaoService.obter_configuracao('analise_transicao_meses', True),
            'correlacao_mes_dezenas': ConfiguracaoService.obter_configuracao('analise_correlacao_mes_dezenas', True),
            'acumulos_mes': ConfiguracaoService.obter_configuracao('analise_acumulos_mes', True),
            'ciclos_temporais': ConfiguracaoService.obter_configuracao('analise_ciclos_temporais', False),

            # ===== AVANÇADAS E PREDITIVAS (8) =====
            'probabilidade_condicional': ConfiguracaoService.obter_configuracao('analise_probabilidade_condicional', True),
            'ciclos_intervalos': ConfiguracaoService.obter_configuracao('analise_ciclos_intervalos', True),
            'frequencia_premios': ConfiguracaoService.obter_configuracao('analise_frequencia_premios', True),
            'tendencia_futura': ConfiguracaoService.obter_configuracao('analise_tendencia_futura', False),
            'regressao': ConfiguracaoService.obter_configuracao('analise_regressao', False),
            'clusters': ConfiguracaoService.obter_configuracao('analise_clusters', False),
            'machine_learning': ConfiguracaoService.obter_configuracao('analise_machine_learning', False),
            'neural_network': ConfiguracaoService.obter_configuracao('analise_neural_network', False)
        }

        return analises

    @staticmethod
    def salvar_analises(analises_dict):
        """
        Salva múltiplas configurações de análises

        Args:
            analises_dict: Dicionário com chaves e valores booleanos

        Returns:
            dict com resultado da operação
        """
        try:
            erros = []

            for chave, valor in analises_dict.items():
                # Adiciona prefixo 'analise_' se não estiver presente
                chave_completa = chave if chave.startswith('analise_') else f'analise_{chave}'

                resultado = ConfiguracaoService.salvar_configuracao(
                    chave=chave_completa,
                    valor=valor,
                    tipo='boolean'
                )

                if not resultado['sucesso']:
                    erros.append(f"{chave}: {resultado['mensagem']}")

            if erros:
                return {
                    'sucesso': False,
                    'mensagem': f'Alguns erros ocorreram: {"; ".join(erros)}'
                }

            return {
                'sucesso': True,
                'mensagem': f'{len(analises_dict)} configuração(ões) de análise salva(s) com sucesso!'
            }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao salvar configurações de análises: {str(e)}'
            }

    # ========================================================================
    # DATABASE UPDATE METHODS
    # ========================================================================

    @staticmethod
    def obter_status_banco():
        """
        Obtém o status atual do banco de dados

        Returns:
            dict com informações do banco
        """
        try:
            # Busca o último sorteio
            ultimo_sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

            # Busca o primeiro sorteio
            primeiro_sorteio = Sorteio.query.order_by(Sorteio.concurso.asc()).first()

            # Total de concursos
            total_concursos = Sorteio.query.count()

            if ultimo_sorteio:
                return {
                    'sucesso': True,
                    'ultimo_concurso': ultimo_sorteio.concurso,
                    'data_ultimo_concurso': ultimo_sorteio.data_sorteio.strftime('%d/%m/%Y') if ultimo_sorteio.data_sorteio else 'N/A',
                    'primeiro_concurso': primeiro_sorteio.concurso if primeiro_sorteio else None,
                    'total_concursos': total_concursos,
                    'banco_vazio': False
                }
            else:
                return {
                    'sucesso': True,
                    'ultimo_concurso': None,
                    'data_ultimo_concurso': None,
                    'primeiro_concurso': None,
                    'total_concursos': 0,
                    'banco_vazio': True
                }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao obter status do banco: {str(e)}'
            }

    @staticmethod
    def _converter_data(data_str):
        """Converte data do formato DD/MM/YYYY para objeto date"""
        if not data_str:
            return None
        try:
            return datetime.strptime(data_str, '%d/%m/%Y').date()
        except:
            return None

    @staticmethod
    def _obter_mes_numero(mes_nome):
        """Converte nome do mês para número (1-12)"""
        meses = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }
        return meses.get(mes_nome.lower(), 1)

    @staticmethod
    def _buscar_concurso_api(numero_concurso=None, max_retries=3):
        """
        Busca dados de um concurso específico ou do último concurso

        Args:
            numero_concurso: Número do concurso ou None para último
            max_retries: Número máximo de tentativas

        Returns:
            dict com dados do concurso ou None em caso de erro
        """
        url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte"

        if numero_concurso:
            url += f"/{numero_concurso}"

        # Headers para simular navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        for tentativa in range(max_retries):
            try:
                if tentativa > 0:
                    time.sleep(2)  # Aguarda 2 segundos entre tentativas

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=15,
                    verify=True
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.SSLError:
                if tentativa == max_retries - 1:
                    # Última tentativa: tenta sem verificar SSL
                    try:
                        response = requests.get(
                            url,
                            headers=headers,
                            timeout=15,
                            verify=False
                        )
                        response.raise_for_status()
                        return response.json()
                    except:
                        return None

            except requests.exceptions.RequestException:
                if tentativa == max_retries - 1:
                    return None

        return None

    @staticmethod
    def _atualizar_sorteio_db(data_api):
        """
        Atualiza ou insere um sorteio no banco

        Args:
            data_api: Dados do concurso da API

        Returns:
            bool: True se sucesso, False se erro
        """
        numero_concurso = data_api.get('numero')

        if not numero_concurso:
            return False

        try:
            # Busca ou cria o sorteio
            sorteio = Sorteio.query.filter_by(concurso=numero_concurso).first()

            if not sorteio:
                sorteio = Sorteio(concurso=numero_concurso)

            # Dezenas (em ordem)
            lista_dezenas = data_api.get('listaDezenas', [])
            if len(lista_dezenas) >= 7:
                sorteio.posicao_1 = int(lista_dezenas[0])
                sorteio.posicao_2 = int(lista_dezenas[1])
                sorteio.posicao_3 = int(lista_dezenas[2])
                sorteio.posicao_4 = int(lista_dezenas[3])
                sorteio.posicao_5 = int(lista_dezenas[4])
                sorteio.posicao_6 = int(lista_dezenas[5])
                sorteio.posicao_7 = int(lista_dezenas[6])

            # Mês da sorte
            mes_nome = data_api.get('nomeTimeCoracaoMesSorte', 'Janeiro')
            sorteio.mes_sorte = ConfiguracaoService._obter_mes_numero(mes_nome)

            # Datas
            sorteio.data_apuracao = ConfiguracaoService._converter_data(data_api.get('dataApuracao'))
            sorteio.data_sorteio = sorteio.data_apuracao
            sorteio.data_proximo_concurso = ConfiguracaoService._converter_data(data_api.get('dataProximoConcurso'))

            # Números de concursos
            sorteio.numero_concurso_anterior = data_api.get('numeroConcursoAnterior')
            sorteio.numero_concurso_proximo = data_api.get('numeroConcursoProximo')

            # Local
            sorteio.local_sorteio = data_api.get('localSorteio')
            sorteio.municipio_uf_sorteio = data_api.get('nomeMunicipioUFSorteio')

            # Valores
            sorteio.acumulado = data_api.get('acumulado', False)
            sorteio.valor_arrecadado = data_api.get('valorArrecadado', 0.0)
            sorteio.valor_acumulado_proximo_concurso = data_api.get('valorAcumuladoProximoConcurso', 0.0)
            sorteio.valor_estimado_proximo_concurso = data_api.get('valorEstimadoProximoConcurso', 0.0)
            sorteio.valor_acumulado_concurso_especial = data_api.get('valorAcumuladoConcursoEspecial', 0.0)

            # Flag último concurso
            sorteio.ultimo_concurso = data_api.get('ultimoConcurso', False)

            # Premiação
            lista_rateio = data_api.get('listaRateioPremio', [])
            for rateio in lista_rateio:
                faixa = rateio.get('faixa')
                num_ganhadores = rateio.get('numeroDeGanhadores', 0)
                valor_premio = rateio.get('valorPremio', 0.0)

                if faixa == 1:
                    sorteio.ganhadores_7_acertos = num_ganhadores
                    sorteio.valor_premio_7_acertos = valor_premio
                elif faixa == 2:
                    sorteio.ganhadores_6_acertos = num_ganhadores
                    sorteio.valor_premio_6_acertos = valor_premio
                elif faixa == 3:
                    sorteio.ganhadores_5_acertos = num_ganhadores
                    sorteio.valor_premio_5_acertos = valor_premio
                elif faixa == 4:
                    sorteio.ganhadores_4_acertos = num_ganhadores
                    sorteio.valor_premio_4_acertos = valor_premio
                elif faixa == 5:
                    sorteio.ganhadores_mes_sorte = num_ganhadores
                    sorteio.valor_premio_mes_sorte = valor_premio

            # Timestamp de atualização
            sorteio.atualizado_em = datetime.utcnow()

            # Salva no banco
            if sorteio.id is None:
                db.session.add(sorteio)

            db.session.commit()
            return True

        except Exception as e:
            print(f"Erro ao atualizar concurso {numero_concurso}: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def atualizar_ultimo_concurso():
        """
        Atualiza apenas o último concurso disponível

        Returns:
            dict com resultado da operação
        """
        try:
            data = ConfiguracaoService._buscar_concurso_api()

            if not data:
                return {
                    'sucesso': False,
                    'mensagem': 'Não foi possível buscar o último concurso da API. Verifique sua conexão com a internet.'
                }

            numero_concurso = data.get('numero')

            if ConfiguracaoService._atualizar_sorteio_db(data):
                return {
                    'sucesso': True,
                    'mensagem': f'Concurso {numero_concurso} atualizado com sucesso!',
                    'concurso': numero_concurso
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': f'Erro ao atualizar concurso {numero_concurso} no banco de dados'
                }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao atualizar último concurso: {str(e)}'
            }

    @staticmethod
    def atualizar_concurso_especifico(numero):
        """
        Atualiza um concurso específico

        Args:
            numero: Número do concurso

        Returns:
            dict com resultado da operação
        """
        try:
            numero = int(numero)

            if numero <= 0:
                return {
                    'sucesso': False,
                    'mensagem': 'Número do concurso deve ser maior que zero'
                }

            data = ConfiguracaoService._buscar_concurso_api(numero)

            if not data:
                return {
                    'sucesso': False,
                    'mensagem': f'Não foi possível buscar o concurso {numero} da API'
                }

            if ConfiguracaoService._atualizar_sorteio_db(data):
                return {
                    'sucesso': True,
                    'mensagem': f'Concurso {numero} atualizado com sucesso!',
                    'concurso': numero
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': f'Erro ao atualizar concurso {numero} no banco de dados'
                }

        except ValueError:
            return {
                'sucesso': False,
                'mensagem': 'Número do concurso inválido'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao atualizar concurso: {str(e)}'
            }

    @staticmethod
    def atualizar_range_concursos(inicio, fim):
        """
        Atualiza um range de concursos

        Args:
            inicio: Número inicial
            fim: Número final

        Returns:
            dict com resultado da operação
        """
        try:
            inicio = int(inicio)
            fim = int(fim)

            if inicio <= 0 or fim <= 0:
                return {
                    'sucesso': False,
                    'mensagem': 'Os números devem ser maiores que zero'
                }

            if inicio > fim:
                return {
                    'sucesso': False,
                    'mensagem': 'O número inicial deve ser menor ou igual ao final'
                }

            total = fim - inicio + 1

            if total > 500:
                return {
                    'sucesso': False,
                    'mensagem': f'Range muito grande ({total} concursos). Máximo permitido: 500 concursos por vez'
                }

            sucesso = 0
            falhas = 0
            detalhes = []

            for numero in range(inicio, fim + 1):
                data = ConfiguracaoService._buscar_concurso_api(numero)

                if data and ConfiguracaoService._atualizar_sorteio_db(data):
                    sucesso += 1
                else:
                    falhas += 1
                    detalhes.append(f'Falha no concurso {numero}')

                # Delay entre requisições para não sobrecarregar a API
                if numero < fim:
                    time.sleep(1)

            return {
                'sucesso': True,
                'mensagem': f'Atualização concluída: {sucesso} sucessos, {falhas} falhas',
                'total': total,
                'sucessos': sucesso,
                'falhas': falhas,
                'detalhes': detalhes[:10]  # Retorna no máximo 10 detalhes de erro
            }

        except ValueError:
            return {
                'sucesso': False,
                'mensagem': 'Números inválidos'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao atualizar range de concursos: {str(e)}'
            }

    @staticmethod
    def atualizar_todos_concursos():
        """
        Atualiza todos os concursos disponíveis (1 até o último)

        Returns:
            dict com resultado da operação
        """
        try:
            # Primeiro busca o último para saber até onde ir
            data_ultimo = ConfiguracaoService._buscar_concurso_api()

            if not data_ultimo:
                return {
                    'sucesso': False,
                    'mensagem': 'Não foi possível determinar o último concurso disponível'
                }

            ultimo_numero = data_ultimo.get('numero')

            # Utiliza o método de range para fazer a atualização
            return ConfiguracaoService.atualizar_range_concursos(1, ultimo_numero)

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao atualizar todos os concursos: {str(e)}'
            }

    # ========================================================================
    # MONTH COLORS CONFIGURATION METHODS
    # ========================================================================

    @staticmethod
    def obter_cores_meses():
        """
        Obtém as cores dos 12 meses do banco de dados

        Returns:
            dict: {1: '#cor1', 2: '#cor2', ..., 12: '#cor12'}
        """
        cores_meses = {}

        # Cores padrão
        cores_padrao = {
            1: '#FF6B9D',   # Janeiro - Rosa
            2: '#C5A880',   # Fevereiro - Dourado
            3: '#95A5A6',   # Março - Cinza
            4: '#9B59B6',   # Abril - Roxo
            5: '#27AE60',   # Maio - Verde
            6: '#3498DB',   # Junho - Azul
            7: '#E67E22',   # Julho - Laranja
            8: '#E74C3C',   # Agosto - Vermelho
            9: '#F39C12',   # Setembro - Amarelo
            10: '#16A085',  # Outubro - Turquesa
            11: '#8E44AD',  # Novembro - Roxo Escuro
            12: '#C0392B',  # Dezembro - Vermelho Escuro
        }

        for mes in range(1, 13):
            chave = f'cor_mes_{mes}'
            cor = ConfiguracaoService.obter_configuracao(chave, cores_padrao[mes])
            cores_meses[mes] = cor

        return cores_meses

    @staticmethod
    def salvar_cores_meses(cores_dict):
        """
        Salva múltiplas cores de meses

        Args:
            cores_dict: Dicionário {mes: cor_hex, ...}

        Returns:
            dict com resultado da operação
        """
        try:
            erros = []
            sucessos = 0

            for mes_str, cor_hex in cores_dict.items():
                try:
                    mes = int(mes_str)
                    if mes < 1 or mes > 12:
                        erros.append(f"Mês {mes} inválido (deve ser 1-12)")
                        continue

                    chave = f'cor_mes_{mes}'
                    resultado = ConfiguracaoService.salvar_configuracao(
                        chave=chave,
                        valor=cor_hex,
                        tipo='string',
                        descricao=f'Cor do mês {mes}'
                    )

                    if resultado['sucesso']:
                        sucessos += 1
                    else:
                        erros.append(f"Mês {mes}: {resultado['mensagem']}")

                except Exception as e:
                    erros.append(f"Mês {mes_str}: {str(e)}")

            if erros:
                return {
                    'sucesso': False if sucessos == 0 else True,
                    'mensagem': f'{sucessos} cores salvas. Erros: ' + ', '.join(erros)
                }
            else:
                return {
                    'sucesso': True,
                    'mensagem': f'{sucessos} cores atualizadas com sucesso!'
                }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao salvar cores: {str(e)}'
            }

    @staticmethod
    def restaurar_cores_meses_padrao():
        """
        Restaura todas as cores dos meses para os valores padrão

        Returns:
            dict com resultado da operação
        """
        cores_padrao = {
            1: '#FF6B9D',   # Janeiro - Rosa
            2: '#C5A880',   # Fevereiro - Dourado
            3: '#95A5A6',   # Março - Cinza
            4: '#9B59B6',   # Abril - Roxo
            5: '#27AE60',   # Maio - Verde
            6: '#3498DB',   # Junho - Azul
            7: '#E67E22',   # Julho - Laranja
            8: '#E74C3C',   # Agosto - Vermelho
            9: '#F39C12',   # Setembro - Amarelo
            10: '#16A085',  # Outubro - Turquesa
            11: '#8E44AD',  # Novembro - Roxo Escuro
            12: '#C0392B',  # Dezembro - Vermelho Escuro
        }

        return ConfiguracaoService.salvar_cores_meses(cores_padrao)

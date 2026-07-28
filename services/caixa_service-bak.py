"""
Serviço de integração com API da Caixa - COM RETRY E DELAY
COPIE ESTE ARQUIVO PARA: services/caixa_service.py
"""

import requests
from datetime import datetime
from models.sorteio import Sorteio, db
import time

class CaixaService:
    """Serviço para buscar e sincronizar sorteios da API da Caixa"""

    API_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte"
    
    # Configurações para evitar bloqueio
    DELAY_ENTRE_REQUISICOES = 0.5  # 500ms entre cada requisição Mude para 1.0 se necessário
    MAX_TENTATIVAS = 3  # Tentar até 3 vezes antes de desistir
    TIMEOUT = 15  # 15 segundos de timeout

    @staticmethod
    def normalizar_mes(valor_mes):
        """Normaliza o mês para número 1-12"""
        if isinstance(valor_mes, int):
            return valor_mes if 1 <= valor_mes <= 12 else 1

        valor_str = str(valor_mes).strip()

        try:
            mes_num = int(valor_str)
            if 1 <= mes_num <= 12:
                return mes_num
        except ValueError:
            pass

        meses_completos = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3, 'abril': 4,
            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }

        meses_abreviados = {
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4,
            'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8,
            'set': 9, 'out': 10, 'nov': 11, 'dez': 12
        }

        valor_lower = valor_str.lower()

        if valor_lower in meses_completos:
            return meses_completos[valor_lower]

        if valor_lower in meses_abreviados:
            return meses_abreviados[valor_lower]

        return 1

    @staticmethod
    def fazer_requisicao_com_retry(url, max_tentativas=None):
        """
        Faz requisição com retry automático em caso de erro
        """
        if max_tentativas is None:
            max_tentativas = CaixaService.MAX_TENTATIVAS
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                response = requests.get(
                    url, 
                    timeout=CaixaService.TIMEOUT,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                if response.status_code == 200:
                    return response
                
                # Se não for 200, esperar mais antes de tentar novamente
                if tentativa < max_tentativas:
                    time.sleep(2)
                    
            except requests.exceptions.SSLError as e:
                print(f"⚠️  Erro SSL na tentativa {tentativa}/{max_tentativas}: {str(e)[:100]}")
                if tentativa < max_tentativas:
                    # Esperar mais tempo em caso de erro SSL
                    tempo_espera = tentativa * 2
                    print(f"   Aguardando {tempo_espera}s antes de tentar novamente...")
                    time.sleep(tempo_espera)
                else:
                    raise
                    
            except requests.exceptions.Timeout:
                print(f"⚠️  Timeout na tentativa {tentativa}/{max_tentativas}")
                if tentativa < max_tentativas:
                    time.sleep(2)
                else:
                    raise
                    
            except Exception as e:
                print(f"⚠️  Erro na tentativa {tentativa}/{max_tentativas}: {str(e)[:100]}")
                if tentativa < max_tentativas:
                    time.sleep(2)
                else:
                    raise
        
        return None

    @staticmethod
    def buscar_ultimo_concurso():
        """Busca o último concurso disponível na API"""
        try:
            response = CaixaService.fazer_requisicao_com_retry(CaixaService.API_URL)
            if response and response.status_code == 200:
                dados = response.json()
                return dados.get('numero', 0)
            return 0
        except Exception as e:
            print(f"Erro ao buscar último concurso: {str(e)}")
            return 0

    @staticmethod
    def buscar_concurso(numero):
        """Busca um concurso específico na API com retry"""
        try:
            url = f"{CaixaService.API_URL}/{numero}"
            response = CaixaService.fazer_requisicao_com_retry(url)
            
            if response and response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar concurso {numero}: {str(e)[:100]}")
            return None

    @staticmethod
    def salvar_concurso(dados_api):
        """Salva um concurso no banco"""
        try:
            concurso = dados_api.get('numero')
            data_str = dados_api.get('dataApuracao')
            data_sorteio = datetime.strptime(data_str, '%d/%m/%Y').date()

            dezenas_ordem = dados_api.get('dezenasSorteadasOrdemSorteio', [])
            mes_valor_api = dados_api.get('nomeTimeCoracaoMesSorte', 'Janeiro')
            mes_sorte = CaixaService.normalizar_mes(mes_valor_api)

            sorteio_existente = Sorteio.query.filter_by(concurso=concurso).first()
            if sorteio_existente:
                return sorteio_existente, 'ja_existe'

            novo_sorteio = Sorteio(
                concurso=concurso,
                posicao_1=int(dezenas_ordem[0]),
                posicao_2=int(dezenas_ordem[1]),
                posicao_3=int(dezenas_ordem[2]),
                posicao_4=int(dezenas_ordem[3]),
                posicao_5=int(dezenas_ordem[4]),
                posicao_6=int(dezenas_ordem[5]),
                posicao_7=int(dezenas_ordem[6]),
                mes_sorte=mes_sorte,
                data_sorteio=data_sorteio
            )

            db.session.add(novo_sorteio)
            db.session.commit()

            return novo_sorteio, 'inserido'

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao salvar concurso: {str(e)}")

    @staticmethod
    def sincronizar_todos():
        """Sincroniza todos os concursos com delay entre requisições"""
        try:
            ultimo = CaixaService.buscar_ultimo_concurso()
            if ultimo == 0:
                return {'erro': 'Não foi possível buscar o último concurso'}

            print(f"📊 Último concurso: {ultimo}")
            print(f"⏱️  Delay entre requisições: {CaixaService.DELAY_ENTRE_REQUISICOES}s")
            print()

            inseridos = 0
            ja_existentes = 0
            erros = 0

            for num in range(1, ultimo + 1):
                try:
                    # Mostrar progresso a cada 50 concursos
                    if num % 50 == 0:
                        print(f"📍 Processando: {num}/{ultimo} ({int(num/ultimo*100)}%)")
                    
                    dados = CaixaService.buscar_concurso(num)
                    
                    if dados:
                        _, status = CaixaService.salvar_concurso(dados)
                        if status == 'inserido':
                            inseridos += 1
                            if inseridos <= 10 or inseridos % 50 == 0:
                                print(f"✅ Concurso {num} inserido")
                        else:
                            ja_existentes += 1
                    else:
                        erros += 1
                        print(f"⚠️  Concurso {num} não encontrado")
                    
                    # DELAY para não sobrecarregar a API
                    time.sleep(CaixaService.DELAY_ENTRE_REQUISICOES)
                    
                except Exception as e:
                    erros += 1
                    print(f"❌ Erro no concurso {num}: {str(e)[:100]}")
                    # Delay maior em caso de erro
                    time.sleep(2)

            return {
                'sucesso': True,
                'ultimo_concurso': ultimo,
                'inseridos': inseridos,
                'ja_existentes': ja_existentes,
                'erros': erros
            }

        except Exception as e:
            return {'erro': str(e)}

    @staticmethod
    def sincronizar_novos():
        """Sincroniza apenas os concursos novos com delay"""
        try:
            ultimo_api = CaixaService.buscar_ultimo_concurso()
            if ultimo_api == 0:
                return {'erro': 'Não foi possível buscar o último concurso da API'}

            ultimo_banco = db.session.query(db.func.max(Sorteio.concurso)).scalar()

            if ultimo_banco is None:
                print("💾 Banco vazio, sincronizando todos...")
                return CaixaService.sincronizar_todos()

            if ultimo_banco >= ultimo_api:
                return {
                    'sucesso': True,
                    'mensagem': 'Banco já está atualizado',
                    'ultimo_banco': ultimo_banco,
                    'ultimo_api': ultimo_api,
                    'inseridos': 0
                }

            print(f"📊 Sincronizando do {ultimo_banco + 1} até {ultimo_api}...")
            print(f"⏱️  Delay entre requisições: {CaixaService.DELAY_ENTRE_REQUISICOES}s")
            print()

            inseridos = 0
            erros = 0
            total = ultimo_api - ultimo_banco

            for num in range(ultimo_banco + 1, ultimo_api + 1):
                try:
                    # Mostrar progresso
                    progresso = num - ultimo_banco
                    print(f"📍 {progresso}/{total}: Buscando concurso {num}...", end=' ')
                    
                    dados = CaixaService.buscar_concurso(num)
                    
                    if dados:
                        _, status = CaixaService.salvar_concurso(dados)
                        if status == 'inserido':
                            inseridos += 1
                            print(f"✅")
                        else:
                            print(f"⏭️  já existe")
                    else:
                        erros += 1
                        print(f"❌ não encontrado")
                    
                    # DELAY para não sobrecarregar
                    time.sleep(CaixaService.DELAY_ENTRE_REQUISICOES)
                    
                except Exception as e:
                    erros += 1
                    print(f"❌ Erro: {str(e)[:50]}")
                    time.sleep(2)

            return {
                'sucesso': True,
                'ultimo_banco': ultimo_banco,
                'ultimo_api': ultimo_api,
                'inseridos': inseridos,
                'erros': erros
            }

        except Exception as e:
            return {'erro': str(e)}

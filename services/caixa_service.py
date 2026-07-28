"""
Serviço FINAL - Busca paralela + Salvamento sequencial
COPIE ESTE ARQUIVO PARA: services/caixa_service.py
"""

import requests
from datetime import datetime
from models.sorteio import Sorteio, db
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

# Desabilitar warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CaixaService:
    """Serviço para buscar e sincronizar sorteios da API da Caixa"""

    API_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte"
    MAX_WORKERS = 10  # Buscar em paralelo
    TIMEOUT = 20
    MAX_RETRIES = 3

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
    def buscar_ultimo_concurso():
        """Busca o último concurso disponível na API"""
        for tentativa in range(1, CaixaService.MAX_RETRIES + 1):
            try:
                response = requests.get(
                    CaixaService.API_URL,
                    timeout=CaixaService.TIMEOUT,
                    headers={'User-Agent': 'Mozilla/5.0'},
                    verify=False
                )
                if response.status_code == 200:
                    dados = response.json()
                    return dados.get('numero', 0)
                time.sleep(1)
            except Exception as e:
                if tentativa == CaixaService.MAX_RETRIES:
                    print(f"Erro ao buscar último concurso: {str(e)[:100]}")
                    return 0
                time.sleep(2)
        return 0

    @staticmethod
    def buscar_concurso(numero):
        """Busca um concurso específico na API com retry (SEM SALVAR NO BANCO)"""
        url = f"{CaixaService.API_URL}/{numero}"

        for tentativa in range(1, CaixaService.MAX_RETRIES + 1):
            try:
                response = requests.get(
                    url,
                    timeout=CaixaService.TIMEOUT,
                    headers={'User-Agent': 'Mozilla/5.0'},
                    verify=False
                )

                if response.status_code == 200:
                    return response.json()

                if tentativa < CaixaService.MAX_RETRIES:
                    time.sleep(1)

            except requests.exceptions.SSLError:
                if tentativa < CaixaService.MAX_RETRIES:
                    time.sleep(2)
                continue
            except requests.exceptions.Timeout:
                if tentativa < CaixaService.MAX_RETRIES:
                    time.sleep(2)
                continue
            except Exception:
                if tentativa < CaixaService.MAX_RETRIES:
                    time.sleep(1)
                continue

        return None

    @staticmethod
    def salvar_concurso(dados_api):
        """Salva um concurso no banco (CHAMADO DENTRO DO APP CONTEXT)"""
        try:
            concurso = dados_api.get('numero')
            data_str = dados_api.get('dataApuracao')
            data_sorteio = datetime.strptime(data_str, '%d/%m/%Y').date()

            dezenas_ordem = dados_api.get('dezenasSorteadasOrdemSorteio', [])
            dezenas_cresc = dados_api.get('listaDezenas', sorted([int(x) for x in dezenas_ordem]) if dezenas_ordem else [])
            mes_valor_api = dados_api.get('nomeTimeCoracaoMesSorte', 'Janeiro')
            mes_sorte = CaixaService.normalizar_mes(mes_valor_api)

            # Verificar se já existe
            sorteio_existente = Sorteio.query.filter_by(concurso=concurso).first()
            if sorteio_existente:
                # SE o banco já tem o concurso mas a ORDEM DE SORTEIO tá vazia/nula, vamos atualizá-la!
                if sorteio_existente.sorteio_1 is None and len(dezenas_ordem) == 7:
                    sorteio_existente.sorteio_1 = int(dezenas_ordem[0])
                    sorteio_existente.sorteio_2 = int(dezenas_ordem[1])
                    sorteio_existente.sorteio_3 = int(dezenas_ordem[2])
                    sorteio_existente.sorteio_4 = int(dezenas_ordem[3])
                    sorteio_existente.sorteio_5 = int(dezenas_ordem[4])
                    sorteio_existente.sorteio_6 = int(dezenas_ordem[5])
                    sorteio_existente.sorteio_7 = int(dezenas_ordem[6])
                    db.session.commit()
                return 'ja_existe'

            if not dezenas_cresc or not dezenas_ordem:
                return 'dados_invalidos'

            # Criar novo
            novo_sorteio = Sorteio(
                concurso=concurso,
                posicao_1=int(dezenas_cresc[0]),
                posicao_2=int(dezenas_cresc[1]),
                posicao_3=int(dezenas_cresc[2]),
                posicao_4=int(dezenas_cresc[3]),
                posicao_5=int(dezenas_cresc[4]),
                posicao_6=int(dezenas_cresc[5]),
                posicao_7=int(dezenas_cresc[6]),
                sorteio_1=int(dezenas_ordem[0]),
                sorteio_2=int(dezenas_ordem[1]),
                sorteio_3=int(dezenas_ordem[2]),
                sorteio_4=int(dezenas_ordem[3]),
                sorteio_5=int(dezenas_ordem[4]),
                sorteio_6=int(dezenas_ordem[5]),
                sorteio_7=int(dezenas_ordem[6]),
                mes_sorte=mes_sorte,
                data_sorteio=data_sorteio
            )

            db.session.add(novo_sorteio)
            db.session.commit()

            return 'inserido'

        except Exception as e:
            db.session.rollback()
            return f'erro: {str(e)[:50]}'

    @staticmethod
    def sincronizar_todos():
        """
        Sincroniza todos os concursos
        ESTRATÉGIA: Buscar em paralelo (threads), salvar sequencial (sem threads)
        """
        try:
            ultimo = CaixaService.buscar_ultimo_concurso()
            if ultimo == 0:
                return {'erro': 'Não foi possível buscar o último concurso'}

            print(f"📊 Último concurso: {ultimo}")
            print(f"⚡ Buscando com {CaixaService.MAX_WORKERS} threads paralelas")
            print(f"💾 Salvando sequencialmente (evita erro de contexto)")
            print()

            inseridos = 0
            ja_existentes = 0
            erros = 0

            inicio = time.time()

            # FASE 1: Buscar todos os dados em paralelo
            print("🔄 Fase 1: Buscando dados da API...")
            dados_concursos = {}

            with ThreadPoolExecutor(max_workers=CaixaService.MAX_WORKERS) as executor:
                futures = {
                    executor.submit(CaixaService.buscar_concurso, num): num
                    for num in range(1, ultimo + 1)
                }

                for i, future in enumerate(as_completed(futures), 1):
                    numero = futures[future]
                    dados = future.result()

                    if dados:
                        dados_concursos[numero] = dados

                    if i % 100 == 0 or i == ultimo:
                        print(f"   📥 Baixados: {i}/{ultimo} ({int(i/ultimo*100)}%)")

            print(f"✅ {len(dados_concursos)} concursos baixados da API")
            print()

            # FASE 2: Salvar no banco sequencialmente (dentro do app context)
            print("💾 Fase 2: Salvando no banco de dados...")

            for i, (numero, dados) in enumerate(sorted(dados_concursos.items()), 1):
                status = CaixaService.salvar_concurso(dados)

                if status == 'inserido':
                    inseridos += 1
                elif status == 'ja_existe':
                    ja_existentes += 1
                else:
                    erros += 1
                    if erros <= 5:
                        print(f"   ❌ Concurso {numero}: {status}")

                if i % 100 == 0 or i == len(dados_concursos):
                    print(f"   💾 Salvos: {i}/{len(dados_concursos)} ({int(i/len(dados_concursos)*100)}%)")

            tempo_total = time.time() - inicio

            print()
            print(f"⏱️  Tempo total: {tempo_total:.1f}s ({tempo_total/60:.1f} min)")
            print(f"⚡ Velocidade: {ultimo/tempo_total:.1f} concursos/seg")

            return {
                'sucesso': True,
                'ultimo_concurso': ultimo,
                'inseridos': inseridos,
                'ja_existentes': ja_existentes,
                'erros': erros,
                'tempo_segundos': tempo_total
            }

        except Exception as e:
            return {'erro': str(e)}

    @staticmethod
    def sincronizar_novos():
        """Sincroniza apenas os concursos novos"""
        try:
            ultimo_api = CaixaService.buscar_ultimo_concurso()
            if ultimo_api == 0:
                return {'erro': 'Não foi possível buscar o último concurso da API'}

            ultimo_banco = db.session.query(db.func.max(Sorteio.concurso)).scalar()

            if ultimo_banco is None:
                print("💾 Banco vazio, sincronizando todos...")
                return CaixaService.sincronizar_todos()

            concursos_pendentes = []
            
            # 1. Procurar novos concursos
            if ultimo_banco < ultimo_api:
                concursos_pendentes.extend(list(range(ultimo_banco + 1, ultimo_api + 1)))
                
            # 2. Procurar concursos existentes mas sem ordem de sorteio (garantia para exibir sempre ORDEM SORTEIO)
            concursos_sem_ordem = db.session.query(Sorteio.concurso).filter(Sorteio.sorteio_1.is_(None)).all()
            for (conc,) in concursos_sem_ordem:
                if conc not in concursos_pendentes:
                    concursos_pendentes.append(conc)

            if not concursos_pendentes:
                return {
                    'sucesso': True,
                    'mensagem': 'Banco já está atualizado e todas as ordens de sorteio estao corretas',
                    'ultimo_banco': ultimo_banco,
                    'ultimo_api': ultimo_api,
                    'inseridos': 0
                }

            print(f"📊 Processando {len(concursos_pendentes)} concursos (Novos / Atualização de Ordem)...")
            print(f"⚡ Buscando com {CaixaService.MAX_WORKERS} threads")
            print()

            inseridos = 0
            atualizados = 0
            erros = 0
            inicio = time.time()

            # Buscar em paralelo
            dados_concursos = {}

            with ThreadPoolExecutor(max_workers=CaixaService.MAX_WORKERS) as executor:
                futures = {
                    executor.submit(CaixaService.buscar_concurso, num): num
                    for num in concursos_pendentes
                }

                for future in as_completed(futures):
                    numero = futures[future]
                    dados = future.result()
                    if dados:
                        dados_concursos[numero] = dados

            # Salvar sequencialmente
            for numero, dados in sorted(dados_concursos.items()):
                status = CaixaService.salvar_concurso(dados)

                if status == 'inserido':
                    inseridos += 1
                elif status == 'ja_existe':
                    atualizados += 1
                else:
                    erros += 1

            tempo_total = time.time() - inicio
            print(f"\n⏱️  Tempo: {tempo_total:.1f}s")
            print(f"✅ Inseridos: {inseridos}")
            print(f"🔄 Atualizados: {atualizados}")
            print(f"❌ Erros: {erros}")

            return {
                'sucesso': True,
                'ultimo_banco': ultimo_banco,
                'ultimo_api': ultimo_api,
                'inseridos': inseridos,
                'erros': erros,
                'tempo_segundos': tempo_total
            }

        except Exception as e:
            return {'erro': str(e)}

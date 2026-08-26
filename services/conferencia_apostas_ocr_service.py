"""

Serviço de Conferência de Apostas com OCR - Dia de Sorte

Responsável por processar screenshots de apostas via OCR e comparar com resultados oficiais



IMPORTANTE: Os prêmios são ACUMULATIVOS!

- Se acertar 4 números + Mês da Sorte = ganha AMBOS os prêmios (soma)

- Se acertar 5 números + Mês da Sorte = ganha AMBOS os prêmios (soma)

- E assim por diante...

"""



import os

import re

from typing import Dict, List, Optional

from PIL import Image

try:

    import pytesseract

except ImportError:

    pytesseract = None



from models.sorteio import Sorteio

from services.configuracao_service import ConfiguracaoService





class ConferenciaApostasOCRService:

    """

    Service para processar screenshots de apostas via OCR e comparar com resultados

    """



    # Tabela de preços oficial da Dia de Sorte (valores oficiais Caixa)

    TABELA_PRECOS = {

        7: 2.50,       # 7 dezenas

        8: 20.00,      # 8 dezenas

        9: 90.00,      # 9 dezenas

        10: 300.00,    # 10 dezenas

        11: 825.00,    # 11 dezenas

        12: 1980.00,   # 12 dezenas

        13: 4290.00,   # 13 dezenas

        14: 8580.00,   # 14 dezenas

        15: 16302.00   # 15 dezenas

    }



    # Mapeamento de meses em português

    MESES_PT = {

        'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'MARCO': 3,

        'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,

        'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9,

        'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12,

        # Abreviações

        'JAN': 1, 'FEV': 2, 'MAR': 3, 'ABR': 4,

        'MAI': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8,

        'SET': 9, 'OUT': 10, 'NOV': 11, 'DEZ': 12

    }



    # Diretório base para screenshots

    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conferencia_apostas')



    progress_store = {}



    @classmethod

    def atualizar_progresso(cls, task_id: str, status: str, progresso: int, total: int = 0, processados: int = 0, resultado = None):

        if not task_id: return

        cls.progress_store[task_id] = {

            'status': status,

            'progresso': progresso,

            'total': total,

            'processados': processados,

            'resultado': resultado

        }



    @classmethod

    def obter_progresso(cls, task_id: str):

        return cls.progress_store.get(task_id, {'status': 'nao_encontrado'})



    @staticmethod

    def calcular_valor_aposta(quantidade_dezenas: int) -> float:

        """

        Calcula o valor da aposta baseado na quantidade de dezenas



        Args:

            quantidade_dezenas: Quantidade de dezenas apostadas (7 a 15)



        Returns:

            Valor da aposta em reais

        """

        if quantidade_dezenas < 7 or quantidade_dezenas > 15:

            return 2.50  # Valor padrão para apostas inválidas



        return ConferenciaApostasOCRService.TABELA_PRECOS.get(quantidade_dezenas, 2.50)



    @staticmethod

    def normalizar_mes(mes_input) -> Optional[int]:

        """

        Converte mês em qualquer formato para int (1-12)



        Aceita formatos:

        - Numérico: 1, 01, "1", "01"

        - Abreviado: "Jan", "Fev", etc.

        - Nome completo: "Janeiro", "Fevereiro", etc.



        Args:

            mes_input: Mês em qualquer formato



        Returns:

            Número do mês (1-12) ou None se inválido

        """

        # Se já é int ou float

        if isinstance(mes_input, (int, float)):

            mes_num = int(mes_input)

            if 1 <= mes_num <= 12:

                return mes_num

            return None



        # Se for None

        if mes_input is None:

            return None



        # Converter para string e limpar

        mes_str = str(mes_input).strip()



        # Tentar conversão numérica direta

        try:

            mes_num = int(mes_str)

            if 1 <= mes_num <= 12:

                return mes_num

        except ValueError:

            pass



        # Tentar buscar no mapeamento de nomes

        mes_upper = mes_str.upper()

        if mes_upper in ConferenciaApostasOCRService.MESES_PT:

            return ConferenciaApostasOCRService.MESES_PT[mes_upper]



        # Não encontrado

        return None



    @staticmethod

    def listar_concursos_disponiveis() -> List[Dict]:

        """

        Lista todos os concursos disponíveis na pasta mnt/conferencia_apostas/



        Returns:

            Lista de dicionários com informações dos concursos

        """

        try:

            if not os.path.exists(ConferenciaApostasOCRService.BASE_DIR):

                os.makedirs(ConferenciaApostasOCRService.BASE_DIR)

                return []



            concursos = []



            for pasta in os.listdir(ConferenciaApostasOCRService.BASE_DIR):

                pasta_path = os.path.join(ConferenciaApostasOCRService.BASE_DIR, pasta)



                # Ignorar arquivos, processar apenas pastas

                if not os.path.isdir(pasta_path):

                    continue



                # Tentar extrair número do concurso do nome da pasta

                try:

                    numero_concurso = int(pasta)

                except ValueError:

                    continue  # Ignorar pastas com nomes não numéricos



                # Contar screenshots na pasta

                screenshots = [

                    f for f in os.listdir(pasta_path)

                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))

                ]



                # Verificar se concurso existe no banco

                sorteio = Sorteio.query.filter_by(concurso=numero_concurso).first()



                # Verificar se existe arquivo JSON

                arquivo_json = os.path.join(pasta_path, 'apostas.json')

                tem_json = os.path.exists(arquivo_json)

                

                total_apostas = 0

                if tem_json:

                    try:

                        import json

                        with open(arquivo_json, 'r', encoding='utf-8') as f:

                            dados = json.load(f)

                            total_apostas = len(dados.get('apostas', []))

                    except Exception:

                        pass

                else:

                    total_apostas = len(screenshots)



                concursos.append({

                    'numero_concurso': numero_concurso,

                    'total_screenshots': len(screenshots),

                    'total_apostas': total_apostas,

                    'resultado_disponivel': sorteio is not None,

                    'pasta': pasta,

                    'screenshots': screenshots,

                    'tem_json': tem_json,

                    'data_sorteio': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio and sorteio.data_sorteio else None

                })



            # Ordenar por número do concurso (mais recente primeiro)

            concursos.sort(key=lambda x: x['numero_concurso'], reverse=True)



            return concursos



        except Exception as e:

            print(f"Erro ao listar concursos: {str(e)}")

            return []



    @staticmethod

    def extrair_numeros_do_texto(texto: str) -> List[int]:

        """

        Extrai números de 1 a 31 do texto OCR



        Args:

            texto: Texto extraído via OCR



        Returns:

            Lista de números encontrados (ordenados e sem duplicatas)

        """

        # Encontrar todos os números no texto

        numeros_encontrados = re.findall(r'\b(\d{1,2})\b', texto)



        # Converter para int e filtrar apenas 1-31

        numeros = []

        for num_str in numeros_encontrados:

            try:

                num = int(num_str)

                if 1 <= num <= 31 and num not in numeros:

                    numeros.append(num)

            except ValueError:

                continue



        return sorted(numeros)



    @staticmethod

    def extrair_mes_do_texto(texto: str) -> Optional[int]:

        """

        Extrai o mês do texto OCR



        Args:

            texto: Texto extraído via OCR



        Returns:

            Número do mês (1-12) ou None se não encontrado

        """

        texto_upper = texto.upper()



        for mes_nome, mes_num in ConferenciaApostasOCRService.MESES_PT.items():

            if mes_nome in texto_upper:

                return mes_num



        return None



    @staticmethod

    def processar_screenshot_ocr(caminho_imagem: str) -> Dict:

        """

        Processa um screenshot usando OCR



        Args:

            caminho_imagem: Caminho completo para o arquivo de imagem



        Returns:

            Dicionário com dados extraídos ou erro

        """

        # Verificar se pytesseract está disponível

        if pytesseract is None:

            return {

                'sucesso': False,

                'erro': 'OCR não disponível. Instale: pip install pytesseract',

                'mensagem': 'Biblioteca pytesseract não instalada'

            }



        try:

            # Abrir imagem

            imagem = Image.open(caminho_imagem)



            # Executar OCR

            texto_completo = pytesseract.image_to_string(imagem, lang='por')



            # Dividir texto em linhas para análise

            linhas = texto_completo.split('\n')



            # Tentar extrair informações

            numeros_sorteados = []

            numeros_apostados = []

            mes_sorteado = None

            mes_apostado = None

            concurso_encontrado = None



            # Procurar padrões no texto

            procurar_apostados = False



            for linha in linhas:

                linha_limpa = linha.strip()



                # Procurar número do concurso

                if 'Concurso' in linha_limpa or 'concurso' in linha_limpa:

                    nums = re.findall(r'\d{3,5}', linha_limpa)

                    if nums:

                        concurso_encontrado = int(nums[0])



                # Identificar seção de números sorteados

                if 'Números sorteados' in linha_limpa or 'sorteados' in linha_limpa.lower():

                    procurar_apostados = False

                    continue



                # Identificar seção de seus números

                if 'Seus números' in linha_limpa or 'seus n' in linha_limpa.lower():

                    procurar_apostados = True

                    continue



                # Extrair números

                nums = ConferenciaApostasOCRService.extrair_numeros_do_texto(linha_limpa)

                if nums:

                    if procurar_apostados:

                        numeros_apostados.extend(nums)

                    else:

                        numeros_sorteados.extend(nums)



                # Extrair meses

                mes = ConferenciaApostasOCRService.extrair_mes_do_texto(linha_limpa)

                if mes:

                    if procurar_apostados:

                        mes_apostado = mes

                    else:

                        mes_sorteado = mes



            # Remover duplicatas e limitar a 7-15 números para apostados, 7 para sorteados

            numeros_sorteados = sorted(list(set(numeros_sorteados)))[:7]

            numeros_apostados = sorted(list(set(numeros_apostados)))[:15]  # Aceita até 15 dezenas



            return {

                'sucesso': True,

                'concurso': concurso_encontrado,

                'numeros_sorteados': numeros_sorteados,

                'numeros_apostados': numeros_apostados,

                'mes_sorteado': mes_sorteado,

                'mes_apostado': mes_apostado,

                'texto_completo': texto_completo,

                'confianca': ConferenciaApostasOCRService._calcular_confianca(

                    numeros_sorteados, numeros_apostados, mes_sorteado, mes_apostado

                )

            }



        except Exception as e:

            return {

                'sucesso': False,

                'erro': str(e),

                'mensagem': f'Erro ao processar OCR: {str(e)}'

            }



    @staticmethod

    def _calcular_confianca(nums_sort: List, nums_apost: List, mes_sort: int, mes_apost: int) -> str:

        """

        Calcula o nível de confiança da extração OCR



        Returns:

            'alta', 'media' ou 'baixa'

        """

        pontos = 0



        # Números sorteados completos (7 números)

        if len(nums_sort) == 7:

            pontos += 2

        elif len(nums_sort) >= 5:

            pontos += 1



        # Números apostados completos (7 a 15 números)

        if 7 <= len(nums_apost) <= 15:

            pontos += 2

        elif len(nums_apost) >= 5:

            pontos += 1



        # Mês sorteado encontrado

        if mes_sort:

            pontos += 1



        # Mês apostado encontrado

        if mes_apost:

            pontos += 1



        if pontos >= 5:

            return 'alta'

        elif pontos >= 3:

            return 'media'

        else:

            return 'baixa'



    @staticmethod

    def comparar_aposta_com_resultado(numeros_apostados: List[int],

                                     mes_apostado: int,

                                     sorteio: Sorteio) -> Dict:

        """

        Compara uma aposta com o resultado oficial do sorteio



        IMPORTANTE: Os prêmios são ACUMULATIVOS!

        Se acertar 4 números + Mês da Sorte = ganha AMBOS (soma dos valores)



        Args:

            numeros_apostados: Lista com os 7 números apostados

            mes_apostado: Número do mês apostado (1-12)

            sorteio: Objeto Sorteio com resultado oficial



        Returns:

            Dicionário com análise da aposta incluindo faixas detalhadas

        """

        # Extrair números sorteados do objeto Sorteio

        numeros_sorteados = [

            sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,

            sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,

            sorteio.posicao_7

        ]



        # Calcular acertos

        acertos = len(set(numeros_apostados) & set(numeros_sorteados))



        # Verificar acerto do mês (normalizar para int antes de comparar)

        mes_apostado_normalizado = ConferenciaApostasOCRService.normalizar_mes(mes_apostado)

        acertou_mes = (mes_apostado_normalizado == sorteio.mes_sorte) if mes_apostado_normalizado else False



        # Determinar TODAS as faixas de premiação atingidas (ACUMULATIVO!)

        faixas_atingidas = ConferenciaApostasOCRService._determinar_faixas_premiacao(acertos, acertou_mes)



        # Obter valores de cada prêmio e somar (ACUMULATIVO!)

        detalhes_premios = ConferenciaApostasOCRService._obter_valores_premios(sorteio, faixas_atingidas)



        # Valor total do prêmio é a SOMA de todas as faixas atingidas

        valor_premio_total = sum(p['valor'] for p in detalhes_premios)



        # Manter compatibilidade com campo 'faixa' (agora mostra todas separadas por ' + ')

        faixa_display = ' + '.join(faixas_atingidas) if faixas_atingidas else None



        return {

            'acertos': acertos,

            'acertou_mes': acertou_mes,

            'faixa': faixa_display,  # Ex: "5ª Faixa (4 acertos) + 6ª Faixa (mês da sorte)"

            'faixas_atingidas': faixas_atingidas,  # Lista: ['5ª Faixa (4 acertos)', '6ª Faixa (mês da sorte)']

            'detalhes_premios': detalhes_premios,  # Lista com detalhes de cada prêmio

            'valor_premio': valor_premio_total,  # Soma total ACUMULATIVA

            'numeros_acertados': sorted(list(set(numeros_apostados) & set(numeros_sorteados))),

            'premiado': len(faixas_atingidas) > 0

        }



    @staticmethod

    def _determinar_faixas_premiacao(acertos: int, acertou_mes: bool) -> List[str]:

        """

        Determina TODAS as faixas de premiação atingidas (ACUMULATIVO!)



        Na Dia de Sorte, os prêmios são acumulativos:

        - Se acertar 4 números + Mês = ganha prêmio de 4 acertos E prêmio do mês

        - Se acertar 5 números + Mês = ganha prêmio de 5 acertos E prêmio do mês

        - E assim por diante...



        Returns:

            Lista de faixas atingidas (pode ter múltiplas!)

        """

        faixas = []



        # Verificar faixas por quantidade de acertos

        if acertos == 7 and acertou_mes:

            faixas.append('1ª Faixa (7 acertos + mês)')

        elif acertos == 7:

            faixas.append('2ª Faixa (7 acertos)')

        elif acertos == 6:

            faixas.append('3ª Faixa (6 acertos)')

        elif acertos == 5:

            faixas.append('4ª Faixa (5 acertos)')

        elif acertos == 4:

            faixas.append('5ª Faixa (4 acertos)')



        # ACUMULATIVO: Se acertou o mês E tem acertos de 4 a 6, adiciona também o prêmio do mês

        # (Se tem 7 acertos + mês, já entra na 1ª Faixa especial, não soma separado)

        if acertou_mes and acertos >= 4 and acertos < 7:

            faixas.append('6ª Faixa (mês da sorte)')



        # Se APENAS acertou o mês (sem acertos de números suficientes)

        if acertou_mes and acertos < 4:

            faixas.append('6ª Faixa (mês da sorte)')



        return faixas



    @staticmethod

    def _obter_valores_premios(sorteio: Sorteio, faixas: List[str]) -> List[Dict]:

        """

        Obtém os valores de prêmio para cada faixa atingida



        Args:

            sorteio: Objeto Sorteio com os valores dos prêmios

            faixas: Lista de faixas atingidas



        Returns:

            Lista de dicionários com detalhes de cada prêmio

        """

        if not faixas:

            return []



        # Mapeamento de faixas para campos do Sorteio

        mapa_faixas = {

            '1ª Faixa (7 acertos + mês)': ('valor_premio_7_acertos', '7 acertos + mês'),

            '2ª Faixa (7 acertos)': ('valor_premio_7_acertos', '7 acertos'),

            '3ª Faixa (6 acertos)': ('valor_premio_6_acertos', '6 acertos'),

            '4ª Faixa (5 acertos)': ('valor_premio_5_acertos', '5 acertos'),

            '5ª Faixa (4 acertos)': ('valor_premio_4_acertos', '4 acertos'),

            '6ª Faixa (mês da sorte)': ('valor_premio_mes_sorte', 'Mês da Sorte')

        }



        detalhes = []

        for faixa in faixas:

            if faixa in mapa_faixas:

                campo, descricao = mapa_faixas[faixa]

                valor = getattr(sorteio, campo, 0.0)

                valor = float(valor) if valor else 0.0

                detalhes.append({

                    'faixa': faixa,

                    'descricao': descricao,

                    'valor': valor

                })



        return detalhes



    @staticmethod

    def _obter_valor_premio(sorteio: Sorteio, faixa: Optional[str]) -> float:

        """

        Obtém o valor do prêmio para uma faixa específica

        DEPRECATED: Use _obter_valores_premios para prêmios acumulativos



        Returns:

            Valor do prêmio ou 0.0 se não premiado

        """

        if not faixa:

            return 0.0



        # Mapeamento de faixas para campos do Sorteio

        mapa_faixas = {

            '1ª Faixa (7 acertos + mês)': sorteio.valor_premio_7_acertos,

            '2ª Faixa (7 acertos)': sorteio.valor_premio_7_acertos,

            '3ª Faixa (6 acertos)': sorteio.valor_premio_6_acertos,

            '4ª Faixa (5 acertos)': sorteio.valor_premio_5_acertos,

            '5ª Faixa (4 acertos)': sorteio.valor_premio_4_acertos,

            '6ª Faixa (mês da sorte)': sorteio.valor_premio_mes_sorte

        }



        valor = mapa_faixas.get(faixa, 0.0)

        return float(valor) if valor else 0.0



    @staticmethod

    def processar_apostas_json(arquivo_json: str, sorteio: Sorteio, task_id: str = None) -> Dict:

        """

        Processa apostas de um arquivo JSON



        Args:

            arquivo_json: Caminho completo para o arquivo apostas.json

            sorteio: Objeto Sorteio com resultado oficial

            task_id: ID da tarefa em segundo plano para relatar progresso



        Returns:

            Dicionário com resultados do processamento

        """

        try:

            import json



            # Ler arquivo JSON

            with open(arquivo_json, 'r', encoding='utf-8') as f:

                dados = json.load(f)



            # Validar estrutura do JSON

            if 'concurso' not in dados or 'apostas' not in dados:

                return {

                    'sucesso': False,

                    'erro': 'json_invalido',

                    'mensagem': 'Arquivo JSON deve conter "concurso" e "apostas"'

                }



            total_items = len(dados['apostas'])

            if task_id:

                ConferenciaApostasOCRService.atualizar_progresso(task_id, 'processando', 0, total=total_items, processados=0)



            # Processar cada aposta

            apostas_processadas = []

            total_investido = 0.0

            total_ganho = 0.0



            for idx, aposta in enumerate(dados['apostas'], 1):

                if task_id:

                    progresso = int((idx / total_items) * 100)

                    ConferenciaApostasOCRService.atualizar_progresso(task_id, 'processando', progresso, total=total_items, processados=idx)



                # Validar estrutura da aposta

                if 'numeros' not in aposta:

                    apostas_processadas.append({

                        'numero_aposta': idx,

                        'erro': True,

                        'mensagem': f'Aposta {idx} não contém campo "numeros"'

                    })

                    continue



                numeros_apostados = aposta['numeros']

                mes_apostado = aposta.get('mes')



                # Validar quantidade de números (7 a 15 dezenas permitidas)

                if len(numeros_apostados) < 7 or len(numeros_apostados) > 15:

                    apostas_processadas.append({

                        'numero_aposta': idx,

                        'erro': True,

                        'mensagem': f'Aposta {idx} deve ter entre 7 e 15 números (tem {len(numeros_apostados)})'

                    })

                    continue



                # Calcular valor da aposta baseado na quantidade de dezenas

                qtd_dezenas = len(numeros_apostados)

                valor_aposta = ConferenciaApostasOCRService.calcular_valor_aposta(qtd_dezenas)



                # Comparar com resultado oficial (agora retorna prêmios ACUMULATIVOS)

                resultado = ConferenciaApostasOCRService.comparar_aposta_com_resultado(

                    numeros_apostados,

                    mes_apostado,

                    sorteio

                )



                # Calcular valores

                total_investido += valor_aposta

                total_ganho += resultado['valor_premio']



                apostas_processadas.append({

                    'numero_aposta': idx,

                    'arquivo': 'apostas.json',

                    'erro_ocr': False,

                    'dados_incompletos': False,

                    'dados_extraidos': {

                        'numeros_apostados': numeros_apostados,

                        'mes_apostado': mes_apostado,

                        'confianca': 'alta'

                    },

                    'resultado': resultado,

                    'valor_aposta': valor_aposta,

                    'valor_ganho': resultado['valor_premio']

                })



            # Calcular estatísticas

            apostas_validas = [a for a in apostas_processadas if not a.get('erro')]



            distribuicao_acertos = {}

            for aposta in apostas_validas:

                acertos = aposta['resultado']['acertos']

                distribuicao_acertos[acertos] = distribuicao_acertos.get(acertos, 0) + 1



            apostas_premiadas = sum(1 for a in apostas_validas if a['resultado']['premiado'])



            lucro = total_ganho - total_investido

            roi = (lucro / total_investido * 100) if total_investido > 0 else 0



            # Calcular distribuição por faixa (ATUALIZADO para múltiplas faixas)

            distribuicao_faixas = {}

            for aposta in apostas_validas:

                # Iterar sobre todas as faixas atingidas (pode ser mais de uma!)

                faixas_atingidas = aposta['resultado'].get('faixas_atingidas', [])

                detalhes_premios = aposta['resultado'].get('detalhes_premios', [])



                for detalhe in detalhes_premios:

                    faixa = detalhe['faixa']

                    valor = detalhe['valor']

                    if faixa not in distribuicao_faixas:

                        distribuicao_faixas[faixa] = {'quantidade': 0, 'total_ganho': 0.0}

                    distribuicao_faixas[faixa]['quantidade'] += 1

                    distribuicao_faixas[faixa]['total_ganho'] += valor



            # ==========================================================

            # NOVO: Calcular e Salvar Métricas Estratégicas no Banco

            # ==========================================================

            try:

                ConferenciaApostasOCRService.salvar_metricas_estrategicas(

                    sorteio.concurso,

                    sorteio,

                    apostas_validas,

                    total_investido,

                    total_ganho,

                    lucro

                )

            except Exception as e:

                print(f"Erro ao salvar métricas estratégicas: {str(e)}")

                # Não interromper o fluxo principal se falhar o salvamento de métricas



            retorno = {

                'sucesso': True,

                'concurso': sorteio.concurso,

                'origem': 'JSON',

                'resultado_sorteio': {

                    'concurso': sorteio.concurso,

                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else None,

                    'numeros': [

                        sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,

                        sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,

                        sorteio.posicao_7

                    ],

                    'numeros_ordem_sorteio': sorteio.get_ordem_sorteio_lista(),

                    'mes_sorte': sorteio.mes_sorte

                },

                'apostas': apostas_processadas,

                'resumo': {

                    'total_apostas': len(dados['apostas']),

                    'apostas_processadas': len(apostas_validas),

                    'apostas_com_erro': len([a for a in apostas_processadas if a.get('erro')]),

                    'apostas_incompletas': 0,

                    'total_investido': total_investido,

                    'total_ganho': total_ganho,

                    'lucro': lucro,

                    'roi': roi,

                    'apostas_premiadas': apostas_premiadas,

                    'distribuicao_acertos': distribuicao_acertos,

                    'distribuicao_faixas': distribuicao_faixas

                }

            }

            if task_id:

                ConferenciaApostasOCRService.atualizar_progresso(task_id, 'concluido', 100, total=total_items, processados=total_items, resultado=retorno)

            return retorno



        except json.JSONDecodeError as e:

            return {

                'sucesso': False,

                'erro': 'json_malformado',

                'mensagem': f'Erro ao decodificar JSON: {str(e)}'

            }

        except Exception as e:

            return {

                'sucesso': False,

                'erro': 'excecao',

                'mensagem': f'Erro ao processar apostas.json: {str(e)}'

            }







    @staticmethod

    def processar_concurso(numero_concurso: int, task_id: str = None) -> Dict:

        """

        Processa todos os screenshots de um concurso OU arquivo apostas.json



        Args:

            numero_concurso: Número do concurso a processar

            task_id: ID da tarefa em segundo plano para relatar progresso



        Returns:

            Dicionário com resultados completos do processamento

        """

        try:

            # Buscar sorteio no banco

            sorteio = Sorteio.query.filter_by(concurso=numero_concurso).first()



            if not sorteio:

                return {

                    'sucesso': False,

                    'erro': 'concurso_nao_encontrado',

                    'mensagem': f'Concurso {numero_concurso} não encontrado no banco de dados'

                }



            # Caminho da pasta do concurso

            pasta_concurso = os.path.join(ConferenciaApostasOCRService.BASE_DIR, str(numero_concurso))



            if not os.path.exists(pasta_concurso):

                return {

                    'sucesso': False,

                    'erro': 'pasta_nao_encontrada',

                    'mensagem': f'Pasta do concurso {numero_concurso} não encontrada'

                }



            # Listar screenshots

            screenshots = [

                f for f in os.listdir(pasta_concurso)

                if f.lower().endswith(('.jpg', '.jpeg', '.png'))

            ]



            # Se não há screenshots, procurar arquivo apostas.json

            if not screenshots:

                arquivo_json = os.path.join(pasta_concurso, 'apostas.json')

                if os.path.exists(arquivo_json):

                    return ConferenciaApostasOCRService.processar_apostas_json(arquivo_json, sorteio, task_id)

                else:

                    return {

                        'sucesso': False,

                        'erro': 'sem_screenshots_nem_json',

                        'mensagem': f'Nenhum screenshot ou arquivo apostas.json encontrado na pasta do concurso {numero_concurso}'

                    }



            total_items = len(screenshots)

            if task_id:

                ConferenciaApostasOCRService.atualizar_progresso(task_id, 'processando', 0, total=total_items, processados=0)



            # Processar cada screenshot

            apostas_processadas = []

            total_investido = 0.0

            total_ganho = 0.0



            for idx, screenshot in enumerate(screenshots, 1):

                if task_id:

                    progresso = int((idx / total_items) * 100)

                    ConferenciaApostasOCRService.atualizar_progresso(task_id, 'processando', progresso, total=total_items, processados=idx)



                caminho_completo = os.path.join(pasta_concurso, screenshot)



                # Processar OCR

                dados_ocr = ConferenciaApostasOCRService.processar_screenshot_ocr(caminho_completo)



                if not dados_ocr['sucesso']:

                    apostas_processadas.append({

                        'numero_aposta': idx,

                        'arquivo': screenshot,

                        'erro_ocr': True,

                        'mensagem': dados_ocr.get('mensagem', 'Erro no OCR')

                    })

                    continue



                # Validar se temos dados suficientes (7 a 15 números)

                if len(dados_ocr['numeros_apostados']) < 7 or len(dados_ocr['numeros_apostados']) > 15 or not dados_ocr['mes_apostado']:

                    apostas_processadas.append({

                        'numero_aposta': idx,

                        'arquivo': screenshot,

                        'erro_ocr': False,

                        'dados_incompletos': True,

                        'dados_extraidos': dados_ocr,

                        'mensagem': f'Dados incompletos - necessita entre 7 e 15 números (encontrados: {len(dados_ocr["numeros_apostados"])})'

                    })

                    continue



                # Calcular valor da aposta baseado na quantidade de dezenas

                qtd_dezenas = len(dados_ocr['numeros_apostados'])

                valor_aposta = ConferenciaApostasOCRService.calcular_valor_aposta(qtd_dezenas)



                # Comparar com resultado oficial (agora retorna prêmios ACUMULATIVOS)

                resultado = ConferenciaApostasOCRService.comparar_aposta_com_resultado(

                    dados_ocr['numeros_apostados'],

                    dados_ocr['mes_apostado'],

                    sorteio

                )



                # Calcular valores

                total_investido += valor_aposta

                total_ganho += resultado['valor_premio']



                apostas_processadas.append({

                    'numero_aposta': idx,

                    'arquivo': screenshot,

                    'erro_ocr': False,

                    'dados_incompletos': False,

                    'dados_extraidos': dados_ocr,

                    'resultado': resultado,

                    'valor_aposta': valor_aposta,

                    'valor_ganho': resultado['valor_premio']

                })



            # Calcular estatísticas

            apostas_validas = [a for a in apostas_processadas if not a.get('erro_ocr') and not a.get('dados_incompletos')]



            distribuicao_acertos = {}

            for aposta in apostas_validas:

                acertos = aposta['resultado']['acertos']

                distribuicao_acertos[acertos] = distribuicao_acertos.get(acertos, 0) + 1



            apostas_premiadas = sum(1 for a in apostas_validas if a['resultado']['premiado'])



            lucro = total_ganho - total_investido

            roi = (lucro / total_investido * 100) if total_investido > 0 else 0



            # Calcular distribuição por faixa (ATUALIZADO para múltiplas faixas)

            distribuicao_faixas = {}

            for aposta in apostas_validas:

                # Iterar sobre todas as faixas atingidas (pode ser mais de uma!)

                detalhes_premios = aposta['resultado'].get('detalhes_premios', [])



                for detalhe in detalhes_premios:

                    faixa = detalhe['faixa']

                    valor = detalhe['valor']

                    if faixa not in distribuicao_faixas:

                        distribuicao_faixas[faixa] = {'quantidade': 0, 'total_ganho': 0.0}

                    distribuicao_faixas[faixa]['quantidade'] += 1

                    distribuicao_faixas[faixa]['total_ganho'] += valor



            # Análise de cobertura estratégica (reutiliza lógica do pós-apostas)

            from services.conferencia_apostas_service import ConferenciaApostasService

            jogos_para_cobertura = [

                {'numeros': a['dados_extraidos']['numeros_apostados']} for a in apostas_validas

            ]

            cobertura_estrategica = ConferenciaApostasService.analise_cobertura_estrategica(jogos_para_cobertura, numero_concurso)

            

            # ==========================================================

            # NOVO: Calcular e Salvar Métricas Estratégicas no Banco

            # ==========================================================

            try:

                print(f"   >>> Preparando para salvar métricas. Concurso: {numero_concurso}")

                ConferenciaApostasOCRService.salvar_metricas_estrategicas(

                    numero_concurso,

                    sorteio,

                    apostas_validas,

                    total_investido,

                    total_ganho,

                    lucro

                )

            except Exception as e:

                print(f"Erro ao salvar métricas estratégicas: {str(e)}")

                import traceback

                traceback.print_exc()



            retorno = {

                'sucesso': True,

                'concurso': numero_concurso,

                'resultado_sorteio': {

                    'concurso': sorteio.concurso,

                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else None,

                    'numeros': [

                        sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,

                        sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,

                        sorteio.posicao_7

                    ],

                    'numeros_ordem_sorteio': sorteio.get_ordem_sorteio_lista(),

                    'mes_sorte': sorteio.mes_sorte

                },

                'apostas': apostas_processadas,

                'resumo': {

                    'total_apostas': len(screenshots),

                    'apostas_processadas': len(apostas_validas),

                    'apostas_com_erro': len([a for a in apostas_processadas if a.get('erro_ocr')]),

                    'apostas_incompletas': len([a for a in apostas_processadas if a.get('dados_incompletos')]),

                    'total_investido': total_investido,

                    'total_ganho': total_ganho,

                    'lucro': lucro,

                    'roi': roi,

                    'apostas_premiadas': apostas_premiadas,

                    'distribuicao_acertos': distribuicao_acertos,

                    'distribuicao_faixas': distribuicao_faixas

                },

                'cobertura_estrategica': cobertura_estrategica

            }

            if task_id:

                ConferenciaApostasOCRService.atualizar_progresso(task_id, 'concluido', 100, total=total_items, processados=total_items, resultado=retorno)

            return retorno



        except Exception as e:

            return {

                'sucesso': False,

                'erro': 'excecao',

                'mensagem': f'Erro ao processar concurso: {str(e)}'

            }



    @staticmethod

    def processar_multiplos_concursos(concursos: List[int]) -> Dict:

        """

        Processa múltiplos concursos e gera relatório consolidado



        Args:

            concursos: Lista com números dos concursos a processar



        Returns:

            Dicionário com relatório consolidado

        """

        resultados = []

        total_investido_geral = 0.0

        total_ganho_geral = 0.0

        total_apostas_geral = 0

        total_premiadas_geral = 0

        distribuicao_acertos_geral = {}



        for concurso in concursos:

            resultado = ConferenciaApostasOCRService.processar_concurso(concurso)



            if resultado['sucesso']:

                resultados.append(resultado)

                total_investido_geral += resultado['resumo']['total_investido']

                total_ganho_geral += resultado['resumo']['total_ganho']

                total_apostas_geral += resultado['resumo']['apostas_processadas']

                total_premiadas_geral += resultado['resumo']['apostas_premiadas']



                # Consolidar distribuição de acertos

                for acertos, qtd in resultado['resumo']['distribuicao_acertos'].items():

                    distribuicao_acertos_geral[acertos] = distribuicao_acertos_geral.get(acertos, 0) + qtd



        lucro_geral = total_ganho_geral - total_investido_geral

        roi_geral = (lucro_geral / total_investido_geral * 100) if total_investido_geral > 0 else 0



        # Encontrar melhor e pior concurso

        melhor_concurso = max(resultados, key=lambda x: x['resumo']['roi']) if resultados else None

        pior_concurso = min(resultados, key=lambda x: x['resumo']['roi']) if resultados else None



        return {

            'sucesso': True,

            'concursos_processados': len(resultados),

            'concursos_com_erro': len(concursos) - len(resultados),

            'resultados': resultados,

            'total_investido': total_investido_geral,

            'total_ganho': total_ganho_geral,

            'lucro': lucro_geral,

            'roi': roi_geral,

            'total_apostas': total_apostas_geral,

            'total_premiadas': total_premiadas_geral,

            'taxa_premiacao': (total_premiadas_geral / total_apostas_geral * 100) if total_apostas_geral > 0 else 0,

            'distribuicao_acertos': distribuicao_acertos_geral,

            'melhor_concurso': melhor_concurso['concurso'] if melhor_concurso else None,

            'pior_concurso': pior_concurso['concurso'] if pior_concurso else None

        }



    @staticmethod

    def salvar_metricas_estrategicas(concurso_num, sorteio, apostas_validas, investido, ganho, lucro):

        print(f"   >>> Executando salvar_metricas_estrategicas para concurso {concurso_num}")

        print(f"   >>> Apostas válidas: {len(apostas_validas)}")

        try:

            from models import db

            from models.metricas_conferencia_ocr import MetricasConferenciaOCR

            import json



            # 1. Preparar dados

            dezenas_sorteio = {

                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,

                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,

                sorteio.posicao_7

            }

            

            dezenas_jogadas_unicas = set()

            total_dezenas_marcadas = 0

            

            for aposta in apostas_validas:

                # Extrair números (depende se é JSON ou OCR)

                numeros = []

                if aposta.get('fonte') == 'JSON':

                    numeros = aposta.get('numeros_apostados', [])

                else:

                    numeros = aposta.get('dados_extraidos', {}).get('numeros_apostados', [])

                

                if numeros:

                    total_dezenas_marcadas += len(numeros)

                    for n in numeros:

                        dezenas_jogadas_unicas.add(int(n))



            # 2. Calcular Métricas

            qtd_unicas = len(dezenas_jogadas_unicas)

            indice_redundancia = (total_dezenas_marcadas / qtd_unicas) if qtd_unicas > 0 else 0

            custo_por_dezena = (investido / qtd_unicas) if qtd_unicas > 0 else 0

            

            dezenas_cobertas = [n for n in dezenas_sorteio if n in dezenas_jogadas_unicas]

            dezenas_nao_cobertas = [n for n in dezenas_sorteio if n not in dezenas_jogadas_unicas]

            

            qtd_cobertas = len(dezenas_cobertas)

            percentual_cobertura = (qtd_cobertas / 7) * 100



            # 3. Verificar se já existe registro para atualizar

            registro = MetricasConferenciaOCR.query.filter_by(concurso=concurso_num).first()

            if not registro:

                registro = MetricasConferenciaOCR(concurso=concurso_num)

            

            # 4. Atualizar campos

            registro.total_apostas = len(apostas_validas)

            registro.total_investido = investido

            registro.total_ganho = ganho

            registro.lucro_prejuizo = lucro

            

            registro.dezenas_cobertas_qtd = qtd_cobertas

            registro.cobertura_percentual = percentual_cobertura

            

            registro.indice_redundancia = indice_redundancia

            registro.custo_por_dezena_unica = custo_por_dezena

            

            registro.dezenas_jogadas_json = json.dumps(list(dezenas_jogadas_unicas))

            registro.dezenas_nao_cobertas_json = json.dumps(list(dezenas_nao_cobertas))

            

            # 5. Salvar

            db.session.add(registro)

            db.session.commit()

            print(f"   >>> Métricas salvas com sucesso! ID: {registro.id}")

            

        except Exception as e:

            print(f"   >>> ERRO em salvar_metricas_estrategicas: {str(e)}")

            import traceback

            traceback.print_exc()


    @classmethod
    def processar_ranking_global_background(cls, task_id):
        """
        Processa o historico de concursos e calcula o ranking global de ABS.
        """
        try:
            cls.atualizar_progresso(task_id, 'em_andamento', 0)
            
            from models import db
            from models.sorteio import Sorteio
            import os
            import json
            
            base_dir = cls.BASE_DIR
            if not os.path.exists(base_dir):
                cls.atualizar_progresso(task_id, 'erro', 100, resultado={"erro": "Diretorio de concursos noo encontrado."})
                return
                
            concursos = cls.listar_concursos_disponiveis()
            total_concursos = len(concursos)
            
            if total_concursos == 0:
                cls.atualizar_progresso(task_id, 'concluido', 100, resultado={"ranking": [], "media_global": 0})
                return
            
            ranking = []
            soma_abs_global = 0
            total_apostas_global = 0
            
            for index, conc_info in enumerate(concursos):
                conc_num = conc_info['numero_concurso']
                # Atualizar progresso a cada concurso processado (ato 90%)
                progresso_percentual = int((index / total_concursos) * 90)
                cls.atualizar_progresso(task_id, 'em_andamento', progresso_percentual, total=total_concursos, processados=index)
                
                sorteio = Sorteio.query.filter_by(concurso=conc_num).first()
                if not sorteio:
                    continue
                    
                sorteados = [sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3, 
                             sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6, sorteio.posicao_7]
                
                json_path = os.path.join(base_dir, str(conc_num), 'apostas.json')
                if not os.path.exists(json_path):
                    continue
                    
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        apostas = json.load(f)
                except Exception:
                    continue
                
                soma_abs_concurso = 0
                apostas_validas_concurso = 0
                
                lista_apostas = apostas if isinstance(apostas, list) else apostas.get('apostas', [])
                
                for aposta in lista_apostas:
                    nums = aposta.get('numeros_apostados', aposta.get('numeros', aposta.get('dezenas', [])))
                    if len(nums) >= 7:
                        nums_sorted = sorted([int(n) for n in nums])[:7]
                        abs_aposta = sum(abs(nums_sorted[i] - sorteados[i]) for i in range(7))
                        soma_abs_concurso += abs_aposta
                        apostas_validas_concurso += 1
                        
                        soma_abs_global += abs_aposta
                        total_apostas_global += 1
                
                if apostas_validas_concurso > 0:
                    media_concurso = soma_abs_concurso / apostas_validas_concurso
                    
                    pares = sum(1 for n in sorteados if n % 2 == 0)
                    impares = 7 - pares
                    soma_sorteio = sum(sorteados)
                    
                    ranking.append({
                        'concurso': conc_num,
                        'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if hasattr(sorteio, 'data_sorteio') and sorteio.data_sorteio else None,
                        'total_apostas': apostas_validas_concurso,
                        'media_abs': round(media_concurso, 2),
                        'sorteados': sorteados,
                        'pares': pares,
                        'impares': impares,
                        'soma': soma_sorteio
                    })
            # Ordenar ranking pelo menor ABS (melhor performance)
            ranking_por_abs = sorted(ranking, key=lambda x: x['media_abs'])
            top_3 = ranking_por_abs[:3]
            
            # Ordenar cronologicamente para a evolução (mais recente primeiro)
            historico_completo = sorted(ranking, key=lambda x: x['concurso'], reverse=True)
            
            media_geral_historica = 0
            if total_apostas_global > 0:
                media_geral_historica = round(soma_abs_global / total_apostas_global, 2)
                
            resultado_final = {
                'ranking': top_3,
                'historico_completo': historico_completo,
                'media_global': media_geral_historica,
                'total_concursos_analisados': len(ranking)
            }
            
            cls.atualizar_progresso(task_id, 'concluido', 100, resultado=resultado_final)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            cls.atualizar_progresso(task_id, 'erro', 100, resultado={"erro": str(e)})

    @staticmethod
    def resumo_abs_historico_pasta(max_abs: int = 20, excluir_concurso: Optional[int] = None) -> Dict:
        """Resumo ABS de todas as apostas JSON na pasta (filtro ABS <= max_abs)."""
        import json
        from models.sorteio import Sorteio

        concursos = ConferenciaApostasOCRService.listar_concursos_disponiveis()
        concursos.sort(key=lambda x: x['numero_concurso'], reverse=True)

        apostas_filtradas = []
        total_validas = 0
        total_concursos_analisados = 0

        for conc_info in concursos:
            conc_num = conc_info['numero_concurso']
            if excluir_concurso is not None and conc_num == excluir_concurso:
                continue

            sorteio = Sorteio.query.filter_by(concurso=conc_num).first()
            if not sorteio:
                continue

            json_path = os.path.join(ConferenciaApostasOCRService.BASE_DIR, str(conc_num), 'apostas.json')
            if not os.path.exists(json_path):
                continue

            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
            except Exception:
                continue

            lista_apostas = dados.get('apostas', []) if isinstance(dados, dict) else dados
            if not lista_apostas:
                continue

            total_concursos_analisados += 1
            sorteados = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]
            sorteados_ordenados = sorted(sorteados)
            ctx_sorteio = {
                'concurso': conc_num,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else None,
                'numeros': sorteados,
                'mes_sorte': sorteio.mes_sorte
            }

            for idx, aposta in enumerate(lista_apostas, 1):
                nums = (
                    aposta.get('numeros_apostados')
                    or aposta.get('numeros')
                    or aposta.get('dezenas')
                    or []
                )
                if len(nums) < 7:
                    continue

                nums_int = [int(n) for n in nums]
                nums_posicional = sorted(nums_int)[:7]
                abs_aposta = sum(
                    abs(nums_posicional[i] - sorteados_ordenados[i]) for i in range(7)
                )
                total_validas += 1
                if abs_aposta > max_abs:
                    continue

                mes = aposta.get('mes_apostado') or aposta.get('mes')
                numero_aposta = aposta.get('numero_aposta') or aposta.get('indice') or idx
                comparacao = ConferenciaApostasOCRService.comparar_aposta_com_resultado(
                    nums_int[:7], mes, sorteio
                )

                apostas_filtradas.append({
                    'numero_aposta': numero_aposta,
                    'fonte': 'JSON',
                    'numeros_apostados': nums_int,
                    'mes_apostado': mes,
                    'resultado': comparacao,
                    '_ctx_sorteio': ctx_sorteio,
                    '_abs': abs_aposta,
                    '_concurso': conc_num,
                })

        apostas_filtradas.sort(
            key=lambda a: (a['_abs'], -a['_concurso'], a.get('numero_aposta') or 0)
        )

        return {
            'sucesso': True,
            'historico': True,
            'max_abs': max_abs,
            'total_concursos_pasta': len(concursos),
            'total_concursos_analisados': total_concursos_analisados,
            'total_apostas_validas': total_validas,
            'total_apostas_filtradas': len(apostas_filtradas),
            'resultado_sorteio': None,
            'apostas': apostas_filtradas,
        }



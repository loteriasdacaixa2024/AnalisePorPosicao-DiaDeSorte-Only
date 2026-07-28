from models import Sorteio
from datetime import datetime
import re


class ConferidorApostasService:

    MESES_MAP = {
        '1': 'Janeiro', '01': 'Janeiro', 'jan': 'Janeiro', 'janeiro': 'Janeiro',
        '2': 'Fevereiro', '02': 'Fevereiro', 'fev': 'Fevereiro', 'fevereiro': 'Fevereiro',
        '3': 'Março', '03': 'Março', 'mar': 'Março', 'março': 'Março', 'marco': 'Março',
        '4': 'Abril', '04': 'Abril', 'abr': 'Abril', 'abril': 'Abril',
        '5': 'Maio', '05': 'Maio', 'mai': 'Maio', 'maio': 'Maio',
        '6': 'Junho', '06': 'Junho', 'jun': 'Junho', 'junho': 'Junho',
        '7': 'Julho', '07': 'Julho', 'jul': 'Julho', 'julho': 'Julho',
        '8': 'Agosto', '08': 'Agosto', 'ago': 'Agosto', 'agosto': 'Agosto',
        '9': 'Setembro', '09': 'Setembro', 'set': 'Setembro', 'setembro': 'Setembro',
        '10': 'Outubro', 'out': 'Outubro', 'outubro': 'Outubro',
        '11': 'Novembro', 'nov': 'Novembro', 'novembro': 'Novembro',
        '12': 'Dezembro', 'dez': 'Dezembro', 'dezembro': 'Dezembro'
    }

    @staticmethod
    def obter_ultimo_sorteio():
        """Obtém o último sorteio do banco de dados"""
        try:
            ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
            if not ultimo:
                return None

            return {
                'concurso': ultimo.concurso,
                'data': ultimo.data_sorteio.strftime('%d/%m/%Y') if ultimo.data_sorteio else '',
                'numeros': [
                    ultimo.posicao_1,
                    ultimo.posicao_2,
                    ultimo.posicao_3,
                    ultimo.posicao_4,
                    ultimo.posicao_5,
                    ultimo.posicao_6,
                    ultimo.posicao_7
                ],
                'mes': ultimo.get_nome_mes(),
                'premiacao': {
                    '7_acertos': {
                        'ganhadores': ultimo.ganhadores_7_acertos or 0,
                        'valor': ultimo.valor_premio_7_acertos or 0.0
                    },
                    '6_acertos': {
                        'ganhadores': ultimo.ganhadores_6_acertos or 0,
                        'valor': ultimo.valor_premio_6_acertos or 0.0
                    },
                    '5_acertos': {
                        'ganhadores': ultimo.ganhadores_5_acertos or 0,
                        'valor': ultimo.valor_premio_5_acertos or 25.0
                    },
                    '4_acertos': {
                        'ganhadores': ultimo.ganhadores_4_acertos or 0,
                        'valor': ultimo.valor_premio_4_acertos or 5.0
                    },
                    'mes_sorte': {
                        'ganhadores': ultimo.ganhadores_mes_sorte or 0,
                        'valor': ultimo.valor_premio_mes_sorte or 2.5
                    }
                }
            }
        except Exception as e:
            print(f"Erro ao obter último sorteio: {e}")
            return None

    @staticmethod
    def obter_sorteio_por_concurso(numero_concurso):
        """Obtém um sorteio específico pelo número do concurso"""
        try:
            sorteio = Sorteio.query.filter_by(concurso=numero_concurso).first()
            if not sorteio:
                return None

            return {
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': [
                    sorteio.posicao_1,
                    sorteio.posicao_2,
                    sorteio.posicao_3,
                    sorteio.posicao_4,
                    sorteio.posicao_5,
                    sorteio.posicao_6,
                    sorteio.posicao_7
                ],
                'mes': sorteio.get_nome_mes(),
                'premiacao': {
                    '7_acertos': {
                        'ganhadores': sorteio.ganhadores_7_acertos or 0,
                        'valor': sorteio.valor_premio_7_acertos or 0.0
                    },
                    '6_acertos': {
                        'ganhadores': sorteio.ganhadores_6_acertos or 0,
                        'valor': sorteio.valor_premio_6_acertos or 0.0
                    },
                    '5_acertos': {
                        'ganhadores': sorteio.ganhadores_5_acertos or 0,
                        'valor': sorteio.valor_premio_5_acertos or 25.0
                    },
                    '4_acertos': {
                        'ganhadores': sorteio.ganhadores_4_acertos or 0,
                        'valor': sorteio.valor_premio_4_acertos or 5.0
                    },
                    'mes_sorte': {
                        'ganhadores': sorteio.ganhadores_mes_sorte or 0,
                        'valor': sorteio.valor_premio_mes_sorte or 2.5
                    }
                }
            }
        except Exception as e:
            print(f"Erro ao obter sorteio {numero_concurso}: {e}")
            return None

    @staticmethod
    def listar_todos_concursos():
        """Lista todos os números de concursos disponíveis"""
        try:
            concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
            return [{'concurso': c.concurso, 'data': c.data_sorteio.strftime('%d/%m/%Y') if c.data_sorteio else ''} for c in concursos]
        except Exception as e:
            print(f"Erro ao listar concursos: {e}")
            return []

    @staticmethod
    def normalizar_mes(mes_entrada):
        """Normaliza diferentes formatos de mês para o nome completo"""
        mes_str = str(mes_entrada).lower().strip()
        return ConferidorApostasService.MESES_MAP.get(mes_str, mes_entrada)

    @staticmethod
    def normalizar_numero(numero):
        """Normaliza número para formato com 2 dígitos"""
        try:
            num = int(numero)
            if 1 <= num <= 31:
                return f"{num:02d}"
            return None
        except:
            return None

    @staticmethod
    def validar_aposta(linha):
        """
        Valida e normaliza uma linha de aposta
        Formato esperado: "01 02 03 04 05 06 07 Janeiro" ou "1 2 3 4 5 6 7 1"
        Retorna: dict com 'valida', 'numeros', 'mes', 'quantidade_dezenas', 'erro'
        """
        linha = linha.strip()
        if not linha:
            return {'valida': False, 'erro': 'Linha vazia'}

        # Remove múltiplos espaços e quebras de linha
        linha = re.sub(r'\s+', ' ', linha)

        # Separa por espaços
        partes = linha.split()

        if len(partes) < 8:
            return {'valida': False, 'erro': f'Formato inválido. Esperado pelo menos 8 valores (7 números + mês), encontrado {len(partes)}'}

        # Últimas parte é o mês
        mes_entrada = partes[-1]
        mes_normalizado = ConferidorApostasService.normalizar_mes(mes_entrada)

        # Demais partes são números
        numeros_entrada = partes[:-1]
        numeros_normalizados = []

        for num in numeros_entrada:
            num_normalizado = ConferidorApostasService.normalizar_numero(num)
            if num_normalizado is None:
                return {'valida': False, 'erro': f'Número inválido: {num}. Números devem estar entre 1 e 31'}
            numeros_normalizados.append(num_normalizado)

        # Verifica se há números duplicados
        if len(numeros_normalizados) != len(set(numeros_normalizados)):
            return {'valida': False, 'erro': 'Números duplicados na aposta'}

        quantidade_dezenas = len(numeros_normalizados)

        # Valida quantidade de dezenas (mínimo 7, máximo permitido normalmente é 15)
        if quantidade_dezenas < 7:
            return {'valida': False, 'erro': f'Quantidade de números inválida: {quantidade_dezenas}. Mínimo: 7'}

        if quantidade_dezenas > 15:
            return {'valida': False, 'erro': f'Quantidade de números inválida: {quantidade_dezenas}. Máximo: 15'}

        return {
            'valida': True,
            'numeros': numeros_normalizados,
            'mes': mes_normalizado,
            'quantidade_dezenas': quantidade_dezenas,
            'erro': None
        }

    @staticmethod
    def processar_apostas(texto):
        """
        Processa múltiplas apostas de um texto
        Retorna lista de apostas validadas
        """
        linhas = texto.strip().split('\n')
        apostas = []
        erros = []

        for i, linha in enumerate(linhas, 1):
            if not linha.strip():
                continue

            resultado = ConferidorApostasService.validar_aposta(linha)

            if resultado['valida']:
                apostas.append({
                    'linha': i,
                    'numeros': resultado['numeros'],
                    'mes': resultado['mes'],
                    'quantidade_dezenas': resultado['quantidade_dezenas']
                })
            else:
                erros.append({
                    'linha': i,
                    'texto': linha,
                    'erro': resultado['erro']
                })

        return {
            'apostas_validas': apostas,
            'erros': erros,
            'total_linhas': len(linhas),
            'total_validas': len(apostas),
            'total_erros': len(erros)
        }

    @staticmethod
    def conferir_aposta(numeros_aposta, mes_aposta, sorteio):
        """
        Confere uma aposta contra um sorteio
        Retorna: dict com acertos, números acertados e comparação do mês
        """
        numeros_sorteio = [f"{n:02d}" for n in sorteio['numeros']]

        # Converte números da aposta para string com 2 dígitos
        numeros_aposta_str = [str(n) if len(str(n)) == 2 else f"0{n}" for n in numeros_aposta]

        # Encontra acertos
        acertos_numeros = [n for n in numeros_aposta_str if n in numeros_sorteio]
        quantidade_acertos = len(acertos_numeros)

        # Verifica mês
        mes_acertou = mes_aposta.lower() == sorteio['mes'].lower()

        # Mapeia posições dos acertos
        acertos_com_posicao = []
        for num in acertos_numeros:
            pos_aposta = numeros_aposta_str.index(num)
            pos_sorteio = numeros_sorteio.index(num)
            acertos_com_posicao.append({
                'numero': num,
                'posicao_aposta': pos_aposta,
                'posicao_sorteio': pos_sorteio
            })

        return {
            'quantidade_acertos': quantidade_acertos,
            'acertos_numeros': acertos_numeros,
            'acertos_com_posicao': acertos_com_posicao,
            'mes_acertou': mes_acertou,
            'numeros_aposta': numeros_aposta_str,
            'numeros_sorteio': numeros_sorteio,
            'mes_aposta': mes_aposta,
            'mes_sorteio': sorteio['mes']
        }

    @staticmethod
    def calcular_premio(quantidade_acertos, mes_acertou, sorteio):
        """
        Calcula quanto a pessoa ganhou baseado nos acertos

        Args:
            quantidade_acertos: 4, 5, 6 ou 7
            mes_acertou: True/False
            sorteio: dict com dados do sorteio incluindo premiação

        Returns:
            dict com valor ganho
        """
        valor_total = 0.0
        detalhes = []

        premiacao = sorteio.get('premiacao', {})

        if quantidade_acertos == 7 and premiacao.get('7_acertos', {}).get('valor', 0) > 0:
            valor = premiacao['7_acertos']['valor']
            valor_total += valor
            detalhes.append({'faixa': '7 acertos', 'valor': valor})

        if quantidade_acertos == 6 and premiacao.get('6_acertos', {}).get('valor', 0) > 0:
            valor = premiacao['6_acertos']['valor']
            valor_total += valor
            detalhes.append({'faixa': '6 acertos', 'valor': valor})

        if quantidade_acertos == 5:
            valor = premiacao.get('5_acertos', {}).get('valor', 25.0)
            valor_total += valor
            detalhes.append({'faixa': '5 acertos', 'valor': valor})

        if quantidade_acertos == 4:
            valor = premiacao.get('4_acertos', {}).get('valor', 5.0)
            valor_total += valor
            detalhes.append({'faixa': '4 acertos', 'valor': valor})

        if mes_acertou:
            valor = premiacao.get('mes_sorte', {}).get('valor', 2.5)
            valor_total += valor
            detalhes.append({'faixa': 'Mês da Sorte', 'valor': valor})

        return {
            'ganhou': valor_total > 0,
            'valor_total': valor_total,
            'detalhes': detalhes
        }

    @staticmethod
    def conferir_multiplas_apostas(apostas, sorteio):
        """
        Confere múltiplas apostas contra um sorteio
        Retorna lista de resultados
        """
        resultados = []
        valor_total_ganho = 0.0

        for aposta in apostas:
            conferencia = ConferidorApostasService.conferir_aposta(
                aposta['numeros'],
                aposta['mes'],
                sorteio
            )

            premio = ConferidorApostasService.calcular_premio(
                conferencia['quantidade_acertos'],
                conferencia['mes_acertou'],
                sorteio
            )

            conferencia['premio'] = premio
            valor_total_ganho += premio['valor_total']

            resultados.append({
                'linha': aposta['linha'],
                'quantidade_dezenas': aposta['quantidade_dezenas'],
                'conferencia': conferencia
            })

        # Estatísticas gerais
        total_7_acertos = sum(1 for r in resultados if r['conferencia']['quantidade_acertos'] == 7)
        total_6_acertos = sum(1 for r in resultados if r['conferencia']['quantidade_acertos'] == 6)
        total_5_acertos = sum(1 for r in resultados if r['conferencia']['quantidade_acertos'] == 5)
        total_4_acertos = sum(1 for r in resultados if r['conferencia']['quantidade_acertos'] == 4)

        return {
            'resultados': resultados,
            'total_apostas': len(apostas),
            'total_7_acertos': total_7_acertos,
            'total_6_acertos': total_6_acertos,
            'total_5_acertos': total_5_acertos,
            'total_4_acertos': total_4_acertos,
            'valor_total_ganho': valor_total_ganho,
            'concurso': sorteio['concurso'],
            'data_sorteio': sorteio['data'],
            'tem_premiacao': 'premiacao' in sorteio
        }

"""
Service de Análise de Posição Mínima e Máxima
Sistema Dia de Sorte - Gerador Inteligente de Palpites
"""

from models.sorteio import Sorteio, db
from collections import defaultdict
import statistics
import random
from datetime import datetime


class PosicaoMinimaMaximaService:
    """
    Análise de faixas Min-Max por posição e geração inteligente de palpites
    """

    @staticmethod
    def analisar_posicoes():
        """
        Analisa todos os sorteios e retorna Min, Max, Média e Frequência por posição
        IMPORTANTE: Ordena as dezenas de cada sorteio do menor para o maior
        """
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)

        # Estrutura para armazenar dados por posição
        dados_posicoes = {}
        for pos in range(1, 8):
            dados_posicoes[pos] = {
                'numeros': [],
                'frequencia': defaultdict(int),
                'historico': defaultdict(list)
            }

        # Coletar todos os números por posição ORDENANDO cada sorteio
        for sorteio in sorteios:
            # Pega todas as dezenas do sorteio
            dezenas_sorteio = []
            for pos in range(1, 8):
                numero = getattr(sorteio, f'posicao_{pos}')
                if numero:
                    dezenas_sorteio.append(numero)

            # ORDENA as dezenas do menor para o maior
            dezenas_sorteio.sort()

            # Agora atribui cada dezena ordenada à sua posição
            for idx, numero in enumerate(dezenas_sorteio, start=1):
                dados_posicoes[idx]['numeros'].append(numero)
                dados_posicoes[idx]['frequencia'][numero] += 1
                
                # Armazena o histórico completo onde este dígito assumiu essa posição
                dados_posicoes[idx]['historico'][numero].append({
                    'concurso': sorteio.concurso,
                    'combinacao': dezenas_sorteio.copy(),
                    'mes_sorte': sorteio.get_nome_mes() if hasattr(sorteio, 'get_nome_mes') else sorteio.mes_sorte,
                    'mes_sorte_id': sorteio.mes_sorte
                })

        # Calcular estatísticas por posição
        analise = []
        for pos in range(1, 8):
            numeros = dados_posicoes[pos]['numeros']
            frequencia = dados_posicoes[pos]['frequencia']

            if not numeros:
                continue

            minimo = min(numeros)
            maximo = max(numeros)
            media = round(statistics.mean(numeros), 1)

            # Encontrar número mais frequente
            mais_frequente = max(frequencia.items(), key=lambda x: x[1])
            numero_freq = mais_frequente[0]
            qtd_freq = mais_frequente[1]

            # Histórico dos extremos
            historico_minimo = dados_posicoes[pos]['historico'][minimo]
            historico_maximo = dados_posicoes[pos]['historico'][maximo]

            analise.append({
                'posicao': pos,
                'minimo': minimo,
                'maximo': maximo,
                'media': media,
                'intervalo': f"{minimo}–{maximo}",
                'mais_frequente': numero_freq,
                'frequencia_max': qtd_freq,
                'total_numeros': len(set(numeros)),
                'frequencia_detalhada': dict(sorted(frequencia.items())),
                'detalhes_minimo': historico_minimo,
                'detalhes_maximo': historico_maximo
            })

        return {
            'total_concursos': total_concursos,
            'analise_posicoes': analise
        }

    @staticmethod
    def obter_ultimo_sorteio():
        """Retorna o último sorteio do banco"""
        ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

        if not ultimo:
            return None

        numeros = []
        for pos in range(1, 8):
            numero = getattr(ultimo, f'posicao_{pos}')
            if numero:
                numeros.append(numero)

        return {
            'concurso': ultimo.concurso,
            'data': ultimo.data_sorteio.strftime('%d/%m/%Y') if ultimo.data_sorteio else '',
            'numeros': sorted(numeros),
            'mes_sorte': ultimo.get_nome_mes() if hasattr(ultimo, 'get_nome_mes') else ultimo.mes_sorte
        }

    @staticmethod
    def validar_compatibilidade_regras(regras_selecionadas, analise_posicoes):
        """
        Valida se as regras selecionadas são compatíveis entre si
        Retorna (bool_valido, mensagem_erro)
        """
        # Esta função pode ser expandida conforme necessário
        # Por enquanto, retorna sempre válido
        return True, ""

    @staticmethod
    def gerar_palpites_inteligentes(quantidade_jogos, quantidade_dezenas, regras=None):
        """
        Gera palpites inteligentes respeitando faixas Min-Max e regras opcionais

        Args:
            quantidade_jogos: número de jogos a gerar
            quantidade_dezenas: 7 a 15 dezenas por jogo
            regras: dict com regras opcionais selecionadas
        """
        if regras is None:
            regras = {}

        # Obter análise de posições
        analise_data = PosicaoMinimaMaximaService.analisar_posicoes()
        if 'error' in analise_data:
            return {'error': analise_data['error']}

        analise_posicoes = analise_data['analise_posicoes']

        # Validar compatibilidade de regras
        valido, mensagem = PosicaoMinimaMaximaService.validar_compatibilidade_regras(regras, analise_posicoes)
        if not valido:
            return {'error': mensagem, 'tipo': 'conflito_regras'}

        palpites_gerados = []

        for _ in range(quantidade_jogos):
            tentativas = 0
            max_tentativas = 1000

            while tentativas < max_tentativas:
                tentativas += 1

                # Gerar dezenas respeitando Min-Max por posição
                dezenas = []

                for pos_data in analise_posicoes:
                    pos = pos_data['posicao']
                    minimo = pos_data['minimo']
                    maximo = pos_data['maximo']

                    # Gerar número aleatório dentro da faixa
                    numero = random.randint(minimo, maximo)

                    # Evitar repetição
                    while numero in dezenas:
                        numero = random.randint(minimo, maximo)

                    dezenas.append(numero)

                # Se quantidade_dezenas > 7, adicionar mais números respeitando 01-31
                while len(dezenas) < quantidade_dezenas:
                    numero = random.randint(1, 31)
                    if numero not in dezenas:
                        dezenas.append(numero)

                # Ordenar dezenas
                dezenas = sorted(dezenas)

                # Aplicar regras opcionais
                if not PosicaoMinimaMaximaService._validar_regras(dezenas, regras):
                    continue

                # Gerar mês da sorte aleatório
                mes_sorte = random.randint(1, 12)
                meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                              'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                mes_nome = meses_nomes[mes_sorte - 1]

                palpites_gerados.append({
                    'numeros': dezenas,
                    'numeros_formatados': ' '.join([f'{n:02d}' for n in dezenas]),
                    'mes_sorte': mes_sorte,
                    'mes_nome': mes_nome
                })

                break

            if tentativas >= max_tentativas:
                return {
                    'error': 'Não foi possível gerar palpites compatíveis com as regras selecionadas',
                    'tipo': 'impossivel'
                }

        return {
            'palpites': palpites_gerados,
            'quantidade': len(palpites_gerados),
            'quantidade_dezenas': quantidade_dezenas,
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }

    @staticmethod
    def _validar_regras(dezenas, regras):
        """
        Valida se um jogo (dezenas) atende às regras selecionadas
        """
        # Regra: Grupos de finais iguais
        # Formato: "1:2" significa 1 grupo de 2 dezenas com finais iguais
        #          "2:2" significa 2 grupos de 2 dezenas com finais iguais
        #          "3:2" significa 3 grupos de 2 dezenas com finais iguais
        if 'grupos_finais' in regras and regras['grupos_finais']:
            partes = regras['grupos_finais'].split(':')
            if len(partes) == 2:
                qtd_grupos = int(partes[0])
                tamanho_grupo = int(partes[1])

                # Conta os finais
                from collections import Counter
                finais = [n % 10 for n in dezenas]
                contagem_finais = Counter(finais)

                # Conta quantos grupos do tamanho desejado existem
                grupos_encontrados = sum(1 for count in contagem_finais.values() if count >= tamanho_grupo)

                if grupos_encontrados < qtd_grupos:
                    return False

        # Regra: Repetir dezenas do último sorteio
        if 'repetir_dezenas' in regras and regras['repetir_dezenas']:
            dezenas_repetir = regras['repetir_dezenas']  # Lista de dezenas
            # Verifica se todas as dezenas selecionadas estão no jogo
            for dez in dezenas_repetir:
                if dez not in dezenas:
                    return False

        # Regra: Sequências
        if 'sequencias' in regras and regras['sequencias']:
            tipo_seq = regras['sequencias']
            tem_sequencia = PosicaoMinimaMaximaService._tem_sequencia(dezenas, tipo_seq)
            if not tem_sequencia:
                return False

        # Regra: Padrão dígito inicial
        if 'padrao_digito_inicial' in regras and regras['padrao_digito_inicial']:
            padrao_desejado = regras['padrao_digito_inicial']
            if not PosicaoMinimaMaximaService._valida_padrao_inicial(dezenas, padrao_desejado):
                return False

        # Regra: Soma das dezenas
        if 'soma_faixa' in regras and regras['soma_faixa']:
            faixa = regras['soma_faixa']  # Ex: '110-120'
            soma_atual = sum(dezenas)
            min_soma, max_soma = map(int, faixa.split('-'))
            if not (min_soma <= soma_atual <= max_soma):
                return False

        # Regra: Dígitos únicos
        if 'digitos_unicos' in regras and regras['digitos_unicos']:
            qtd_desejada = int(regras['digitos_unicos'])
            digitos = set()
            for n in dezenas:
                digitos.update(str(n))
            if len(digitos) != qtd_desejada:
                return False

        return True

    @staticmethod
    def _tem_sequencia(dezenas, tipo):
        """
        Verifica se há sequência no jogo
        tipo: '2', '3', 'nenhuma'
        """
        if tipo == 'nenhuma':
            # Verifica se NÃO há sequências
            for i in range(len(dezenas) - 1):
                if dezenas[i + 1] == dezenas[i] + 1:
                    return False
            return True
        else:
            # Verifica se HÁ sequência de tamanho especificado
            tamanho = int(tipo)
            seq_atual = 1
            for i in range(len(dezenas) - 1):
                if dezenas[i + 1] == dezenas[i] + 1:
                    seq_atual += 1
                    if seq_atual >= tamanho:
                        return True
                else:
                    seq_atual = 1
            return False

    @staticmethod
    def _valida_padrao_inicial(dezenas, padrao_desejado):
        """
        Valida se o padrão de dígitos INICIAIS corresponde ao desejado
        padrao_desejado: string como "0:1 | 1:2 | 2:3 | 3:1"
        Dígito inicial: primeiro dígito do número (0 para 01-09, 1 para 10-19, 2 para 20-29, 3 para 30-31)
        """
        # Contar dígitos iniciais
        contagem_iniciais = defaultdict(int)
        for n in dezenas:
            digito_inicial = n // 10  # 01-09 → 0, 10-19 → 1, 20-29 → 2, 30-31 → 3
            contagem_iniciais[digito_inicial] += 1

        # Extrair padrão desejado
        partes = padrao_desejado.split(' | ')
        for parte in partes:
            digito_str, qtd_str = parte.split(':')
            digito = int(digito_str)
            qtd_esperada = int(qtd_str)

            if contagem_iniciais.get(digito, 0) != qtd_esperada:
                return False

        return True

    @staticmethod
    def exportar_txt(palpites):
        """
        Exporta palpites em formato TXT
        Formato: 01 07 14 18 21 23 30 Mai
        """
        linhas = []
        for palpite in palpites:
            nums = ' '.join([f'{n:02d}' for n in palpite['numeros']])
            linha = f"{nums} {palpite['mes_nome']}"
            linhas.append(linha)

        return '\n'.join(linhas)

    @staticmethod
    def exportar_html(analise_posicoes, palpites=None):
        """
        Exporta análise (e palpites, se fornecidos) em formato HTML
        """
        html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Análise Posição Mínima × Máxima - Dia de Sorte</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #D4B31A; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: center; }
        th { background-color: #D4B31A; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .palpite { margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #D4B31A; }
    </style>
</head>
<body>
    <h1>📊 Análise Posição Mínima × Máxima</h1>
    <p><strong>Sistema Dia de Sorte</strong></p>

    <h2>Análise por Posição</h2>
    <table>
        <tr>
            <th>Posição</th>
            <th>Mínimo</th>
            <th>Máximo</th>
            <th>Média</th>
            <th>Intervalo</th>
            <th>+ Frequente</th>
        </tr>
"""
        for pos in analise_posicoes:
            html += f"""
        <tr>
            <td>{pos['posicao']}</td>
            <td>{pos['minimo']}</td>
            <td>{pos['maximo']}</td>
            <td>{pos['media']}</td>
            <td>{pos['intervalo']}</td>
            <td>{pos['mais_frequente']} ({pos['frequencia_max']}x)</td>
        </tr>
"""

        html += """
    </table>
"""

        if palpites:
            html += """
    <h2>Palpites Gerados</h2>
"""
            for idx, palpite in enumerate(palpites, 1):
                nums = ' '.join([f'{n:02d}' for n in palpite['numeros']])
                html += f"""
    <div class="palpite">
        <strong>Jogo #{idx}:</strong> {nums} <strong>{palpite['mes_nome']}</strong>
    </div>
"""

        html += """
    <p style="margin-top: 30px; color: #666; font-size: 12px;">
        Gerado pelo Sistema Dia de Sorte - Análise Inteligente
    </p>
</body>
</html>
"""
        return html

    @staticmethod
    def exportar_xls(analise_posicoes, palpites=None):
        """
        Retorna dados formatados para Excel (será usado com biblioteca openpyxl ou similar)
        Por simplicidade, retorna CSV que pode ser aberto no Excel
        """
        import io

        output = io.StringIO()

        # Cabeçalho análise
        output.write("Análise Posição Mínima × Máxima - Dia de Sorte\n")
        output.write("\n")

        # Tabela análise
        output.write("Posição,Mínimo,Máximo,Média,Intervalo,+ Frequente,Freq Max\n")
        for pos in analise_posicoes:
            output.write(f"{pos['posicao']},{pos['minimo']},{pos['maximo']},{pos['media']},{pos['intervalo']},{pos['mais_frequente']},{pos['frequencia_max']}\n")

        if palpites:
            output.write("\n")
            output.write("Palpites Gerados\n")
            output.write("Jogo,Pos1,Pos2,Pos3,Pos4,Pos5,Pos6,Pos7")

            # Verificar se há mais de 7 posições
            max_pos = max(len(p['numeros']) for p in palpites)
            for i in range(8, max_pos + 1):
                output.write(f",Pos{i}")

            output.write(",Mês\n")

            for idx, palpite in enumerate(palpites, 1):
                nums = ','.join([f'{n:02d}' for n in palpite['numeros']])
                output.write(f"{idx},{nums},{palpite['mes_nome']}\n")

        conteudo = output.getvalue()
        output.close()

        return conteudo

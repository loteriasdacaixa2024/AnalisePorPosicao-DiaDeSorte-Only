"""
Service para conversão de apostas entre diversos formatos
Converte TXT → JSON e JSON → TXT
Aceita múltiplos formatos de entrada
Atualizado para aceitar apostas com 7 a 15 dezenas
"""

import re
import json
from typing import Dict, List, Optional, Union


class ConversorApostasService:
    """Service para converter apostas entre formatos TXT e JSON"""

    # Mapeamento completo de meses
    MESES_NUMERO = {
        '1': 'Jan', '01': 'Jan',
        '2': 'Fev', '02': 'Fev',
        '3': 'Mar', '03': 'Mar',
        '4': 'Abr', '04': 'Abr',
        '5': 'Mai', '05': 'Mai',
        '6': 'Jun', '06': 'Jun',
        '7': 'Jul', '07': 'Jul',
        '8': 'Ago', '08': 'Ago',
        '9': 'Set', '09': 'Set',
        '10': 'Out',
        '11': 'Nov',
        '12': 'Dez'
    }

    MESES_NOME_COMPLETO = {
        'janeiro': 'Jan', 'fevereiro': 'Fev', 'março': 'Mar', 'marco': 'Mar',
        'abril': 'Abr', 'maio': 'Mai', 'junho': 'Jun',
        'julho': 'Jul', 'agosto': 'Ago', 'setembro': 'Set',
        'outubro': 'Out', 'novembro': 'Nov', 'dezembro': 'Dez'
    }

    MESES_ABREVIADO = {
        'jan': 'Jan', 'fev': 'Fev', 'mar': 'Mar', 'abr': 'Abr',
        'mai': 'Mai', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Ago',
        'set': 'Set', 'out': 'Out', 'nov': 'Nov', 'dez': 'Dez'
    }

    MESES_PARA_NUMERO = {
        'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04',
        'Mai': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
        'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'
    }

    MESES_PARA_EXTENSO = {
        'Jan': 'Janeiro', 'Fev': 'Fevereiro', 'Mar': 'Março', 'Abr': 'Abril',
        'Mai': 'Maio', 'Jun': 'Junho', 'Jul': 'Julho', 'Ago': 'Agosto',
        'Set': 'Setembro', 'Out': 'Outubro', 'Nov': 'Novembro', 'Dez': 'Dezembro'
    }

    @staticmethod
    def normalizar_mes(mes_input: Union[str, int]) -> str:
        """
        Normaliza mês para formato padrão (Jan, Fev, Mar, etc.)

        Args:
            mes_input: Mês em qualquer formato (1, 01, Jan, Janeiro, etc.)

        Returns:
            Mês normalizado (Jan-Dez) ou mes_input se não reconhecido
        """
        if mes_input is None:
            return None

        # Converter para string e limpar
        mes_str = str(mes_input).strip()

        # Tentar numérico
        if mes_str in ConversorApostasService.MESES_NUMERO:
            return ConversorApostasService.MESES_NUMERO[mes_str]

        # Tentar nome completo (case-insensitive)
        mes_lower = mes_str.lower()
        if mes_lower in ConversorApostasService.MESES_NOME_COMPLETO:
            return ConversorApostasService.MESES_NOME_COMPLETO[mes_lower]

        # Tentar abreviado (case-insensitive)
        if mes_lower in ConversorApostasService.MESES_ABREVIADO:
            return ConversorApostasService.MESES_ABREVIADO[mes_lower]

        # Já está no formato correto
        if mes_str in ConversorApostasService.MESES_PARA_NUMERO:
            return mes_str

        # Não reconhecido, retornar original
        return mes_str

    @staticmethod
    def serializar_mes(mes_input: str, formato: str = 'abreviado') -> str:
        """
        Serializa mês para formato específico

        Args:
            mes_input: Mês em qualquer formato
            formato: 'numero' (01-12), 'abreviado' (Jan-Dez), 'extenso' (Janeiro-Dezembro)

        Returns:
            Mês no formato solicitado
        """
        # Normalizar primeiro
        mes_normalizado = ConversorApostasService.normalizar_mes(mes_input)

        if formato == 'numero':
            return ConversorApostasService.MESES_PARA_NUMERO.get(mes_normalizado, mes_input)
        elif formato == 'extenso':
            return ConversorApostasService.MESES_PARA_EXTENSO.get(mes_normalizado, mes_input)
        else:  # abreviado (padrão)
            return mes_normalizado

    @staticmethod
    def extrair_numeros_linha(linha: str) -> List[int]:
        """
        Extrai números de uma linha com qualquer separador

        Args:
            linha: Linha de texto contendo números

        Returns:
            Lista de números inteiros (1-31)
        """
        # Remover qualquer caractere que não seja dígito ou espaço/vírgula/pipe/ponto-e-vírgula
        # Manter apenas números e separadores comuns
        numeros = re.findall(r'\d+', linha)

        # Converter para int e filtrar apenas 1-31
        resultado = []
        for num_str in numeros:
            try:
                num = int(num_str)
                if 1 <= num <= 31:
                    resultado.append(num)
            except ValueError:
                continue

        return resultado

    @staticmethod
    def extrair_mes_linha(linha: str) -> Optional[str]:
        """
        Extrai mês de uma linha de texto

        Args:
            linha: Linha de texto que pode conter mês

        Returns:
            Mês normalizado ou None
        """
        # Procurar por padrões de mês
        palavras = linha.split()

        for palavra in palavras:
            palavra_limpa = re.sub(r'[^\w]', '', palavra)  # Remove pontuação

            # IGNORAR números de 1-31 (são dezenas, não meses!)
            if palavra_limpa.isdigit() and 1 <= int(palavra_limpa) <= 31:
                continue

            # Tentar normalizar
            mes_normalizado = ConversorApostasService.normalizar_mes(palavra_limpa)

            # Se normalizou para um mês válido, retornar
            if mes_normalizado in ConversorApostasService.MESES_PARA_NUMERO:
                return mes_normalizado

        return None

    @staticmethod
    def texto_para_json(texto: str, concurso: int) -> Dict:
        """
        Converte texto de apostas para JSON padrão

        Args:
            texto: Texto contendo apostas (múltiplos formatos aceitos)
            concurso: Número do concurso

        Returns:
            Dicionário no formato JSON padrão
        """
        linhas = texto.strip().split('\n')
        apostas = []
        numero_aposta = 1

        # Buffer para apostas multi-linha
        buffer_numeros = []
        buffer_mes = None

        for linha in linhas:
            linha = linha.strip()

            # Ignorar linhas vazias
            if not linha:
                continue

            # Extrair números da linha
            numeros_linha = ConversorApostasService.extrair_numeros_linha(linha)

            # Extrair mês da linha
            mes_linha = ConversorApostasService.extrair_mes_linha(linha)

            # Se encontrou números, adicionar ao buffer
            if numeros_linha:
                buffer_numeros.extend(numeros_linha)

            # Se encontrou mês, atualizar buffer (MANTER para próximas apostas)
            if mes_linha:
                buffer_mes = mes_linha

            # Se buffer tem entre 7 e 15 números, criar aposta
            if len(buffer_numeros) >= 7:
                # Determinar quantos números pegar (7 a 15)
                qtd_numeros = min(len(buffer_numeros), 15)

                apostas.append({
                    'numero': numero_aposta,
                    'numeros': buffer_numeros[:qtd_numeros],  # NÃO ORDENAR - manter ordem original
                    'mes': buffer_mes if buffer_mes else 'Jan'
                })
                numero_aposta += 1

                # Limpar buffer de números usados (MAS MANTER O MÊS!)
                buffer_numeros = buffer_numeros[qtd_numeros:]  # Manter excedente para próxima aposta
                # buffer_mes NÃO é resetado - mantém o último mês encontrado

        return {
            'concurso': concurso,
            'apostas': apostas
        }

    @staticmethod
    def json_para_texto(dados_json: Dict) -> str:
        """
        Converte JSON padrão para texto formato apostas.txt

        Args:
            dados_json: Dicionário no formato JSON padrão

        Returns:
            String no formato texto (uma aposta por linha)
        """
        linhas = []

        for aposta in dados_json.get('apostas', []):
            numeros = aposta.get('numeros', [])
            mes = aposta.get('mes', 'Jan')

            # Formatar: numero1 numero2 ... numeroN Mes (N entre 7 e 15)
            linha = ' '.join(map(str, numeros)) + f' {mes}'
            linhas.append(linha)

        return '\n'.join(linhas)

    @staticmethod
    def validar_apostas(dados_json: Dict) -> Dict:
        """
        Valida estrutura do JSON e cada aposta

        Args:
            dados_json: Dicionário para validar

        Returns:
            {'valido': bool, 'erros': List[str]}
        """
        erros = []

        # Validar estrutura
        if 'concurso' not in dados_json:
            erros.append('Campo "concurso" obrigatório')

        if 'apostas' not in dados_json:
            erros.append('Campo "apostas" obrigatório')
            return {'valido': False, 'erros': erros}

        # Validar cada aposta
        for idx, aposta in enumerate(dados_json['apostas'], 1):
            if 'numeros' not in aposta:
                erros.append(f'Aposta {idx}: campo "numeros" obrigatório')
                continue

            numeros = aposta['numeros']

            # Validar quantidade (7 a 15 dezenas permitidas para Dia de Sorte)
            if len(numeros) < 7 or len(numeros) > 15:
                erros.append(f'Aposta {idx}: deve ter entre 7 e 15 números (tem {len(numeros)})')

            # Validar intervalo
            for num in numeros:
                if not isinstance(num, int) or num < 1 or num > 31:
                    erros.append(f'Aposta {idx}: número {num} inválido (deve ser 1-31)')
                    break

            # Validar duplicatas
            if len(set(numeros)) != len(numeros):
                erros.append(f'Aposta {idx}: números duplicados')

            # Validar mês (opcional)
            if 'mes' in aposta:
                mes = aposta['mes']
                mes_normalizado = ConversorApostasService.normalizar_mes(mes)
                if mes_normalizado not in ConversorApostasService.MESES_PARA_NUMERO:
                    erros.append(f'Aposta {idx}: mês "{mes}" inválido')

        return {
            'valido': len(erros) == 0,
            'erros': erros,
            'total_apostas': len(dados_json.get('apostas', [])),
            'apostas_validas': len(dados_json.get('apostas', [])) - len([e for e in erros if 'Aposta' in e])
        }

    @staticmethod
    def processar_arquivo_upload(arquivo_conteudo: str, tipo_arquivo: str, concurso: int) -> Dict:
        """
        Processa arquivo enviado via upload

        Args:
            arquivo_conteudo: Conteúdo do arquivo
            tipo_arquivo: 'txt' ou 'json'
            concurso: Número do concurso

        Returns:
            Resultado do processamento
        """
        try:
            if tipo_arquivo == 'json':
                # Parse JSON
                dados = json.loads(arquivo_conteudo)

                # Validar
                validacao = ConversorApostasService.validar_apostas(dados)

                return {
                    'sucesso': True,
                    'dados': dados,
                    'validacao': validacao,
                    'tipo_origem': 'json'
                }

            elif tipo_arquivo == 'txt':
                # Converter TXT para JSON
                dados = ConversorApostasService.texto_para_json(arquivo_conteudo, concurso)

                # Validar
                validacao = ConversorApostasService.validar_apostas(dados)

                return {
                    'sucesso': True,
                    'dados': dados,
                    'validacao': validacao,
                    'tipo_origem': 'txt'
                }

            else:
                return {
                    'sucesso': False,
                    'erro': f'Tipo de arquivo não suportado: {tipo_arquivo}'
                }

        except json.JSONDecodeError as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao decodificar JSON: {str(e)}'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao processar arquivo: {str(e)}'
            }

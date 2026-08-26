# -*- coding: utf-8 -*-
"""
Service para gerenciar as cores dos meses
Sistema: Análise por Posição - Dia de Sorte
Desenvolvido para: Márcio Fernando Maia
"""

from models.cores_meses_model import CoresMeses


class CoresMesesService:
    """
    Service para gerenciar as cores dos 12 meses do sistema.
    """

    @staticmethod
    def obter_todas_cores():
        """
        Retorna todas as cores dos meses em formato de dicionário.
        """
        try:
            cores = CoresMeses.obter_todas_cores()

            return {
                'sucesso': True,
                'cores': [cor.to_dict() for cor in cores]
            }
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao obter cores: {str(e)}'
            }


    @staticmethod
    def obter_cores_css():
        """
        Retorna as cores formatadas para uso em CSS.
        Retorna um dicionário {0: '#cor1', 1: '#cor2', ...}
        """
        try:
            cores = CoresMeses.obter_todas_cores()

            cores_dict = {}
            for cor in cores:
                cores_dict[cor.mes] = cor.cor_hex

            return {
                'sucesso': True,
                'cores': cores_dict
            }
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao obter cores CSS: {str(e)}'
            }


    @staticmethod
    def gerar_css_dinamico():
        """
        Gera o CSS dinâmico com as cores dos meses.
        Retorna uma string CSS pronta para uso.
        """
        try:
            cores = CoresMeses.obter_todas_cores()

            css = "/* Cores dos meses - Gerado dinamicamente */\n"

            for cor in cores:
                # Ajuste para 1-based (1=Janeiro, 12=Dezembro) se o banco estiver 0-based
                # O Config usa 0-11, então assumimos que o banco é 0-11.
                # O USER espera mes-cor-5 para Maio (mês 5).
                css += f".mes-cor-{cor.mes + 1}  {{ background-color: {cor.cor_hex} !important; }} /* {cor.nome_mes} */\n"

            return {
                'sucesso': True,
                'css': css
            }
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao gerar CSS: {str(e)}'
            }


    @staticmethod
    def atualizar_cor(mes, cor_hex):
        """
        Atualiza a cor de um mês específico.
        """
        try:
            mes_int = int(mes)

            sucesso, mensagem = CoresMeses.atualizar_cor(mes_int, cor_hex)

            return {
                'sucesso': sucesso,
                'mensagem': mensagem
            }
        except ValueError:
            return {
                'sucesso': False,
                'mensagem': 'Mês inválido. Deve ser um número entre 0 e 11.'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao atualizar cor: {str(e)}'
            }


    @staticmethod
    def atualizar_varias_cores(cores_dict):
        """
        Atualiza várias cores de uma vez.
        cores_dict: {'0': '#cor1', '1': '#cor2', ...}
        """
        try:
            erros = []
            sucessos = 0

            for mes_str, cor_hex in cores_dict.items():
                try:
                    mes_int = int(mes_str)
                    sucesso, mensagem = CoresMeses.atualizar_cor(mes_int, cor_hex)

                    if sucesso:
                        sucessos += 1
                    else:
                        erros.append(f"Mês {mes_int}: {mensagem}")
                except Exception as e:
                    erros.append(f"Mês {mes_str}: {str(e)}")

            if erros:
                return {
                    'sucesso': False,
                    'mensagem': f'{sucessos} cores atualizadas. Erros: ' + ', '.join(erros)
                }
            else:
                return {
                    'sucesso': True,
                    'mensagem': f'{sucessos} cores atualizadas com sucesso!'
                }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao atualizar cores: {str(e)}'
            }


    @staticmethod
    def restaurar_padrao():
        """
        Restaura todas as cores para os valores padrão.
        """
        try:
            sucesso, mensagem = CoresMeses.restaurar_cores_padrao()

            return {
                'sucesso': sucesso,
                'mensagem': mensagem
            }
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao restaurar cores padrão: {str(e)}'
            }


    @staticmethod
    def validar_cor_hex(cor_hex):
        """
        Valida se uma cor está no formato hexadecimal correto (#RRGGBB).
        """
        if not cor_hex:
            return False, "Cor não pode ser vazia"

        if not isinstance(cor_hex, str):
            return False, "Cor deve ser uma string"

        if not cor_hex.startswith('#'):
            return False, "Cor deve começar com #"

        if len(cor_hex) != 7:
            return False, "Cor deve ter 7 caracteres (#RRGGBB)"

        try:
            # Tentar converter para verificar se é hexadecimal válido
            int(cor_hex[1:], 16)
            return True, "Cor válida"
        except ValueError:
            return False, "Cor contém caracteres inválidos. Use apenas 0-9 e A-F"

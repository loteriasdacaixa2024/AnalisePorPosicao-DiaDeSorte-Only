# Sistema: Análise por Posição - Dia de Sorte
# Serviço: Resultados - Exibição de Concursos
# Desenvolvido para: Márcio Fernando Maia

from models.sorteio import Sorteio, db
from datetime import datetime

class ResultadosService:
    """
    Serviço responsável por fornecer dados de resultados dos concursos do Dia de Sorte.
    Consulta o banco de dados local (analise_por_posicao.db) para exibição de resultados.
    """

    # Mapeamento de números para nomes dos meses
    NOMES_MESES = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    @staticmethod
    def obter_nome_mes(numero):
        """Converte número do mês para nome"""
        return ResultadosService.NOMES_MESES.get(numero, 'Desconhecido')

    @staticmethod
    def formatar_data(data_obj):
        """Formata objeto datetime para string dd/mm/aaaa"""
        if not data_obj:
            return ''
        try:
            return data_obj.strftime('%d/%m/%Y')
        except:
            return str(data_obj)

    @staticmethod
    def obter_dia_semana(data_obj):
        """Retorna o nome do dia da semana"""
        if not data_obj:
            return ''
        try:
            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            return dias_semana[data_obj.weekday()]
        except:
            return ''

    @staticmethod
    def formatar_moeda(valor):
        """Formata valor numérico para moeda brasileira"""
        if not valor:
            return 'R$ 0,00'
        try:
            return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return f"R$ {valor}"

    @staticmethod
    def obter_ultimo_concurso():
        """
        Retorna os dados do último concurso registrado no banco.
        """
        try:
            sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

            if not sorteio:
                return None

            return ResultadosService._formatar_sorteio(sorteio)

        except Exception as e:
            print(f"❌ Erro ao obter último concurso: {e}")
            return None

    @staticmethod
    def obter_concurso_por_numero(numero):
        """
        Retorna os dados de um concurso específico pelo número.
        """
        try:
            sorteio = Sorteio.query.filter_by(concurso=numero).first()

            if not sorteio:
                return None

            return ResultadosService._formatar_sorteio(sorteio)

        except Exception as e:
            print(f"❌ Erro ao obter concurso {numero}: {e}")
            return None

    @staticmethod
    def obter_ultimos_concursos(quantidade=6):
        """
        Retorna os últimos N concursos ordenados do mais recente para o mais antigo.
        """
        try:
            if quantidade < 1:
                quantidade = 6
            if quantidade > 100:
                quantidade = 100

            sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(quantidade).all()

            if not sorteios:
                return {
                    'sucesso': True,
                    'concursos': [],
                    'total': 0,
                    'mensagem': 'Nenhum concurso encontrado. Sincronize com a API da Caixa.'
                }

            concursos = [ResultadosService._formatar_sorteio(s) for s in sorteios]

            return {
                'sucesso': True,
                'concursos': concursos,
                'total': len(concursos),
                'ultimo_concurso': sorteios[0].concurso if sorteios else 0
            }

        except Exception as e:
            print(f"❌ Erro ao obter últimos concursos: {e}")
            return {
                'sucesso': False,
                'erro': str(e),
                'concursos': [],
                'total': 0
            }

    @staticmethod
    def obter_concursos_paginados(pagina=1, por_pagina=6):
        """
        Retorna concursos com paginação.
        """
        try:
            if por_pagina > 50:
                por_pagina = 50

            paginacao = Sorteio.query.order_by(Sorteio.concurso.desc()).paginate(
                page=pagina,
                per_page=por_pagina,
                error_out=False
            )

            concursos = [ResultadosService._formatar_sorteio(s) for s in paginacao.items]

            return {
                'sucesso': True,
                'concursos': concursos,
                'total': paginacao.total,
                'pagina': paginacao.page,
                'total_paginas': paginacao.pages,
                'por_pagina': por_pagina,
                'tem_proxima': paginacao.has_next,
                'tem_anterior': paginacao.has_prev,
                'ultimo_concurso': concursos[0]['numero'] if concursos else 0
            }

        except Exception as e:
            print(f"❌ Erro ao obter concursos paginados: {e}")
            return {
                'sucesso': False,
                'erro': str(e),
                'concursos': [],
                'total': 0
            }

    @staticmethod
    def obter_concursos_intervalo(inicio, fim):
        """
        Retorna concursos em um intervalo específico de números.
        """
        try:
            if inicio > fim:
                inicio, fim = fim, inicio

            sorteios = Sorteio.query.filter(
                Sorteio.concurso >= inicio,
                Sorteio.concurso <= fim
            ).order_by(Sorteio.concurso.desc()).all()

            concursos = [ResultadosService._formatar_sorteio(s) for s in sorteios]

            return {
                'sucesso': True,
                'concursos': concursos,
                'total': len(concursos),
                'inicio': inicio,
                'fim': fim
            }

        except Exception as e:
            print(f"❌ Erro ao obter concursos no intervalo {inicio}-{fim}: {e}")
            return {
                'sucesso': False,
                'erro': str(e),
                'concursos': [],
                'total': 0
            }

    @staticmethod
    def obter_estatisticas_gerais():
        """
        Retorna estatísticas gerais dos concursos.
        """
        try:
            total = Sorteio.query.count()
            ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
            primeiro = Sorteio.query.order_by(Sorteio.concurso.asc()).first()

            # Contagem de acumulados
            acumulados = Sorteio.query.filter_by(acumulado=True).count() if hasattr(Sorteio, 'acumulado') else 0

            return {
                'sucesso': True,
                'total_concursos': total,
                'primeiro_concurso': primeiro.concurso if primeiro else 0,
                'ultimo_concurso': ultimo.concurso if ultimo else 0,
                'proximo_concurso': (ultimo.concurso + 1) if ultimo else 1,
                'total_acumulados': acumulados,
                'percentual_acumulados': round((acumulados / total * 100), 2) if total > 0 else 0
            }

        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {
                'sucesso': False,
                'erro': str(e)
            }

    @staticmethod
    def _formatar_sorteio(sorteio):
        """
        Formata um objeto Sorteio para o formato esperado pelo frontend.
        """
        # Dezenas originais: sempre ordem crescente (travado)
        dezenas = sorted([
            sorteio.posicao_1,
            sorteio.posicao_2,
            sorteio.posicao_3,
            sorteio.posicao_4,
            sorteio.posicao_5,
            sorteio.posicao_6,
            sorteio.posicao_7
        ])

        # Formatar data
        data_formatada = ResultadosService.formatar_data(sorteio.data_sorteio)
        dia_semana = ResultadosService.obter_dia_semana(sorteio.data_sorteio)

        # Nome do mês da sorte
        mes_sorte_nome = ResultadosService.obter_nome_mes(sorteio.mes_sorte) if sorteio.mes_sorte else ''

        # Verificar se acumulou
        acumulou = getattr(sorteio, 'acumulado', False)

        # ============================================================
        # CORREÇÃO: Usar valor_premio_7_acertos como prêmio principal
        # ============================================================
        valor_premio_principal = getattr(sorteio, 'valor_premio_7_acertos', 0) or 0

        # Ganhadores e prêmios (se disponíveis no banco)
        ganhadores = {
            'seteAcertos': getattr(sorteio, 'ganhadores_7_acertos', 0) or 0,
            'seisAcertos': getattr(sorteio, 'ganhadores_6_acertos', 0) or 0,
            'cincoAcertos': getattr(sorteio, 'ganhadores_5_acertos', 0) or 0,
            'quatroAcertos': getattr(sorteio, 'ganhadores_4_acertos', 0) or 0,
            'mesDeSorte': getattr(sorteio, 'ganhadores_mes_sorte', 0) or 0
        }

        # Usar valorPremio para o prêmio de 7 acertos
        premios = {
            'seteAcertos': valor_premio_principal,  # <-- CORREÇÃO AQUI
            'seisAcertos': getattr(sorteio, 'valor_premio_6_acertos', 0) or 0,
            'cincoAcertos': getattr(sorteio, 'valor_premio_5_acertos', 0) or 0,
            'quatroAcertos': getattr(sorteio, 'valor_premio_4_acertos', 0) or 0,
            'mesDeSorte': getattr(sorteio, 'valor_premio_mes_sorte', 0) or 0
        }

        # Próximo concurso (se disponível no banco)
        proximo_numero = getattr(sorteio, 'numero_concurso_proximo', None) or (sorteio.concurso + 1)
        data_proximo = getattr(sorteio, 'data_proximo_concurso', None)
        valor_estimado = getattr(sorteio, 'valor_estimado_proximo_concurso', 0) or 0

        proximo_concurso = {
            'numero': proximo_numero,
            'data': ResultadosService.formatar_data(data_proximo) if data_proximo else '',
            'diaSemana': ResultadosService.obter_dia_semana(data_proximo) if data_proximo else '',
            'estimativaPremio': valor_estimado
        }

        # Local do sorteio
        local_sorteio = getattr(sorteio, 'local_sorteio', None) or 'CAIXA - Brasília/DF'

        return {
            'numero': sorteio.concurso,
            'data': data_formatada,
            'diaSemana': dia_semana,
            'numeros': dezenas,
            'mesSorte': mes_sorte_nome,
            'mesSorteNumero': sorteio.mes_sorte,
            'acumulou': acumulou,
            'localSorteio': local_sorteio,
            'ganhadores': ganhadores,
            'premios': premios,
            'valorPremio': valor_premio_principal,  # <-- CAMPO ADICIONAL
            'proximoConcurso': proximo_concurso,
            'premiosFormatados': {
                'seteAcertos': ResultadosService.formatar_moeda(premios['seteAcertos']),
                'seisAcertos': ResultadosService.formatar_moeda(premios['seisAcertos']),
                'cincoAcertos': ResultadosService.formatar_moeda(premios['cincoAcertos']),
                'quatroAcertos': ResultadosService.formatar_moeda(premios['quatroAcertos']),
                'mesDeSorte': ResultadosService.formatar_moeda(premios['mesDeSorte']),
                'estimativaProximo': ResultadosService.formatar_moeda(valor_estimado),
                'valorPremio': ResultadosService.formatar_moeda(valor_premio_principal)  # <-- FORMATADO
            }
        }

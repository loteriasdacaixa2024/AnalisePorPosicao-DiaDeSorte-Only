"""
Service para Dashboard de Análises - Consolidação de todas as análises do sistema
Lê dinamicamente todos os serviços de análise e consolida TOP 3 e insights
"""

import os
import importlib
import sys
from pathlib import Path


class DashboardAnalisesService:

    # Mapeamento de nome do serviço para informações de exibição
    ANALISES_CONFIG = {
        'analise_atrasados': {
            'titulo': 'Análise de Atrasados',
            'icone': 'fa-clock',
            'descricao': 'Números que estão há mais tempo sem aparecer',
            'rota_api': '/api/analise/atrasados'
        },
        'analise_meses': {
            'titulo': 'Análise de Meses',
            'icone': 'fa-calendar-alt',
            'descricao': 'Frequência e padrões dos meses da sorte',
            'rota_api': '/api/analise/meses'
        },
        'analise_combinacoes': {
            'titulo': 'Análise de Combinações',
            'icone': 'fa-link',
            'descricao': 'Combinações de números que aparecem juntos',
            'rota_api': '/api/analise/combinacoes'
        },
        'analise_quentes_frios': {
            'titulo': 'Análise de Quentes e Frios',
            'icone': 'fa-thermometer-half',
            'descricao': 'Números mais e menos frequentes recentemente',
            'rota_api': '/api/analise/quentes-frios'
        },
        'analise_pares_impares': {
            'titulo': 'Análise de Pares e Ímpares',
            'icone': 'fa-balance-scale',
            'descricao': 'Distribuição entre números pares e ímpares',
            'rota_api': '/api/analise/pares-impares'
        },
        'analise_dezenas': {
            'titulo': 'Análise de Dezenas',
            'icone': 'fa-hashtag',
            'descricao': 'Frequência geral de todas as dezenas',
            'rota_api': '/api/analise/dezenas'
        },
        'analise_repeticoes': {
            'titulo': 'Análise de Repetições',
            'icone': 'fa-redo',
            'descricao': 'Números que se repetem entre sorteios consecutivos',
            'rota_api': '/api/analise/repeticoes'
        },
        'analise_sequencias': {
            'titulo': 'Análise de Sequências',
            'icone': 'fa-stream',
            'descricao': 'Sequências de números consecutivos',
            'rota_api': '/api/analise/sequencias'
        },
        'analise_gaps': {
            'titulo': 'Análise de GAPS',
            'icone': 'fa-ruler-horizontal',
            'descricao': 'Distâncias entre números sorteados',
            'rota_api': '/api/analise/gaps'
        },
        'analise_consecutivos': {
            'titulo': 'Análise de Consecutivos',
            'icone': 'fa-sort-numeric-up',
            'descricao': 'Quantidade de números consecutivos por jogo',
            'rota_api': '/api/analise/consecutivos'
        },
        'analise_quadrantes': {
            'titulo': 'Análise de Quadrantes',
            'icone': 'fa-th',
            'descricao': 'Distribuição por faixas numéricas (quadrantes)',
            'rota_api': '/api/analise/quadrantes'
        },
        'analise_soma_dezenas': {
            'titulo': 'Análise de Soma',
            'icone': 'fa-calculator',
            'descricao': 'Análise da soma das dezenas sorteadas',
            'rota_api': '/api/analise/soma-dezenas'
        },
        'analise_primos_compostos': {
            'titulo': 'Análise de Primos e Compostos',
            'icone': 'fa-divide',
            'descricao': 'Números primos vs números compostos',
            'rota_api': '/api/analise/primos-compostos'
        },
        'analise_multiplos': {
            'titulo': 'Análise de Múltiplos',
            'icone': 'fa-times',
            'descricao': 'Múltiplos de 3, 5, 7 e outros padrões',
            'rota_api': '/api/analise/multiplos'
        },
        'analise_espelhados': {
            'titulo': 'Análise de Espelhados',
            'icone': 'fa-mirror',
            'descricao': 'Números espelhados (01-31, 02-30, etc)',
            'rota_api': '/api/analise/espelhados'
        },
        'analise_digitos_unicos': {
            'titulo': 'Análise de Dígitos Únicos',
            'icone': 'fa-fingerprint',
            'descricao': 'Quantidade de dígitos únicos por jogo',
            'rota_api': '/api/analise/digitos-unicos'
        },
        'analise_raiz_digital': {
            'titulo': 'Análise de Raiz Digital',
            'icone': 'fa-square-root-alt',
            'descricao': 'Soma reduzida dos números (numerologia)',
            'rota_api': '/api/analise/raiz-digital'
        },
        'analise_fibonacci': {
            'titulo': 'Análise de Fibonacci',
            'icone': 'fa-wave-square',
            'descricao': 'Números que fazem parte da sequência Fibonacci',
            'rota_api': '/api/analise/fibonacci'
        },
        'analise_frequencia_premios': {
            'titulo': 'Análise de Frequência de Prêmios',
            'icone': 'fa-trophy',
            'descricao': 'Padrões dos jogos que tiveram acertadores',
            'rota_api': '/api/analise/frequencia-premios'
        },
        'analise_correlacao_mes_dezenas': {
            'titulo': 'Análise de Correlação Mês × Dezenas',
            'icone': 'fa-project-diagram',
            'descricao': 'Relação entre mês da sorte e dezenas',
            'rota_api': '/api/analise/correlacao-mes-dezenas'
        },
        'analise_defasagem': {
            'titulo': 'Análise de Defasagem',
            'icone': 'fa-chart-line',
            'descricao': 'Análise de atrasos e tendências',
            'rota_api': '/api/analise/defasagem'
        },
        'analise_numeros_devidos': {
            'titulo': 'Análise de Números Devidos',
            'icone': 'fa-bell',
            'descricao': 'Números com alta probabilidade de sair',
            'rota_api': '/api/analise/numeros-devidos'
        },
        'analise_distribuicao_numerica': {
            'titulo': 'Análise de Distribuição Numérica',
            'icone': 'fa-chart-area',
            'descricao': 'Distribuição dos números ao longo do intervalo',
            'rota_api': '/api/analise/distribuicao-numerica'
        },
        'analise_ciclos_meses': {
            'titulo': 'Análise de Ciclos de Meses',
            'icone': 'fa-sync',
            'descricao': 'Ciclos e padrões de repetição dos meses',
            'rota_api': '/api/analise/ciclos-meses'
        },
        'analise_sazonal': {
            'titulo': 'Análise Sazonal',
            'icone': 'fa-leaf',
            'descricao': 'Padrões sazonais e tendências temporais',
            'rota_api': '/api/analise/sazonal'
        },
        'analise_interse_apostas': {
            'titulo': 'Análise de Interseção entre Apostas',
            'icone': 'fa-link',
            'descricao': 'Interseção média e pares compartilhados entre apostas',
            'rota_api': '/api/analise/interse-apostas'
        },
        'analise_frequencia_interna_apostas': {
            'titulo': 'Frequência Interna das Apostas',
            'icone': 'fa-bar-chart',
            'descricao': 'Frequência de cada dezena dentro do conjunto de apostas',
            'rota_api': '/api/analise/freq-interna-apostas'
        },
        'analise_desdobramento_validator': {
            'titulo': 'Validador de Desdobramento 2x2',
            'icone': 'fa-check-double',
            'descricao': 'Confere cobertura dos 21 pares do concurso anterior nas apostas',
            'rota_api': '/api/analise/valida-desdobramento'
        },
        'analise_gaps_transicoes_apostas': {
            'titulo': 'Análise de Gaps e Transições (Apostas)',
            'icone': 'fa-exchange-alt',
            'descricao': 'Repetidas, deslocadas e novas dezenas vs. concurso anterior',
            'rota_api': '/api/analise/gaps-transicoes-apostas'
        },
        'analise_simulacao_reversa': {
            'titulo': 'Simulação Reversa (Histórico)',
            'icone': 'fa-history',
            'descricao': 'Simula 10 apostas a partir do concurso anterior e mede dispersão',
            'rota_api': '/api/analise/simulacao-reversa'
        },
    }

    @staticmethod
    def obter_lista_analises():
        """Retorna lista de todas as análises disponíveis no sistema"""
        services_dir = Path('services')

        if not services_dir.exists():
            return []

        analises = []

        # Listar todos os arquivos *_service.py, excluindo BAK
        for arquivo in services_dir.glob('analise_*_service.py'):
            # Ignorar arquivos com BAK no nome
            if 'BAK' in arquivo.name.upper() or 'bak' in arquivo.name:
                continue

            # Extrair nome base (sem _service.py)
            nome_base = arquivo.stem.replace('_service', '')

            # Pegar configuração ou criar uma padrão
            config = DashboardAnalisesService.ANALISES_CONFIG.get(
                nome_base,
                {
                    'titulo': nome_base.replace('_', ' ').title(),
                    'icone': 'fa-chart-bar',
                    'descricao': f'Análise de {nome_base.replace("_", " ")}',
                    'rota_api': f'/api/{nome_base.replace("_", "-")}'
                }
            )

            analises.append({
                'nome': nome_base,
                'titulo': config['titulo'],
                'icone': config['icone'],
                'descricao': config['descricao'],
                'rota_api': config['rota_api'],
                'link_visualizar': f'/analise/{nome_base.replace("analise_", "")}'
            })

        # Ordenar alfabeticamente
        return sorted(analises, key=lambda x: x['titulo'])

    @staticmethod
    def obter_dashboard_completo():
        """Retorna dados consolidados de todas as análises para o dashboard"""
        analises = DashboardAnalisesService.obter_lista_analises()

        return {
            'total_analises': len(analises),
            'analises': analises,
            'categorias': {
                'Frequência e Padrões': [
                    'analise_dezenas', 'analise_meses', 'analise_frequencia_premios',
                    'analise_quentes_frios', 'analise_atrasados'
                ],
                'Distribuição Numérica': [
                    'analise_pares_impares', 'analise_quadrantes', 'analise_soma_dezenas',
                    'analise_distribuicao_numerica', 'analise_primos_compostos'
                ],
                'Padrões Avançados': [
                    'analise_sequencias', 'analise_gaps', 'analise_consecutivos',
                    'analise_repeticoes', 'analise_espelhados'
                ],
                'Análises Matemáticas': [
                    'analise_multiplos', 'analise_fibonacci', 'analise_raiz_digital',
                    'analise_digitos_unicos'
                ],
                'Tendências e Previsões': [
                    'analise_numeros_devidos', 'analise_defasagem', 'analise_ciclos_meses',
                    'analise_sazonal', 'analise_correlacao_mes_dezenas'
                ],
                'Análises de Apostas Múltiplas': [
                    'analise_interse_apostas',
                    'analise_frequencia_interna_apostas',
                    'analise_desdobramento_validator',
                    'analise_gaps_transicoes_apostas',
                    'analise_simulacao_reversa'
                ]
            }
        }

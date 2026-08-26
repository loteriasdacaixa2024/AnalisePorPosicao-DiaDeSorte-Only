"""
Serviço de Monitoramento de Apostas - VERSÃO MODIFICADA
Analisa desempenho de apostas comparando com resultados oficiais do banco de dados
Filtro: Apenas apostas vencedoras com 4, 5, 6 e 7 pontos
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple
import json
from collections import Counter, defaultdict
from models.sorteio import Sorteio
from models.analise_aposta import AnaliseAposta
from models import db
from sqlalchemy import func, desc


class MonitoramentoApostasService:
    """Service para análise e monitoramento de apostas - MODIFICADO"""

    # Cores de destaque conforme especificação
    CORES_PONTUACAO = {
        7: {'cor': '#EB5757', 'nome': 'Vermelho', 'descricao': 'Prêmio máximo - destaque absoluto'},
        6: {'cor': '#F2C94C', 'nome': 'Amarelo', 'descricao': '"Quase 7" - prêmio relevante'},
        5: {'cor': '#2D9CDB', 'nome': 'Azul forte', 'descricao': 'Prêmio médio'},
        4: {'cor': '#DDDDDD', 'nome': 'Cinza claro', 'descricao': 'Prêmio menor'}
    }

    @staticmethod
    def validar_aposta(aposta: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida formato de uma aposta

        Args:
            aposta: Dicionário com dados da aposta

        Returns:
            Tuple (válida: bool, mensagem: str)
        """
        # Verificar se tem campo 'numeros' ou 'dezenas'
        numeros = aposta.get('numeros') or aposta.get('dezenas') or aposta.get('numbers')

        if not numeros:
            return False, "Aposta sem campo de números"

        # Converter para lista se for string
        if isinstance(numeros, str):
            numeros = [int(n.strip()) for n in numeros.replace('-', ' ').split() if n.strip().isdigit()]

        # Validar quantidade (7 números)
        if len(numeros) != 7:
            return False, f"Aposta deve ter exatamente 7 números (encontrado: {len(numeros)})"

        # Validar range (1-31)
        if not all(1 <= n <= 31 for n in numeros):
            return False, "Números devem estar entre 1 e 31"

        # Validar números únicos
        if len(set(numeros)) != 7:
            return False, "Números devem ser únicos"

        return True, "Válida"

    @staticmethod
    def processar_apostas_json(json_data: str) -> Tuple[List[Dict], List[str]]:
        """
        Processa apostas de um JSON

        Args:
            json_data: String JSON com apostas

        Returns:
            Tuple (apostas_validas: List, erros: List)
        """
        apostas_validas = []
        erros = []

        try:
            data = json.loads(json_data)

            # Se for um objeto com campo 'apostas'
            if isinstance(data, dict) and 'apostas' in data:
                data = data['apostas']

            # Se não for lista, transformar em lista
            if not isinstance(data, list):
                data = [data]

            for idx, aposta in enumerate(data, 1):
                valida, msg = MonitoramentoApostasService.validar_aposta(aposta)

                if valida:
                    # Normalizar formato
                    numeros = aposta.get('numeros') or aposta.get('dezenas') or aposta.get('numbers')
                    if isinstance(numeros, str):
                        numeros = [int(n.strip()) for n in numeros.replace('-', ' ').split() if n.strip().isdigit()]

                    apostas_validas.append({
                        'id_original': aposta.get('id', idx),
                        'numeros': sorted(numeros),
                        'mes': aposta.get('mes'),
                        'nome': aposta.get('nome', f'Aposta {idx}'),
                        'data_aposta': aposta.get('data_aposta'),
                        'valor': aposta.get('valor', 2.50)
                    })
                else:
                    erros.append(f"Aposta {idx}: {msg}")

        except json.JSONDecodeError as e:
            erros.append(f"Erro ao decodificar JSON: {str(e)}")
        except Exception as e:
            erros.append(f"Erro ao processar apostas: {str(e)}")

        return apostas_validas, erros

    @staticmethod
    def processar_apostas_texto(texto: str) -> Tuple[List[Dict], List[str]]:
        """
        Processa apostas de texto livre
        Formatos aceitos:
        - 01 02 03 04 05 06 07
        - 1 2 3 4 5 6 7
        - 01-02-03-04-05-06-07
        - {"numeros": [1,2,3,4,5,6,7]}

        Args:
            texto: Texto com apostas (uma por linha)

        Returns:
            Tuple (apostas_validas: List, erros: List)
        """
        apostas_validas = []
        erros = []

        linhas = [l.strip() for l in texto.split('\n') if l.strip()]

        for idx, linha in enumerate(linhas, 1):
            try:
                # Tentar como JSON primeiro
                if linha.startswith('{'):
                    data = json.loads(linha)
                    numeros = data.get('numeros') or data.get('dezenas') or data.get('numbers')
                    mes = data.get('mes')
                    nome = data.get('nome', f'Aposta {idx}')
                else:
                    # Processar como texto simples
                    numeros = [int(n.strip()) for n in linha.replace('-', ' ').split() if n.strip().isdigit()]
                    mes = None
                    nome = f'Aposta {idx}'

                if isinstance(numeros, str):
                    numeros = [int(n.strip()) for n in numeros.replace('-', ' ').split() if n.strip().isdigit()]

                aposta = {'numeros': numeros, 'mes': mes, 'nome': nome}
                valida, msg = MonitoramentoApostasService.validar_aposta(aposta)

                if valida:
                    apostas_validas.append({
                        'id_original': idx,
                        'numeros': sorted(numeros),
                        'mes': mes,
                        'nome': nome,
                        'valor': 2.50
                    })
                else:
                    erros.append(f"Linha {idx}: {msg}")

            except Exception as e:
                erros.append(f"Linha {idx}: Erro ao processar - {str(e)}")

        return apostas_validas, erros

    @staticmethod
    def calcular_acertos(aposta: List[int], resultado: List[int]) -> Dict[str, Any]:
        """
        Calcula acertos entre aposta e resultado

        Args:
            aposta: Lista de números apostados
            resultado: Lista de números sorteados

        Returns:
            Dict com estatísticas de acertos
        """
        aposta_set = set(aposta)
        resultado_set = set(resultado)

        acertos = aposta_set.intersection(resultado_set)
        qtd_acertos = len(acertos)

        # Determinar faixa de premiação
        faixa = None
        if qtd_acertos == 7:
            faixa = '7_acertos'
        elif qtd_acertos == 6:
            faixa = '6_acertos'
        elif qtd_acertos == 5:
            faixa = '5_acertos'
        elif qtd_acertos == 4:
            faixa = '4_acertos'

        return {
            'qtd_acertos': qtd_acertos,
            'numeros_acertados': sorted(list(acertos)),
            'faixa_premiacao': faixa,
            'premiada': qtd_acertos >= 4  # ✅ MODIFICAÇÃO: Apenas apostas com 4+ pontos são premiadas
        }

    @staticmethod
    def analisar_apostas(apostas: List[Dict], concurso_inicio: int = None,
                        concurso_fim: int = None, data_inicio: str = None,
                        data_fim: str = None) -> Dict[str, Any]:
        """
        Analisa desempenho das apostas contra resultados do banco
        ✅ MODIFICAÇÃO: Filtra apenas apostas vencedoras (4, 5, 6, 7 pontos)

        Args:
            apostas: Lista de apostas para analisar
            concurso_inicio: Concurso inicial (opcional)
            concurso_fim: Concurso final (opcional)
            data_inicio: Data inicial (opcional)
            data_fim: Data final (opcional)

        Returns:
            Dict com análise completa
        """
        # Buscar sorteios do banco
        query = db.session.query(Sorteio).order_by(Sorteio.concurso.desc())

        if concurso_inicio:
            query = query.filter(Sorteio.concurso >= concurso_inicio)
        if concurso_fim:
            query = query.filter(Sorteio.concurso <= concurso_fim)
        if data_inicio:
            query = query.filter(Sorteio.data_sorteio >= datetime.strptime(data_inicio, '%Y-%m-%d'))
        if data_fim:
            query = query.filter(Sorteio.data_sorteio <= datetime.strptime(data_fim, '%Y-%m-%d'))

        sorteios = query.all()

        if not sorteios:
            return {
                'sucesso': False,
                'mensagem': 'Nenhum sorteio encontrado no período especificado'
            }

        # Análise detalhada
        resultados_detalhados = []
        estatisticas_globais = {
            'total_apostas': len(apostas),
            'total_sorteios_analisados': len(sorteios),
            'total_comparacoes': len(apostas) * len(sorteios),
            'apostas_premiadas': 0,  # ✅ APENAS apostas com 4+ pontos
            'total_premios_4': 0,
            'total_premios_5': 0,
            'total_premios_6': 0,
            'total_premios_7': 0,
            'frequencia_numeros': Counter(),
            'frequencia_numeros_acertados': Counter(),
            'melhor_aposta': None,
            'melhor_concurso': None,
            'maior_quantidade_acertos': 0,
            'apostas_premiadas_detalhadas': Counter(),  # ✅ NOVO: Rastreamento por nome da aposta
            'cores_por_pontuacao': MonitoramentoApostasService.CORES_PONTUACAO  # ✅ NOVO: Sistema de cores
        }

        # Para cada aposta, comparar com todos os sorteios
        for aposta in apostas:
            acertos_por_concurso = []
            total_acertos_aposta = 0
            premiada = False  # ✅ MODIFICAÇÃO: Apenas True para 4+ pontos
            premios_aposta = {4: 0, 5: 0, 6: 0, 7: 0}  # ✅ NOVO: Contador de prêmios por aposta

            for sorteio in sorteios:
                resultado = sorteio.get_posicoes_lista()
                acertos_info = MonitoramentoApostasService.calcular_acertos(
                    aposta['numeros'], resultado
                )

                if acertos_info['premiada']:  # ✅ MODIFICAÇÃO: Só considera premios de 4+ pontos
                    premiada = True
                    
                    if acertos_info['faixa_premiacao'] == '4_acertos':
                        estatisticas_globais['total_premios_4'] += 1
                        premios_aposta[4] += 1
                    elif acertos_info['faixa_premiacao'] == '5_acertos':
                        estatisticas_globais['total_premios_5'] += 1
                        premios_aposta[5] += 1
                    elif acertos_info['faixa_premiacao'] == '6_acertos':
                        estatisticas_globais['total_premios_6'] += 1
                        premios_aposta[6] += 1
                    elif acertos_info['faixa_premiacao'] == '7_acertos':
                        estatisticas_globais['total_premios_7'] += 1
                        premios_aposta[7] += 1

                acertos_por_concurso.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%Y-%m-%d') if sorteio.data_sorteio else None,
                    'resultado': resultado,
                    **acertos_info,
                    'cor_destaque': MonitoramentoApostasService.CORES_PONTUACAO.get(acertos_info['qtd_acertos'], {}).get('cor')  # ✅ NOVO: Cor por pontuação
                })

                total_acertos_aposta += acertos_info['qtd_acertos']

                # Atualizar frequência de números acertados
                for num in acertos_info['numeros_acertados']:
                    estatisticas_globais['frequencia_numeros_acertados'][num] += 1

                # Rastrear melhor desempenho
                if acertos_info['qtd_acertos'] > estatisticas_globais['maior_quantidade_acertos']:
                    estatisticas_globais['maior_quantidade_acertos'] = acertos_info['qtd_acertos']
                    estatisticas_globais['melhor_aposta'] = aposta.get('nome', 'Aposta')
                    estatisticas_globais['melhor_concurso'] = sorteio.concurso

            # ✅ NOVO: Contar apostas premiadoras (4+ pontos apenas)
            if premiada:
                estatisticas_globais['apostas_premiadas'] += 1
                # Contar total de prêmios desta aposta
                total_premios_aposta = sum(premios_aposta.values())
                estatisticas_globais['apostas_premiadas_detalhadas'][aposta.get('nome', 'Aposta')] = total_premios_aposta

            # Atualizar frequência de números apostados
            for num in aposta['numeros']:
                estatisticas_globais['frequencia_numeros'][num] += 1

            resultados_detalhados.append({
                'aposta': aposta,
                'total_acertos': total_acertos_aposta,
                'media_acertos': round(total_acertos_aposta / len(sorteios), 2) if sorteios else 0,
                'premiada': premiada,
                'premios_por_pontuacao': premios_aposta,  # ✅ NOVO: Detalhamento de prêmios
                'total_premios': sum(premios_aposta.values()),  # ✅ NOVO: Total de prêmios da aposta
                'acertos_por_concurso': acertos_por_concurso,
                'cores_aplicadas': MonitoramentoApostasService.CORES_PONTUACAO  # ✅ NOVO: Sistema de cores aplicado
            })

        # ✅ NOVO: Análise de qual aposta mais premiou
        analise_melhor_premio = MonitoramentoApostasService._analisar_melhor_premio(resultados_detalhados, estatisticas_globais)

        # Ordenar apostas por desempenho (apenas premiadas primeiro)
        resultados_detalhados.sort(key=lambda x: (x['premiada'], x['total_premios']), reverse=True)

        # Calcular insights
        insights = MonitoramentoApostasService._gerar_insights(
            estatisticas_globais, resultados_detalhados, sorteios, analise_melhor_premio
        )

        return {
            'sucesso': True,
            'timestamp': datetime.now().isoformat(),
            'periodo': {
                'concurso_inicio': sorteios[-1].concurso if sorteios else None,
                'concurso_fim': sorteios[0].concurso if sorteios else None,
                'data_inicio': sorteios[-1].data_sorteio.strftime('%Y-%m-%d') if sorteios and sorteios[-1].data_sorteio else None,
                'data_fim': sorteios[0].data_sorteio.strftime('%Y-%m-%d') if sorteios and sorteios[0].data_sorteio else None
            },
            'estatisticas': estatisticas_globais,
            'resultados_detalhados': resultados_detalhados,
            'insights': insights,
            'melhor_premio_analise': analise_melhor_premio,  # ✅ NOVO: Análise de melhor prêmio
            'sistema_cores': MonitoramentoApostasService.CORES_PONTUACAO,  # ✅ NOVO: Sistema de cores
            'apostas_vencedoras_para_evitar': MonitoramentoApostasService._obter_apostas_vencedoras_para_evitar(resultados_detalhados)  # ✅ NOVO: Lista de apostas vencedoras
        }

    @staticmethod
    def _analisar_melhor_premio(resultados_detalhados: List[Dict], estatisticas: Dict) -> Dict[str, Any]:
        """
        ✅ NOVO: Analisa qual aposta mais premiou historicamente
        """
        apostas_premiadas = [r for r in resultados_detalhados if r['premiada']]
        
        if not apostas_premiadas:
            return {
                'melhor_aposta': None,
                'total_premios': 0,
                'pontuacoes': {},
                'detalhamento': 'Nenhuma aposta premiada encontrada',
                'ranking': []
            }

        # Ordenar por total de prêmios (4+ pontos apenas)
        ranking = sorted(apostas_premiadas, key=lambda x: x['total_premios'], reverse=True)
        
        melhor_aposta = ranking[0]
        
        # Análise por pontuação
        analise_pontuacao = {
            7: {'apostas': [], 'total': 0},
            6: {'apostas': [], 'total': 0},
            5: {'apostas': [], 'total': 0},
            4: {'apostas': [], 'total': 0}
        }
        
        for aposta_resultado in ranking:
            nome = aposta_resultado['aposta'].get('nome', 'Aposta')
            premios = aposta_resultado['premios_por_pontuacao']
            total_premios = aposta_resultado['total_premios']
            
            for pontos in [7, 6, 5, 4]:
                if premios[pontos] > 0:
                    analise_pontuacao[pontos]['apostas'].append({
                        'nome': nome,
                        'quantidade': premios[pontos],
                        'total_premios': total_premios,
                        'numeros': aposta_resultado['aposta']['numeros']
                    })
                    analise_pontuacao[pontos]['total'] += 1
        
        return {
            'melhor_aposta': {
                'nome': melhor_aposta['aposta']['nome'],
                'numeros': melhor_aposta['aposta']['numeros'],
                'total_premios': melhor_aposta['total_premios'],
                'premios_por_pontuacao': melhor_aposta['premios_por_pontuacao']
            },
            'total_premios': melhor_aposta['total_premios'],
            'ranking': [
                {
                    'posicao': idx + 1,
                    'nome': r['aposta']['nome'],
                    'total_premios': r['total_premios'],
                    'premios_4': r['premios_por_pontuacao'][4],
                    'premios_5': r['premios_por_pontuacao'][5],
                    'premios_6': r['premios_por_pontuacao'][6],
                    'premios_7': r['premios_por_pontuacao'][7],
                    'numeros': r['aposta']['numeros']
                }
                for idx, r in enumerate(ranking[:10])  # Top 10
            ],
            'analise_por_pontuacao': analise_pontuacao,
            'estatisticas_gerais': {
                'total_apostas_premiadas': len(apostas_premiadas),
                'total_premios_capturados': sum(r['total_premios'] for r in apostas_premiadas),
                'distribuicao_pontos': {
                    'premios_7': sum(r['premios_por_pontuacao'][7] for r in apostas_premiadas),
                    'premios_6': sum(r['premios_por_pontuacao'][6] for r in apostas_premiadas),
                    'premios_5': sum(r['premios_por_pontuacao'][5] for r in apostas_premiadas),
                    'premios_4': sum(r['premios_por_pontuacao'][4] for r in apostas_premiadas)
                }
            }
        }

    @staticmethod
    def _obter_apostas_vencedoras_para_evitar(resultados_detalhados: List[Dict]) -> List[Dict]:
        """
        ✅ NOVO: Obtém lista das apostas vencedoras que devem ser evitadas
        Retorna apostas que já conseguiram prêmios para não apostar novamente
        """
        apostas_vencedoras = []
        
        for resultado in resultados_detalhados:
            if resultado['premiada']:  # Apenas apostas com 4+ pontos
                aposta_info = {
                    'nome': resultado['aposta'].get('nome', 'Aposta'),
                    'numeros': resultado['aposta']['numeros'],
                    'valor': resultado['aposta'].get('valor', 0),
                    'total_premios': resultado['total_premios'],
                    'premios_por_pontuacao': resultado['premios_por_pontuacao'],
                    'melhor_pontuacao': max([
                        pontos for pontos, count in resultado['premios_por_pontuacao'].items() 
                        if count > 0
                    ]),
                    'data_ultimo_premio': None,  # Pode ser implementado se necessário
                    'concurso_ultimo_premio': None,  # Pode ser implementado se necessário
                    'historico_completo': resultado.get('acertos_por_concurso', [])
                }
                
                apostas_vencedoras.append(aposta_info)
        
        # Ordenar por total de prêmios (mais premiadas primeiro)
        apostas_vencedoras.sort(key=lambda x: x['total_premios'], reverse=True)
        
        return apostas_vencedoras

    @staticmethod
    def _gerar_insights(estatisticas: Dict, resultados: List[Dict], sorteios: List, analise_melhor_premio: Dict) -> List[Dict]:
        """Gera insights automáticos da análise - MODIFICADO para incluir melhor prêmio"""
        insights = []

        # ✅ NOVO: Insight principal sobre qual aposta mais premiou
        if analise_melhor_premio['melhor_aposta']:
            melhor = analise_melhor_premio['melhor_aposta']
            insights.append({
                'tipo': 'melhor_aposta_premiada',
                'titulo': '🏆 Aposta que Mais Premiou',
                'valor': f"{melhor['nome']} - {melhor['total_premios']} prêmios",
                'descricao': f"A aposta '{melhor['nome']}' com números {melhor['numeros']} conquistou {melhor['total_premios']} prêmios (4+ pontos): " +
                           f"7 pontos: {melhor['premios_por_pontuacao'][7]}, 6 pontos: {melhor['premios_por_pontuacao'][6]}, " +
                           f"5 pontos: {melhor['premios_por_pontuacao'][5]}, 4 pontos: {melhor['premios_por_pontuacao'][4]}",
                'nivel': 'success',
                'cor_destaque': MonitoramentoApostasService.CORES_PONTUACAO[7]['cor']
            })

        # Insight 1: Taxa de premiação (apenas 4+ pontos)
        if estatisticas['total_apostas'] > 0:
            taxa_premiacao = (estatisticas['apostas_premiadas'] / estatisticas['total_apostas']) * 100
            insights.append({
                'tipo': 'taxa_premiacao',
                'titulo': 'Taxa de Premiação',
                'valor': f"{taxa_premiacao:.1f}%",
                'descricao': f"{estatisticas['apostas_premiadas']} de {estatisticas['total_apostas']} apostas foram premiadas (4+ pontos)",
                'nivel': 'success' if taxa_premiacao > 20 else 'warning',
                'cor_destaque': '#10b981' if taxa_premiacao > 20 else '#f59e0b'
            })

        # Insight 2: Distribuição de prêmios por cor
        total_premios = sum([
            estatisticas['total_premios_4'],
            estatisticas['total_premios_5'],
            estatisticas['total_premios_6'],
            estatisticas['total_premios_7']
        ])

        if total_premios > 0:
            distribuicao_cores = []
            cores = MonitoramentoApostasService.CORES_PONTUACAO
            
            for pontos, info_cor in cores.items():
                quantidade = estatisticas[f'total_premios_{pontos}']
                if quantidade > 0:
                    distribuicao_cores.append(f"<span style='color: {info_cor['cor']}'>●</span> {pontos} pontos: {quantidade}")
            
            insights.append({
                'tipo': 'distribuicao_premios_cores',
                'titulo': 'Distribuição de Prêmios por Cor',
                'valor': f"{total_premios} prêmios",
                'descricao': f"Prêmios capturados: {' | '.join(distribuicao_cores)}",
                'nivel': 'info',
                'cores_destaque': True
            })

        # Insight 3: Ranking das melhores apostas
        if len(analise_melhor_premio['ranking']) > 0:
            top_3 = analise_melhor_premio['ranking'][:3]
            ranking_text = []
            for i, aposta in enumerate(top_3, 1):
                emoji = '🥇' if i == 1 else '🥈' if i == 2 else '🥉'
                ranking_text.append(f"{emoji} {aposta['nome']}: {aposta['total_premios']} prêmios")
            
            insights.append({
                'tipo': 'ranking_premios',
                'titulo': 'Top 3 Apostas Mais Premiadas',
                'valor': f"{top_3[0]['total_premios']} prêmios",
                'descricao': f"{' | '.join(ranking_text)}",
                'nivel': 'info'
            })

        # Insight 4: Análise por pontuação máxima
        apostas_7_pontos = sum(1 for r in resultados if r['premios_por_pontuacao'][7] > 0)
        apostas_6_pontos = sum(1 for r in resultados if r['premios_por_pontuacao'][6] > 0)
        
        if apostas_7_pontos > 0:
            insights.append({
                'tipo': 'premio_maximo',
                'titulo': 'Premio Máximo (7 Pontos)',
                'valor': f"{apostas_7_pontos} apostas",
                'descricao': f"{apostas_7_pontos} aposta(s) conseguiram o prêmio máximo de 7 pontos",
                'nivel': 'success',
                'cor_destaque': MonitoramentoApostasService.CORES_PONTUACAO[7]['cor']
            })
        elif apostas_6_pontos > 0:
            insights.append({
                'tipo': 'quase_maximo',
                'titulo': 'Quase Máximo (6 Pontos)',
                'valor': f"{apostas_6_pontos} apostas",
                'descricao': f"{apostas_6_pontos} aposta(s) conseguiram 6 pontos (um abaixo do máximo)",
                'nivel': 'warning',
                'cor_destaque': MonitoramentoApostasService.CORES_PONTUACAO[6]['cor']
            })

        return insights

    @staticmethod
    def salvar_analise(analise_data: Dict, tipo_upload: str, usuario_id: int = None) -> AnaliseAposta:
        """
        Salva análise no banco de dados

        Args:
            analise_data: Dados da análise completa
            tipo_upload: Tipo de upload (json, texto, drag_drop)
            usuario_id: ID do usuário (opcional)

        Returns:
            AnaliseAposta: Registro salvo
        """
        try:
            analise = AnaliseAposta(
                data_analise=datetime.now(),
                usuario_id=usuario_id,
                tipo_upload=tipo_upload,
                total_apostas=analise_data['estatisticas']['total_apostas'],
                total_concursos=analise_data['estatisticas']['total_sorteios_analisados'],
                concurso_inicio=analise_data['periodo']['concurso_inicio'],
                concurso_fim=analise_data['periodo']['concurso_fim'],
                data_inicio=datetime.strptime(analise_data['periodo']['data_inicio'], '%Y-%m-%d') if analise_data['periodo']['data_inicio'] else None,
                data_fim=datetime.strptime(analise_data['periodo']['data_fim'], '%Y-%m-%d') if analise_data['periodo']['data_fim'] else None,
                apostas_premiadas=analise_data['estatisticas']['apostas_premiadas'],
                total_premios_4=analise_data['estatisticas']['total_premios_4'],
                total_premios_5=analise_data['estatisticas']['total_premios_5'],
                total_premios_6=analise_data['estatisticas']['total_premios_6'],
                total_premios_7=analise_data['estatisticas']['total_premios_7'],
                metricas_json=json.dumps(analise_data['estatisticas'], ensure_ascii=False),
                apostas_detalhadas_json=json.dumps(analise_data['resultados_detalhados'], ensure_ascii=False),
                insights_json=json.dumps(analise_data['insights'], ensure_ascii=False),
                status='Concluído - Apenas Premiadas 4+ Pontos'  # ✅ NOVO: Indicar filtro aplicado
            )

            db.session.add(analise)
            db.session.commit()

            return analise

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erro ao salvar análise: {str(e)}")

    @staticmethod
    def listar_analises(usuario_id: int = None, limit: int = 50, offset: int = 0) -> List[AnaliseAposta]:
        """
        Lista análises salvas

        Args:
            usuario_id: Filtrar por usuário (opcional)
            limit: Quantidade de registros
            offset: Deslocamento

        Returns:
            List de AnaliseAposta
        """
        query = db.session.query(AnaliseAposta).order_by(desc(AnaliseAposta.data_analise))

        if usuario_id:
            query = query.filter(AnaliseAposta.usuario_id == usuario_id)

        return query.limit(limit).offset(offset).all()

    @staticmethod
    def obter_analise(analise_id: int) -> AnaliseAposta:
        """
        Obtém uma análise específica

        Args:
            analise_id: ID da análise

        Returns:
            AnaliseAposta ou None
        """
        return db.session.query(AnaliseAposta).filter(AnaliseAposta.id == analise_id).first()

    @staticmethod
    def deletar_analise(analise_id: int) -> bool:
        """
        Deleta uma análise

        Args:
            analise_id: ID da análise

        Returns:
            bool: Sucesso ou não
        """
        try:
            analise = MonitoramentoApostasService.obter_analise(analise_id)
            if analise:
                db.session.delete(analise)
                db.session.commit()
                return True
            return False
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def obter_estatisticas_historicas(usuario_id: int = None) -> Dict[str, Any]:
        """
        Obtém estatísticas históricas de todas as análises

        Args:
            usuario_id: Filtrar por usuário (opcional)

        Returns:
            Dict com estatísticas agregadas
        """
        query = db.session.query(AnaliseAposta)

        if usuario_id:
            query = query.filter(AnaliseAposta.usuario_id == usuario_id)

        analises = query.all()

        if not analises:
            return {
                'total_analises': 0,
                'total_apostas_analisadas': 0,
                'total_premios': 0,
                'sistema_cores': MonitoramentoApostasService.CORES_PONTUACAO
            }

        return {
            'total_analises': len(analises),
            'total_apostas_analisadas': sum(a.total_apostas for a in analises),
            'total_apostas_premiadas': sum(a.apostas_premiadas for a in analises),  # Apenas 4+ pontos
            'total_premios_4': sum(a.total_premios_4 for a in analises),
            'total_premios_5': sum(a.total_premios_5 for a in analises),
            'total_premios_6': sum(a.total_premios_6 for a in analises),
            'total_premios_7': sum(a.total_premios_7 for a in analises),
            'primeira_analise': min(a.data_analise for a in analises).strftime('%Y-%m-%d %H:%M'),
            'ultima_analise': max(a.data_analise for a in analises).strftime('%Y-%m-%d %H:%M'),
            'sistema_cores': MonitoramentoApostasService.CORES_PONTUACAO,
            'filtro_aplicado': 'Apenas apostas vencedoras com 4, 5, 6 e 7 pontos'
        }
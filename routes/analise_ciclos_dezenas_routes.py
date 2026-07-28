# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Rotas: Análise de Ciclos das Dezenas

from flask import Blueprint, render_template, jsonify, request
from services.analise_ciclos_dezenas_service import AnaliseCiclosDezenasService
from services.analise_meses_service import AnaliseMesesService
from services.ciclo_inteligencia_service import CicloInteligenciaService
import random

analise_ciclos_dezenas_bp = Blueprint('analise_ciclos_dezenas', __name__)

# ========================================================================
# ABA 1 - ANÁLISE DO CICLO ATUAL
# ========================================================================

@analise_ciclos_dezenas_bp.route('/analise-ciclos-dezenas')
def analise_ciclos_dezenas():
    """Página principal - Análise do Ciclo Atual"""
    return render_template('analise_ciclos_dezenas/ciclo_atual.html', active_tab='ciclo-atual')

@analise_ciclos_dezenas_bp.route('/api/ciclos-dezenas/ciclo-atual')
def api_ciclo_atual():
    """API: Retorna dados do ciclo atual"""
    try:
        ciclo = AnaliseCiclosDezenasService.obter_ciclo_atual()
        
        if not ciclo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum ciclo encontrado. Verifique se há sorteios cadastrados.'
            }), 404
            
        insights_data = AnaliseCiclosDezenasService.obter_insights_e_recomendacoes()
        top_3 = AnaliseCiclosDezenasService.obter_dezenas_sugeridas(3)
        sugestao_completa = AnaliseCiclosDezenasService.obter_dezenas_sugeridas(7)
        estatisticas = AnaliseCiclosDezenasService.obter_estatisticas_comportamento()
        motor = CicloInteligenciaService.analisar_ciclo_completo()
        comparacao = AnaliseCiclosDezenasService.comparar_ciclo_atual_com_historico()
        
        return jsonify({
            'sucesso': True,
            'dados': ciclo,
            'inteligencia': insights_data,
            'motor_ciclo': motor,
            'comparacao': comparacao,
            'top_3': top_3,
            'sugestao_completa': sugestao_completa,
            'estatisticas': estatisticas
        })
    
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

# ========================================================================
# ABA 2 - MÉTRICAS HISTÓRICAS
# ========================================================================

@analise_ciclos_dezenas_bp.route('/analise-ciclos-dezenas/metricas')
def metricas_ciclos():
    """Página de Métricas Históricas"""
    return render_template('analise_ciclos_dezenas/metricas_historicas.html', active_tab='metricas')

@analise_ciclos_dezenas_bp.route('/api/ciclos-dezenas/metricas-historicas')
def api_metricas_historicas():
    """API: Retorna métricas históricas dos ciclos"""
    try:
        metricas = AnaliseCiclosDezenasService.obter_metricas_historicas()
        comparacao = AnaliseCiclosDezenasService.comparar_ciclo_atual_com_historico()
        historico = AnaliseCiclosDezenasService.obter_historico_ultimos_ciclos(10)
        insights_data = AnaliseCiclosDezenasService.obter_insights_e_recomendacoes()
        estatisticas = AnaliseCiclosDezenasService.obter_estatisticas_comportamento()
        
        return jsonify({
            'sucesso': True,
            'dados': {
                'metricas': metricas,
                'comparacao': comparacao,
                'historico': historico,
                'inteligencia': insights_data,
                'estatisticas': estatisticas
            }
        })
    
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

# ========================================================================
# INTELIGÊNCIA DE CICLO / OPERACIONAL
# ========================================================================

@analise_ciclos_dezenas_bp.route('/analise-ciclos-dezenas/inteligencia-operacional')
def inteligencia_operacional_page():
    """Aba Inteligência Operacional — estratégia e alertas"""
    return render_template(
        'analise_ciclos_dezenas/inteligencia_operacional.html',
        active_tab='inteligencia',
    )


@analise_ciclos_dezenas_bp.route('/api/ciclos-dezenas/dezenas-por-mes')
def api_dezenas_por_mes():
    """Top dezenas que costumam sair com o Mês da Sorte informado."""
    try:
        from services.analise_correlacao_mes_dezenas_service import AnaliseCorrelacaoMesDezenaService
        mes_ref = request.args.get('mes') or request.args.get('mes_sorte')
        info = AnaliseCorrelacaoMesDezenaService.obter_top_dezenas_do_mes(mes_ref)
        if not info:
            return jsonify({'sucesso': False, 'mensagem': 'Mês inválido ou sem dados.'}), 400
        return jsonify({'sucesso': True, 'dados': info})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@analise_ciclos_dezenas_bp.route('/api/ciclos-dezenas/inteligencia-ciclo')
def api_inteligencia_ciclo():
    try:
        mes_ref = request.args.get('mes') or request.args.get('mes_sorte')
        motor = CicloInteligenciaService.analisar_ciclo_completo(mes_ref)
        if not motor:
            return jsonify({'sucesso': False, 'mensagem': 'Nenhum ciclo encontrado.'}), 404
        return jsonify({'sucesso': True, 'dados': motor})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@analise_ciclos_dezenas_bp.route('/api/ciclos-dezenas/inteligencia-operacional')
def api_inteligencia_operacional():
    try:
        mes_ref = request.args.get('mes') or request.args.get('mes_sorte')
        dados = CicloInteligenciaService.obter_inteligencia_operacional(mes_ref)
        if not dados:
            return jsonify({'sucesso': False, 'mensagem': 'Nenhum ciclo encontrado.'}), 404
        return jsonify({'sucesso': True, 'dados': dados})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@analise_ciclos_dezenas_bp.route('/api/ciclos-dezenas/analisar-ciclo', methods=['POST'])
def api_analisar_ciclo():
    """Analisa o ciclo antes de gerar apostas (motor completo)."""
    try:
        dados_req = request.get_json(silent=True) or {}
        mes_ref = dados_req.get('mes_sorte') or dados_req.get('mes') or request.args.get('mes')
        motor = CicloInteligenciaService.analisar_ciclo_completo(mes_ref)
        if not motor:
            return jsonify({'sucesso': False, 'mensagem': 'Nenhum ciclo encontrado.'}), 404
        return jsonify({'sucesso': True, 'dados': motor})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


# ========================================================================
# ABA 3 - SELEÇÃO POR CICLO (DOIS GRIDS)
# ========================================================================

@analise_ciclos_dezenas_bp.route('/analise-ciclos-dezenas/selecao')
def selecao_ciclos():
    """Página de Seleção com Dois Grids"""
    return render_template('analise_ciclos_dezenas/selecao_grids.html', active_tab='selecao')

@analise_ciclos_dezenas_bp.route('/api/ciclos-dezenas/dados-selecao')
def api_dados_selecao():
    """API: Retorna dados para os grids de seleção"""
    try:
        ciclo = AnaliseCiclosDezenasService.obter_ciclo_atual()
        
        if not ciclo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum ciclo atual encontrado.'
            }), 404
        
        # Grid 1: Apenas dezenas pendentes (para OBSERVAR)
        dezenas_pendentes = ciclo['dezenas_pendentes']
        
        # Grid 2: TODAS as 31 dezenas (para SELECIONAR e complementar)
        todas_dezenas = list(range(1, 32))
        
        return jsonify({
            'sucesso': True,
            'dados': {
                'ciclo_info': {
                    'numero': ciclo['numero_ciclo'],
                    'concursos': ciclo['quantidade_concursos'],
                    'percentual': ciclo['percentual_completo']
                },
                'grid1_pendentes': dezenas_pendentes,
                'grid2_todas': todas_dezenas,
                'total_pendentes': len(dezenas_pendentes)
            }
        })
    
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

# ========================================================================
# ABA 4 - GERADOR DE APOSTAS POR CICLO
# ========================================================================

@analise_ciclos_dezenas_bp.route('/analise-ciclos-dezenas/gerador')
def gerador_apostas_ciclo():
    """Página do Gerador de Apostas por Ciclo"""
    estatisticas = AnaliseCiclosDezenasService.obter_estatisticas_comportamento()
    
    # Processamento para a feature UI "Mês da Sorte"
    estatisticas_meses = AnaliseMesesService.obter_estatisticas_meses()
    meses_lista = estatisticas_meses['meses']
    
    if meses_lista:
        mais_frequente = max(meses_lista, key=lambda x: x['frequencia'])
        mais_atrasado = max(meses_lista, key=lambda x: x['atraso'])
    else:
        mais_frequente = None
        mais_atrasado = None
        
    return render_template('analise_ciclos_dezenas/gerador_apostas.html', 
                           active_tab='gerador', 
                           estatisticas=estatisticas,
                           meses_lista=meses_lista,
                           mes_frequente=mais_frequente,
                           mes_atrasado=mais_atrasado)

@analise_ciclos_dezenas_bp.route('/api/ciclos-dezenas/gerar-apostas', methods=['POST'])
def api_gerar_apostas():
    """API: Gera apostas respeitando o ciclo atual"""
    try:
        dados = request.get_json()
        
        # Parâmetros
        quantidade_apostas = dados.get('quantidade_apostas', 5)
        dezenas_por_aposta = dados.get('dezenas_por_aposta', 7)
        estrategia_evolucao = dados.get('estrategia_evolucao', 'padrao')
        usar_pendentes_fixas = dados.get('usar_pendentes_fixas', False)
        dezenas_selecionadas = dados.get('dezenas_selecionadas', [])
        modo_inteligente = dados.get('modo_inteligente')
        analise_previa = dados.get('analise')

        # Obter ciclo atual
        ciclo = AnaliseCiclosDezenasService.obter_ciclo_atual()
        
        if not ciclo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum ciclo atual encontrado.'
            }), 404

        # Gerador inteligente contextual (após análise do ciclo)
        if modo_inteligente:
            mes_ref = dados.get('mes_sorte') or dados.get('mes')
            analise = analise_previa or CicloInteligenciaService.analisar_ciclo_completo(mes_ref)
            apostas, meta = CicloInteligenciaService.gerar_apostas_inteligentes(
                quantidade_apostas=quantidade_apostas,
                dezenas_por_aposta=dezenas_por_aposta,
                modo=modo_inteligente,
                dezenas_fixas=dezenas_selecionadas or None,
                analise=analise,
                mes_ref=mes_ref,
            )
            if not apostas:
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Não foi possível gerar apostas com o modo inteligente selecionado.',
                }), 400
            return jsonify({
                'sucesso': True,
                'dados': {
                    'apostas': apostas,
                    'total_gerado': len(apostas),
                    'ciclo_usado': ciclo['numero_ciclo'],
                    'pendentes_usadas': dezenas_selecionadas or [],
                    'modo_inteligente': modo_inteligente,
                    'analise': meta,
                },
            })
        
        # Definir pool de dezenas
        # Se houver dezenas selecionadas, elas são SEMPRE fixas (independente da flag)
        if dezenas_selecionadas:
            dezenas_fixas = dezenas_selecionadas
            # Pool de complemento: dezenas pendentes + outras disponíveis
            todas_dezenas = set(range(1, 32))
            pool_complemento = list(todas_dezenas - set(dezenas_fixas))
            pool_complemento = sorted(pool_complemento)
        else:
            # Sem seleção: usar pool de pendentes
            dezenas_fixas = []
            pool_complemento = ciclo['dezenas_pendentes']
        
        # Lógica de Geração Customizada vs Padrão
        estrategias_ranges = {
            'nula': [0],
            'baixa': [1, 2],
            'media': [3, 4],
            'alta': [5, 6, 7]
        }
        
        apostas = []
        apostas_unicas = set()
        
        if estrategia_evolucao in estrategias_ranges:
            novas_possiveis = estrategias_ranges[estrategia_evolucao]
            
            # Análise das fixas fornecidas nas duas perspectivas de ciclo
            fixas_pendentes = [d for d in dezenas_fixas if d in ciclo['dezenas_pendentes']]
            fixas_saidas = [d for d in dezenas_fixas if d in ciclo['dezenas_saidas']]
            
            tentativas_gerais = 0
            max_tentativas_gerais = quantidade_apostas * 100
            
            while len(apostas_unicas) < quantidade_apostas and tentativas_gerais < max_tentativas_gerais:
                tentativas_gerais += 1
                
                # Valida alvo
                valid_novas = [n for n in novas_possiveis if n <= dezenas_por_aposta]
                if not valid_novas:
                    break
                    
                target_novas = random.choice(valid_novas)
                target_repetidas = dezenas_por_aposta - target_novas
                
                # Validação de capacidade
                if len(fixas_pendentes) > target_novas or len(fixas_saidas) > target_repetidas:
                    continue 
                
                pool_pendentes_disp = [d for d in ciclo['dezenas_pendentes'] if d not in dezenas_fixas]
                pool_saidas_disp = [d for d in ciclo['dezenas_saidas'] if d not in dezenas_fixas]
                
                faltam_pendentes = target_novas - len(fixas_pendentes)
                faltam_saidas = target_repetidas - len(fixas_saidas)
                
                if len(pool_pendentes_disp) < faltam_pendentes or len(pool_saidas_disp) < faltam_saidas:
                    continue
                
                escolha_pendentes = random.sample(pool_pendentes_disp, faltam_pendentes)
                escolha_saidas = random.sample(pool_saidas_disp, faltam_saidas)
                
                nova_aposta = dezenas_fixas.copy() + escolha_pendentes + escolha_saidas
                apostas_unicas.add(tuple(sorted(nova_aposta)))
                
            apostas = [list(a) for a in apostas_unicas]
            
            if not apostas:
                return jsonify({
                    'sucesso': False,
                    'mensagem': f'Não foi possível gerar apostas para a estratégia de Evolução escolhida. Conflito matemático com dezenas fixas ou limite atingido.'
                }), 400
                
        else:
            # Estratégia PADRÃO: foca unicamente em usar as pendentes caso não haja pinagem contrária
            faltam = dezenas_por_aposta - len(dezenas_fixas)
            
            if faltam < 0:
                return jsonify({
                    'sucesso': False,
                    'mensagem': f'Você selecionou {len(dezenas_fixas)} dezenas fixas, mas o limite é {dezenas_por_aposta}.'
                }), 400
                
            if faltam == 0:
                apostas.append(sorted(dezenas_fixas))
            else:
                disponiveis = [d for d in pool_complemento if d not in dezenas_fixas]
                import math
                
                if len(disponiveis) < faltam:
                    return jsonify({
                        'sucesso': False,
                        'mensagem': f'Não há dezenas suficientes ({len(disponiveis)}) para sortear as {faltam} que faltam.'
                    }), 400
                    
                max_comb = math.comb(len(disponiveis), faltam)
                qtd_desejada = min(quantidade_apostas, max_comb)
                
                tentativas = 0
                max_tentativas = qtd_desejada * 20
                
                while len(apostas_unicas) < qtd_desejada and tentativas < max_tentativas:
                    aposta = dezenas_fixas.copy()
                    complemento = random.sample(disponiveis, faltam)
                    aposta.extend(complemento)
                    
                    aposta_tuple = tuple(sorted(aposta))
                    apostas_unicas.add(aposta_tuple)
                    tentativas += 1
                    
                apostas = [list(a) for a in apostas_unicas]
        
        return jsonify({
            'sucesso': True,
            'dados': {
                'apostas': apostas,
                'total_gerado': len(apostas),
                'ciclo_usado': ciclo['numero_ciclo'],
                'pendentes_usadas': dezenas_fixas
            }
        })
    
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

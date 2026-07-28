from flask import Blueprint, jsonify, render_template

# Criar blueprint unificado para Resumo das Apostas
resumo_apostas_bp = Blueprint('resumo_apostas', __name__)

@resumo_apostas_bp.route('/central-conferencias/resumo-apostas')
def pagina_resumo_apostas():
    """Página isolada para Resumo das Apostas Automático"""
    return render_template('resumo_apostas.html')

@resumo_apostas_bp.route('/api/resumo-apostas/todos-processados', methods=['GET'])
def get_resumo_todos_processados():
    """
    Detecta automaticamente TODOS os concursos em /conferencia_apostas,
    processa os resultados matematicamente e consolida os ganhos, perdas
    e melhores acertos de TODOS os concursos disponíveis.
    """
    try:
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
        
        concursos = ConferenciaApostasOCRService.listar_concursos_disponiveis()
        
        if not concursos:
            return jsonify({
                'sucesso': False, 
                'mensagem': 'Nenhuma pasta ou arquivo de aposta encontrado.'
            }), 404
            
        total_concursos_analisados = 0
        total_jogos_gerais = 0
        total_jogos_premiados = 0
        total_investido_geral = 0.0
        total_ganho_geral = 0.0
        melhor_acerto_global = 0
        teve_mes_sorte_global = False
        concursos_detalhados = []
        jogos_4_acertos_global = []

        # Iterar sobre todos os concursos disponíveis
        for item in concursos:
            num_concurso = item['numero_concurso']
            
            # Processar resultado individual do concurso
            res = ConferenciaApostasOCRService.processar_concurso(num_concurso)
            
            if res.get('sucesso'):
                total_concursos_analisados += 1
                
                # Resumo do concurso
                resumo = res.get('resumo', {})
                jogos_processados = resumo.get('apostas_processadas', 0)
                jogos_premiados = resumo.get('apostas_premiadas', 0)
                investido = float(resumo.get('total_investido', 0.0))
                ganho = float(resumo.get('total_ganho', 0.0))
                lucro = float(resumo.get('lucro', 0.0))
                
                # Identificar melhor acerto deste concurso e seu detalhamento
                melhor_acerto_concurso = 0
                teve_mes_concurso = False
                jogo_destaque = None
                
                for ap in res.get('apostas', []):
                    if not ap.get('erro'):
                        acertos = ap['resultado']['acertos']
                        mes = ap['resultado']['acertou_mes']
                        
                        # Coletar jogos vencedores (4 ou mais acertos) para a Inteligência Avançada
                        if acertos >= 4:
                            jogos_4_acertos_global.append({
                                'concurso': num_concurso,
                                'numeros_apostados': ap.get('dados_extraidos', {}).get('numeros_apostados', []),
                                'numeros_acertados': ap.get('resultado', {}).get('numeros_acertados', []),
                                'numeros_sorteados': res.get('resultado_sorteio', {}).get('numeros', [])
                            })

                        if acertos > melhor_acerto_concurso or (acertos == melhor_acerto_concurso and mes and not teve_mes_concurso):
                            melhor_acerto_concurso = acertos
                            teve_mes_concurso = mes
                            jogo_destaque = {
                                'numeros_apostados': ap.get('dados_extraidos', {}).get('numeros_apostados', []),
                                'numeros_acertados': ap.get('resultado', {}).get('numeros_acertados', []),
                                'mes_apostado': ap.get('dados_extraidos', {}).get('mes_apostado'),
                                'acertou_mes': mes,
                                'premio': float(ap.get('resultado', {}).get('valor_premio', 0.0))
                            }
                            
                        # Atualizar melhor acerto global
                        if acertos > melhor_acerto_global or (acertos == melhor_acerto_global and mes and not teve_mes_sorte_global):
                            melhor_acerto_global = acertos
                            teve_mes_sorte_global = mes

                total_jogos_gerais += jogos_processados
                total_jogos_premiados += jogos_premiados
                total_investido_geral += investido
                total_ganho_geral += ganho
                
                concursos_detalhados.append({
                    'concurso': num_concurso,
                    'data': res.get('resultado_sorteio', {}).get('data', '--'),
                    'numeros_sorteados': res.get('resultado_sorteio', {}).get('numeros', []),
                    'mes_sorteado': res.get('resultado_sorteio', {}).get('mes_sorte'),
                    'jogos_processados': jogos_processados,
                    'jogos_premiados': jogos_premiados,
                    'investido': investido,
                    'ganho': ganho,
                    'lucro': lucro,
                    'melhor_acerto': melhor_acerto_concurso,
                    'teve_mes': teve_mes_concurso,
                    'jogo_destaque': jogo_destaque
                })
        
        # Calcular lucro global e final
        lucro_global = total_ganho_geral - total_investido_geral
        
        # Ordenar detalhados do concurso mais recente pro mais antigo
        concursos_detalhados.sort(key=lambda x: x['concurso'], reverse=True)
        
        # --- PROCESSAR INTELIGÊNCIA DOS 4 ACERTOS ---
        freq_acertos = {}
        freq_erros = {}
        freq_faltantes = {}
        
        for j in jogos_4_acertos_global:
            apostados = set(j['numeros_apostados'])
            acertados = set(j['numeros_acertados'])
            sorteados = set(j['numeros_sorteados'])
            errados = apostados - acertados
            faltantes = sorteados - acertados
            
            for n in acertados: freq_acertos[n] = freq_acertos.get(n, 0) + 1
            for n in errados: freq_erros[n] = freq_erros.get(n, 0) + 1
            for n in faltantes: freq_faltantes[n] = freq_faltantes.get(n, 0) + 1
            
        nucleo_forte = sorted(freq_acertos.keys(), key=lambda x: freq_acertos[x], reverse=True)[:4]
        zona_erro = sorted(freq_erros.keys(), key=lambda x: freq_erros[x], reverse=True)[:5]
        # Números para completar que mais faltaram nas apostas de 4 acertos
        candidatos_faltantes = sorted(freq_faltantes.keys(), key=lambda x: freq_faltantes[x], reverse=True)
        
        # Calcular distribuição das faixas faltantes (Baixas, Médias, Altas)
        total_faltantes_ocorrencias = sum(freq_faltantes.values()) if freq_faltantes else 1
        baixas = sum(v for k, v in freq_faltantes.items() if 1 <= k <= 10)
        medias = sum(v for k, v in freq_faltantes.items() if 11 <= k <= 20)
        altas =  sum(v for k, v in freq_faltantes.items() if 21 <= k <= 31)
        
        distribuicao_faltantes = {
            'baixas': round((baixas / total_faltantes_ocorrencias) * 100),
            'medias': round((medias / total_faltantes_ocorrencias) * 100),
            'altas': round((altas / total_faltantes_ocorrencias) * 100)
        }
        
        # Se não houver dados suficientes, usar padrão seguro (apenas para não quebrar a lógica)
        if len(nucleo_forte) < 4:
            nucleo_forte = nucleo_forte + [n for n in range(1, 32) if n not in nucleo_forte][:4 - len(nucleo_forte)]
        if not candidatos_faltantes:
            candidatos_faltantes = [n for n in range(1, 32) if n not in nucleo_forte]
            
        # Gerar 4 Jogos Sugeridos
        jogos_sugeridos = []
        import random
        # Fixar a seed apenas para manter a consistência baseado no histórico, ou deixar dinâmico se preferir,
        # Mas para parecer "processado", se o núcleo não mudar, os jogos devem ter uma certa lógica.
        candidatos_seguros = [n for n in candidatos_faltantes if n not in zona_erro and n not in nucleo_forte]
        if len(candidatos_seguros) < 15:
            # Completa com outros não banidos pra ter opções
            candidatos_seguros += [n for n in range(1, 32) if n not in zona_erro and n not in nucleo_forte and n not in candidatos_seguros]
            
        for i in range(4):
            jogo = list(nucleo_forte)
            altas_permitidas = 2 if random.random() > 0.5 else 1
            altas_atual = sum(1 for x in jogo if x > 25)
            
            # Escolher 3 variáveis
            vars_escolhidas = set()
            tentativas = 0
            # Preferência para faltantes do topo, com uma pequena aleatoriedade pros blocos diferentes
            pool_selecionado = candidatos_seguros[:10]
            random.shuffle(pool_selecionado)
            
            for var in pool_selecionado:
                if len(vars_escolhidas) == 3: break
                if var > 25:
                    if altas_atual < altas_permitidas:
                        vars_escolhidas.add(var)
                        altas_atual += 1
                else:
                    vars_escolhidas.add(var)
            
            # Se ainda faltar, force completion ignora regra limite só pra não dar erro
            restantes_force = [n for n in candidatos_seguros if n not in vars_escolhidas]
            for r in restantes_force:
                if len(vars_escolhidas) == 3: break
                vars_escolhidas.add(r)
                
            jogo.extend(list(vars_escolhidas))
            jogo.sort()
            jogos_sugeridos.append(jogo)
        
        freq_meses = {}
        for c in concursos_detalhados:
            m = c.get('mes_sorteado')
            if m:
                try:
                    m_int = int(m)
                    freq_meses[m_int] = freq_meses.get(m_int, 0) + 1
                except:
                    pass
        melhor_mes = 1
        if freq_meses:
            melhor_mes = sorted(freq_meses.keys(), key=lambda x: freq_meses[x], reverse=True)[0]
        
        analise_inteligente = {
            'total_jogos_4_acertos': len(jogos_4_acertos_global),
            'nucleo_forte': nucleo_forte,
            'zona_erro': zona_erro,
            'top_faltantes': candidatos_faltantes[:5],
            'distribuicao_faltantes': distribuicao_faltantes,
            'jogos_sugeridos': jogos_sugeridos,
            'melhor_mes_sugerido': melhor_mes
        }
            
        return jsonify({
            'sucesso': True,
            'total_concursos_analisados': total_concursos_analisados,
            'total_jogos_gerais': total_jogos_gerais,
            'total_jogos_premiados': total_jogos_premiados,
            'total_investido_geral': total_investido_geral,
            'total_ganho_geral': total_ganho_geral,
            'lucro_global': lucro_global,
            'melhor_acerto_global': melhor_acerto_global,
            'teve_mes_sorte_global': teve_mes_sorte_global,
            'concursos_detalhados': concursos_detalhados,
            'analise_inteligente': analise_inteligente
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'sucesso': False, 
            'erro': str(e),
            'mensagem': 'Erro interno ao processar o resumo automático.'
        }), 500

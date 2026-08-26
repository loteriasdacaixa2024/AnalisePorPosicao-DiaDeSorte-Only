"""
Routes para Central de Conferências - Dia de Sorte
Unifica conferência via OCR e conferência pós-apostas em um único serviço
"""

from flask import Blueprint, request, jsonify, render_template
import os
import time

# Criar blueprint unificado
central_conferencias_bp = Blueprint('central_conferencias', __name__)

# ============================================
# CONFIGURAÇÃO DE CAMINHOS (Fácil de alterar)
# ============================================
# Se precisar mudar a pasta ou o drive, altere aqui:
CAMINHO_BASE_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_FILTROS_BAIXADOS = os.path.join(CAMINHO_BASE_PROJETO, 'conferencia_filtros-baixados')


# ============================================
# ROTA PRINCIPAL - PÁGINA CENTRAL
# ============================================

@central_conferencias_bp.route('/central-conferencias')
def pagina_central_conferencias():
    """Página principal da Central de Conferências (4 abas)"""
    return render_template('central_conferencias.html')


# ============================================
# ROTAS DE CONFERÊNCIA VIA OCR (Abas 1-3)
# ============================================

@central_conferencias_bp.route('/api/conferencia-ocr/concursos-disponiveis', methods=['GET'])
def listar_concursos_disponiveis_ocr():
    """Lista todos os concursos disponíveis na pasta mnt/conferencia_apostas/"""
    try:
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
        concursos = ConferenciaApostasOCRService.listar_concursos_disponiveis()

        return jsonify({
            'sucesso': True,
            'total': len(concursos),
            'concursos': concursos
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao listar concursos: {str(e)}'
        }), 500


@central_conferencias_bp.route('/api/conferencia-ocr/processar-concurso/<int:concurso>', methods=['POST'])
def processar_concurso_ocr(concurso):
    print(f"[DEBUG] ROTA ACIONADA (ASYNC): /api/conferencia-ocr/processar-concurso/{concurso}")
    """Processa todos os screenshots de um concurso específico em background"""
    try:
        import uuid
        import threading
        from flask import current_app
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService

        task_id = str(uuid.uuid4())
        app = current_app._get_current_object()

        def run_in_background(app_context, num_concurso, t_id):
            with app_context.app_context():
                try:
                    ConferenciaApostasOCRService.processar_concurso(num_concurso, task_id=t_id)
                except Exception as e:
                    print(f"Erro no processamento background: {e}")
                    ConferenciaApostasOCRService.atualizar_progresso(t_id, 'erro', 100, resultado={'sucesso': False, 'mensagem': str(e)})

        thread = threading.Thread(target=run_in_background, args=(app, concurso, task_id), daemon=True)
        thread.start()

        return jsonify({
            'sucesso': True,
            'task_id': task_id,
            'mensagem': 'Processamento em Background Iniciado'
        }), 202

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao iniciar processamento do concurso {concurso}: {str(e)}'
        }), 500

@central_conferencias_bp.route('/api/conferencia-ocr/status/<task_id>', methods=['GET'])
def status_concurso_ocr(task_id):
    """Consulta o status de um processamento OCR em background"""
    from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
    progresso = ConferenciaApostasOCRService.obter_progresso(task_id)
    return jsonify(progresso)

@central_conferencias_bp.route('/api/conferencia-ocr/ranking-global', methods=['POST'])
def iniciar_ranking_global():
    """Inicia o cálculo do ranking global de ABS em background"""
    try:
        import uuid
        import threading
        from flask import current_app
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
        
        task_id = str(uuid.uuid4())
        app = current_app._get_current_object()
        
        # Inicializa a task
        ConferenciaApostasOCRService.atualizar_progresso(task_id, 'iniciando', 0)
        
        def run_in_background(app_context, t_id):
            with app_context.app_context():
                ConferenciaApostasOCRService.processar_ranking_global_background(t_id)
                
        # Inicia a thread
        thread = threading.Thread(
            target=run_in_background,
            args=(app, task_id),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'sucesso': True,
            'task_id': task_id,
            'mensagem': 'Processamento do ranking iniciado em background'
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao iniciar ranking: {str(e)}'
        }), 500


@central_conferencias_bp.route('/api/conferencia-ocr/resumo-abs-historico', methods=['GET'])
def resumo_abs_historico():
    """Resumo ABS de todas as apostas JSON na pasta (histórico entre concursos)."""
    try:
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService

        max_abs = request.args.get('max_abs', 20, type=int)
        excluir_concurso = request.args.get('excluir_concurso', type=int)
        resultado = ConferenciaApostasOCRService.resumo_abs_historico_pasta(
            max_abs=max_abs,
            excluir_concurso=excluir_concurso,
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao montar resumo histórico ABS: {str(e)}'
        }), 500


@central_conferencias_bp.route('/api/conferencia-ocr/historico-aposta', methods=['POST'])
def historico_aposta_ocr():
    """Retorna os concursos em que esta aposta (combinação de números) obteve grandes acertos"""
    try:
        dados = request.get_json(force=True, silent=True) or {}
        apostas = dados.get('numeros', [])
        if not apostas:
            return jsonify({'sucesso': False, 'erro': 'Sem numeros'}), 400
            
        from models.sorteio import Sorteio
        from models import db
        todos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        
        acertos_historico = []
        numeros_set = set(apostas)
        
        for s in todos:
            sorteados = {s.posicao_1, s.posicao_2, s.posicao_3, s.posicao_4, s.posicao_5, s.posicao_6, s.posicao_7}
            acertos = len(numeros_set.intersection(sorteados))
            if acertos >= 5: # Vamos mostrar acertos a partir de 5 para ser mais rico
                acertos_historico.append({
                    'concurso': s.concurso,
                    'acertos': acertos,
                    'data': s.data_sorteio.strftime('%d/%m/%Y') if s.data_sorteio else '--/--/----',
                    'sorteados': list(sorteados)
                })
                
        return jsonify({
            'sucesso': True,
            'historico': sorted(acertos_historico, key=lambda x: x['acertos'], reverse=True)
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/salvar-backtest', methods=['POST'])
def salvar_backtest():
    """Salva um backtest global no Hall da Fama (SQLite)"""
    try:
        from models.historico_backtests import HistoricoBacktest
        from models.shared import db
        dados = request.get_json()
        
        if not dados or 'nome_lote' not in dados:
            return jsonify({'sucesso': False, 'erro': 'Nome do lote não fornecido'}), 400
            
        novo_backtest = HistoricoBacktest(
            nome_lote=dados['nome_lote'],
            total_jogos=dados.get('total_jogos', 0),
            acertos_7=dados.get('acertos_7', 0),
            acertos_6=dados.get('acertos_6', 0),
            acertos_5=dados.get('acertos_5', 0),
            acertos_4=dados.get('acertos_4', 0),
            concurso_alvo=dados.get('concurso_alvo', 'Global'),
            melhor_concurso_id=dados.get('melhor_concurso_id')
        )
        
        db.session.add(novo_backtest)
        db.session.commit()
        
        return jsonify({'sucesso': True, 'msg': 'Estratégia salva com sucesso!'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@central_conferencias_bp.route('/api/conferencia/listar-backtests', methods=['GET'])
def listar_backtests():
    """Lista todos os backtests globais do Hall da Fama"""
    try:
        from models.historico_backtests import HistoricoBacktest
        testes = HistoricoBacktest.query.order_by(HistoricoBacktest.id.desc()).all()
        return jsonify({
            'sucesso': True, 
            'backtests': [t.to_dict() for t in testes]
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

def processar_multiplos_concursos_ocr():
    """Processa múltiplos concursos de uma vez"""
    try:
        dados = request.get_json()

        if not dados or 'concursos' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'dados_invalidos',
                'mensagem': 'É necessário fornecer uma lista de concursos'
            }), 400

        concursos = dados['concursos']

        if not isinstance(concursos, list) or len(concursos) == 0:
            return jsonify({
                'sucesso': False,
                'erro': 'lista_vazia',
                'mensagem': 'A lista de concursos está vazia'
            }), 400

        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
        resultado = ConferenciaApostasOCRService.processar_multiplos_concursos(concursos)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao processar concursos: {str(e)}'
        }), 500


@central_conferencias_bp.route('/api/conferencia-ocr/testar-ocr', methods=['POST'])
def testar_ocr():
    """Testa o OCR em um screenshot específico"""
    try:
        dados = request.get_json()

        if not dados or 'concurso' not in dados or 'arquivo' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'dados_invalidos',
                'mensagem': 'É necessário fornecer concurso e arquivo'
            }), 400

        import os
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService

        caminho = os.path.join(
            ConferenciaApostasOCRService.BASE_DIR,
            str(dados['concurso']),
            dados['arquivo']
        )

        if not os.path.exists(caminho):
            return jsonify({
                'sucesso': False,
                'erro': 'arquivo_nao_encontrado',
                'mensagem': f'Arquivo não encontrado: {caminho}'
            }), 404

        resultado = ConferenciaApostasOCRService.processar_screenshot_ocr(caminho)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao testar OCR: {str(e)}'
        }), 500


@central_conferencias_bp.route('/api/conferencia-ocr/validar-dados', methods=['POST'])
def validar_dados_extraidos_ocr():
    """Valida e permite correção manual dos dados extraídos via OCR"""
    try:
        dados = request.get_json()

        # Validar campos obrigatórios
        campos_obrigatorios = ['concurso', 'numeros_apostados', 'mes_apostado']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({
                    'sucesso': False,
                    'erro': 'campo_faltando',
                    'mensagem': f'Campo obrigatório ausente: {campo}'
                }), 400

        # Validar números (7 a 15 dezenas permitidas)
        numeros = dados['numeros_apostados']
        if len(numeros) < 7 or len(numeros) > 15:
            return jsonify({
                'sucesso': False,
                'erro': 'quantidade_numeros',
                'mensagem': f'Deve ter entre 7 e 15 números (fornecido: {len(numeros)})'
            }), 400

        if any(n < 1 or n > 31 for n in numeros):
            return jsonify({
                'sucesso': False,
                'erro': 'numeros_invalidos',
                'mensagem': 'Números devem estar entre 1 e 31'
            }), 400

        if len(set(numeros)) != len(numeros):
            return jsonify({
                'sucesso': False,
                'erro': 'numeros_duplicados',
                'mensagem': 'Números não podem se repetir'
            }), 400

        # Validar mês
        mes = dados['mes_apostado']
        if mes < 1 or mes > 12:
            return jsonify({
                'sucesso': False,
                'erro': 'mes_invalido',
                'mensagem': 'Mês deve estar entre 1 e 12'
            }), 400

        # Buscar concurso no banco e comparar
        from models.sorteio import Sorteio
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService

        sorteio = Sorteio.query.filter_by(concurso=dados['concurso']).first()

        if not sorteio:
            return jsonify({
                'sucesso': False,
                'erro': 'concurso_nao_encontrado',
                'mensagem': f'Concurso {dados["concurso"]} não encontrado no banco'
            }), 404

        # Comparar com resultado oficial
        resultado = ConferenciaApostasOCRService.comparar_aposta_com_resultado(
            numeros,
            mes,
            sorteio
        )

        return jsonify({
            'sucesso': True,
            'valido': True,
            'resultado': resultado
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao validar dados: {str(e)}'
        }), 500


@central_conferencias_bp.route('/api/conferencia-ocr/exportar-relatorio/<int:concurso>', methods=['GET'])
def exportar_relatorio_ocr(concurso):
    """Exporta relatório de um concurso em formato JSON/CSV"""
    try:
        formato = request.args.get('formato', 'json')

        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
        resultado = ConferenciaApostasOCRService.processar_concurso(concurso)

        if not resultado['sucesso']:
            return jsonify(resultado), 400

        if formato == 'csv':
            import io
            import csv
            from flask import send_file

            output = io.StringIO()
            writer = csv.writer(output)

            # Cabeçalho
            writer.writerow([
                'Aposta', 'Arquivo', 'Números Apostados', 'Mês Apostado',
                'Acertos', 'Acertou Mês', 'Faixa', 'Valor Ganho'
            ])

            # Dados
            for aposta in resultado['apostas']:
                if not aposta.get('erro_ocr') and not aposta.get('dados_incompletos'):
                    writer.writerow([
                        aposta['numero_aposta'],
                        aposta['arquivo'],
                        ' '.join(map(str, aposta['dados_extraidos']['numeros_apostados'])),
                        aposta['dados_extraidos']['mes_apostado'],
                        aposta['resultado']['acertos'],
                        'Sim' if aposta['resultado']['acertou_mes'] else 'Não',
                        aposta['resultado']['faixa'] or 'Sem prêmio',
                        f"R$ {aposta['valor_ganho']:.2f}"
                    ])

            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'concurso_{concurso}_relatorio.csv'
            )

        else:
            return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao exportar relatório: {str(e)}'
        }), 500


@central_conferencias_bp.route('/central-conferencias/api/metricas-estrategicas', methods=['GET'])
def obter_metricas_estrategicas():
    print("[DEBUG] Rota de metricas estrategicas ACIONADA!")
    """Retorna dados históricos para o dashboard estratégico"""
    try:
        from models.metricas_conferencia_ocr import MetricasConferenciaOCR
        
        # Buscar todas as métricas ordenadas por concurso
        metricas = MetricasConferenciaOCR.query.order_by(MetricasConferenciaOCR.concurso.asc()).all()
        
        return jsonify({
            'sucesso': True,
            'dados': [m.to_dict() for m in metricas]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao buscar métricas estratégicas: {str(e)}'
        }), 500


# ============================================
# Integração Automática Filtrador -> Conferidor
# ============================================

@central_conferencias_bp.route('/api/conferencia/filtros-baixados', methods=['GET'])
def listar_filtros_baixados():
    """Lista todos os .txt disponíveis na pasta definida em PASTA_FILTROS_BAIXADOS"""
    try:
        if not os.path.exists(PASTA_FILTROS_BAIXADOS):
            os.makedirs(PASTA_FILTROS_BAIXADOS, exist_ok=True)
            return jsonify({'sucesso': True, 'arquivos': []})
            
        arquivos = []
        for file in os.listdir(PASTA_FILTROS_BAIXADOS):
            if file.lower().endswith('.txt'):
                info = os.stat(os.path.join(PASTA_FILTROS_BAIXADOS, file))
                arquivos.append({
                    'nome': file,
                    'tamanho': info.st_size,
                    'data_criacao': info.st_mtime
                })
                
        # Ordenar os mais recentes primeiro
        arquivos = sorted(arquivos, key=lambda x: x['data_criacao'], reverse=True)
        return jsonify({'sucesso': True, 'arquivos': arquivos})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@central_conferencias_bp.route('/api/conferencia/ler-filtro-baixado', methods=['POST'])
def ler_filtro_baixado():
    """Lê o conteúdo de um TXT salvo localmente pelo Filtrador"""
    import os
    try:
        dados = request.get_json()
        if not dados or 'nome_arquivo' not in dados:
            return jsonify({'sucesso': False, 'erro': 'Nome do arquivo não fornecido'}), 400
            
        caminho_absoluto = os.path.join(PASTA_FILTROS_BAIXADOS, dados['nome_arquivo'])
        
        # Validar se tentou escape de path para segurança
        if not os.path.isfile(caminho_absoluto) or not os.path.commonpath([os.path.abspath(caminho_absoluto), os.path.abspath(PASTA_FILTROS_BAIXADOS)]) == os.path.abspath(PASTA_FILTROS_BAIXADOS):
            return jsonify({'sucesso': False, 'erro': 'Arquivo não localizado'}), 404
            
        with open(caminho_absoluto, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        return jsonify({'sucesso': True, 'conteudo': conteudo})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@central_conferencias_bp.route('/api/conferencia/limpar-pasta-espelho', methods=['POST'])
def limpar_pasta_espelho():
    """Remove todos os arquivos .txt da pasta definida em PASTA_FILTROS_BAIXADOS"""
    try:
        if not os.path.exists(PASTA_FILTROS_BAIXADOS):
            return jsonify({'sucesso': True, 'msg': 'Pasta não existe'})
            
        removidos = 0
        for file in os.listdir(PASTA_FILTROS_BAIXADOS):
            if file.lower().endswith('.txt'):
                os.remove(os.path.join(PASTA_FILTROS_BAIXADOS, file))
                removidos += 1
                
        return jsonify({'sucesso': True, 'total_removidos': removidos})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ============================================
# ROTAS DE CONFERÊNCIA PÓS-APOSTAS (Aba 4)
# ============================================

@central_conferencias_bp.route('/api/conferencia/colunas', methods=['GET'])
def listar_colunas():
    """Lista colunas adicionais"""
    try:
        from services.conferencia_apostas_service import ConferenciaApostasService
        colunas = ConferenciaApostasService.listar_colunas_adicionais()
        return jsonify(colunas), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/colunas', methods=['POST'])
def adicionar_coluna():
    """Adiciona nova coluna adicional"""
    try:
        dados = request.get_json()

        if not dados or 'nome' not in dados:
            return jsonify({'erro': 'Campo "nome" é obrigatório'}), 400

        from services.conferencia_apostas_service import ConferenciaApostasService
        nova_coluna = ConferenciaApostasService.adicionar_coluna(
            dados['nome'],
            dados.get('tipo', 'text'),
            dados.get('descricao', '')
        )

        return jsonify(nova_coluna), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/colunas/<coluna_id>', methods=['DELETE'])
def remover_coluna(coluna_id):
    """Remove coluna adicional"""
    try:
        from services.conferencia_apostas_service import ConferenciaApostasService
        resultado = ConferenciaApostasService.remover_coluna(coluna_id)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/normalizar', methods=['POST'])
def normalizar_jogo():
    """Normaliza entrada de jogo com vários formatos"""
    try:
        dados = request.get_json()

        if not dados or 'texto' not in dados:
            return jsonify({'erro': 'Campo "texto" é obrigatório'}), 400

        from services.conferencia_apostas_service import ConferenciaApostasService
        resultado = ConferenciaApostasService.normalizar_combinacao(dados['texto'])

        if not resultado:
            return jsonify({'erro': 'Formato inválido'}), 400

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/validar-jogo', methods=['POST'])
def validar_jogo():
    """Valida um jogo"""
    try:
        dados = request.get_json()

        if not dados or 'numeros' not in dados:
            return jsonify({'erro': 'Campo "numeros" é obrigatório'}), 400

        from services.conferencia_apostas_service import ConferenciaApostasService
        resultado = ConferenciaApostasService.validar_jogo(
            dados['numeros'],
            dados.get('mes')
        )
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/analisar-jogo', methods=['POST'])
def analisar_jogo():
    """Analisa características de um jogo"""
    try:
        dados = request.get_json()

        if not dados or 'numeros' not in dados:
            return jsonify({'erro': 'Campo "numeros" é obrigatório'}), 400

        from services.conferencia_apostas_service import ConferenciaApostasService

        validacao = ConferenciaApostasService.validar_jogo(
            dados['numeros'],
            dados.get('mes')
        )
        if not validacao['valido']:
            return jsonify(validacao), 400

        analise = ConferenciaApostasService.analisar_jogo(
            dados['numeros'],
            dados.get('mes'),
            dados.get('concurso_numero')
        )
        return jsonify(analise), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/conferir', methods=['POST'])
def conferir_jogos():
    """
    Confere jogos com resultado de um concurso

    POST /api/conferencia/conferir
    Body: {
        jogos: [
            {numeros: [1,2,3,4,5,6,7], mes: 1},
            {numeros: [8,9,10,11,12,13,14], mes: 2},
            ...
        ],
        concurso: 1133,
        valor_aposta: 2.50
    }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        if 'jogos' not in dados or 'concurso' not in dados:
            return jsonify({'erro': 'Campos "jogos" e "concurso" são obrigatórios'}), 400

        jogos = dados['jogos']
        concurso = dados['concurso']
        valor_aposta = dados.get('valor_aposta', 2.50)

        from services.conferencia_apostas_service import ConferenciaApostasService

        for idx, jogo in enumerate(jogos):
            numeros = jogo.get('numeros', jogo) if isinstance(jogo, dict) else jogo
            mes = jogo.get('mes') if isinstance(jogo, dict) else None

            validacao = ConferenciaApostasService.validar_jogo(numeros, mes)
            if not validacao['valido']:
                return jsonify({
                    'erro': f"Jogo {idx + 1}: {validacao['erro']}"
                }), 400

        resultado = ConferenciaApostasService.conferir_multiplos_jogos(
            jogos,
            concurso,
            valor_aposta
        )

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/concursos', methods=['GET'])
def listar_concursos():
    """Lista concursos disponíveis para conferência (TODOS do primeiro ao último)"""
    try:
        from services.conferencia_apostas_service import ConferenciaApostasService
        concursos = ConferenciaApostasService.listar_concursos_disponiveis()
        return jsonify(concursos), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ============================================
# ROTAS DE CONFERÊNCIA HISTÓRICA (Aba 5)
# Processa apostas contra TODO o histórico
# ============================================

@central_conferencias_bp.route('/api/conferencia-historica/sessoes', methods=['GET'])
def listar_sessoes_historica():
    """Lista todas as sessões de conferência histórica"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 20, type=int)

        from services.conferencia_historica_service import ConferenciaHistoricaService
        resultado = ConferenciaHistoricaService.listar_sessoes(pagina, por_pagina)

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/sessoes', methods=['POST'])
def criar_sessao_historica():
    """
    Cria uma nova sessão e processa o arquivo de apostas

    Request (multipart/form-data):
        - arquivo: Arquivo TXT com apostas
        - descricao: Descrição opcional
        - estrategia: 'ordenada' ou 'sorteio'
        - filtro_min: Mínimo de acertos (4-7)
        - separar_sessoes: 'true' se quiser que múltiplos arquivos gerem sessões distintas
    """
    try:
        # Verificar se tem arquivo
        arquivos = request.files.getlist('arquivos[]')
        if not arquivos and 'arquivo' in request.files:
             arquivos = [request.files['arquivo']]
            
        if not arquivos:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400

        # Ler parâmetros
        descricao = request.form.get('descricao', '')
        estrategia = request.form.get('estrategia', 'ordenada')
        filtro_min = request.form.get('filtro_min', 4, type=int)
        separar_sessoes = request.form.get('separar_sessoes', 'false').lower() == 'true'

        # Validar estratégia
        if estrategia not in ['ordenada', 'sorteio']:
            estrategia = 'ordenada'

        # Validar filtro
        if filtro_min < 4 or filtro_min > 7:
            filtro_min = 4

        from services.conferencia_historica_service import ConferenciaHistoricaService
        from flask import current_app
        import threading
        app = current_app._get_current_object()

        if separar_sessoes and len(arquivos) > 1:
            # Modo Separado: Cada arquivo gera uma sessão
            sessoes_criadas = []
            tarefas_processamento = []

            for arq in arquivos:
                if not arq.filename: continue
                conteudo = arq.read().decode('utf-8', errors='ignore')
                
                # Definir a descrição baseada no nome se necessário
                desc = descricao
                
                sessao = ConferenciaHistoricaService.criar_sessao(
                    nome_arquivo=arq.filename,
                    descricao=desc,
                    estrategia=estrategia,
                    filtro_min=filtro_min
                )
                sessoes_criadas.append(sessao.id)
                tarefas_processamento.append((sessao.id, conteudo))

            if not sessoes_criadas:
                return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo válido selecionado'}), 400

            # Executa sequencialmente em uma única thread para evitar locks no SQLite
            def run_multiple_in_background(app_obj, tarefas):
                import time
                for s_id, cont_str in tarefas:
                    try:
                        # Cria um contexto NOVO para cada arquivo, limpando a session do SQLAlchemy
                        with app_obj.app_context():
                            ConferenciaHistoricaService.processar_arquivo(s_id, cont_str)
                    except Exception as e:
                        print(f"[ERRO CRÍTICO] Falha ao processar sessão múltipla {s_id}: {e}")
                    
                    # Pausa essencial de 2 segundos para o SQLite e o SO liberarem todos os locks do arquivo
                    time.sleep(2)

            thread = threading.Thread(target=run_multiple_in_background, args=(app, tarefas_processamento), daemon=True)
            thread.start()

            return jsonify({
                'sucesso': True, 
                'sessao_id': sessoes_criadas[0], # Retorna a primeira para o painel focar nela
                'sessoes_multiplas': sessoes_criadas,
                'mensagem': f'{len(sessoes_criadas)} sessões iniciadas sequencialmente em segundo plano.'
            }), 202

        else:
            # Modo Agrupado (Comportamento original)
            conteudo_total = ""
            nomes_arquivos = []
            for arq in arquivos:
                if arq.filename:
                    conteudo_total += arq.read().decode('utf-8', errors='ignore') + "\n"
                    nomes_arquivos.append(arq.filename)

            if not nomes_arquivos:
                return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo válido selecionado'}), 400

            nome_final = ", ".join(nomes_arquivos)
            if len(nome_final) > 100:
                nome_final = f"{len(nomes_arquivos)} arquivos múltiplos"

            sessao = ConferenciaHistoricaService.criar_sessao(
                nome_arquivo=nome_final,
                descricao=descricao,
                estrategia=estrategia,
                filtro_min=filtro_min
            )

            def run_in_background(app_obj, s_id, cont_str):
                try:
                    with app_obj.app_context():
                        ConferenciaHistoricaService.processar_arquivo(s_id, cont_str)
                except Exception as e:
                    print(f"[ERRO CRÍTICO] Falha ao processar sessão única {s_id}: {e}")

            thread = threading.Thread(target=run_in_background, args=(app, sessao.id, conteudo_total), daemon=True)
            thread.start()

            return jsonify({'sucesso': True, 'sessao_id': sessao.id, 'mensagem': 'Processamento iniciado em segundo plano.'}), 202

    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/sessoes/<int:sessao_id>', methods=['GET'])
def obter_sessao_historica(sessao_id):
    """Obtém detalhes de uma sessão específica"""
    try:
        from models.conferencia_historica import SessaoConferenciaHistorica

        sessao = SessaoConferenciaHistorica.query.get(sessao_id)
        if not sessao:
            return jsonify({'sucesso': False, 'erro': 'Sessão não encontrada'}), 404

        return jsonify({'sucesso': True, 'sessao': sessao.to_dict()}), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/sessoes/<int:sessao_id>', methods=['DELETE'])
def excluir_sessao_historica(sessao_id):
    """Exclui uma sessão e todos os dados relacionados"""
    try:
        from services.conferencia_historica_service import ConferenciaHistoricaService
        resultado = ConferenciaHistoricaService.excluir_sessao(sessao_id)

        return jsonify(resultado), 200 if resultado['sucesso'] else 400
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/sessoes/<int:sessao_id>/ranking', methods=['GET'])
def obter_ranking_historica(sessao_id):
    """
    Obtém ranking das apostas de uma sessão

    Query params:
        - pagina: Número da página (default: 1)
        - por_pagina: Itens por página (default: 50)
        - filtro_acertos: Filtrar por número mínimo de acertos (4, 5, 6 ou 7)
        - ordenacao: 'score', 'vitorias', '7_acertos', '6_acertos', '5_acertos', 'premios'
        - ord_dir: 'asc' ou 'desc' (default: 'desc')
        - Filtros dinamicos: f_vitorias, f_7_acertos, f_6_acertos, f_5_acertos, f_4_acertos, f_score, f_premios
    """
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        filtro_acertos = request.args.get('filtro_acertos', type=int)
        ordenacao = request.args.get('ordenacao', 'score')
        ord_dir = request.args.get('ord_dir', 'desc')

        filtros_dinamicos = {
            'vitorias': request.args.get('f_vitorias'),
            '7_acertos': request.args.get('f_7_acertos'),
            '6_acertos': request.args.get('f_6_acertos'),
            '5_acertos': request.args.get('f_5_acertos'),
            '4_acertos': request.args.get('f_4_acertos'),
            'score': request.args.get('f_score'),
            'premios': request.args.get('f_premios')
        }

        from services.conferencia_historica_service import ConferenciaHistoricaService
        resultado = ConferenciaHistoricaService.obter_ranking(
            sessao_id, pagina, por_pagina, filtro_acertos, ordenacao, ord_dir, filtros_dinamicos
        )

        return jsonify(resultado), 200 if resultado['sucesso'] else 400
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/apostas/<int:aposta_id>', methods=['GET'])
def obter_detalhes_aposta_historica(aposta_id):
    """Obtém detalhes completos de uma aposta, incluindo todos os resultados"""
    try:
        from services.conferencia_historica_service import ConferenciaHistoricaService
        resultado = ConferenciaHistoricaService.obter_detalhes_aposta(aposta_id)

        return jsonify(resultado), 200 if resultado['sucesso'] else 400
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/sessoes/<int:sessao_id>/gerar-matriz', methods=['POST'])
def gerar_matriz_historica(sessao_id):
    """
    Gera matriz extraindo dezenas quentes e cruzando com ausentes
    """
    try:
        from services.conferencia_historica_service import ConferenciaHistoricaService
        from flask import send_file
        import io

        conteudo = ConferenciaHistoricaService.gerar_matriz_inteligente(sessao_id)
        
        if not conteudo:
            return jsonify({'sucesso': False, 'erro': 'Não foi possível gerar a matriz para esta sessão'}), 400

        output = io.BytesIO(conteudo.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'Matriz_Evoluida_HotCold_{sessao_id}.txt'
        )
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/sessoes/<int:sessao_id>/exportar', methods=['GET'])
def exportar_ranking_historica(sessao_id):
    """
    Exporta ranking em formato TXT ou CSV

    Query params:
        - formato: 'txt' ou 'csv' (default: 'txt')
        - limite: Número máximo de apostas
        - filtro_acertos: Filtrar por número mínimo de acertos
    """
    try:
        formato = request.args.get('formato', 'txt')
        limite = request.args.get('limite', type=int)
        filtro_acertos = request.args.get('filtro_acertos', type=int)
        ordenacao = request.args.get('ordenacao', 'score')
        ord_dir = request.args.get('ord_dir', 'desc')
        
        filtros_dinamicos = {
            'vitorias': request.args.get('f_vitorias'),
            '7_acertos': request.args.get('f_7_acertos'),
            '6_acertos': request.args.get('f_6_acertos'),
            '5_acertos': request.args.get('f_5_acertos'),
            '4_acertos': request.args.get('f_4_acertos'),
            'score': request.args.get('f_score'),
            'premios': request.args.get('f_premios')
        }

        from services.conferencia_historica_service import ConferenciaHistoricaService
        from flask import send_file
        import io

        conteudo = ConferenciaHistoricaService.exportar_ranking(
            sessao_id, formato, limite, filtro_acertos,
            ordenacao=ordenacao, ord_dir=ord_dir, filtros_dinamicos=filtros_dinamicos
        )

        if not conteudo:
            return jsonify({'sucesso': False, 'erro': 'Erro ao exportar'}), 400

        # Preparar arquivo para download
        output = io.BytesIO(conteudo.encode('utf-8'))
        output.seek(0)

        extensao = 'txt' if formato == 'txt' else 'csv'
        mimetype = 'text/plain' if formato == 'txt' else 'text/csv'

        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f'ranking_historico_{sessao_id}.{extensao}'
        )

    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/parse-preview', methods=['POST'])
def preview_parse_arquivo():
    """
    Faz preview do parse de um arquivo sem processar

    Útil para validar formato antes de enviar para processamento
    """
    try:
        if 'arquivo' not in request.files:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400

        arquivo = request.files['arquivo']
        conteudo = arquivo.read().decode('utf-8', errors='ignore')

        from services.conferencia_historica_service import ConferenciaHistoricaService
        apostas = ConferenciaHistoricaService.parse_arquivo(conteudo)

        # Retornar preview (primeiras 10 apostas)
        preview = apostas[:10]

        return jsonify({
            'sucesso': True,
            'total_apostas': len(apostas),
            'preview': preview,
            'nome_arquivo': arquivo.filename
        }), 200

    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia-historica/estatisticas', methods=['GET'])
def estatisticas_gerais_historica():
    """Retorna estatísticas gerais do banco de dados histórico"""
    try:
        from models.sorteio import Sorteio
        from models.conferencia_historica import SessaoConferenciaHistorica, ApostaHistorica

        total_sorteios = Sorteio.query.count()
        primeiro_sorteio = Sorteio.query.order_by(Sorteio.concurso.asc()).first()
        ultimo_sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()

        total_sessoes = SessaoConferenciaHistorica.query.count()
        total_apostas = ApostaHistorica.query.count()

        return jsonify({
            'sucesso': True,
            'estatisticas': {
                'total_sorteios': total_sorteios,
                'primeiro_concurso': primeiro_sorteio.concurso if primeiro_sorteio else None,
                'ultimo_concurso': ultimo_sorteio.concurso if ultimo_sorteio else None,
                'data_primeiro': primeiro_sorteio.data_sorteio.strftime('%d/%m/%Y') if primeiro_sorteio else None,
                'data_ultimo': ultimo_sorteio.data_sorteio.strftime('%d/%m/%Y') if ultimo_sorteio else None,
                'total_sessoes': total_sessoes,
                'total_apostas_processadas': total_apostas
            }
        }), 200

    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from config import Config
from models import db
from models.sorteio import Sorteio
import os
# Importar os novos modelos
from models.conferencia_historica import SessaoConferenciaHistorica, ApostaHistorica, ResultadoApostaHistorica
from models.metricas_conferencia_ocr import MetricasConferenciaOCR




# ========================================================================
# INICIALIZAÇÃO DO MONITORAMENTO DE APOSTAS
# ========================================================================

def inicializar_monitoramento():
    """
    Inicializa o serviço de monitoramento de apostas
    - Verifica/cria tabelas
    - Configura estrutura inicial
    - Valida integridade dos dados
    """
    try:
        print(" [INFO] Verificando estrutura do monitoramento...")
        
        # Importar models necessários
        from models.analise_aposta import AnaliseAposta
        
        # Verificar se tabela existe
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'analises_apostas' not in inspector.get_table_names():
            print(" [DADOS] Criando tabela analises_apostas...")
            db.create_all()
            print(" [OK] Tabela criada com sucesso!")
        else:
            print(" [OK] Tabela analises_apostas já existe")
            
        # Verificar dados existentes
        total_analises = AnaliseAposta.query.count()
        if total_analises == 0:
            print(" [SUGESTÃO] Nenhuma análise encontrada - sistema pronto para primeira análise")
        else:
            print(f" [STATS] {total_analises} análise(s) encontrada(s) no histórico")
            
            # Mostrar estatísticas rápidas
            total_apostas = db.session.query(db.func.sum(AnaliseAposta.total_apostas)).scalar() or 0
            total_premiadas = db.session.query(db.func.sum(AnaliseAposta.apostas_premiadas)).scalar() or 0
            
            print(f" [META] Total de apostas analisadas: {total_apostas}")
            print(f" [PREMIO] Total de apostas premiadas: {total_premiadas}")
            
            if total_apostas > 0:
                taxa = (total_premiadas / total_apostas) * 100
                print(f" [DADOS] Taxa de premiação geral: {taxa:.1f}%")
        
        print(" [OK] Monitoramento de apostas inicializado!")
        return True
        
    except ImportError as e:
        print(f" [ERRO] Erro de importação no monitoramento: {e}")
        print(" [INFO] Verifique se todos os arquivos do monitoramento foram criados")
        return False
        
    except Exception as e:
        print(f" [ERRO] Erro ao inicializar monitoramento: {e}")
        return False

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 🔧 AQUI é o local correto
    app.config['TEMPLATES_AUTO_RELOAD'] = True

      

    CORS(app)
    db.init_app(app)
    
    # 🔧 Habilitar modo WAL no SQLite para resolver problemas "database is locked" com Multi-Threading!
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    from sqlite3 import Connection as SQLite3Connection
    
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if type(dbapi_connection) is SQLite3Connection:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
            except Exception as e:
                print(f"[AVISO] Não foi possível ativar modo WAL (possível uso no Google Drive): {e}")
            
            # timeout generoso para evitar database is locked
            cursor.execute("PRAGMA busy_timeout=15000")  
            cursor.close()
    
    @app.after_request
    def add_header(response):
        """Força o navegador a não fazer cache de NADA (Resolve problema de 'mostrando apenas poucos')"""
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    # ========================================================================
    # CONFIGURAÇÃO DE CORES DOS MESES (INDEPENDENTE)
    # ========================================================================
    import json
    import os
    
    def carregar_config_meses():
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_meses.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar config_meses.json: {e}")
            return {"meses": {}}
            
    # Carregamento inicial
    meses_config_global = carregar_config_meses()
    
    @app.context_processor
    def inject_meses():
        return dict(config_meses=meses_config_global)
        
    @app.route('/api/config_meses', methods=['GET'])
    def api_config_meses():
        # Sempre recarrega na chamada API para facilitar atualizações em tempo real
        return jsonify(carregar_config_meses())

    # ========================================================================
    # IMPORTS DOS BLUEPRINTS
    # ========================================================================


    # Rotas principais
    from routes.sorteio_routes import sorteio_bp
    from routes.api_routes import api_bp
    from routes.estatisticas_routes import estatisticas_bp
    from routes.ciclo_por_posicao_routes import ciclo_por_posicao_bp
    from routes.palpites_routes import palpites_bp

    # Análises estatísticas básicas
    from routes.analise_atrasados_routes import analise_atrasados_bp
    from routes.analise_meses_routes import analise_meses_bp
    from routes.analise_combinacoes_routes import analise_combinacoes_bp
    from routes.analise_quentes_frios_routes import analise_quentes_frios_bp
    from routes.analise_defasagem_routes import analise_defasagem_bp
    from routes.analise_numeros_devidos_routes import analise_numeros_devidos_bp
    from routes.analise_numeros_juntos_routes import analise_numeros_juntos_bp #Adicionado Hoje

    # Análises de padrões numéricos
    from routes.analise_pares_impares_routes import analise_pares_impares_bp
    from routes.analise_primos_compostos_routes import analise_primos_compostos_bp
    from routes.analise_multiplos_routes import analise_multiplos_bp
    from routes.analise_fibonacci_routes import analise_fibonacci_bp
    from routes.analise_capicua_routes import analise_capicua_bp
    from routes.analise_raiz_digital_routes import analise_raiz_digital_bp
    from routes.analise_digitos_unicos_routes import analise_digitos_unicos_bp
    from routes.analise_digito_padrao_inicial_final_routes import analise_digito_padrao_inicial_final_bp

    # Análises de distribuição
    from routes.analise_dezenas_routes import analise_dezenas_bp
    from routes.analise_quadrantes_routes import analise_quadrantes_bp
    from routes.analise_gaps_routes import analise_gaps_bp
    from routes.analise_gaps_completo_routes import analise_gaps_completo_bp # Dígitos X Gaps Menu Cruzamentos
    from routes.analise_gaps_expandido_routes import analise_gaps_expandido_bp
    from routes.analise_consecutivos_routes import analise_consecutivos_bp
    from routes.analise_espelhados_routes import analise_espelhados_bp
    from routes.analise_soma_dezenas_routes import analise_soma_dezenas_bp

    # Análises de relacionamento
    from routes.analise_repeticoes_routes import analise_repeticoes_bp
    from routes.analise_sequencias_routes import analise_sequencias_bp

    # Análises temporais
    from routes.analise_evolucao_meses_routes import analise_evolucao_meses_bp
    from routes.analise_ciclos_meses_routes import analise_ciclos_meses_bp
    from routes.analise_expectativa_meses_routes import analise_expectativa_meses_bp

    # Análises preditivas e ferramentas
    from routes.analise_previsao_atrasados_routes import analise_previsao_atrasados_bp
    from routes.analise_calculadora_probabilidade_routes import analise_calculadora_probabilidade_bp
    from routes.analise_matriz_probabilidade_routes import analise_matriz_probabilidade_bp
    from routes.analise_fatiamento_routes import analise_fatiamento_bp
    from routes.analise_simulador_apostas_routes import analise_simulador_apostas_bp
    from routes.analise_simulador_filtros_routes import analise_simulador_filtros_bp
    from routes.analise_interse_apostas_routes import analise_interse_apostas_bp
    from routes.analise_frequencia_interna_apostas_routes import analise_freq_interna_apostas_bp
    from routes.analise_desdobramento_validator_routes import analise_desdobramento_validator_bp
    from routes.analise_gaps_transicoes_apostas_routes import analise_gaps_transicoes_apostas_bp
    from routes.analise_simulacao_reversa_routes import analise_simulacao_reversa_bp

    # Ferramentas de conferência e premiação
    from routes.conferidor_apostas_routes import conferidor_apostas_bp
    from routes.valores_probabilidades_routes import valores_probabilidades_bp
    from routes.atualizar_premiacao_routes import atualizar_premiacao_bp
    # 🆕 UNIFICADO: Substitui gerar_fechamento_routes e gerar_fechamento_tubular_routes
    from routes.fechamentos_unificado_routes import fechamentos_bp

    # Visualizações personalizadas
    from routes.visualizacao_tubular_routes import visualizacao_tubular_bp
    from routes.visualizacao_routes import visualizacao_bp
    from routes.configuracao_routes import configuracao_bp  # 🆕 NOVA LINHA
    from models.cores_meses_model import CoresMeses
    from routes.cores_meses_routes import cores_meses_bp
    from routes.analise_tubular_routes import analise_tubular_bp
    
    
    # Análises Avançadas - Novas
    from routes.analise_frequencia_premios_routes import analise_frequencia_premios_bp
    from routes.analise_transicao_meses_routes import analise_transicao_meses_bp
    from routes.analise_correlacao_mes_dezenas_routes import analise_correlacao_mes_dezenas_bp
    from routes.analise_ciclos_intervalos_routes import analise_ciclos_intervalos_bp
    from routes.analise_repeticao_persistencia_routes import analise_repeticao_persistencia_bp
    from routes.analise_distribuicao_numerica_routes import analise_distribuicao_numerica_bp
    from routes.analise_sazonal_routes import analise_sazonal_bp
    from routes.analise_acumulos_mes_routes import analise_acumulos_mes_bp
    from routes.analise_padroes_sequencias_routes import analise_padroes_sequencias_bp
    from routes.analise_probabilidade_condicional_routes import analise_probabilidade_condicional_bp
    from routes.proximo_sorteio_routes import proximo_sorteio_bp
    
    # 3 Novos serviços     # Adicione o import
    # from routes.conferencia_apostas_routes import conferencia_apostas_bp
    # from routes.garantias_routes import garantias_bp
    # from routes.estrategias_routes import estrategias_bp
    # from routes.conferencia_apostas_ocr_routes import conferencia_ocr_bp
    
    # Monitoramento de apostas
    from routes.monitoramento_apostas_routes import monitoramento_apostas_bp as monitoramento_bp
    
    # No topo do arquivo (junto com outros imports)
    from routes.descobrir_tecnicas_routes import descobrir_tecnicas_bp
    from routes.analise_profunda_routes import analise_profunda_bp
    from routes.conversor_apostas_routes import conversor_apostas_bp
    from routes.dashboard_analises_routes import dashboard_analises_bp
    # from routes.analise_distribuicao_linha_coluna_routes import analise_volante_bp
    from routes.analise_distribuicao_linha_coluna_routes import distribuicao_lc_bp
    from routes.posicao_minima_maxima_routes import posicao_min_max_bp
    from routes.desdobramento_routes import desdobramento_bp
    from routes.desdobramento_com_pares_routes import desdobramento_pares_bp
    from routes.gerador_inteligente_routes import gerador_inteligente_bp
    
    # Novos serviços
    from routes.analise_finais_iguais_routes import analise_finais_iguais_bp
    from routes.analise_sequencia_dezenas_routes import analise_sequencia_dezenas_bp
    from routes.analise_repeticao_concurso_anterior_routes import analise_repeticao_concurso_anterior_bp
    from routes.filtrador_combinacoes_routes import filtrador_bp
    from routes.eventos_intuitivos_routes import eventos_bp
    from routes.analise_colunas_routes import colunas_bp
    from routes.analise_cruzamentos_routes import cruzamentos_bp
    from routes.analises_sequenciais_routes import sequenciais_bp
    from routes.gerador_padroes_completo_routes import gerador_padroes_bp
    from routes.repeticao_routes import repeticao_bp
    from routes.combinacoes_routes import combinacoes_bp
    from routes.analise_visual_routes import analise_visual_bp
    from routes.resultados_routes import resultados_bp
    from routes.central_conferencias_routes import central_conferencias_bp
    from routes.resumo_apostas_routes import resumo_apostas_bp
    from routes.locais_sorte_routes import locais_sorte_bp
    # Importar
    from routes.central_garantias_routes import central_garantias_bp
    
    # 🆕 NOVO MÓDULO: Analise Ciclos das Dezenas
    from routes.analise_ciclos_dezenas_routes import analise_ciclos_dezenas_bp
    
    # 🆕 NOVO MÓDULO: Gerador Especial de Apostas
    from routes.gerador_especial_routes import gerador_especial_bp
    
    # 🆕 NOVO: Índice Central de Análises
    from routes.indice_analises_routes import indice_analises_bp
    
    # NOVO: Analise de Ausentes
    from routes.analise_ausentes_routes import analise_ausentes_bp

    # Concentração Estratégica (score de união + API)
    from routes.concentracao_estrategica_routes import concentracao_estrategica_bp
    
    
    # ========================================================================
    # REGISTRO DOS BLUEPRINTS
    # ========================================================================

    # Rotas principais
    app.register_blueprint(sorteio_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(estatisticas_bp)
    app.register_blueprint(ciclo_por_posicao_bp)
    app.register_blueprint(palpites_bp)

    # Análises estatísticas básicas
    app.register_blueprint(analise_atrasados_bp)
    app.register_blueprint(analise_meses_bp)
    app.register_blueprint(analise_combinacoes_bp)
    app.register_blueprint(analise_quentes_frios_bp)
    app.register_blueprint(analise_defasagem_bp)
    app.register_blueprint(analise_numeros_devidos_bp)
    app.register_blueprint(analise_numeros_juntos_bp) #Adicionado Hoje

    # Análises de padrões numéricos
    app.register_blueprint(analise_pares_impares_bp)
    app.register_blueprint(analise_primos_compostos_bp)
    app.register_blueprint(analise_multiplos_bp)
    app.register_blueprint(analise_fibonacci_bp)
    app.register_blueprint(analise_capicua_bp)
    app.register_blueprint(analise_raiz_digital_bp)
    app.register_blueprint(analise_digitos_unicos_bp)
    app.register_blueprint(analise_fatiamento_bp)
    app.register_blueprint(analise_digito_padrao_inicial_final_bp)
    

    # Análises de distribuição
    app.register_blueprint(analise_dezenas_bp)
    app.register_blueprint(analise_quadrantes_bp)
    app.register_blueprint(analise_gaps_bp)
    app.register_blueprint(analise_gaps_completo_bp)
    app.register_blueprint(analise_gaps_expandido_bp)
    app.register_blueprint(analise_consecutivos_bp)
    app.register_blueprint(analise_espelhados_bp)
    app.register_blueprint(analise_soma_dezenas_bp)

    # Análises de relacionamento
    app.register_blueprint(analise_repeticoes_bp)
    app.register_blueprint(analise_sequencias_bp)

    # Análises temporais
    app.register_blueprint(analise_evolucao_meses_bp)
    app.register_blueprint(analise_ciclos_meses_bp)
    app.register_blueprint(analise_expectativa_meses_bp)

    # Análises preditivas e ferramentas
    app.register_blueprint(analise_previsao_atrasados_bp)
    app.register_blueprint(analise_calculadora_probabilidade_bp)
    app.register_blueprint(analise_matriz_probabilidade_bp)
    app.register_blueprint(analise_simulador_apostas_bp)
    app.register_blueprint(analise_simulador_filtros_bp)
    app.register_blueprint(analise_interse_apostas_bp)
    app.register_blueprint(analise_freq_interna_apostas_bp)
    app.register_blueprint(analise_desdobramento_validator_bp)
    app.register_blueprint(analise_gaps_transicoes_apostas_bp)
    app.register_blueprint(analise_simulacao_reversa_bp)

    # Ferramentas de conferência e premiação
    app.register_blueprint(conferidor_apostas_bp)
    app.register_blueprint(valores_probabilidades_bp)
    app.register_blueprint(atualizar_premiacao_bp)
    # 🆕 UNIFICADO: Um blueprint para ambos fechamentos
    app.register_blueprint(fechamentos_bp)

    # Visualizações personalizadas
    app.register_blueprint(visualizacao_tubular_bp)
    app.register_blueprint(visualizacao_bp)
    app.register_blueprint(configuracao_bp)  # 🆕 NOVA LINHA
    app.register_blueprint(cores_meses_bp)
    app.register_blueprint(analise_tubular_bp)
    
    # Análises Avançadas - Novas
    app.register_blueprint(analise_frequencia_premios_bp)
    app.register_blueprint(analise_transicao_meses_bp)
    app.register_blueprint(analise_correlacao_mes_dezenas_bp)
    app.register_blueprint(analise_ciclos_intervalos_bp)
    app.register_blueprint(analise_repeticao_persistencia_bp)
    app.register_blueprint(analise_distribuicao_numerica_bp)
    app.register_blueprint(analise_sazonal_bp)
    app.register_blueprint(analise_acumulos_mes_bp)
    app.register_blueprint(analise_padroes_sequencias_bp)
    app.register_blueprint(analise_probabilidade_condicional_bp)
    app.register_blueprint(proximo_sorteio_bp)
    
    # 3 Novos serviço # Registre o blueprint
    # app.register_blueprint(conferencia_apostas_bp)
    # app.register_blueprint(garantias_bp)
    # app.register_blueprint(estrategias_bp)
    # app.register_blueprint(conferencia_ocr_bp)

    # Monitoramento de apostas
    app.register_blueprint(monitoramento_bp)
    
    
     # Depois de criar o app (junto com outros registros de blueprint)
    app.register_blueprint(descobrir_tecnicas_bp)
    app.register_blueprint(analise_profunda_bp)
    app.register_blueprint(conversor_apostas_bp)
    app.register_blueprint(dashboard_analises_bp)
   

   # app.register_blueprint(analise_volante_bp)
    app.register_blueprint(distribuicao_lc_bp)
    app.register_blueprint(posicao_min_max_bp)
    app.register_blueprint(desdobramento_bp)
    app.register_blueprint(desdobramento_pares_bp)
    app.register_blueprint(gerador_inteligente_bp)
    
    # Novos serviços
    app.register_blueprint(analise_finais_iguais_bp)
    app.register_blueprint(analise_sequencia_dezenas_bp)
    app.register_blueprint(analise_repeticao_concurso_anterior_bp)
    app.register_blueprint(filtrador_bp)
    app.register_blueprint(eventos_bp)
    app.register_blueprint(colunas_bp)
    app.register_blueprint(cruzamentos_bp)
    app.register_blueprint(sequenciais_bp)
    app.register_blueprint(gerador_padroes_bp)
    app.register_blueprint(repeticao_bp)
    app.register_blueprint(combinacoes_bp)
    app.register_blueprint(analise_visual_bp)
    from routes.laboratorio_alteracoes_routes import laboratorio_alteracoes_bp
    app.register_blueprint(laboratorio_alteracoes_bp)
    app.register_blueprint(concentracao_estrategica_bp)
    app.register_blueprint(resultados_bp)
    app.register_blueprint(central_conferencias_bp)
    app.register_blueprint(resumo_apostas_bp)
    app.register_blueprint(locais_sorte_bp)
    # Registrar o Blueprint    
    # 🆕 NOVO MÓDULO: Ciclos das Dezenas
    app.register_blueprint(analise_ciclos_dezenas_bp)
    app.register_blueprint(central_garantias_bp)
    
    # 🆕 NOVO MÓDULO: Gerador Especial de Apostas
    app.register_blueprint(gerador_especial_bp)
    
    # 🆕 NOVO: Índice Central de Análises
    app.register_blueprint(indice_analises_bp)
    
    # NOVO: Analise de Ausentes
    app.register_blueprint(analise_ausentes_bp)
    
    # =====================================================
    # ROTA: Página de Conceitos (Garantias, Desdobramentos, Fechamentos)
    # =====================================================
    @app.route('/conceitos')
    def pagina_conceitos():
        """Página explicativa sobre Garantias, Desdobramentos e Fechamentos"""
        return render_template('conceitos_apostas.html')

    # =====================================================
    # FUNÇÃO AUXILIAR: Converte número do mês para nome
    # =====================================================
    def obter_nome_mes(numero):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')

    # =====================================================
    # NOVO ENDPOINT: Retorna TODOS os sorteios (sem limite)
    # =====================================================
    @app.route('/api/sorteios/todos', methods=['GET'])
    def obter_todos_sorteios():
        """
        Retorna TODOS os sorteios do banco de dados, sem paginação.
        Usado para download completo dos resultados.
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

            resultado = []
            for s in sorteios:
                resultado.append({
                    'concurso': s.concurso,
                    'data_sorteio': s.data_sorteio.strftime('%d/%m/%Y') if s.data_sorteio else '',
                    'mes_sorte': s.mes_sorte,
                    'mes_sorte_nome': obter_nome_mes(s.mes_sorte),
                    'posicoes': {
                        'posicao_1': s.sorteio_1 if s.sorteio_1 is not None else s.posicao_1,
                        'posicao_2': s.sorteio_2 if s.sorteio_2 is not None else s.posicao_2,
                        'posicao_3': s.sorteio_3 if s.sorteio_3 is not None else s.posicao_3,
                        'posicao_4': s.sorteio_4 if s.sorteio_4 is not None else s.posicao_4,
                        'posicao_5': s.sorteio_5 if s.sorteio_5 is not None else s.posicao_5,
                        'posicao_6': s.sorteio_6 if s.sorteio_6 is not None else s.posicao_6,
                        'posicao_7': s.sorteio_7 if s.sorteio_7 is not None else s.posicao_7
                    },
                    # Campos de premiação para coluna Valor
                    'valor_premio_7_acertos': s.valor_premio_7_acertos or 0,
                    'valor_premio_6_acertos': s.valor_premio_6_acertos or 0,
                    'valor_premio_5_acertos': s.valor_premio_5_acertos or 0,
                    'valor_premio_4_acertos': s.valor_premio_4_acertos or 0,
                    'valor_premio_mes_sorte': s.valor_premio_mes_sorte or 0,
                    
                    # Campos adicionais para cálculo de valor potencial
                    'acumulado': s.acumulado or False,
                    'valor_acumulado_proximo_concurso': s.valor_acumulado_proximo_concurso or 0,
                    'valor_arrecadado': s.valor_arrecadado or 0
                })

            return jsonify({
                'sorteios': resultado,
                'total': len(resultado)
            })
        except Exception as e:
            return jsonify({'erro': str(e)}), 500
    
    # ========================================================================
    # INICIALIZAÇÃO DO BANCO DE DADOS
    # ========================================================================

    with app.app_context():
        from models.laboratorio_alteracoes import LaboratorioAlteracoesRegistro  # noqa: F401
        db.create_all()
        print("[OK] Banco de dados inicializado com sucesso!")

        # Inicializa configurações padrão
        from models.configuracao import Configuracao
        Configuracao.criar_configuracoes_padrao()
        print("[OK] Configurações padrão inicializadas!")


        # 🆕 NOVO: Inicializar cores dos meses
        from models.cores_meses_model import CoresMeses
        CoresMeses.criar_cores_padrao()
        print("[OK] Cores dos meses inicializadas!")

        # 🆕 NOVO: Inicializar tabela de métricas OCR
        from models.metricas_conferencia_ocr import MetricasConferenciaOCR
        print("[OK] Tabela de métricas OCR registrada!")



        # 🆕 NOVO: Verificar monitoramento de apostas
        from models.analise_aposta import AnaliseAposta
        try:
            total_analises = AnaliseAposta.query.count()
            if total_analises > 0:
                # Mostrar estatísticas resumidas
                total_apostas = db.session.query(db.func.sum(AnaliseAposta.total_apostas)).scalar() or 0
                total_premiadas = db.session.query(db.func.sum(AnaliseAposta.apostas_premiadas)).scalar() or 0

                print(f"[STATS] Monitoramento de Apostas:")
                print(f"   • {total_analises} análise(s) no histórico")
                print(f"   • {total_apostas} apostas analisadas")
                print(f"   • {total_premiadas} apostas premiadas")

                if total_apostas > 0:
                    taxa = (total_premiadas / total_apostas) * 100
                    print(f"   • Taxa geral de premiação: {taxa:.1f}%")
            else:
                print("[STATS] Monitoramento de Apostas: Sistema pronto para primeira análise!")
        except Exception as e:
            print("[STATS] Monitoramento de Apostas: Tabela criada com sucesso!")

    return app


def main():
    app = create_app()
    modo = os.getenv('FLASK_ENV', 'development')
    porta = int(os.getenv('PORT', 5151))

    if modo == 'production':
        from waitress import serve
        print(f"[OK] Servidor rodando em PRODUÇÃO na porta {porta}")
        print(f"[URL] Acesse: http://localhost:{porta}")
        print(f"[STATS] Monitoramento: http://localhost:{porta}/monitoramento-apostas/")
        serve(app, host='0.0.0.0', port=porta)
    else:
        print(f"[INFO] Servidor rodando em DESENVOLVIMENTO na porta {porta}")
        print(f"[URL] Acesse: http://localhost:{porta}")
        print(f"[STATS] Monitoramento: http://localhost:{porta}/monitoramento-apostas/")
        
        # DEBUG: Listar rotas registradas para debug
        print("\n[DEBUG] Rotas registradas (Filtro: metricas):")
        for rule in app.url_map.iter_rules():
            if 'metricas' in str(rule):
                print(f"   -> {rule} ({', '.join(rule.methods)})")
        print("="*50 + "\n")

        # app.run(host='0.0.0.0', port=porta, debug=True)
        app.run(host='0.0.0.0', port=porta, debug=False)


if __name__ == '__main__':
    main()
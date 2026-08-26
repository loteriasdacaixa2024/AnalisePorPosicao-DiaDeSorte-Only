"""
Rotas Flask para Análise Profunda de Técnicas
Sistema de descoberta de padrões matemáticos em concursos do Dia de Sorte
"""

from flask import Blueprint, render_template, request, jsonify
from services.analise_profunda_service_EXPANDIDO import analisar_concurso_profundo
import sqlite3
import os

# Criar blueprint
analise_profunda_bp = Blueprint('analise_profunda', __name__, url_prefix='/analise-profunda')

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'analise_por_posicao.db')


@analise_profunda_bp.route('/')
def index():
    """Página principal da análise profunda"""
    return render_template('analise_profunda.html')


@analise_profunda_bp.route('/v2')
def index_v2():
    """Página da análise profunda v2 (com análise em massa)"""
    return render_template('analise_profunda_v2.html')


@analise_profunda_bp.route('/analisar/<int:concurso>', methods=['GET'])
def analisar_concurso(concurso):
    """
    Analisa um concurso específico

    Args:
        concurso: Número do concurso a analisar

    Returns:
        JSON com análise completa dezena por dezena
    """
    try:
        resultado = analisar_concurso_profundo(concurso)

        if not resultado.get('sucesso'):
            return jsonify({
                'sucesso': False,
                'erro': resultado.get('erro', 'Erro desconhecido ao analisar concurso')
            }), 404

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao processar análise: {str(e)}'
        }), 500


@analise_profunda_bp.route('/salvar', methods=['POST'])
def salvar_analise():
    """
    Salva uma análise no banco de dados

    Body JSON:
        {
            "concurso": 1134,
            "resultado_analise": {...}
        }

    Returns:
        JSON confirmando salvamento
    """
    try:
        dados = request.get_json()
        concurso = dados.get('concurso')
        resultado = dados.get('resultado_analise')

        if not concurso or not resultado:
            return jsonify({
                'sucesso': False,
                'erro': 'Dados incompletos. Forneça concurso e resultado_analise'
            }), 400

        # Conectar ao banco
        db_analises = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'analise_por_posicao.db')
        conn = sqlite3.connect(db_analises)
        cursor = conn.cursor()

        # Verificar se as tabelas existem
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analises_tecnicas'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'sucesso': False,
                'erro': 'Tabelas de análise não encontradas. Execute criar_tabelas_analise_profunda.py primeiro'
            }), 500

        # Salvar resumo na tabela analises_resumo
        resumo = resultado.get('resumo', {})

        cursor.execute('''
            INSERT OR REPLACE INTO analises_resumo (
                concurso_analisado,
                total_dezenas,
                dezenas_com_tecnica,
                dezenas_sem_tecnica,
                total_tecnicas_testadas,
                total_tecnicas_acertaram,
                percentual_cobertura,
                percentual_eficacia,
                categoria_mais_usada,
                campo_mais_usado,
                dezenas_sorteadas,
                lista_dezenas_sem_tecnica,
                tempo_processamento_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            concurso,
            resumo.get('total_dezenas', 7),
            resumo.get('dezenas_com_tecnica', 0),
            resumo.get('dezenas_sem_tecnica', 0),
            resumo.get('total_tecnicas_testadas', 0),
            resumo.get('total_tecnicas_acertaram', 0),
            resumo.get('percentual_cobertura', 0),
            resumo.get('percentual_eficacia', 0),
            resumo.get('categoria_mais_usada', ''),
            resumo.get('campo_mais_usado', ''),
            ','.join(map(str, resultado.get('dezenas_sorteadas', []))),
            ','.join(map(str, resumo.get('lista_dezenas_sem_tecnica', []))),
            resumo.get('tempo_processamento_ms', 0)
        ))

        # Salvar detalhes na tabela analises_tecnicas
        dados_gatilho = resultado.get('dados_gatilho', {})

        for analise_dez in resultado.get('analise_por_dezena', []):
            dezena = analise_dez.get('dezena')
            posicao = analise_dez.get('posicao')

            for tecnica in analise_dez.get('tecnicas', []):
                cursor.execute('''
                    INSERT INTO analises_tecnicas (
                        concurso_analisado,
                        numero_concurso_proximo,
                        data_proximo_concurso,
                        valor_estimado_proximo_concurso,
                        dezena,
                        posicao_dezena,
                        tecnica_id,
                        tecnica_nome,
                        tecnica_categoria,
                        campo_usado,
                        formula,
                        calculo_passo_a_passo,
                        valor_saida,
                        acertou,
                        confianca
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    concurso,
                    dados_gatilho.get('numero_concurso_proximo'),
                    dados_gatilho.get('data_proximo_concurso'),
                    dados_gatilho.get('valor_estimado_proximo_concurso'),
                    dezena,
                    posicao,
                    tecnica.get('id'),
                    tecnica.get('nome'),
                    tecnica.get('categoria'),
                    tecnica.get('campo'),
                    tecnica.get('formula'),
                    tecnica.get('calculo'),
                    tecnica.get('resultado'),
                    1,  # acertou = True (técnica gerou a dezena correta)
                    1.0  # confiança (pode ser calculada depois)
                ))

        conn.commit()
        conn.close()

        return jsonify({
            'sucesso': True,
            'mensagem': f'Análise do concurso {concurso} salva com sucesso!',
            'registros_salvos': {
                'resumo': 1,
                'tecnicas_detalhadas': sum(len(a.get('tecnicas', [])) for a in resultado.get('analise_por_dezena', []))
            }
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao salvar análise: {str(e)}'
        }), 500


@analise_profunda_bp.route('/estatisticas', methods=['GET'])
def estatisticas_gerais():
    """
    Retorna estatísticas gerais das análises realizadas

    Returns:
        JSON com estatísticas consolidadas
    """
    try:
        db_analises = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'analise_por_posicao.db')
        conn = sqlite3.connect(db_analises)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Total de análises realizadas
        cursor.execute('SELECT COUNT(*) as total FROM analises_resumo')
        total_analises = cursor.fetchone()['total']

        # Técnicas mais eficazes (usando a view)
        cursor.execute('''
            SELECT * FROM vw_tecnicas_top
            LIMIT 10
        ''')
        tecnicas_top = [dict(row) for row in cursor.fetchall()]

        # Estatísticas por campo
        cursor.execute('''
            SELECT * FROM vw_tecnicas_por_campo
            ORDER BY taxa_acerto DESC
        ''')
        stats_por_campo = [dict(row) for row in cursor.fetchall()]

        # Análises recentes
        cursor.execute('''
            SELECT * FROM vw_analises_recentes
            LIMIT 10
        ''')
        analises_recentes = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'sucesso': True,
            'total_analises_realizadas': total_analises,
            'tecnicas_top_10': tecnicas_top,
            'estatisticas_por_campo': stats_por_campo,
            'analises_recentes': analises_recentes
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao buscar estatísticas: {str(e)}'
        }), 500


@analise_profunda_bp.route('/historico/<int:concurso>', methods=['GET'])
def buscar_historico(concurso):
    """
    Busca análise histórica de um concurso

    Args:
        concurso: Número do concurso

    Returns:
        JSON com análise salva anteriormente
    """
    try:
        db_analises = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'analise_por_posicao.db')
        conn = sqlite3.connect(db_analises)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Buscar resumo
        cursor.execute('''
            SELECT * FROM analises_resumo
            WHERE concurso_analisado = ?
        ''', (concurso,))

        resumo_row = cursor.fetchone()

        if not resumo_row:
            conn.close()
            return jsonify({
                'sucesso': False,
                'erro': f'Nenhuma análise encontrada para o concurso {concurso}'
            }), 404

        resumo = dict(resumo_row)

        # Buscar técnicas detalhadas
        cursor.execute('''
            SELECT * FROM analises_tecnicas
            WHERE concurso_analisado = ?
            ORDER BY posicao_dezena, tecnica_id
        ''', (concurso,))

        tecnicas_rows = cursor.fetchall()
        tecnicas = [dict(row) for row in tecnicas_rows]

        conn.close()

        return jsonify({
            'sucesso': True,
            'concurso': concurso,
            'resumo': resumo,
            'tecnicas_detalhadas': tecnicas
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao buscar histórico: {str(e)}'
        }), 500


@analise_profunda_bp.route('/listar-concursos', methods=['GET'])
def listar_concursos_disponiveis():
    """
    Lista concursos disponíveis no banco de dados

    Query params:
        limit: Quantidade máxima de concursos (default: 50)

    Returns:
        JSON com lista de concursos
    """
    try:
        limit = request.args.get('limit', 50, type=int)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                concurso,
                data_proximo_concurso,
                numero_concurso_proximo,
                valor_estimado_proximo_concurso
            FROM sorteios
            WHERE numero_concurso_proximo IS NOT NULL
            ORDER BY concurso DESC
            LIMIT ?
        ''', (limit,))

        concursos = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'sucesso': True,
            'total': len(concursos),
            'concursos': concursos
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao listar concursos: {str(e)}'
        }), 500


@analise_profunda_bp.route('/analisar-massa', methods=['POST'])
def analisar_massa():
    """
    Analisa múltiplos concursos em sequência (análise em massa)

    Body JSON:
        {
            "concurso_inicial": 1090,
            "concurso_final": 1138,
            "salvar_automatico": true
        }

    Returns:
        JSON com resumo do processamento em massa
    """
    try:
        import time

        dados = request.get_json()

        # Converter para int (importante para comparações)
        try:
            concurso_inicial = int(dados.get('concurso_inicial')) if dados.get('concurso_inicial') else None
            concurso_final = int(dados.get('concurso_final')) if dados.get('concurso_final') else None
        except (ValueError, TypeError):
            return jsonify({
                'sucesso': False,
                'erro': 'concurso_inicial e concurso_final devem ser números inteiros'
            }), 400

        salvar_auto = dados.get('salvar_automatico', True)

        # Validações
        if not concurso_inicial or not concurso_final:
            return jsonify({
                'sucesso': False,
                'erro': 'Forneça concurso_inicial e concurso_final'
            }), 400

        if concurso_inicial > concurso_final:
            return jsonify({
                'sucesso': False,
                'erro': 'Concurso inicial deve ser menor ou igual ao final'
            }), 400

        total_concursos = concurso_final - concurso_inicial + 1

        if total_concursos > 200:
            return jsonify({
                'sucesso': False,
                'erro': 'Limite máximo de 200 concursos por vez'
            }), 400

        # Buscar concursos disponíveis no banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT concurso
            FROM sorteios
            WHERE concurso BETWEEN ? AND ?
              AND numero_concurso_proximo IS NOT NULL
              AND data_proximo_concurso IS NOT NULL
              AND valor_estimado_proximo_concurso IS NOT NULL
            ORDER BY concurso
        ''', (concurso_inicial, concurso_final))

        concursos_disponiveis = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not concursos_disponiveis:
            return jsonify({
                'sucesso': False,
                'erro': f'Nenhum concurso disponível entre {concurso_inicial} e {concurso_final}'
            }), 404

        # Processar cada concurso
        inicio_processamento = time.time()
        resultados = {
            'processados': 0,
            'sucessos': 0,
            'erros': 0,
            'salvos': 0,
            'total_tecnicas_acertaram': 0,
            'detalhes': []
        }

        for concurso in concursos_disponiveis:
            try:
                # Analisar concurso
                resultado = analisar_concurso_profundo(concurso)

                if resultado.get('sucesso'):
                    resultados['sucessos'] += 1
                    resultados['total_tecnicas_acertaram'] += resultado['resumo']['total_tecnicas_acertaram']

                    # Salvar no banco se solicitado
                    if salvar_auto:
                        try:
                            salvar_analise_automatico(concurso, resultado)
                            resultados['salvos'] += 1
                        except Exception as e_save:
                            resultados['detalhes'].append({
                                'concurso': concurso,
                                'status': 'analisado_nao_salvo',
                                'erro': str(e_save)
                            })

                    resultados['detalhes'].append({
                        'concurso': concurso,
                        'status': 'sucesso',
                        'cobertura': resultado['resumo']['percentual_cobertura'],
                        'acertos': resultado['resumo']['total_tecnicas_acertaram']
                    })
                else:
                    resultados['erros'] += 1
                    resultados['detalhes'].append({
                        'concurso': concurso,
                        'status': 'erro',
                        'erro': resultado.get('erro', 'Erro desconhecido')
                    })

            except Exception as e:
                resultados['erros'] += 1
                resultados['detalhes'].append({
                    'concurso': concurso,
                    'status': 'erro',
                    'erro': str(e)
                })

            resultados['processados'] += 1

        tempo_total_ms = int((time.time() - inicio_processamento) * 1000)

        return jsonify({
            'sucesso': True,
            'range': {
                'inicial': concurso_inicial,
                'final': concurso_final,
                'solicitados': total_concursos,
                'disponiveis': len(concursos_disponiveis)
            },
            'resumo': {
                'processados': resultados['processados'],
                'sucessos': resultados['sucessos'],
                'erros': resultados['erros'],
                'salvos': resultados['salvos'],
                'total_tecnicas_acertaram': resultados['total_tecnicas_acertaram'],
                'tempo_processamento_ms': tempo_total_ms
            },
            'detalhes': resultados['detalhes']
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao processar análise em massa: {str(e)}'
        }), 500


def salvar_analise_automatico(concurso, resultado):
    """
    Função auxiliar para salvar análise no banco (chamada internamente)
    """
    db_analises = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'analise_por_posicao.db')
    conn = sqlite3.connect(db_analises)
    cursor = conn.cursor()

    # Salvar resumo
    resumo = resultado.get('resumo', {})

    cursor.execute('''
        INSERT OR REPLACE INTO analises_resumo (
            concurso_analisado, total_dezenas, dezenas_com_tecnica, dezenas_sem_tecnica,
            total_tecnicas_testadas, total_tecnicas_acertaram, percentual_cobertura,
            percentual_eficacia, categoria_mais_usada, campo_mais_usado,
            dezenas_sorteadas, lista_dezenas_sem_tecnica, tempo_processamento_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        concurso,
        resumo.get('total_dezenas', 7),
        resumo.get('dezenas_com_tecnica', 0),
        resumo.get('dezenas_sem_tecnica', 0),
        resumo.get('total_tecnicas_testadas', 0),
        resumo.get('total_tecnicas_acertaram', 0),
        resumo.get('percentual_cobertura', 0),
        resumo.get('percentual_eficacia', 0),
        resumo.get('categoria_mais_usada', ''),
        resumo.get('campo_mais_usado', ''),
        ','.join(map(str, resultado.get('dezenas_sorteadas', []))),
        ','.join(map(str, resumo.get('lista_dezenas_sem_tecnica', []))),
        resumo.get('tempo_processamento_ms', 0)
    ))

    # Deletar técnicas antigas deste concurso (para evitar duplicação)
    cursor.execute('DELETE FROM analises_tecnicas WHERE concurso_analisado = ?', (concurso,))

    # Salvar técnicas
    dados_gatilho = resultado.get('dados_gatilho', {})

    for analise_dez in resultado.get('analise_por_dezena', []):
        dezena = analise_dez.get('dezena')
        posicao = analise_dez.get('posicao')

        for tecnica in analise_dez.get('tecnicas', []):
            cursor.execute('''
                INSERT INTO analises_tecnicas (
                    concurso_analisado, numero_concurso_proximo, data_proximo_concurso,
                    valor_estimado_proximo_concurso, dezena, posicao_dezena, tecnica_id,
                    tecnica_nome, tecnica_categoria, campo_usado, formula, calculo_passo_a_passo,
                    valor_saida, acertou, confianca
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                concurso,
                dados_gatilho.get('numero_concurso_proximo'),
                dados_gatilho.get('data_proximo_concurso'),
                dados_gatilho.get('valor_estimado_proximo_concurso'),
                dezena, posicao,
                tecnica.get('id'), tecnica.get('nome'), tecnica.get('categoria'),
                tecnica.get('campo'), tecnica.get('formula'), tecnica.get('calculo'),
                tecnica.get('resultado'), 1, 1.0
            ))

    conn.commit()
    conn.close()


@analise_profunda_bp.route('/ranking-tecnicas', methods=['GET'])
def ranking_tecnicas():
    """
    Retorna ranking das técnicas mais eficazes baseado em análises salvas

    Query params:
        top: Quantidade de técnicas no ranking (default: 10)

    Returns:
        JSON com:
        - top_tecnicas: Ranking das técnicas mais eficazes
        - insights: Insights automáticos sobre padrões
        - dezenas_literais: Dezenas que aparecem literalmente nos dados
    """
    try:
        top_n = request.args.get('top', 10, type=int)

        db_analises = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'analise_por_posicao.db')
        conn = sqlite3.connect(db_analises)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Verificar se há dados
        cursor.execute('SELECT COUNT(*) as total FROM analises_tecnicas')
        total_registros = cursor.fetchone()['total']

        if total_registros == 0:
            conn.close()
            return jsonify({
                'sucesso': True,
                'mensagem': 'Nenhuma análise salva ainda. Analise e salve concursos primeiro.',
                'top_tecnicas': [],
                'insights': [],
                'dezenas_literais': []
            }), 200

        # TOP N Técnicas (por quantidade de acertos)
        cursor.execute('''
            SELECT
                tecnica_id,
                tecnica_nome,
                tecnica_categoria,
                campo_usado,
                COUNT(*) as total_acertos,
                COUNT(DISTINCT concurso_analisado) as concursos_diferentes,
                COUNT(DISTINCT dezena) as dezenas_diferentes,
                GROUP_CONCAT(DISTINCT dezena ORDER BY dezena) as dezenas_acertadas
            FROM analises_tecnicas
            WHERE acertou = 1
            GROUP BY tecnica_id, tecnica_nome, tecnica_categoria, campo_usado
            ORDER BY total_acertos DESC, concursos_diferentes DESC
            LIMIT ?
        ''', (top_n,))

        top_tecnicas = []
        for row in cursor.fetchall():
            top_tecnicas.append({
                'rank': len(top_tecnicas) + 1,
                'tecnica_id': row['tecnica_id'],
                'tecnica_nome': row['tecnica_nome'],
                'categoria': row['tecnica_categoria'],
                'campo': row['campo_usado'],
                'total_acertos': row['total_acertos'],
                'concursos_diferentes': row['concursos_diferentes'],
                'dezenas_diferentes': row['dezenas_diferentes'],
                'dezenas_acertadas': row['dezenas_acertadas']
            })

        # Insights automáticos
        insights = []

        # Insight 1: Categoria mais eficaz
        cursor.execute('''
            SELECT
                tecnica_categoria,
                COUNT(*) as acertos
            FROM analises_tecnicas
            WHERE acertou = 1
            GROUP BY tecnica_categoria
            ORDER BY acertos DESC
            LIMIT 1
        ''')
        cat_row = cursor.fetchone()
        if cat_row:
            insights.append({
                'tipo': 'CATEGORIA_MAIS_EFICAZ',
                'titulo': f'Categoria mais eficaz: {cat_row["tecnica_categoria"]}',
                'descricao': f'A categoria "{cat_row["tecnica_categoria"]}" tem {cat_row["acertos"]} acertos registrados.',
                'valor': cat_row['tecnica_categoria'],
                'metrica': cat_row['acertos']
            })

        # Insight 2: Campo mais produtivo
        cursor.execute('''
            SELECT
                campo_usado,
                COUNT(*) as acertos
            FROM analises_tecnicas
            WHERE acertou = 1
            GROUP BY campo_usado
            ORDER BY acertos DESC
            LIMIT 1
        ''')
        campo_row = cursor.fetchone()
        if campo_row:
            insights.append({
                'tipo': 'CAMPO_MAIS_PRODUTIVO',
                'titulo': f'Campo mais produtivo: {campo_row["campo_usado"]}',
                'descricao': f'O campo "{campo_row["campo_usado"]}" gerou {campo_row["acertos"]} acertos.',
                'valor': campo_row['campo_usado'],
                'metrica': campo_row['acertos']
            })

        # Insight 3: Dezena mais "descoberta"
        cursor.execute('''
            SELECT
                dezena,
                COUNT(*) as vezes_descoberta,
                COUNT(DISTINCT tecnica_id) as tecnicas_diferentes
            FROM analises_tecnicas
            WHERE acertou = 1
            GROUP BY dezena
            ORDER BY vezes_descoberta DESC
            LIMIT 1
        ''')
        dez_row = cursor.fetchone()
        if dez_row:
            insights.append({
                'tipo': 'DEZENA_MAIS_DESCOBERTA',
                'titulo': f'Dezena mais "descoberta": {dez_row["dezena"]}',
                'descricao': f'A dezena {dez_row["dezena"]} foi descoberta {dez_row["vezes_descoberta"]} vezes usando {dez_row["tecnicas_diferentes"]} técnicas diferentes.',
                'valor': dez_row['dezena'],
                'metrica': dez_row['vezes_descoberta']
            })

        # Insight 4: Taxa média de cobertura
        cursor.execute('''
            SELECT
                AVG(percentual_cobertura) as media_cobertura,
                AVG(dezenas_com_tecnica) as media_dezenas_com_tecnica
            FROM analises_resumo
        ''')
        cob_row = cursor.fetchone()
        if cob_row:
            insights.append({
                'tipo': 'TAXA_MEDIA_COBERTURA',
                'titulo': f'Taxa média de cobertura: {cob_row["media_cobertura"]:.2f}%',
                'descricao': f'Em média, {cob_row["media_dezenas_com_tecnica"]:.1f} de 7 dezenas são descobertas por técnicas.',
                'valor': cob_row['media_cobertura'],
                'metrica': cob_row['media_dezenas_com_tecnica']
            })

        # Dezenas literais (técnicas TEC-E-01, TEC-E-02, TEC-J-01, TEC-J-02)
        cursor.execute('''
            SELECT DISTINCT
                concurso_analisado,
                dezena,
                tecnica_id,
                tecnica_nome,
                formula,
                calculo_passo_a_passo
            FROM analises_tecnicas
            WHERE acertou = 1
              AND tecnica_id IN ('TEC-E-01', 'TEC-E-02', 'TEC-J-01', 'TEC-J-02', 'TEC-J-03', 'TEC-J-04')
            ORDER BY concurso_analisado DESC, dezena
        ''')

        dezenas_literais = []
        for row in cursor.fetchall():
            dezenas_literais.append({
                'concurso': row['concurso_analisado'],
                'dezena': row['dezena'],
                'tecnica_id': row['tecnica_id'],
                'tecnica_nome': row['tecnica_nome'],
                'formula': row['formula'],
                'calculo': row['calculo_passo_a_passo'],
                'tipo': 'LITERAL_DATA' if row['tecnica_id'].startswith('TEC-E') else 'LITERAL_ANO'
            })

        conn.close()

        return jsonify({
            'sucesso': True,
            'total_analises_base': total_registros,
            'top_tecnicas': top_tecnicas,
            'insights': insights,
            'dezenas_literais': dezenas_literais
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao gerar ranking: {str(e)}'
        }), 500

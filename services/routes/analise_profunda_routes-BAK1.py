"""
Rotas Flask para Análise Profunda de Técnicas
Sistema de descoberta de padrões matemáticos em concursos do Dia de Sorte
"""

from flask import Blueprint, render_template, request, jsonify
# from services.analise_profunda_service import analisar_concurso_profundo
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
        # resultado = analisar_concurso_profundo(concurso, DB_PATH)
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

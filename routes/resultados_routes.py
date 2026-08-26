# Sistema: Análise por Posição - Dia de Sorte
# Rotas: Resultados - Exibição de Concursos
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify, request, render_template
from services.resultados_service import ResultadosService

# Criar Blueprint
resultados_bp = Blueprint('resultados', __name__)

# ============================================================
# ROTAS DE PÁGINA (HTML)
# ============================================================

@resultados_bp.route('/resultados')
def pagina_resultados():
    """
    Página principal de resultados.
    Exibe os últimos concursos do Dia de Sorte.
    """
    return render_template('resultados.html')


@resultados_bp.route('/resultados/')
def pagina_resultados_barra():
    """Rota alternativa com barra final"""
    return render_template('resultados.html')


# ============================================================
# ROTAS DE API (JSON)
# ============================================================

@resultados_bp.route('/api/resultados/ultimo', methods=['GET'])
def api_ultimo_resultado():
    """
    Retorna o último concurso registrado.
    """
    try:
        resultado = ResultadosService.obter_ultimo_concurso()

        if resultado:
            return jsonify({
                'sucesso': True,
                'concurso': resultado
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum concurso encontrado'
            }), 404

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@resultados_bp.route('/api/resultados/concurso/<int:numero>', methods=['GET'])
def api_concurso_por_numero(numero):
    """
    Retorna os dados de um concurso específico.
    """
    try:
        resultado = ResultadosService.obter_concurso_por_numero(numero)

        if resultado:
            return jsonify({
                'sucesso': True,
                'concurso': resultado
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': f'Concurso {numero} não encontrado'
            }), 404

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@resultados_bp.route('/api/resultados/ultimos', methods=['GET'])
def api_ultimos_resultados():
    """
    Retorna os últimos N concursos.
    Query params:
        - quantidade: número de concursos (default: 6, max: 100)
    """
    try:
        quantidade = request.args.get('quantidade', 6, type=int)
        resultado = ResultadosService.obter_ultimos_concursos(quantidade)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@resultados_bp.route('/api/resultados/paginados', methods=['GET'])
def api_resultados_paginados():
    """
    Retorna concursos com paginação.
    Query params:
        - pagina: número da página (default: 1)
        - por_pagina: concursos por página (default: 6, max: 50)
    """
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 6, type=int)

        resultado = ResultadosService.obter_concursos_paginados(pagina, por_pagina)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@resultados_bp.route('/api/resultados/intervalo', methods=['GET'])
def api_resultados_intervalo():
    """
    Retorna concursos em um intervalo específico.
    Query params:
        - inicio: número do concurso inicial (obrigatório)
        - fim: número do concurso final (obrigatório)
    """
    try:
        inicio = request.args.get('inicio', type=int)
        fim = request.args.get('fim', type=int)

        if not inicio or not fim:
            return jsonify({
                'sucesso': False,
                'erro': 'Parâmetros inicio e fim são obrigatórios'
            }), 400

        resultado = ResultadosService.obter_concursos_intervalo(inicio, fim)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@resultados_bp.route('/api/resultados/estatisticas', methods=['GET'])
def api_estatisticas_resultados():
    """
    Retorna estatísticas gerais dos concursos.
    """
    try:
        resultado = ResultadosService.obter_estatisticas_gerais()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@resultados_bp.route('/api/resultados/anteriores', methods=['GET'])
def api_resultados_anteriores():
    """
    Retorna concursos anteriores a um número específico.
    Query params:
        - antes_de: número do concurso de referência (obrigatório)
        - quantidade: número de concursos a retornar (default: 6)
    """
    try:
        antes_de = request.args.get('antes_de', type=int)
        quantidade = request.args.get('quantidade', 6, type=int)

        if not antes_de:
            return jsonify({
                'sucesso': False,
                'erro': 'Parâmetro antes_de é obrigatório'
            }), 400

        # Calcular intervalo
        inicio = antes_de - quantidade
        fim = antes_de - 1

        if inicio < 1:
            inicio = 1

        resultado = ResultadosService.obter_concursos_intervalo(inicio, fim)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@resultados_bp.route('/api/resultados/posteriores', methods=['GET'])
def api_resultados_posteriores():
    """
    Retorna concursos posteriores a um número específico.
    Query params:
        - depois_de: número do concurso de referência (obrigatório)
        - quantidade: número de concursos a retornar (default: 6)
    """
    try:
        depois_de = request.args.get('depois_de', type=int)
        quantidade = request.args.get('quantidade', 6, type=int)

        if not depois_de:
            return jsonify({
                'sucesso': False,
                'erro': 'Parâmetro depois_de é obrigatório'
            }), 400

        # Calcular intervalo
        inicio = depois_de + 1
        fim = depois_de + quantidade

        resultado = ResultadosService.obter_concursos_intervalo(inicio, fim)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@resultados_bp.route('/api/resultados/enviar-conferencia', methods=['POST'])
def enviar_conferencia():
    import os
    from services.conferencia_historica_service import ConferenciaHistoricaService
    from flask import request
    
    data = request.json
    nome_arquivo = data.get('nome_arquivo', 'Resultados_Ajustados.txt')
    conteudo = data.get('conteudo')
    
    if not conteudo:
        return jsonify({'sucesso': False, 'erro': 'Conteúdo não fornecido'}), 400
        
    afin_dir = os.path.join(os.getcwd(), 'conferencia_filtros-baixados')
    os.makedirs(afin_dir, exist_ok=True)
    
    path_arquivo = os.path.join(afin_dir, nome_arquivo)
    
    with open(path_arquivo, 'w') as f:
        f.write(conteudo)
        
    try:
        sessao = ConferenciaHistoricaService.criar_sessao(
            nome_arquivo=nome_arquivo,
            descricao=f"Resultados Alterados: {nome_arquivo}",
            estrategia='ordenada', filtro_min=4
        )
        ConferenciaHistoricaService.processar_arquivo(sessao.id, conteudo)
        
        return jsonify({'sucesso': True, 'mensagem': f"Arquivo enviado com sucesso para a Central de Conferência!"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

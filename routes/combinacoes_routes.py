"""
Routes para Geração de Combinações Inteligentes - Dia de Sorte
"""

from flask import Blueprint, request, jsonify, render_template, Response
from services.combinacoes_service import CombinacoesService

# Criar blueprint
combinacoes_bp = Blueprint('combinacoes', __name__)


@combinacoes_bp.route('/combinacoes-inteligentes')
def pagina_combinacoes():
    """Página principal de geração de combinações inteligentes"""
    return render_template('combinacoes.html')


@combinacoes_bp.route('/api/combinacoes/concursos-disponiveis', methods=['GET'])
def listar_concursos_disponiveis():
    """
    Lista todos os concursos que possuem apostas cadastradas

    Returns:
        JSON com lista de concursos
    """
    try:
        resultado = CombinacoesService.listar_concursos_com_apostas()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao listar concursos: {str(e)}'
        }), 500


@combinacoes_bp.route('/api/combinacoes/apostas/<int:concurso>', methods=['GET'])
def obter_apostas(concurso):
    """
    Obtém as apostas de um concurso específico

    Args:
        concurso: Número do concurso

    Returns:
        JSON com apostas e universo de números
    """
    try:
        resultado = CombinacoesService.obter_apostas_concurso(concurso)

        if resultado['sucesso']:
            # Adicionar universo
            universo = CombinacoesService.extrair_universo(resultado['apostas'])
            resultado['universo'] = universo
            resultado['total_universo'] = len(universo)

            # Calcular total de combinações possíveis
            from math import comb
            if len(universo) >= 7:
                resultado['total_combinacoes'] = comb(len(universo), 7)
            else:
                resultado['total_combinacoes'] = 0

            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao obter apostas: {str(e)}'
        }), 500


@combinacoes_bp.route('/api/combinacoes/gerar', methods=['POST'])
def gerar_combinacoes():
    """
    Gera combinações analisadas com filtros e ordenação

    Request JSON:
        {
            "concurso": 1200,
            "filtros": {
                "soma_min": 95,
                "soma_max": 155,
                "pares": [3, 4],
                "max_sequencia": 3,
                "score_min": 50,
                "apenas_proporcao_ideal": false,
                "excluir_soma_fora": true
            },
            "ordenacao": "score_desc",
            "pagina": 1,
            "por_pagina": 50,
            "mes_aposta": 9
        }

    Returns:
        JSON com combinações paginadas e analisadas
    """
    try:
        dados = request.get_json()

        if not dados or 'concurso' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'dados_invalidos',
                'mensagem': 'É necessário fornecer o número do concurso'
            }), 400

        concurso = dados['concurso']
        filtros = dados.get('filtros', {})
        ordenacao = dados.get('ordenacao', 'score_desc')
        pagina = dados.get('pagina', 1)
        por_pagina = dados.get('por_pagina', 50)
        mes_aposta = dados.get('mes_aposta')

        # Validar por_pagina (máximo 100)
        if por_pagina > 100:
            por_pagina = 100

        resultado = CombinacoesService.gerar_combinacoes_analisadas(
            numero_concurso=concurso,
            filtros=filtros,
            ordenacao=ordenacao,
            pagina=pagina,
            por_pagina=por_pagina,
            mes_aposta=mes_aposta
        )

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao gerar combinações: {str(e)}'
        }), 500


@combinacoes_bp.route('/api/combinacoes/estatisticas/<int:concurso>', methods=['GET'])
def obter_estatisticas(concurso):
    """
    Obtém estatísticas das combinações de um concurso

    Args:
        concurso: Número do concurso

    Returns:
        JSON com estatísticas resumidas
    """
    try:
        resultado = CombinacoesService.obter_estatisticas_combinacoes(concurso)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao obter estatísticas: {str(e)}'
        }), 500


@combinacoes_bp.route('/api/combinacoes/exportar', methods=['POST'])
def exportar_combinacoes():
    """
    Exporta combinações para arquivo TXT

    Request JSON:
        {
            "concurso": 1200,
            "filtros": {...},
            "ordenacao": "score_desc",
            "limite": 1000,
            "mes_aposta": 9
        }

    Returns:
        Arquivo TXT para download
    """
    try:
        dados = request.get_json()

        if not dados or 'concurso' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'dados_invalidos',
                'mensagem': 'É necessário fornecer o número do concurso'
            }), 400

        concurso = dados['concurso']
        filtros = dados.get('filtros', {})
        ordenacao = dados.get('ordenacao', 'score_desc')
        limite = dados.get('limite')
        mes_aposta = dados.get('mes_aposta')

        resultado = CombinacoesService.exportar_combinacoes(
            numero_concurso=concurso,
            filtros=filtros,
            ordenacao=ordenacao,
            limite=limite,
            mes_aposta=mes_aposta
        )

        if resultado['sucesso']:
            # Retornar como arquivo TXT
            response = Response(
                resultado['conteudo'],
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename={resultado["nome_arquivo"]}'
                }
            )
            return response
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao exportar combinações: {str(e)}'
        }), 500


@combinacoes_bp.route('/api/combinacoes/validar/<int:concurso>', methods=['GET'])
def validar_concurso(concurso):
    """
    Valida se um concurso está pronto para geração de combinações

    Args:
        concurso: Número do concurso

    Returns:
        JSON com status de validação
    """
    try:
        # Obter apostas
        resultado = CombinacoesService.obter_apostas_concurso(concurso)

        if not resultado['sucesso']:
            return jsonify({
                'sucesso': False,
                'valido': False,
                'mensagem': resultado['mensagem']
            })

        # Extrair universo
        universo = CombinacoesService.extrair_universo(resultado['apostas'])

        if len(universo) < 7:
            return jsonify({
                'sucesso': True,
                'valido': False,
                'mensagem': f'Universo insuficiente: apenas {len(universo)} números únicos (mínimo: 7)',
                'universo': universo,
                'total_universo': len(universo)
            })

        from math import comb
        total_combinacoes = comb(len(universo), 7)

        return jsonify({
            'sucesso': True,
            'valido': True,
            'concurso': concurso,
            'universo': universo,
            'total_universo': len(universo),
            'total_combinacoes': total_combinacoes,
            'total_apostas': resultado['total_apostas'],
            'numeros_sorteados': resultado['numeros_sorteados'],
            'mes_sorte': resultado['mes_sorte'],
            'aviso': f'Serão geradas {total_combinacoes:,} combinações' if total_combinacoes > 50000 else None
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'valido': False,
            'erro': str(e),
            'mensagem': f'Erro ao validar concurso: {str(e)}'
        }), 500

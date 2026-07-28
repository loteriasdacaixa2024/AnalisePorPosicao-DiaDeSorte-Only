"""
Rotas de Análise Visual - Dia de Sorte
Blueprint para renderização de páginas e APIs de análise visual
"""

from flask import Blueprint, render_template, jsonify, request
from services.analise_visual_service import AnaliseVisualService

# Criar Blueprint
analise_visual_bp = Blueprint('analise_visual', __name__, url_prefix='/analise-visual')


# ============================================
# ROTAS DE PÁGINA
# ============================================

@analise_visual_bp.route('/')
def pagina_analise_visual():
    """
    Página principal de análise visual
    """
    return render_template('analise_visual.html')


# ============================================
# ROTAS DE API
# ============================================

@analise_visual_bp.route('/api/concursos')
def api_listar_concursos():
    """
    Lista todos os concursos com opções de filtro

    Query params:
        limite: Quantidade máxima de concursos
        ordem: 'desc' (padrão) ou 'asc'
        inicio: Concurso inicial (para range)
        fim: Concurso final (para range)
    """
    try:
        limite = request.args.get('limite', type=int)
        ordem = request.args.get('ordem', 'desc')
        inicio = request.args.get('inicio', type=int)
        fim = request.args.get('fim', type=int)

        # Se especificou range
        if inicio and fim:
            concursos = AnaliseVisualService.buscar_range_concursos(inicio, fim)
        else:
            concursos = AnaliseVisualService.buscar_todos_concursos(limite=limite, ordem=ordem)

        return jsonify({
            'sucesso': True,
            'total': len(concursos),
            'concursos': concursos
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@analise_visual_bp.route('/api/concurso/<int:numero>')
def api_buscar_concurso(numero):
    """
    Busca um concurso específico
    """
    try:
        concurso = AnaliseVisualService.buscar_concurso(numero)

        if concurso:
            return jsonify({
                'sucesso': True,
                'concurso': concurso
            })
        else:
            return jsonify({
                'sucesso': False,
                'erro': 'Concurso não encontrado'
            }), 404

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@analise_visual_bp.route('/api/estatisticas')
def api_estatisticas():
    """
    Retorna estatísticas gerais dos concursos
    """
    try:
        stats = AnaliseVisualService.obter_estatisticas_gerais()

        return jsonify({
            'sucesso': True,
            'estatisticas': stats
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500


@analise_visual_bp.route('/api/concursos/paginado')
def api_concursos_paginado():
    """
    Lista concursos com paginação

    Query params:
        pagina: Número da página (padrão 1)
        por_pagina: Itens por página (padrão 50)
        ordem: 'desc' (padrão) ou 'asc'
    """
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        ordem = request.args.get('ordem', 'desc')

        # Limitar por_pagina para evitar sobrecarga
        por_pagina = min(por_pagina, 200)

        # Buscar todos e paginar
        todos_concursos = AnaliseVisualService.buscar_todos_concursos(ordem=ordem)
        total = len(todos_concursos)

        # Calcular índices
        inicio = (pagina - 1) * por_pagina
        fim = inicio + por_pagina

        # Fatiar
        concursos_pagina = todos_concursos[inicio:fim]

        # Calcular total de páginas
        total_paginas = (total + por_pagina - 1) // por_pagina

        return jsonify({
            'sucesso': True,
            'pagina_atual': pagina,
            'por_pagina': por_pagina,
            'total_concursos': total,
            'total_paginas': total_paginas,
            'tem_anterior': pagina > 1,
            'tem_proxima': pagina < total_paginas,
            'concursos': concursos_pagina
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

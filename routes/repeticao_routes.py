# Sistema: Análise por Posição - Dia de Sorte
# Módulo: posicao_por_repeticao
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify, render_template
from services.repeticao_service import RepeticaoService

repeticao_bp = Blueprint('repeticao', __name__)

@repeticao_bp.route('/repeticao')
def pagina_repeticao():
    """Página principal da análise de repetição por posição"""
    return render_template('repeticao.html')


# ============================================
# APIs DE ANÁLISE DE REPETIÇÃO
# ============================================

@repeticao_bp.route('/api/repeticao/analise-completa', methods=['GET'])
def analise_completa():
    """
    Retorna análise completa de repetição entre concursos.
    Inclui rankings, insights e recomendações.
    """
    return jsonify(RepeticaoService.analisar_repeticoes_completo())


@repeticao_bp.route('/api/repeticao/resumo', methods=['GET'])
def resumo():
    """
    Retorna resumo compacto para uso no Gerador de Palpites.
    Apenas TOP 3 posições e insight principal.
    """
    return jsonify(RepeticaoService.resumo_para_gerador())


@repeticao_bp.route('/api/repeticao/historico', methods=['GET'])
def historico():
    """
    Retorna histórico detalhado das repetições.
    Query param: limite (default 50)
    """
    from flask import request
    limite = request.args.get('limite', 50, type=int)
    limite = min(limite, 100)  # Máximo 100
    return jsonify(RepeticaoService.historico_detalhado(limite))

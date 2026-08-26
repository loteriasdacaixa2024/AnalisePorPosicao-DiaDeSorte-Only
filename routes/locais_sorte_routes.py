from flask import Blueprint, jsonify, request
from services.locais_sorte_service import LocaisSorteService

locais_sorte_bp = Blueprint('locais_sorte', __name__)


def _filtros_da_request():
    """Monta dict de filtros a partir dos query params."""
    chaves = [
        'concurso', 'local', 'acertos', 'tipo_aposta', 'canal_vendas',
        'busca_global', 'estrategia', 'unidade_loterica', 'cidade',
        'teimosinha', 'valor_premio', 'cotas', 'qtd_numeros_apostados',
    ]
    filtros = {}
    for chave in chaves:
        valor = request.args.get(chave, '').strip()
        if valor:
            filtros[chave] = valor
    return filtros or None


@locais_sorte_bp.route('/api/locais-sorte-dia/importar', methods=['POST'])
def importar_locais_sorte_dia():
    """ETL: lê JSON da pasta Dia-de-Sorte e persiste no SQL (incremental)."""
    try:
        stats = LocaisSorteService.importar_arquivos_json()
        LocaisSorteService._cache_comparativo = {'dados': None, 'ts': 0}
        return jsonify({'sucesso': True, **stats}), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@locais_sorte_bp.route('/api/locais-sorte-dia/resumo', methods=['GET'])
def resumo_locais_sorte_dia():
    try:
        return jsonify(LocaisSorteService.obter_resumo()), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@locais_sorte_bp.route('/api/locais-sorte-dia/relatorio', methods=['GET'])
def relatorio_locais_sorte_dia():
    try:
        pagina = max(1, int(request.args.get('pagina', 1)))
        por_pagina = min(200, max(10, int(request.args.get('por_pagina', 50))))
        ordenacao = request.args.get('ordenacao', 'concurso')
        ord_dir = request.args.get('ord_dir', 'desc')
        dados = LocaisSorteService.obter_relatorio_paginado(
            filtros=_filtros_da_request(),
            pagina=pagina,
            por_pagina=por_pagina,
            ordenacao=ordenacao,
            ord_dir=ord_dir,
        )
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@locais_sorte_bp.route('/api/locais-sorte-dia/comparativo', methods=['GET'])
def comparativo_locais_sorte_dia():
    try:
        return jsonify(LocaisSorteService.obter_comparativo_estratificacao()), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@locais_sorte_bp.route('/api/locais-sorte-dia/padroes-acertos', methods=['GET'])
def padroes_acertos_locais_sorte_dia():
    try:
        return jsonify(LocaisSorteService.obter_padroes_faixa_acertos()), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

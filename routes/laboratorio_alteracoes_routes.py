# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request

from services.laboratorio_alteracoes_service import LaboratorioAlteracoesService

laboratorio_alteracoes_bp = Blueprint('laboratorio_alteracoes', __name__)


@laboratorio_alteracoes_bp.route('/api/laboratorio-alteracoes/concurso', methods=['GET'])
def api_concurso():
    concurso = request.args.get('concurso', type=int)
    dados = LaboratorioAlteracoesService.obter_concurso(concurso)
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Concurso não encontrado'}), 404
    return jsonify({'sucesso': True, 'concurso': dados})


@laboratorio_alteracoes_bp.route('/api/laboratorio-alteracoes/concursos', methods=['GET'])
def api_concursos_lista():
    limite = request.args.get('limite', 80, type=int)
    return jsonify({
        'sucesso': True,
        'concursos': LaboratorioAlteracoesService.listar_concursos_recentes(limite),
    })


def _limite_apostas_body(body):
    if body.get('permitir_mais_apostas'):
        req = body.get('limite_apostas')
        if req is not None:
            return min(int(req), LaboratorioAlteracoesService.MAX_APOSTAS_EXPANDIDO)
        return LaboratorioAlteracoesService.MAX_APOSTAS_EXPANDIDO
    return LaboratorioAlteracoesService.MAX_APOSTAS


def _rejeitar_excesso_apostas(lista_raw, limite):
    if len(lista_raw or []) > limite:
        return jsonify({
            'sucesso': False,
            'erro': f'Máximo de {limite} apostas por lote.',
        }), 400
    return None


@laboratorio_alteracoes_bp.route('/api/laboratorio-alteracoes/gerar-alteradas', methods=['POST'])
def api_gerar_alteradas():
    body = request.get_json(silent=True) or {}
    limite = _limite_apostas_body(body)
    excesso = _rejeitar_excesso_apostas(body.get('originais'), limite)
    if excesso:
        return excesso
    originais = LaboratorioAlteracoesService.limitar_apostas(body.get('originais') or [], limite)
    if not originais:
        return jsonify({'sucesso': False, 'erro': f'Nenhuma aposta válida (máx. {limite}, mín. 7 dezenas).'}), 400
    modo = body.get('modo') or 'auto'
    concurso = LaboratorioAlteracoesService.obter_concurso(body.get('concurso_ref'))
    alteradas = LaboratorioAlteracoesService.gerar_alteradas_lote(
        originais,
        modo=modo,
        fixas_por_linha=body.get('fixas_por_linha'),
        fixar_mes_por_linha=body.get('fixar_mes_por_linha'),
        numeros_concurso=concurso.get('numeros') if concurso else None,
    )
    analise = None
    if concurso:
        analise = LaboratorioAlteracoesService.montar_analise(originais, alteradas, concurso)
    return jsonify({
        'sucesso': True,
        'originais': originais,
        'alteradas': alteradas,
        'concurso': concurso,
        'analise': analise,
    })


@laboratorio_alteracoes_bp.route('/api/laboratorio-alteracoes/analisar', methods=['POST'])
def api_analisar():
    body = request.get_json(silent=True) or {}
    limite = _limite_apostas_body(body)
    excesso = _rejeitar_excesso_apostas(body.get('originais'), limite)
    if excesso:
        return excesso
    excesso_alt = _rejeitar_excesso_apostas(body.get('alteradas'), limite)
    if excesso_alt:
        return excesso_alt
    originais = LaboratorioAlteracoesService.limitar_apostas(body.get('originais') or [], limite)
    alteradas_raw = body.get('alteradas') or []
    alteradas = LaboratorioAlteracoesService.limitar_apostas(alteradas_raw, limite)
    if len(originais) != len(alteradas):
        n = min(len(originais), len(alteradas), limite)
        originais = originais[:n]
        alteradas = alteradas[:n]
    if not originais:
        return jsonify({'sucesso': False, 'erro': f'Informe até {limite} apostas.'}), 400
    concurso = LaboratorioAlteracoesService.obter_concurso(body.get('concurso_ref'))
    if not concurso:
        return jsonify({'sucesso': False, 'erro': 'Concurso de referência inválido.'}), 400
    analise = LaboratorioAlteracoesService.montar_analise(originais, alteradas, concurso)
    return jsonify({
        'sucesso': True,
        'concurso': concurso,
        'analise': analise,
    })


@laboratorio_alteracoes_bp.route('/api/laboratorio-alteracoes/salvar', methods=['POST'])
def api_salvar():
    body = request.get_json(silent=True) or {}
    analise = body.get('analise')
    concurso_ref = body.get('concurso_ref')
    if not analise or not concurso_ref:
        return jsonify({'sucesso': False, 'erro': 'Análise ou concurso ausente.'}), 400
    return jsonify(LaboratorioAlteracoesService.salvar_registro(
        int(concurso_ref),
        body.get('origem') or 'manual',
        analise,
    ))


@laboratorio_alteracoes_bp.route('/api/laboratorio-alteracoes/historico', methods=['GET'])
def api_historico():
    limite = request.args.get('limite', 30, type=int)
    return jsonify({
        'sucesso': True,
        'historico': LaboratorioAlteracoesService.listar_historico(limite),
    })

# Sistema: Análise por Posição - Dia de Sorte
# API: Ciclo 01–31 por posição de sorteio (P1–P7)

from flask import Blueprint, jsonify, request

from services.ciclo_por_posicao_service import CicloPorPosicaoService
from services.impressao_30_posicoes_service import Impressao30PosicoesService

ciclo_por_posicao_bp = Blueprint('ciclo_por_posicao', __name__)


@ciclo_por_posicao_bp.route('/api/estatisticas/ciclo-por-posicao/resumo', methods=['GET'])
def ciclo_por_posicao_resumo():
    try:
        payload = {
            'sucesso': True,
            'posicoes': CicloPorPosicaoService.resumo_todas_posicoes(),
        }
        if request.args.get('impressao', '').lower() in ('1', 'true', 'sim'):
            qtd = request.args.get('apostas', default=30, type=int)
            dez = request.args.get('dezenas', default=7, type=int)
            qtd = max(1, min(qtd or 30, 50))
            dez = max(7, min(dez or 7, 15))
            payload['impressao'] = Impressao30PosicoesService.pacote_impressao_completo(qtd, dez)
        return jsonify(payload)
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@ciclo_por_posicao_bp.route('/api/estatisticas/ciclo-por-posicao/gerar-apostas', methods=['POST'])
def ciclo_por_posicao_gerar_apostas():
    try:
        body = request.get_json(silent=True) or {}
        qtd = body.get('quantidade', 10)
        dez = body.get('dezenas_por_aposta', 7)
        foco = body.get('posicao_foco')
        if foco in ('', 'todas', None):
            foco = None
        else:
            foco = int(foco)
        return jsonify(
            CicloPorPosicaoService.gerar_apostas_inteligentes(
                quantidade=qtd,
                dezenas_por_aposta=dez,
                posicao_foco=foco,
            )
        )
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@ciclo_por_posicao_bp.route('/api/estatisticas/ciclo-por-posicao/impressao-30', methods=['GET'])
def ciclo_impressao_30():
    try:
        qtd = request.args.get('apostas', default=30, type=int)
        dez = request.args.get('dezenas', default=7, type=int)
        qtd = max(1, min(qtd, 50))
        dez = max(7, min(dez, 15))
        return jsonify(Impressao30PosicoesService.pacote_impressao_completo(qtd, dez))
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@ciclo_por_posicao_bp.route('/api/estatisticas/ciclo-por-posicao/<int:posicao>', methods=['GET'])
def ciclo_por_posicao_detalhe(posicao):
    try:
        if posicao < 1 or posicao > 7:
            return jsonify({'sucesso': False, 'erro': 'Posição deve ser de 1 a 7'}), 400
        n = request.args.get('n_concursos', type=int)
        data = CicloPorPosicaoService.analise_posicao(posicao)
        if n and n > 0:
            data['simulacao_n_concursos'] = CicloPorPosicaoService.simular_n_concursos(posicao, n)
        return jsonify({'sucesso': True, 'dados': data})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

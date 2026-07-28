# -*- coding: utf-8 -*-
"""
Rotas de API para gerenciar as cores dos meses
Sistema: Análise por Posição - Dia de Sorte
Desenvolvido para: Márcio Fernando Maia
"""

from flask import Blueprint, request, jsonify, make_response
from services.cores_meses_service import CoresMesesService

cores_meses_bp = Blueprint('cores_meses', __name__)


@cores_meses_bp.route('/api/cores-meses/listar', methods=['GET'])
def listar_cores_meses():
    """
    API para listar todas as cores dos meses.
    Retorna as 12 cores em formato JSON.
    """
    resultado = CoresMesesService.obter_todas_cores()
    return jsonify(resultado)


@cores_meses_bp.route('/api/cores-meses/css', methods=['GET'])
def obter_cores_css():
    """
    API para obter as cores em formato de dicionário para JavaScript.
    Útil para aplicações front-end.
    """
    resultado = CoresMesesService.obter_cores_css()
    return jsonify(resultado)


@cores_meses_bp.route('/api/cores-meses/atualizar', methods=['POST'])
def atualizar_cor_mes():
    """
    API para atualizar a cor de um mês específico.

    Body JSON esperado:
    {
        "mes": 0,  // 0-11 (Janeiro-Dezembro)
        "cor_hex": "#ff0000"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Dados não fornecidos'
            }), 400

        mes = data.get('mes')
        cor_hex = data.get('cor_hex')

        if mes is None:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Mês não fornecido'
            }), 400

        if not cor_hex:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Cor não fornecida'
            }), 400

        resultado = CoresMesesService.atualizar_cor(mes, cor_hex)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao processar requisição: {str(e)}'
        }), 500


@cores_meses_bp.route('/api/cores-meses/atualizar-multiplas', methods=['POST'])
def atualizar_multiplas_cores():
    """
    API para atualizar várias cores de uma vez.

    Body JSON esperado:
    {
        "cores": {
            "0": "#ff0000",
            "1": "#00ff00",
            ...
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'cores' not in data:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Cores não fornecidas'
            }), 400

        cores_dict = data['cores']

        if not isinstance(cores_dict, dict):
            return jsonify({
                'sucesso': False,
                'mensagem': 'Formato de cores inválido'
            }), 400

        resultado = CoresMesesService.atualizar_varias_cores(cores_dict)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao processar requisição: {str(e)}'
        }), 500


@cores_meses_bp.route('/api/cores-meses/restaurar-padrao', methods=['POST'])
def restaurar_cores_padrao():
    """
    API para restaurar todas as cores para os valores padrão.
    """
    try:
        resultado = CoresMesesService.restaurar_padrao()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao restaurar cores: {str(e)}'
        }), 500


@cores_meses_bp.route('/static/css/cores-meses.css')
def css_cores_meses():
    """
    Endpoint que serve um CSS dinâmico com as cores personalizadas dos meses.
    Este arquivo é incluído dinamicamente no base.html.
    """
    try:
        resultado = CoresMesesService.gerar_css_dinamico()

        if resultado['sucesso']:
            # Criar resposta com CSS
            response = make_response(resultado['css'])
            response.headers['Content-Type'] = 'text/css'
            # Cache por 1 hora (3600 segundos)
            response.headers['Cache-Control'] = 'public, max-age=3600'
            return response
        else:
            # Retornar CSS vazio em caso de erro
            response = make_response('/* Erro ao gerar CSS de cores dos meses */')
            response.headers['Content-Type'] = 'text/css'
            return response, 500

    except Exception as e:
        response = make_response(f'/* Erro: {str(e)} */')
        response.headers['Content-Type'] = 'text/css'
        return response, 500

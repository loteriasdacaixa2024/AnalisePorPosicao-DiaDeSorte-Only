"""
Routes para Análise Completa de Gaps e Dígitos Iniciais
Sistema: Dia de Sorte
Desenvolvido para: Márcio Fernando Maia
"""

from flask import Blueprint, jsonify, render_template
from services.analise_gaps_completo_service import AnaliseGapsCompletoService

analise_gaps_completo_bp = Blueprint('analise_gaps_completo', __name__)


@analise_gaps_completo_bp.route('/analise/gaps-completo')
def pagina_gaps_completo():
    """
    Página principal da análise de gaps completo

    Returns:
        HTML renderizado
    """
    return render_template('analise_gaps_completo.html')


@analise_gaps_completo_bp.route('/api/analise-gaps/digitos', methods=['GET'])
def analisar_digitos():
    """
    API para análise de dígitos iniciais

    Returns:
        JSON com top 3 padrões de dígitos, frequências e exemplos
    """
    try:
        resultado = AnaliseGapsCompletoService.analisar_digitos_iniciais()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao analisar dígitos: {str(e)}'
        }), 500


@analise_gaps_completo_bp.route('/api/analise-gaps/gaps', methods=['GET'])
def analisar_gaps():
    """
    API para análise de gaps (distâncias)

    Returns:
        JSON com top 3 gaps, padrões completos e exemplos
    """
    try:
        resultado = AnaliseGapsCompletoService.analisar_gaps()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao analisar gaps: {str(e)}'
        }), 500


@analise_gaps_completo_bp.route('/api/analise-gaps/cruzamento', methods=['GET'])
def cruzar_analises():
    """
    API para cruzamento de dígitos × gaps

    Returns:
        JSON com análise cruzada mostrando relação entre padrões
    """
    try:
        resultado = AnaliseGapsCompletoService.cruzar_digitos_gaps()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao cruzar análises: {str(e)}'
        }), 500


@analise_gaps_completo_bp.route('/api/analise-gaps/sugestoes', methods=['GET'])
def sugerir_jogos():
    """
    API para sugestões de jogos baseados nos padrões

    Returns:
        JSON com jogos sugeridos e justificativas
    """
    try:
        resultado = AnaliseGapsCompletoService.sugerir_jogos()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao sugerir jogos: {str(e)}'
        }), 500


@analise_gaps_completo_bp.route('/api/analise-gaps/completa', methods=['GET'])
def analise_completa():
    """
    API para executar TODAS as análises de uma vez
    (Dígitos, Gaps, Cruzamento e Sugestões)

    Returns:
        JSON com todas as análises
    """
    try:
        resultado = AnaliseGapsCompletoService.executar_analise_completa()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao executar análise completa: {str(e)}'
        }), 500

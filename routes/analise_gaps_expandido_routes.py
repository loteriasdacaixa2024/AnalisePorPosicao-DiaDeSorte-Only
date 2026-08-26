from flask import Blueprint, jsonify, render_template, request
from services.analise_gaps_expandido_service import AnaliseGapsExpandidoService

analise_gaps_expandido_bp = Blueprint('analise_gaps_expandido', __name__)


@analise_gaps_expandido_bp.route('/analise/gaps-expandido')
def pagina_gaps_expandido():
    """Página principal da análise de gaps expandida com sistema de toggle"""
    return render_template('analise_gaps_expandido.html')


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/executar', methods=['POST'])
def executar_analises():
    """
    Executa apenas as análises selecionadas pelo usuário

    Body JSON:
    {
        "analises": ["digitos", "gaps", "quadrantes", "pares_impares", ...]
    }

    Returns:
        Resultados apenas das análises ativas
    """
    try:
        dados = request.get_json()

        if not dados or 'analises' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campo "analises" é obrigatório'
            }), 400

        analises_ativas = dados.get('analises', [])

        if not analises_ativas or not isinstance(analises_ativas, list):
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhuma análise selecionada'
            }), 400

        # Executar apenas análises ativas
        resultado = AnaliseGapsExpandidoService.cruzar_analises(analises_ativas)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao executar análises: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/palpites', methods=['POST'])
def gerar_palpites():
    """
    Gera palpites inteligentes baseados nas análises ativas

    Body JSON:
    {
        "analises": ["digitos", "gaps", "duplas_trincas", ...]
    }

    Returns:
        Palpites realistas baseados em padrões históricos
    """
    try:
        dados = request.get_json()

        if not dados or 'analises' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campo "analises" é obrigatório'
            }), 400

        analises_ativas = dados.get('analises', [])

        # Gerar palpites baseados nas análises ativas
        resultado = AnaliseGapsExpandidoService.gerar_palpites_inteligentes(analises_ativas)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao gerar palpites: {str(e)}'
        }), 500


# Endpoints individuais para cada análise (opcionais, para uso avulso)

@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/digitos', methods=['GET'])
def analisar_digitos():
    """API para análise individual de dígitos iniciais"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_digitos_iniciais()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/gaps', methods=['GET'])
def analisar_gaps():
    """API para análise individual de gaps"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_gaps()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/quadrantes', methods=['GET'])
def analisar_quadrantes():
    """API para análise individual de quadrantes"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_quadrantes()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/pares-impares', methods=['GET'])
def analisar_pares_impares():
    """API para análise individual de pares/ímpares"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_pares_impares()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/altos-baixos', methods=['GET'])
def analisar_altos_baixos():
    """API para análise individual de altos/baixos"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_altos_baixos()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/quentes-frios', methods=['GET'])
def analisar_quentes_frios():
    """API para análise individual de números quentes/frios"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_quentes_frios()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/duplas-trincas', methods=['GET'])
def analisar_duplas_trincas():
    """API para análise individual de duplas/trincas recorrentes"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_duplas_trincas()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/repetidos-anterior', methods=['GET'])
def analisar_repetidos_anterior():
    """API para análise individual de repetidos do concurso anterior"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_repetidos_concurso_anterior()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/faixas-esquecidas', methods=['GET'])
def analisar_faixas_esquecidas():
    """API para análise individual de faixas esquecidas"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_faixas_esquecidas()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500


@analise_gaps_expandido_bp.route('/api/analise-gaps-expandido/perfil-mes-sorte', methods=['GET'])
def analisar_perfil_mes():
    """API para análise individual do perfil do mês da sorte"""
    try:
        resultado = AnaliseGapsExpandidoService.analisar_perfil_mes_sorte()
        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

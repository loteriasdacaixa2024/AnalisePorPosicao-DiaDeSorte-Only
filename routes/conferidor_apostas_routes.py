from flask import Blueprint, jsonify, render_template, request
from services.conferidor_apostas_service import ConferidorApostasService

conferidor_apostas_bp = Blueprint('conferidor_apostas', __name__)


@conferidor_apostas_bp.route('/analise/conferidor-apostas')
def pagina_conferidor():
    """Página principal do conferidor de apostas"""
    return render_template('conferidor_apostas.html')


@conferidor_apostas_bp.route('/api/conferidor/ultimo-sorteio', methods=['GET'])
def obter_ultimo_sorteio():
    """API para obter o último sorteio"""
    try:
        resultado = ConferidorApostasService.obter_ultimo_sorteio()

        if resultado is None:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum sorteio encontrado no banco de dados'
            }), 404

        return jsonify({
            'sucesso': True,
            'sorteio': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao buscar último sorteio: {str(e)}'
        }), 500


@conferidor_apostas_bp.route('/api/conferidor/sorteio/<int:concurso>', methods=['GET'])
def obter_sorteio_especifico(concurso):
    """API para obter um sorteio específico"""
    try:
        resultado = ConferidorApostasService.obter_sorteio_por_concurso(concurso)

        if resultado is None:
            return jsonify({
                'sucesso': False,
                'mensagem': f'Concurso {concurso} não encontrado'
            }), 404

        return jsonify({
            'sucesso': True,
            'sorteio': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao buscar concurso: {str(e)}'
        }), 500


@conferidor_apostas_bp.route('/api/conferidor/listar-concursos', methods=['GET'])
def listar_concursos():
    """API para listar todos os concursos disponíveis"""
    try:
        concursos = ConferidorApostasService.listar_todos_concursos()

        return jsonify({
            'sucesso': True,
            'concursos': concursos,
            'total': len(concursos)
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao listar concursos: {str(e)}'
        }), 500


@conferidor_apostas_bp.route('/api/conferidor/validar-apostas', methods=['POST'])
def validar_apostas():
    """API para validar apostas sem conferir"""
    try:
        dados = request.get_json()

        if not dados or 'apostas' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Dados inválidos. Campo "apostas" é obrigatório'
            }), 400

        texto_apostas = dados['apostas']
        resultado = ConferidorApostasService.processar_apostas(texto_apostas)

        return jsonify({
            'sucesso': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao validar apostas: {str(e)}'
        }), 500


@conferidor_apostas_bp.route('/api/conferidor/conferir', methods=['POST'])
def conferir_apostas():
    """API para conferir apostas contra um sorteio"""
    try:
        dados = request.get_json()

        if not dados or 'apostas' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Dados inválidos. Campo "apostas" é obrigatório'
            }), 400

        texto_apostas = dados['apostas']
        concurso = dados.get('concurso', None)

        # Processa e valida as apostas
        processamento = ConferidorApostasService.processar_apostas(texto_apostas)

        if processamento['total_validas'] == 0:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhuma aposta válida encontrada',
                'erros': processamento['erros']
            }), 400

        # Obtém o sorteio para conferir
        if concurso:
            sorteio = ConferidorApostasService.obter_sorteio_por_concurso(concurso)
        else:
            sorteio = ConferidorApostasService.obter_ultimo_sorteio()

        if sorteio is None:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Sorteio não encontrado'
            }), 404

        # Confere as apostas
        resultado = ConferidorApostasService.conferir_multiplas_apostas(
            processamento['apostas_validas'],
            sorteio
        )

        return jsonify({
            'sucesso': True,
            'resultado': resultado,
            'erros': processamento['erros']
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao conferir apostas: {str(e)}'
        }), 500

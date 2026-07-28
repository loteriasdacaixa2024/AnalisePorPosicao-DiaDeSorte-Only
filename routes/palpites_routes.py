# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Atualizado: Com validação de métodos e novas rotas

from flask import Blueprint, jsonify, request, render_template
from services.palpite_service import PalpiteService

palpites_bp = Blueprint('palpites', __name__)


def _mes_override_palpites_query():
    """Converte ?mes= da URL em int 1–12 ou None (automático / surpresinha)."""
    raw = request.args.get('mes')
    if raw is None or raw == '':
        return None
    s = str(raw).strip().lower()
    if s in ('aleatorio', 'aleatório', 'random'):
        return None
    try:
        v = int(s)
        return v if 1 <= v <= 12 else None
    except (TypeError, ValueError):
        return None


@palpites_bp.route('/palpites')
def pagina_palpites():
    return render_template('palpites.html')


@palpites_bp.route('/api/palpites/gerar', methods=['GET'])
def gerar():
    """
    Gera múltiplos palpites

    Parâmetros:
        tipo: Método de geração (default: inteligente)
        quantidade: Número de apostas a gerar (default: 5)

    Tipos disponíveis:
        - simples: Aleatório (Surpresinha)
        - frequencia: Baseado em frequência
        - atraso: Baseado em atraso
        - misto: 4 frequentes + 3 atrasados
        - posicao: Por posição
        - inteligente: 50% freq + 50% atraso
        - padroes_faltantes: Padrões que nunca saíram
        - padroes_frequentes: Top 10 padrões mais frequentes
        - padroes_atrasados: Top 10 padrões mais atrasados
        - digitos_iniciais_top3: Top 3 dígitos iniciais
    """
    tipo = request.args.get('tipo', 'inteligente')
    quantidade = int(request.args.get('quantidade', 5))

    # Limitar quantidade máxima
    if quantidade > 100:
        quantidade = 100
    if quantidade < 1:
        quantidade = 1

    # Validar se o método existe
    metodos_validos = PalpiteService.listar_metodos_disponiveis()

    if tipo not in metodos_validos:
        return jsonify({
            'sucesso': False,
            'erro': f'Método "{tipo}" não encontrado',
            'metodos_disponiveis': metodos_validos
        }), 400

    mes_override = _mes_override_palpites_query()

    # Gerar palpites
    resultado = PalpiteService.gerar_multiplos_palpites(quantidade, tipo, mes_override)

    return jsonify(resultado)


@palpites_bp.route('/api/palpites/metodos', methods=['GET'])
def listar_metodos():
    """
    Lista todos os métodos de geração disponíveis com suas descrições
    """
    return jsonify({
        'sucesso': True,
        'metodos': PalpiteService.obter_info_metodos(),
        'lista': PalpiteService.listar_metodos_disponiveis()
    })


@palpites_bp.route('/api/palpites/validar-metodo/<metodo>', methods=['GET'])
def validar_metodo(metodo):
    """
    Valida se um método de geração existe e retorna suas informações

    Parâmetros:
        metodo: Nome do método a validar
    """
    metodos_validos = PalpiteService.listar_metodos_disponiveis()
    info_metodos = PalpiteService.obter_info_metodos()

    if metodo in metodos_validos:
        return jsonify({
            'sucesso': True,
            'valido': True,
            'metodo': metodo,
            'info': info_metodos.get(metodo, {})
        })
    else:
        return jsonify({
            'sucesso': False,
            'valido': False,
            'metodo': metodo,
            'erro': f'Método "{metodo}" não encontrado',
            'metodos_disponiveis': metodos_validos
        }), 400


@palpites_bp.route('/api/palpites/gerar-unico', methods=['GET'])
def gerar_unico():
    """
    Gera um único palpite

    Parâmetros:
        tipo: Método de geração (default: inteligente)
    """
    tipo = request.args.get('tipo', 'inteligente')

    # Validar método
    metodos_validos = PalpiteService.listar_metodos_disponiveis()
    if tipo not in metodos_validos:
        return jsonify({
            'sucesso': False,
            'erro': f'Método "{tipo}" não encontrado',
            'metodos_disponiveis': metodos_validos
        }), 400

    mes_override = _mes_override_palpites_query()

    # Gerar palpite único
    resultado = PalpiteService.gerar_multiplos_palpites(1, tipo, mes_override)

    if resultado.get('palpites'):
        return jsonify({
            'sucesso': True,
            'palpite': resultado['palpites'][0]
        })
    else:
        return jsonify({
            'sucesso': False,
            'erro': 'Não foi possível gerar o palpite'
        }), 500


@palpites_bp.route('/api/palpites/surpresinha', methods=['GET'])
def surpresinha():
    """
    Gera um palpite totalmente aleatório (surpresinha)

    Parâmetros:
        quantidade: Número de apostas (default: 1)
    """
    quantidade = int(request.args.get('quantidade', 1))

    if quantidade > 50:
        quantidade = 50
    if quantidade < 1:
        quantidade = 1

    resultado = PalpiteService.gerar_multiplos_palpites(quantidade, 'simples')
    return jsonify(resultado)

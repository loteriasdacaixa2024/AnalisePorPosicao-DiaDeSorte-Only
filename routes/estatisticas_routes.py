# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify, render_template, request
from services import EstatisticaService

estatisticas_bp = Blueprint('estatisticas', __name__)

@estatisticas_bp.route('/estatisticas', strict_slashes=False)
def pagina_estatisticas():
    return render_template('estatisticas.html')

@estatisticas_bp.route('/api/estatisticas/frequencia-geral', methods=['GET'])
def frequencia_geral():
    return jsonify(EstatisticaService.frequencia_geral())

@estatisticas_bp.route('/api/estatisticas/frequencia-posicao/<int:posicao>', methods=['GET'])
def frequencia_posicao(posicao):
    return jsonify(EstatisticaService.frequencia_por_posicao(posicao))

@estatisticas_bp.route('/api/estatisticas/atrasados', methods=['GET'])
def atrasados():
    return jsonify(EstatisticaService.numeros_atrasados())

@estatisticas_bp.route('/api/estatisticas/mes-sorte', methods=['GET'])
def mes_sorte():
    return jsonify(EstatisticaService.estatisticas_mes_sorte())

@estatisticas_bp.route('/api/estatisticas/analise-filtrada/<int:posicao>/<int:numero>', methods=['GET'])
def analise_filtrada(posicao, numero):
    """
    Retorna análise de frequência filtrada por posição e número.
    Exemplo: /api/estatisticas/analise-filtrada/1/5
    Retorna quais números mais aparecem quando o 5 está na posição 1
    """
    return jsonify(EstatisticaService.analise_filtrada(posicao, numero))

@estatisticas_bp.route('/api/estatisticas/numeros-disponiveis/<int:posicao>', methods=['GET'])
def numeros_disponiveis(posicao):
    """
    Retorna os números que já apareceram em uma posição específica.
    Números que nunca apareceram não são retornados.
    Exemplo: /api/estatisticas/numeros-disponiveis/7
    """
    return jsonify(EstatisticaService.numeros_disponiveis_posicao(posicao))

# ============================================
# GERADOR DE PALPITES - Combinações Válidas
# ============================================

@estatisticas_bp.route('/api/estatisticas/combinacoes-validas', methods=['GET'])
def combinacoes_validas():
    """
    Retorna estatísticas de combinações válidas vs impossíveis.
    Calcula dinamicamente baseado no histórico de sorteios.
    """
    return jsonify(EstatisticaService.calcular_combinacoes_validas())

@estatisticas_bp.route('/api/estatisticas/combinacoes-impossiveis', methods=['GET'])
def combinacoes_impossiveis():
    """
    Lista todas as combinações impossíveis com paginação.
    Query params: pagina (default 1), por_pagina (default 100)
    """
    from flask import request
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = request.args.get('por_pagina', 100, type=int)
    return jsonify(EstatisticaService.listar_combinacoes_impossiveis(pagina, por_pagina))

@estatisticas_bp.route('/api/estatisticas/gerar-palpites/<int:quantidade>', methods=['GET'])
def gerar_palpites(quantidade):
    """
    Gera palpites válidos aleatórios.
    Exclui combinações impossíveis e já sorteadas.
    Exemplo: /api/estatisticas/gerar-palpites/10
    """
    # Limitar quantidade máxima
    quantidade = min(quantidade, 100)
    return jsonify(EstatisticaService.gerar_palpites(quantidade))

@estatisticas_bp.route('/api/sorteios/ultimo', methods=['GET'])
def ultimo_sorteio():
    """
    Retorna o último sorteio registrado no banco de dados.
    """
    return jsonify(EstatisticaService.ultimo_sorteio())


# ============================================
# NOVAS ROTAS - ANÁLISE POR POSIÇÃO
# ============================================

@estatisticas_bp.route('/api/estatisticas/atraso-por-posicao', methods=['GET'])
def atraso_por_posicao():
    """
    Retorna o atraso de cada número em cada posição específica.
    Diferente do atraso geral, mostra há quantos concursos cada número
    não aparece em cada posição.
    """
    return jsonify(EstatisticaService.atraso_por_posicao())

@estatisticas_bp.route('/api/estatisticas/nucleos-estrategicos', methods=['GET'])
def nucleos_estrategicos():
    """
    Retorna dados reais para geração de núcleos estratégicos:
    - Frequência por dezena
    - Atraso por dezena
    - Padrões (par/ímpar, baixo/alto)
    - Distribuição por quadrantes
    - Score calculado com dados reais
    """
    return jsonify(EstatisticaService.calcular_dados_nucleos())


@estatisticas_bp.route('/api/estatisticas/faixas-por-posicao', methods=['GET'])
def faixas_por_posicao():
    """
    Retorna a distribuição de faixas (baixos/médios/altos) em cada posição.
    - Baixos: 1-10
    - Médios: 11-20
    - Altos: 21-31
    """
    return jsonify(EstatisticaService.faixas_por_posicao())


@estatisticas_bp.route('/api/estatisticas/frequencia-relativa', methods=['GET'])
def frequencia_relativa():
    """
    Retorna a frequência relativa de cada número em cada posição.
    Mostra em qual posição cada número "prefere" aparecer.
    """
    return jsonify(EstatisticaService.frequencia_relativa_por_posicao())


# ============================================
# NOVAS ROTAS - FILTROS DE ORDENAÇÃO
# ============================================

@estatisticas_bp.route('/api/estatisticas/ordenacao', methods=['GET'])
def estatisticas_ordenacao():
    """
    Retorna estatísticas de ORDENAÇÃO do histórico:
    - Distribuição de soma
    - Distribuição pares/ímpares
    - Distribuição por faixas (baixos/médios/altos)
    - Padrões de sequências
    """
    return jsonify(EstatisticaService.analisar_estatisticas_ordenacao())


@estatisticas_bp.route('/api/estatisticas/validar-palpite', methods=['POST'])
def validar_palpite():
    """
    Valida um palpite usando critérios de ORDENAÇÃO.

    Body JSON esperado:
    {
        "numeros": [1, 5, 12, 18, 23, 27, 30],
        "filtros": {
            "soma_min": 95,
            "soma_max": 155,
            "paridade": ["3P/4I", "4P/3I"],
            "max_sequencia": 3
        }
    }
    """
    from flask import request
    dados = request.get_json()

    if not dados or 'numeros' not in dados:
        return jsonify({'erro': 'Números não informados'}), 400

    numeros = dados.get('numeros', [])
    filtros = dados.get('filtros', None)

    return jsonify(EstatisticaService.validar_palpite_ordenacao(numeros, filtros))


@estatisticas_bp.route('/api/estatisticas/gerar-palpites-filtrados', methods=['POST'])
def gerar_palpites_filtrados():
    """
    Gera palpites válidos aplicando filtros de POSIÇÃO e ORDENAÇÃO.

    Body JSON esperado:
    {
        "quantidade": 10,
        "filtros": {
            "soma_min": 95,
            "soma_max": 155,
            "paridade": ["3P/4I", "4P/3I", "2P/5I", "5P/2I"],
            "max_sequencia": 3
        }
    }
    """
    from flask import request
    dados = request.get_json()

    quantidade = dados.get('quantidade', 10) if dados else 10
    filtros = dados.get('filtros', None) if dados else None

    # Limitar quantidade máxima
    quantidade = min(quantidade, 50)

    return jsonify(EstatisticaService.gerar_palpites_com_filtros(quantidade, filtros))
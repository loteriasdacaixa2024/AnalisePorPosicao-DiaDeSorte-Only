from flask import Blueprint, jsonify, render_template, request
from services.desdobramento_service import DesdobramentoService

desdobramento_bp = Blueprint('desdobramento', __name__)


@desdobramento_bp.route('/desdobramentos')
def pagina_desdobramentos():
    """Renderiza a página unificada com todos os modelos de desdobramento"""
    from services.gerador_especial_service import GeradorEspecialService
    stats_mes = GeradorEspecialService.get_month_stats()
    return render_template('desdobramentos.html', stats_mes=stats_mes)


@desdobramento_bp.route('/desdobramento/modelo-a')
def pagina_desdobramento():
    """DEPRECATED: Redireciona para página unificada - Renderiza a página do desdobramento Modelo A"""
    return render_template('desdobramento-modelo-a.html')


@desdobramento_bp.route('/api/desdobramento/sugestao-automatica')
def api_sugestao_automatica():
    """
    API para obter sugestão automática de dezenas (Modelo A)
    Retorna: grupoA (5 fixas), grupoB (8 variáveis) e explicações
    """
    try:
        resultado = DesdobramentoService.gerar_sugestao_automatica()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@desdobramento_bp.route('/api/desdobramento/sugestao-modelo-b')
def api_sugestao_modelo_b():
    """
    API para obter sugestão automática de dezenas (Modelo B)
    Retorna: grupoA (5 dezenas), grupoB (5 dezenas)
    """
    try:
        resultado = DesdobramentoService.gerar_sugestao_modelo_b()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@desdobramento_bp.route('/api/desdobramento/sugestao-modelo-c')
def api_sugestao_modelo_c():
    """
    API para obter sugestão automática de dezenas (Modelo C)
    Retorna: grupoA (5 fixas), grupoC (8 variáveis para trios)
    """
    try:
        resultado = DesdobramentoService.gerar_sugestao_modelo_c()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@desdobramento_bp.route('/api/desdobramento/sugestao-modelo-d')
def api_sugestao_modelo_d():
    """
    API para obter sugestão automática de dezenas (Modelo D)
    Retorna: fixas (4), blocoA (5), blocoB (5), blocoC (5)
    """
    try:
        resultado = DesdobramentoService.gerar_sugestao_modelo_d()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@desdobramento_bp.route('/api/desdobramento/sugestao-modelo-e')
def api_sugestao_modelo_e():
    """
    API para obter sugestão automática de dezenas (Modelo E)
    Retorna: sorteio_base (7 números do último sorteio), complementares (24 números)

    Query params:
    - nivel: nível de redução (1-6, padrão: 2)
    """
    try:
        nivel = request.args.get('nivel', type=int, default=2)
        resultado = DesdobramentoService.gerar_sugestao_modelo_e(nivel)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@desdobramento_bp.route('/api/desdobramento/gerar-jogos', methods=['POST'])
def api_gerar_jogos():
    """
    API para gerar jogos do desdobramento (todos os modelos)

    Body JSON esperado (Modelo A):
    {
        "grupoA": [1, 5, 10, 15, 20],
        "grupoB": [2, 7, 12, 18, 22, 25, 28, 30],
        "mes": "Jan",
        "modelo": "A"
    }

    Body JSON esperado (Modelo B):
    {
        "grupoFixoA": [3, 4, 10, 12, 19],
        "grupoFixoB": [22, 23, 26, 30, 31],
        "variacoesA": [20, 31],
        "variacoesB": [3, 4, 10, 12, 19],
        "mes": "Jan",
        "modelo": "B"
    }

    Body JSON esperado (Modelo E):
    {
        "sorteio_base": [3, 7, 12, 18, 22, 28, 31],
        "complementares": [1, 2, 4, 5, 6, 8, ...],
        "nivel": 2,
        "mes": "Jan",
        "modelo": "E"
    }

    Retorna: lista de jogos gerados
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        modelo = data.get('modelo', 'A')
        mes = data.get('mes', 'Jan')

        # Modelo A (5 FIXAS + 2 VARIÁVEIS)
        if modelo == 'A':
            grupo_a = data.get('grupoA', [])
            grupo_b = data.get('grupoB', [])

            # Validar grupos
            validacao = DesdobramentoService.validar_grupos(grupo_a, grupo_b)

            if not validacao['valido']:
                return jsonify({
                    'erro': 'Validação falhou',
                    'erros': validacao['erros']
                }), 400

            # Gerar jogos
            resultado = DesdobramentoService.gerar_jogos(grupo_a, grupo_b, mes)

            if 'erro' in resultado:
                return jsonify(resultado), 400

            return jsonify(resultado), 200

        # Modelo B (DOIS GRUPOS FIXOS COM VARIAÇÕES CRUZADAS)
        elif modelo == 'B':
            grupo_a = data.get('grupoA', [])
            grupo_b = data.get('grupoB', [])

            # Gerar jogos Modelo B
            resultado = DesdobramentoService.gerar_jogos_modelo_b(
                grupo_a, grupo_b, mes
            )

            if 'erro' in resultado:
                return jsonify(resultado), 400

            return jsonify(resultado), 200

        # Modelo C (5 FIXAS + TRIOS VARIÁVEIS)
        elif modelo == 'C':
            grupo_a = data.get('grupoA', [])
            grupo_c = data.get('grupoC', [])

            # Gerar jogos Modelo C
            resultado = DesdobramentoService.gerar_jogos_modelo_c(
                grupo_a, grupo_c, mes
            )

            if 'erro' in resultado:
                return jsonify(resultado), 400

            return jsonify(resultado), 200

        # Modelo D (BLOCOS ROTATIVOS COM GARANTIA PROGRESSIVA)
        elif modelo == 'D':
            fixas = data.get('fixas', [])
            bloco_a = data.get('blocoA', [])
            bloco_b = data.get('blocoB', [])
            bloco_c = data.get('blocoC', [])

            # Gerar jogos Modelo D
            resultado = DesdobramentoService.gerar_jogos_modelo_d(
                fixas, bloco_a, bloco_b, bloco_c, mes
            )

            if 'erro' in resultado:
                return jsonify(resultado), 400

            return jsonify(resultado), 200

        # Modelo E (REDUÇÃO INTELIGENTE DO ÚLTIMO SORTEIO)
        elif modelo == 'E':
            sorteio_base = data.get('sorteio_base', [])
            complementares = data.get('complementares', [])
            nivel = data.get('nivel', 2)
            dezenas_por_jogo = data.get('dezenas_por_jogo', 7)  # Novo parâmetro: 7 a 15

            # Gerar jogos Modelo E
            resultado = DesdobramentoService.gerar_jogos_modelo_e(
                sorteio_base, complementares, nivel, mes, dezenas_por_jogo
            )

            if 'erro' in resultado:
                return jsonify(resultado), 400

            return jsonify(resultado), 200

        # Modelo F (BAIXA CONECTIVIDADE)
        elif modelo == 'F':
            ultimo_sorteio = data.get('ultimo_sorteio', [])
            base_preferida = data.get('base_preferida', [])
            
            resultado = DesdobramentoService.gerar_jogos_modelo_f(
                ultimo_sorteio, base_preferida, mes
            )

            if 'erro' in resultado:
                return jsonify(resultado), 400

            return jsonify(resultado), 200

        elif modelo == 'G':
            dezenas = data.get('dezenas', []) or data.get('grupoA', [])
            resultado = DesdobramentoService.gerar_jogos_modelo_g(dezenas, mes)

            if 'erro' in resultado:
                return jsonify(resultado), 400

            return jsonify(resultado), 200

        else:
            return jsonify({'erro': f'Modelo {modelo} não implementado'}), 400

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@desdobramento_bp.route('/api/desdobramento/validar-grupos', methods=['POST'])
def api_validar_grupos():
    """
    API para validar grupos de dezenas

    Body JSON esperado:
    {
        "grupoA": [1, 5, 10, 15, 20],
        "grupoB": [2, 7, 12, 18, 22, 25, 28, 30]
    }

    Retorna: validação dos grupos
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        grupo_a = data.get('grupoA', [])
        grupo_b = data.get('grupoB', [])

        validacao = DesdobramentoService.validar_grupos(grupo_a, grupo_b)

        return jsonify(validacao), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@desdobramento_bp.route('/api/desdobramento/calcular-combinacoes')
def api_calcular_combinacoes():
    """
    API para calcular quantidade de combinações C(n, k)

    Query params:
    - n: tamanho do pool
    - k: quantos escolher (padrão: 2)

    Exemplo: /api/desdobramento/calcular-combinacoes?n=8&k=2

    Retorna: número de combinações
    """
    try:
        n = request.args.get('n', type=int)
        k = request.args.get('k', type=int, default=2)

        if n is None:
            return jsonify({'erro': 'Parâmetro n é obrigatório'}), 400

        if n < 0 or k < 0:
            return jsonify({'erro': 'Valores devem ser positivos'}), 400

        total = DesdobramentoService.calcular_combinacoes(n, k)
        custo_unitario = 2.50
        custo_total = total * custo_unitario

        return jsonify({
            'n': n,
            'k': k,
            'total_combinacoes': total,
            'custo_unitario': custo_unitario,
            'custo_total': custo_total,
            'modelo': f'{5}+{k}'
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@desdobramento_bp.route('/api/desdobramento/sugestao-modelo-f')
def api_sugestao_modelo_f():
    """
    API para obter sugestão inicial para o Modelo F.
    Retorna último sorteio e base sugerida.
    """
    try:
        resultado = DesdobramentoService.gerar_sugestao_modelo_f()
        
        if 'erro' in resultado:
            return jsonify(resultado), 404
            
        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@desdobramento_bp.route('/api/desdobramento/ultimo-sorteio-desdobramento')
def api_ultimo_sorteio_desdobramento():
    """
    API para obter dados do último sorteio + nível de redução (2)
    Reutilizável pela rota /gerador-padroes
    
    Retorna:
    {
        'sorteio_base': [3, 7, 12, 18, 22, 28, 31],
        'complementares': [1, 2, 4, 5, 6, ...],
        'nivel': 2,
        'total_jogos_desdobrados': 21,
        'concurso': 1234,
        'mes_sorteio': 'Nov',
        'data_sorteio': 'DD/MM/YYYY'
    }
    """
    try:
        resultado = DesdobramentoService.gerar_sugestao_modelo_e(nivel=2)
        
        # Remover campos não necessários
        dados_simplificados = {
            'sorteio_base': resultado.get('sorteio_base', []),
            'complementares': resultado.get('complementares', []),
            'nivel': resultado.get('nivel', 2),
            'total_jogos_desdobrados': resultado.get('total_jogos', 21),
            'concurso': resultado.get('concurso'),
            'mes_sorteio': resultado.get('mes_sorteio'),
            'complemento_por_jogo': resultado.get('complemento_por_jogo', 5)
        }
        
        if 'erro' in resultado:
            return jsonify({'erro': resultado['erro']}), 404
        
        return jsonify(dados_simplificados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
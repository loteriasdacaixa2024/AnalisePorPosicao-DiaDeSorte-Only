# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, jsonify, render_template, request
from services.configuracao_service import ConfiguracaoService

configuracao_bp = Blueprint('configuracao', __name__)


@configuracao_bp.route('/sistema/configuracoes')
def pagina_configuracoes():
    """Página de configurações do sistema"""
    return render_template('configuracoes.html')


@configuracao_bp.route('/api/configuracoes/listar', methods=['GET'])
def listar_configuracoes():
    """
    API para listar todas as configurações

    Returns:
        JSON com lista de configurações
    """
    try:
        configuracoes = ConfiguracaoService.listar_todas()

        return jsonify({
            'sucesso': True,
            'configuracoes': configuracoes
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao listar configurações: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/obter/<chave>', methods=['GET'])
def obter_configuracao(chave):
    """
    API para obter uma configuração específica

    Args:
        chave: Chave da configuração

    Returns:
        JSON com a configuração
    """
    try:
        valor = ConfiguracaoService.obter_configuracao(chave)

        if valor is None:
            return jsonify({
                'sucesso': False,
                'mensagem': f'Configuração "{chave}" não encontrada'
            }), 404

        return jsonify({
            'sucesso': True,
            'chave': chave,
            'valor': valor
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter configuração: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/valor-aposta', methods=['GET'])
def obter_valor_aposta():
    """
    API para obter o valor da aposta mínima

    Returns:
        JSON com o valor da aposta
    """
    try:
        valor = ConfiguracaoService.obter_valor_aposta()

        return jsonify({
            'sucesso': True,
            'valor_aposta': valor
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter valor da aposta: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/salvar', methods=['POST'])
def salvar_configuracao():
    """
    API para salvar ou atualizar uma configuração

    Body JSON:
    {
        "chave": "nome_da_configuracao",
        "valor": "valor",
        "tipo": "string",  // opcional: string, float, int, boolean
        "descricao": "Descrição da configuração"  // opcional
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados or 'chave' not in dados or 'valor' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campos "chave" e "valor" são obrigatórios'
            }), 400

        chave = dados['chave']
        valor = dados['valor']
        tipo = dados.get('tipo', 'string')
        descricao = dados.get('descricao')

        resultado = ConfiguracaoService.salvar_configuracao(chave, valor, tipo, descricao)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar configuração: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/salvar-valor-aposta', methods=['POST'])
def salvar_valor_aposta():
    """
    API para salvar o valor da aposta mínima

    Body JSON:
    {
        "valor": 2.50
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados or 'valor' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campo "valor" é obrigatório'
            }), 400

        valor = dados['valor']

        resultado = ConfiguracaoService.salvar_valor_aposta(valor)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar valor da aposta: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/excluir/<chave>', methods=['DELETE'])
def excluir_configuracao(chave):
    """
    API para excluir uma configuração

    Args:
        chave: Chave da configuração a ser excluída

    Returns:
        JSON com resultado da operação
    """
    try:
        resultado = ConfiguracaoService.excluir_configuracao(chave)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao excluir configuração: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/inicializar', methods=['POST'])
def inicializar_configuracoes():
    """
    API para inicializar configurações padrão do sistema

    Returns:
        JSON com resultado da operação
    """
    try:
        sucesso = ConfiguracaoService.inicializar_configuracoes()

        if sucesso:
            return jsonify({
                'sucesso': True,
                'mensagem': 'Configurações padrão inicializadas com sucesso'
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Erro ao inicializar configurações padrão'
            }), 500

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao inicializar configurações: {str(e)}'
        }), 500


# ========================================================================
# ANÁLISES CONFIGURATION ENDPOINTS
# ========================================================================

@configuracao_bp.route('/api/configuracoes/analises', methods=['GET'])
def obter_analises():
    """
    API para obter o status de todas as análises

    Returns:
        JSON com dicionário de análises ativas/inativas
    """
    try:
        analises = ConfiguracaoService.obter_analises_ativas()

        return jsonify({
            'sucesso': True,
            'analises': analises
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter análises: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/analises/salvar', methods=['POST'])
def salvar_analises():
    """
    API para salvar múltiplas configurações de análises

    Body JSON:
    {
        "analise_gaps": true,
        "analise_atrasados": false,
        ...
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum dado fornecido'
            }), 400

        resultado = ConfiguracaoService.salvar_analises(dados)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar análises: {str(e)}'
        }), 500


# ========================================================================
# DATABASE UPDATE ENDPOINTS
# ========================================================================

@configuracao_bp.route('/api/configuracoes/status-banco', methods=['GET'])
def obter_status_banco():
    """
    API para obter o status atual do banco de dados

    Returns:
        JSON com informações do banco (último concurso, data, total, etc)
    """
    try:
        status = ConfiguracaoService.obter_status_banco()

        if status['sucesso']:
            return jsonify(status)
        else:
            return jsonify(status), 500

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter status do banco: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/atualizar-banco', methods=['POST'])
def atualizar_banco():
    """
    API para atualizar o banco de dados com informações da API Caixa

    Body JSON:
    {
        "tipo": "ultimo" | "especifico" | "range" | "todos",
        "numero": 1098,  // para tipo "especifico"
        "inicio": 1000,  // para tipo "range"
        "fim": 1133      // para tipo "range"
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados or 'tipo' not in dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Campo "tipo" é obrigatório'
            }), 400

        tipo = dados['tipo']

        # Valida o tipo
        if tipo not in ['ultimo', 'especifico', 'range', 'todos']:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Tipo inválido. Use: ultimo, especifico, range ou todos'
            }), 400

        # Processa conforme o tipo
        if tipo == 'ultimo':
            resultado = ConfiguracaoService.atualizar_ultimo_concurso()

        elif tipo == 'especifico':
            if 'numero' not in dados:
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Campo "numero" é obrigatório para tipo "especifico"'
                }), 400
            resultado = ConfiguracaoService.atualizar_concurso_especifico(dados['numero'])

        elif tipo == 'range':
            if 'inicio' not in dados or 'fim' not in dados:
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Campos "inicio" e "fim" são obrigatórios para tipo "range"'
                }), 400
            resultado = ConfiguracaoService.atualizar_range_concursos(dados['inicio'], dados['fim'])

        elif tipo == 'todos':
            resultado = ConfiguracaoService.atualizar_todos_concursos()

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 500

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao atualizar banco: {str(e)}'
        }), 500


# ========================================================================
# MONTH COLORS ENDPOINTS
# ========================================================================

@configuracao_bp.route('/api/configuracoes/cores-meses', methods=['GET'])
@configuracao_bp.route('/api/cores-meses/css', methods=['GET'])
def obter_cores_meses():
    """
    API para obter as cores dos 12 meses

    Returns:
        JSON com cores {sucesso, cores_meses: {1: '#cor1', 2: '#cor2', ...}}
    """
    try:
        cores = ConfiguracaoService.obter_cores_meses()

        return jsonify({
            'sucesso': True,
            'cores_meses': cores
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter cores dos meses: {str(e)}'
        }), 500


@configuracao_bp.route('/api/cores-meses/listar', methods=['GET'])
def listar_cores_meses():
    """
    API para listar cores dos meses em formato detalhado
    (usado pelo configuracoes.html)

    Returns:
        JSON com cores {sucesso, cores: [{mes, cor_hex}, ...]}
    """
    try:
        cores = ConfiguracaoService.obter_cores_meses()

        # Converter para formato de lista
        cores_lista = []
        for mes, cor_hex in cores.items():
            cores_lista.append({
                'mes': mes,
                'cor_hex': cor_hex
            })

        return jsonify({
            'sucesso': True,
            'cores': cores_lista
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao listar cores dos meses: {str(e)}'
        }), 500


@configuracao_bp.route('/api/cores-meses/atualizar-multiplas', methods=['POST'])
@configuracao_bp.route('/api/configuracoes/cores-meses/salvar', methods=['POST'])
def salvar_cores_meses():
    """
    API para salvar as cores dos meses

    Body JSON:
    {
        "1": "#FF6B9D",
        "2": "#C5A880",
        ...
        "12": "#C0392B"
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum dado fornecido'
            }), 400

        resultado = ConfiguracaoService.salvar_cores_meses(dados)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar cores dos meses: {str(e)}'
        }), 500


@configuracao_bp.route('/api/cores-meses/restaurar-padrao', methods=['POST'])
@configuracao_bp.route('/api/configuracoes/cores-meses/restaurar', methods=['POST'])
def restaurar_cores_meses():
    """
    API para restaurar as cores dos meses para os valores padrão

    Returns:
        JSON com resultado da operação
    """
    try:
        resultado = ConfiguracaoService.restaurar_cores_meses_padrao()

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 500

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao restaurar cores padrão: {str(e)}'
        }), 500


# ========================================================================
# CSS DINÂMICO - SOLUÇÃO UNIVERSAL PARA TODOS OS ARQUIVOS
# ========================================================================

@configuracao_bp.route('/static/css/cores-meses.css')
def gerar_css_cores_meses():
    """
    Gera CSS dinâmico com as cores dos meses do banco de dados

    Esta rota permite que QUALQUER página HTML use as cores apenas incluindo:
    <link rel="stylesheet" href="/static/css/cores-meses.css">

    E usando classes CSS:
    <span class="mes-cor-1">Janeiro</span>  (para mês 1)
    <span class="mes-cor-5">Maio</span>     (para mês 5)
    etc.

    Returns:
        CSS gerado dinamicamente
    """
    from flask import Response

    try:
        # Buscar cores do banco
        cores = ConfiguracaoService.obter_cores_meses()

        # Gerar CSS
        css = """/* Cores dos Meses - Gerado Dinamicamente do Banco de Dados */
/* Atualizado automaticamente quando você altera as cores em Configurações */

"""

        # Nomes dos meses
        nomes_meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        # Gerar classes para cada mês (1-12)
        for mes, cor_hex in cores.items():
            nome_mes = nomes_meses.get(mes, f'Mês {mes}')

            css += f"""
/* {nome_mes} */
.mes-cor-{mes} {{
    background-color: {cor_hex} !important;
    color: white !important;
}}

.mes-bg-{mes} {{
    background-color: {cor_hex} !important;
}}

.mes-text-{mes} {{
    color: {cor_hex} !important;
}}

.mes-border-{mes} {{
    border-color: {cor_hex} !important;
}}
"""

        # Adicionar classes de compatibilidade (0-11 para arquivos antigos)
        css += """
/* ===== COMPATIBILIDADE: Classes com índice 0-11 ===== */
"""
        for i in range(12):
            mes = i + 1
            cor_hex = cores.get(mes, '#cccccc')
            nome_mes = nomes_meses.get(mes, f'Mês {mes}')

            css += f"""
/* {nome_mes} (índice {i}) */
.mes-cor-{i} {{
    background-color: {cor_hex} !important;
    color: white !important;
}}
"""

        # Retornar CSS com headers corretos
        return Response(css, mimetype='text/css')

    except Exception as e:
        # Se der erro, retornar CSS vazio
        error_css = f"""/* Erro ao gerar cores dos meses: {str(e)} */
.mes-cor-1, .mes-cor-2, .mes-cor-3, .mes-cor-4,
.mes-cor-5, .mes-cor-6, .mes-cor-7, .mes-cor-8,
.mes-cor-9, .mes-cor-10, .mes-cor-11, .mes-cor-12 {{
    background-color: #cccccc !important;
    color: white !important;
}}
"""
        return Response(error_css, mimetype='text/css')


# ========================================================================
# PREÇOS POR QUANTIDADE DE DEZENAS ENDPOINTS
# ========================================================================

@configuracao_bp.route('/api/configuracoes/precos-dezenas', methods=['GET'])
def obter_precos_dezenas():
    """
    API para obter os preços por quantidade de dezenas (7 a 15)

    Returns:
        JSON com preços {sucesso, precos: {7: preco, 8: preco, ..., 15: preco}}
    """
    try:
        precos = ConfiguracaoService.obter_todos_precos_dezenas()

        return jsonify({
            'sucesso': True,
            'precos': precos
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter preços por dezenas: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/precos-dezenas/<int:quantidade>', methods=['GET'])
def obter_preco_dezena_especifica(quantidade):
    """
    API para obter o preço de uma quantidade específica de dezenas

    Args:
        quantidade: Número de dezenas (7 a 15)

    Returns:
        JSON com o preço {sucesso, dezenas, preco}
    """
    try:
        if quantidade < 7 or quantidade > 15:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Quantidade de dezenas deve estar entre 7 e 15'
            }), 400

        preco = ConfiguracaoService.obter_preco_por_dezenas(quantidade)

        return jsonify({
            'sucesso': True,
            'dezenas': quantidade,
            'preco': preco
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter preço: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/precos-dezenas/salvar', methods=['POST'])
def salvar_precos_dezenas():
    """
    API para salvar os preços por quantidade de dezenas

    Body JSON:
    {
        "7": 2.50,
        "8": 20.00,
        ...
        "15": 16087.50
    }

    Returns:
        JSON com resultado da operação
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum dado fornecido'
            }), 400

        resultado = ConfiguracaoService.salvar_precos_dezenas(dados)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao salvar preços: {str(e)}'
        }), 500


@configuracao_bp.route('/api/configuracoes/precos-dezenas/restaurar', methods=['POST'])
def restaurar_precos_dezenas():
    """
    API para restaurar os preços para os valores oficiais da Caixa

    Returns:
        JSON com resultado da operação
    """
    try:
        resultado = ConfiguracaoService.restaurar_precos_oficiais()

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 500

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao restaurar preços oficiais: {str(e)}'
        }), 500

# ========================================================================
# ANALYSIS COLORS ENDPOINTS
# ========================================================================

@configuracao_bp.route('/api/configuracoes/cores-analise', methods=['GET'])
def obter_cores_analise():
    """API para obter as cores de análise"""
    try:
        cores = ConfiguracaoService.obter_cores_analise()
        return jsonify({'sucesso': True, 'cores': cores})
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

@configuracao_bp.route('/api/configuracoes/cores-analise/salvar', methods=['POST'])
def salvar_cores_analise():
    """API para salvar as cores de análise"""
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({'sucesso': False, 'mensagem': 'Nenhum dado fornecido'}), 400
        resultado = ConfiguracaoService.salvar_cores_analise(dados)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

@configuracao_bp.route('/api/configuracoes/cores-analise/restaurar', methods=['POST'])
def restaurar_cores_analise():
    """API para restaurar cores de análise padrão"""
    try:
        resultado = ConfiguracaoService.restaurar_cores_analise_padrao()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

@configuracao_bp.route('/api/configuracoes/cores-analise.css')
def gerar_css_cores_analise():
    """Gera CSS dinâmico com as cores de análise do banco de dados com contraste automático"""
    from flask import Response
    
    def get_contrast(hex_color):
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
            return 'black' if yiq >= 128 else 'white'
        except:
            return 'white'

    try:
        cores = ConfiguracaoService.obter_cores_analise()
        
        # Calcular contrastes
        contrastes = {k: get_contrast(v) for k, v in cores.items()}

        css = f"""/* Cores de Análise - Gerado Dinamicamente */
:root {{
    --cor-repetidos: {cores['repetidos']};
    --cor-repetidos-texto: {contrastes['repetidos']};
    
    --cor-sequencia-1: {cores['sequencia_1']};
    --cor-sequencia-1-texto: {contrastes['sequencia_1']};
    
    --cor-sequencia-2: {cores['sequencia_2']};
    --cor-sequencia-2-texto: {contrastes['sequencia_2']};
    
    --cor-sequencia-3: {cores['sequencia_3']};
    --cor-sequencia-3-texto: {contrastes['sequencia_3']};
    
    --cor-pares: {cores['pares']};
    --cor-pares-texto: {contrastes['pares']};
    
    --cor-impares: {cores['impares']};
    --cor-impares-texto: {contrastes['impares']};
    
    --cor-finais-iguais: {cores['finais_iguais']};
    --cor-finais-iguais-texto: {contrastes['finais_iguais']};
}}

/* Classes de Utilidade Semânticas e Aliases */
.color-repeated, .dest-repetidos, .repetition {{ background-color: var(--cor-repetidos) !important; color: var(--cor-repetidos-texto) !important; }}
.color-sequence-level1, .dest-sequencia-1, .seq-2 {{ background-color: var(--cor-sequencia-1) !important; color: var(--cor-sequencia-1-texto) !important; }}
.color-sequence-level2, .dest-sequencia-2, .seq-3 {{ background-color: var(--cor-sequencia-2) !important; color: var(--cor-sequencia-2-texto) !important; }}
.color-sequence-level3, .dest-sequencia-3, .seq-4 {{ background-color: var(--cor-sequencia-3) !important; color: var(--cor-sequencia-3-texto) !important; }}
.color-even, .dest-pares {{ background-color: var(--cor-pares) !important; color: var(--cor-pares-texto) !important; }}
.color-odd, .dest-impares {{ background-color: var(--cor-impares) !important; color: var(--cor-impares-texto) !important; }}
.color-equal-endings, .dest-finais {{ background-color: var(--cor-finais-iguais) !important; color: var(--cor-finais-iguais-texto) !important; }}

/* Compatibilidade com gradientes da tubular (Múltiplas Condições) */
/* 1. Repetição + Sequências (2 cores) */
.repetition.color-sequence-level1, .repetition.dest-sequencia-1, .repetition.seq-2 {{ background: linear-gradient(135deg, var(--cor-repetidos) 0%, var(--cor-repetidos) 50%, var(--cor-sequencia-1) 50%, var(--cor-sequencia-1) 100%) !important; }}
.repetition.color-sequence-level2, .repetition.dest-sequencia-2, .repetition.seq-3 {{ background: linear-gradient(135deg, var(--cor-repetidos) 0%, var(--cor-repetidos) 50%, var(--cor-sequencia-2) 50%, var(--cor-sequencia-2) 100%) !important; }}
.repetition.color-sequence-level3, .repetition.dest-sequencia-3, .repetition.seq-4 {{ background: linear-gradient(135deg, var(--cor-repetidos) 0%, var(--cor-repetidos) 50%, var(--cor-sequencia-3) 50%, var(--cor-sequencia-3) 100%) !important; }}

/* 2. Sequências Triplas (Ex: 4+3+2) */
.color-sequence-level3.color-sequence-level2.color-sequence-level1,
.dest-sequencia-3.dest-sequencia-2.dest-sequencia-1,
.seq-4.seq-3.seq-2 {{ 
    background: linear-gradient(135deg, 
        var(--cor-sequencia-3) 0%, var(--cor-sequencia-3) 33%, 
        var(--cor-sequencia-2) 33%, var(--cor-sequencia-2) 66%, 
        var(--cor-sequencia-1) 66%, var(--cor-sequencia-1) 100%) !important; 
}}
"""
        return Response(css, mimetype='text/css')
    except Exception as e:
        return Response(f"/* Erro: {str(e)} */", mimetype='text/css')

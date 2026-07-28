"""
================================================================================
ROUTES: Análise de Dígitos Padrão Inicial/Final + Padrões por Dezenas
================================================================================
Destino: routes/analise_digito_padrao_inicial_final_routes.py
================================================================================
"""

from flask import Blueprint, jsonify, render_template
from services.analise_digito_padrao_inicial_final_service import AnaliseDigitoPadraoInicialFinalService

analise_digito_padrao_inicial_final_bp = Blueprint('analise_digito_padrao_inicial_final', __name__)

@analise_digito_padrao_inicial_final_bp.route('/analise/digito-padrao-inicial-final')
def pagina_digito_padrao():
    return render_template('analise_digito_padrao_inicial_final.html')

@analise_digito_padrao_inicial_final_bp.route('/api/analise/digito-padrao-inicial-final', methods=['GET'])
def obter_digito_padrao():
    from models.sorteio import Sorteio

    resultado = AnaliseDigitoPadraoInicialFinalService.analisar_padroes()

    if 'error' not in resultado:
        # Calcular frequência campeã para padrões iniciais
        campea_inicial = AnaliseDigitoPadraoInicialFinalService.calcular_frequencia_campea(
            resultado.get('top_padroes_iniciais', []),
            tipo='inicial'
        )

        # Calcular frequência campeã para padrões finais (ainda calculamos mas não exibiremos no HTML)
        campea_final = AnaliseDigitoPadraoInicialFinalService.calcular_frequencia_campea(
            resultado.get('top_padroes_finais', []),
            tipo='final'
        )

        # Adicionar ao resultado
        resultado['campea_inicial'] = campea_inicial
        resultado['campea_final'] = campea_final

        # Gerar timeline de aparições do padrão campeão (APENAS DÍGITOS INICIAIS)
        if campea_inicial['posicoes'].get('primeiro') and campea_inicial['posicoes']['primeiro']['padrao_original']:
            todos_sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()
            timeline = AnaliseDigitoPadraoInicialFinalService.gerar_timeline_aparicoes(
                campea_inicial['posicoes']['primeiro']['padrao_original'],
                todos_sorteios
            )
            resultado['timeline_campea'] = timeline

    return jsonify(resultado)

# NOVA ROTA: Opções de análises para o select de geração de fechamentos
@analise_digito_padrao_inicial_final_bp.route('/api/analise/opcoes-padroes-simples', methods=['GET'])
def obter_opcoes_padroes_simples():
    """
    Retorna as opções de padrões no formato '0 1 1 2 2 3 3' para o select de geração
    """
    resultado = AnaliseDigitoPadraoInicialFinalService.analisar_padroes()

    if 'error' in resultado:
        return jsonify({'error': resultado['error']}), 400

    opcoes = []

    # Adicionar os padrões simples mais frequentes
    if 'top_padroes_digitos_iniciais_simples' in resultado:
        for item in resultado['top_padroes_digitos_iniciais_simples'][:5]:  # Top 5
            opcoes.append({
                'value': item['padrao'],
                'label': f"'{item['padrao']}' ({item['frequencia']} concursos)",
                'descricao': f"Padrão '{item['padrao']}' apareceu em {item['frequencia']} concursos ({item['porcentagem']}% dos sorteios)",
                'frequencia': item['frequencia'],
                'porcentagem': item['porcentagem']
            })

    # Adicionar opção para usar todos os padrões
    opcoes.append({
        'value': 'todos_padroes',
        'label': 'Usar todos os padrões mais frequentes',
        'descricao': 'Gera jogos seguindo todos os padrões mais frequentes alternadamente',
        'frequencia': None,
        'porcentagem': None
    })

    # Adicionar opção para não usar padrão
    opcoes.insert(0, {
        'value': '',
        'label': 'Sem padrão específico',
        'descricao': 'Gera jogos sem seguir padrões específicos',
        'frequencia': None,
        'porcentagem': None
    })

    return jsonify({
        'opcoes': opcoes,
        'total_padroes': len(opcoes) - 1  # Excluindo a opção "sem padrão"
    }), 200


# =========================================================================
# NOVA ROTA: Análise de Padrões por Dezenas (Faltantes, Frequentes, etc)
# =========================================================================

@analise_digito_padrao_inicial_final_bp.route('/api/analise/padroes-dezenas', methods=['GET'])
def obter_padroes_dezenas():
    """
    Retorna análise completa de padrões por dezenas:
    - Todos os padrões possíveis
    - Padrões que já saíram (frequência)
    - Padrões FALTANTES (nunca saíram)
    - Ranking, Insights e Recomendações
    """
    try:
        resultado = AnaliseDigitoPadraoInicialFinalService.analisar_padroes_dezenas()
        return jsonify(resultado)
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@analise_digito_padrao_inicial_final_bp.route('/api/analise/padroes-possiveis', methods=['GET'])
def obter_padroes_possiveis():
    """
    Retorna apenas os padrões possíveis com quantidade de jogos que cada um pode gerar
    """
    try:
        resultado = AnaliseDigitoPadraoInicialFinalService.calcular_padroes_possiveis()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

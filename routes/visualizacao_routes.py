# -*- coding: utf-8 -*-
"""
Rotas para a visualização tubular
"""

from flask import Blueprint, render_template, jsonify
from models.sorteio import Sorteio
from sqlalchemy import desc

visualizacao_bp = Blueprint('visualizacao', __name__)


@visualizacao_bp.route('/visualizacao/tubular')
def pagina_visualizacao_tubular():
    """Página principal da visualização tubular"""
    return render_template('vizualizacao_tubular.html')


@visualizacao_bp.route('/api/visualizacao/sorteios', methods=['GET'])
def obter_todos_sorteios():
    """
    API para obter todos os sorteios do banco de dados
    Retorna no formato compatível com a visualização tubular
    """
    try:
        # Busca todos os sorteios ordenados por concurso (mais recente primeiro)
        sorteios = Sorteio.query.order_by(desc(Sorteio.concurso)).all()

        if not sorteios:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum sorteio encontrado no banco de dados'
            }), 404

        # Converte para o formato esperado pela visualização
        dados_sorteios = []
        for sorteio in sorteios:
            dados_sorteios.append({
                'numero': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y'),
                'listaDezenas': sorteio.get_posicoes_lista(),
                'mesSorte': sorteio.mes_sorte,
                'mesSorteNome': sorteio.get_nome_mes(),
                # Dados de premiação
                'listaRateioPremio': [
                    {
                        'faixa': 1,
                        'numeroDeGanhadores': sorteio.ganhadores_7_acertos or 0,
                        'valorPremio': sorteio.valor_premio_7_acertos or 0.0,
                        'descricaoFaixa': '7 acertos'
                    },
                    {
                        'faixa': 2,
                        'numeroDeGanhadores': sorteio.ganhadores_6_acertos or 0,
                        'valorPremio': sorteio.valor_premio_6_acertos or 0.0,
                        'descricaoFaixa': '6 acertos'
                    },
                    {
                        'faixa': 3,
                        'numeroDeGanhadores': sorteio.ganhadores_5_acertos or 0,
                        'valorPremio': sorteio.valor_premio_5_acertos or 25.0,
                        'descricaoFaixa': '5 acertos'
                    },
                    {
                        'faixa': 4,
                        'numeroDeGanhadores': sorteio.ganhadores_4_acertos or 0,
                        'valorPremio': sorteio.valor_premio_4_acertos or 5.0,
                        'descricaoFaixa': '4 acertos'
                    },
                    {
                        'faixa': 5,
                        'numeroDeGanhadores': sorteio.ganhadores_mes_sorte or 0,
                        'valorPremio': sorteio.valor_premio_mes_sorte or 2.5,
                        'descricaoFaixa': 'Mês da Sorte'
                    }
                ],
                'acumulado': sorteio.acumulado if hasattr(sorteio, 'acumulado') else False,
                'valorArrecadado': sorteio.valor_arrecadado if hasattr(sorteio, 'valor_arrecadado') else 0.0,
                'valorAcumuladoProximoConcurso': sorteio.valor_acumulado_proximo_concurso if hasattr(sorteio, 'valor_acumulado_proximo_concurso') else 0.0,
                'valorEstimadoProximoConcurso': sorteio.valor_estimado_proximo_concurso if hasattr(sorteio, 'valor_estimado_proximo_concurso') else 0.0
            })

        return jsonify({
            'sucesso': True,
            'total': len(dados_sorteios),
            'sorteios': dados_sorteios,
            'ultimoConcurso': sorteios[0].concurso
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao buscar sorteios: {str(e)}'
        }), 500


@visualizacao_bp.route('/api/visualizacao/ultimo-sorteio', methods=['GET'])
def obter_ultimo_sorteio():
    """API para obter apenas o último sorteio"""
    try:
        ultimo = Sorteio.query.order_by(desc(Sorteio.concurso)).first()

        if not ultimo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum sorteio encontrado'
            }), 404

        return jsonify({
            'sucesso': True,
            'sorteio': {
                'numero': ultimo.concurso,
                'data': ultimo.data_sorteio.strftime('%d/%m/%Y'),
                'listaDezenas': ultimo.get_posicoes_lista(),
                'mesSorte': ultimo.mes_sorte,
                'mesSorteNome': ultimo.get_nome_mes()
            }
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao buscar último sorteio: {str(e)}'
        }), 500

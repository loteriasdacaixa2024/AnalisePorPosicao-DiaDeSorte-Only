# Sistema: Análise por Posição - Dia de Sorte
# Rotas: Gerador de Jogos com Dezenas Desdobradas

from flask import Blueprint, jsonify, request
from services.desdobramento_service import DesdobramentoService

desdobramento_pares_bp = Blueprint('desdobramento_pares', __name__, url_prefix='/api/desdobramento')


@desdobramento_pares_bp.route('/gerar-com-desdobradas', methods=['POST'])
def api_gerar_jogos_com_desdobradas():
    """
    🆕 API para gerar 21 jogos a partir de dezenas desdobradas
    
    Essa funcionalidade permite gerar exatamente 21 jogos usando:
    - 21 pares de dezenas desdobradas (um par por jogo)
    - Dezenas selecionadas para complementar cada jogo
    
    Body JSON esperado:
    {
        "dezenas_desdobradas": [
            [2, 11], [2, 13], [2, 16], [2, 17], [2, 23], [2, 25],
            [11, 13], [11, 16], [11, 17], [11, 23], [11, 25],
            [13, 16], [13, 17], [13, 23], [13, 25],
            [16, 17], [16, 23], [16, 25],
            [17, 23], [17, 25],
            [23, 25]
        ],
        "dezenas_selecionadas": [3, 4, 6, 7, 13, 14, 17, 19, 23, 24, 26, 28, 30],
        "mes": "Jan",
        "ignorar_quantidade": true
    }
    
    Response:
    {
        "jogos": [
            {
                "numero": 1,
                "par_desdobrado": [2, 11],
                "complemento": [3, 4, 6, 7, 13],
                "numeros_completos": [2, 3, 4, 6, 7, 11, 13],
                "mes": "Jan"
            },
            ...
        ],
        "total_jogos": 21,
        "custo_unitario": 2.50,
        "custo_total": 52.50,
        "sucesso": true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400
        
        dezenas_desdobradas = data.get('dezenas_desdobradas', [])
        dezenas_selecionadas = data.get('dezenas_selecionadas', [])
        mes = data.get('mes', 'Jan')
        ignorar_quantidade = data.get('ignorar_quantidade', False)
        
        # Validações básicas
        if not dezenas_desdobradas:
            return jsonify({'erro': 'dezenas_desdobradas não fornecido'}), 400
        
        if not dezenas_selecionadas:
            return jsonify({'erro': 'dezenas_selecionadas não fornecido'}), 400
        
        # Gerar os 21 jogos
        resultado = DesdobramentoService.gerar_jogos_com_desdobradas(
            dezenas_desdobradas=dezenas_desdobradas,
            dezenas_selecionadas=dezenas_selecionadas,
            mes=mes,
            ignorar_quantidade=ignorar_quantidade
        )
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao gerar jogos: {str(e)}'}), 500

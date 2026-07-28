from flask import Blueprint, jsonify, render_template, request
from services.gerador_fatiamento_service import GeradorFatiamentoService

analise_fatiamento_bp = Blueprint('analise_fatiamento', __name__)

@analise_fatiamento_bp.route('/analise/matriz-digitos')
def pagina_matriz_digitos():
    return render_template('analise_fatiamento.html')

@analise_fatiamento_bp.route('/api/analise/fatiamento', methods=['GET'])
def obter_fatiamento():
    try:
        limite_raw = request.args.get('limite', '50')
        limite = limite_raw if limite_raw.lower() == 'todos' else int(limite_raw)
        resultado = GeradorFatiamentoService.analisar_historico_associativo(limite=limite)
        return jsonify(resultado)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analise_fatiamento_bp.route('/api/gerar_fatiamento', methods=['POST'])
def gerar_fatiamento():
    try:
        data = request.json
        quantidade = int(data.get('quantidade', 10))
        dezenas_por_jogo = int(data.get('dezenas_por_jogo', 7))
        limites_fatiamento = data.get('limites', {})
        modos_fatiamento = data.get('modos', {})  # 'max' (≤) ou 'min' (≥) por grupo
        mes_selecionado = data.get('mes_tipo', 'aleatorio')
        
        resultado = GeradorFatiamentoService.gerar_apostas(
            qtd_apostas=quantidade, 
            dezenas_por_jogo=dezenas_por_jogo, 
            limites_fatiamento=limites_fatiamento,
            mes_selecionado=mes_selecionado,
            modos_fatiamento=modos_fatiamento
        )
        return jsonify(resultado)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

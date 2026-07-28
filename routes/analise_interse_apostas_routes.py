from flask import Blueprint, jsonify, request, render_template
from services.analise_interse_apostas_service import AnaliseInterseApostasService
from services.sistema_blocos_inteligente_service import SistemaBlocosInteligenteService
from models.sorteio import Sorteio

analise_interse_apostas_bp = Blueprint('analise_interse_apostas', __name__)


@analise_interse_apostas_bp.route('/analise/estrutura-apostas', methods=['GET'])
def pagina_estrutura_apostas():
    return render_template('analise_estrutura_apostas.html')


@analise_interse_apostas_bp.route('/api/conferidor/ultimo-sorteio', methods=['GET'])
def obter_ultimo_sorteio():
    """Retorna o último sorteio com as posições"""
    try:
        ultimo_sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
        
        if not ultimo_sorteio:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum sorteio encontrado no banco de dados'
            }), 404
        
        return jsonify({
            'sucesso': True,
            'sorteio': {
                'concurso': ultimo_sorteio.concurso,
                'posicoes': {
                    'posicao_1': ultimo_sorteio.posicao_1,
                    'posicao_2': ultimo_sorteio.posicao_2,
                    'posicao_3': ultimo_sorteio.posicao_3,
                    'posicao_4': ultimo_sorteio.posicao_4,
                    'posicao_5': ultimo_sorteio.posicao_5,
                    'posicao_6': ultimo_sorteio.posicao_6,
                    'posicao_7': ultimo_sorteio.posicao_7,
                }
            }
        }), 200
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao buscar último sorteio: {str(e)}'
        }), 500


@analise_interse_apostas_bp.route('/api/analise/interse-apostas', methods=['POST'])
def analisar_interse_apostas():
    try:
        data = request.get_json(force=True, silent=True) or {}
        apostas = data.get('apostas')
        if apostas is None:
            return jsonify({'error': 'Campo apostas obrigatorio'}), 400

        resultado = AnaliseInterseApostasService.calcular_interse_apostas(apostas)
        return jsonify(resultado), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Falha ao processar intersecao: {e}'}), 500


@analise_interse_apostas_bp.route('/api/analise/fechamento-faltantes', methods=['POST'])
def gerar_fechamento_faltantes():
    try:
        data = request.get_json(force=True, silent=True) or {}
        apostas = data.get('apostas')
        if not apostas:
            return jsonify({'sucesso': False, 'mensagem': 'Nenhuma aposta fornecida.'}), 400

        from services.fechamento_faltantes_service import FechamentoFaltantesService
        resultado = FechamentoFaltantesService.gerar_fechamento(apostas)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


@analise_interse_apostas_bp.route('/api/analise/sistema-blocos-2', methods=['POST'])
def gerar_sistema_blocos_2():
    """
    Novo endpoint para Geração Inteligente de Sistemas em Blocos 2.0
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        # Validação básica
        fixas = data.get('fixas', [])
        if not fixas or len(fixas) != 4:
            return jsonify({'sucesso': False, 'mensagem': 'Selecione exatamente 4 dezenas fixas.'}), 400
            
        resultado = SistemaBlocosInteligenteService.gerar_jogos(data)
        return jsonify(resultado), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao gerar blocos: {str(e)}'}), 500

@analise_interse_apostas_bp.route('/api/diario-estrategia/salvar', methods=['POST'])
def salvar_diario_estrategia():
    try:
        from core.config import Config
        import os
        import json
        
        data = request.get_json(force=True, silent=True) or {}
        apostas_cruas = data.get('apostas', [])
        tag_estrategia = data.get('estrategia', 'Sem Nome')
        rota_origem = data.get('rota_origem', 'Origem Desconhecida')
        
        if not apostas_cruas:
            return jsonify({'sucesso': False, 'mensagem': 'Nenhuma aposta para salvar.'}), 400
            
        ultimo_sorteio = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
        if not ultimo_sorteio:
            return jsonify({'sucesso': False, 'mensagem': 'Nenhum sorteio no banco.'}), 400
            
        prox_concurso = ultimo_sorteio.concurso + 1
        
        # Build structured apostas list
        apostas_formatadas = []
        for idx, nums in enumerate(apostas_cruas):
            apostas_formatadas.append({
                "numero": idx + 1,
                "numeros": nums,
                "mes": "N/A" # Simplified / random mes if missing, but typically we just save the array
            })
            
        # Target folder
        target_dir = os.path.join(Config.BASE_DIR, 'conferencia_apostas', str(prox_concurso))
        os.makedirs(target_dir, exist_ok=True)
        
        filepath = os.path.join(target_dir, 'apostas.json')
        
        doc = {
            "concurso": prox_concurso,
            "estrategia": tag_estrategia,
            "rota_origem": rota_origem,
            "data_criacao": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "apostas": apostas_formatadas
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
            
        return jsonify({
            'sucesso': True, 
            'mensagem': f'Salvo com sucesso na pasta do Concurso {prox_concurso}!',
            'caminho': filepath
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({'sucesso': False, 'mensagem': str(e), 'trace': traceback.format_exc()}), 500

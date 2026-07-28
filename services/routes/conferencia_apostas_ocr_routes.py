"""
Routes para Conferência de Apostas via OCR - Dia de Sorte
"""

from flask import Blueprint, request, jsonify, render_template
from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService

# Criar blueprint
conferencia_ocr_bp = Blueprint('conferencia_ocr', __name__)


@conferencia_ocr_bp.route('/conferencia-apostas-ocr')
def pagina_conferencia_ocr():
    """Página principal de conferência de apostas via OCR"""
    return render_template('conferencia_ocr.html')


@conferencia_ocr_bp.route('/api/conferencia-ocr/concursos-disponiveis', methods=['GET'])
def listar_concursos_disponiveis():
    """
    Lista todos os concursos disponíveis na pasta mnt/conferencia_apostas/

    Returns:
        JSON com lista de concursos e suas informações
    """
    try:
        concursos = ConferenciaApostasOCRService.listar_concursos_disponiveis()

        return jsonify({
            'sucesso': True,
            'total': len(concursos),
            'concursos': concursos
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao listar concursos: {str(e)}'
        }), 500


@conferencia_ocr_bp.route('/api/conferencia-ocr/processar-concurso/<int:concurso>', methods=['POST'])
def processar_concurso(concurso):
    """
    Processa todos os screenshots de um concurso específico

    Args:
        concurso: Número do concurso

    Returns:
        JSON com resultados do processamento
    """
    try:
        resultado = ConferenciaApostasOCRService.processar_concurso(concurso)

        if resultado['sucesso']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao processar concurso {concurso}: {str(e)}'
        }), 500


@conferencia_ocr_bp.route('/api/conferencia-ocr/processar-multiplos', methods=['POST'])
def processar_multiplos_concursos():
    """
    Processa múltiplos concursos de uma vez

    Request JSON:
        {
            "concursos": [1134, 1135, 1136]
        }

    Returns:
        JSON com relatório consolidado
    """
    try:
        dados = request.get_json()

        if not dados or 'concursos' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'dados_invalidos',
                'mensagem': 'É necessário fornecer uma lista de concursos'
            }), 400

        concursos = dados['concursos']

        if not isinstance(concursos, list) or len(concursos) == 0:
            return jsonify({
                'sucesso': False,
                'erro': 'lista_vazia',
                'mensagem': 'A lista de concursos está vazia'
            }), 400

        resultado = ConferenciaApostasOCRService.processar_multiplos_concursos(concursos)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao processar concursos: {str(e)}'
        }), 500


@conferencia_ocr_bp.route('/api/conferencia-ocr/testar-ocr', methods=['POST'])
def testar_ocr():
    """
    Testa o OCR em um screenshot específico

    Request JSON:
        {
            "concurso": 1134,
            "arquivo": "1 (1).jpg"
        }

    Returns:
        JSON com dados extraídos do OCR
    """
    try:
        dados = request.get_json()

        if not dados or 'concurso' not in dados or 'arquivo' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'dados_invalidos',
                'mensagem': 'É necessário fornecer concurso e arquivo'
            }), 400

        import os
        caminho = os.path.join(
            ConferenciaApostasOCRService.BASE_DIR,
            str(dados['concurso']),
            dados['arquivo']
        )

        if not os.path.exists(caminho):
            return jsonify({
                'sucesso': False,
                'erro': 'arquivo_nao_encontrado',
                'mensagem': f'Arquivo não encontrado: {caminho}'
            }), 404

        resultado = ConferenciaApostasOCRService.processar_screenshot_ocr(caminho)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao testar OCR: {str(e)}'
        }), 500


@conferencia_ocr_bp.route('/api/conferencia-ocr/validar-dados', methods=['POST'])
def validar_dados_extraidos():
    """
    Valida e permite correção manual dos dados extraídos via OCR

    Request JSON:
        {
            "concurso": 1134,
            "arquivo": "1 (1).jpg",
            "numeros_apostados": [5, 9, 16, 21, 23, 29, 31],
            "mes_apostado": 9
        }

    Returns:
        JSON com resultado da validação
    """
    try:
        dados = request.get_json()

        # Validar campos obrigatórios
        campos_obrigatorios = ['concurso', 'numeros_apostados', 'mes_apostado']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({
                    'sucesso': False,
                    'erro': 'campo_faltando',
                    'mensagem': f'Campo obrigatório ausente: {campo}'
                }), 400

        # Validar números
        numeros = dados['numeros_apostados']
        if len(numeros) != 7:
            return jsonify({
                'sucesso': False,
                'erro': 'quantidade_numeros',
                'mensagem': 'Deve ter exatamente 7 números'
            }), 400

        if any(n < 1 or n > 31 for n in numeros):
            return jsonify({
                'sucesso': False,
                'erro': 'numeros_invalidos',
                'mensagem': 'Números devem estar entre 1 e 31'
            }), 400

        if len(set(numeros)) != 7:
            return jsonify({
                'sucesso': False,
                'erro': 'numeros_duplicados',
                'mensagem': 'Números não podem se repetir'
            }), 400

        # Validar mês
        mes = dados['mes_apostado']
        if mes < 1 or mes > 12:
            return jsonify({
                'sucesso': False,
                'erro': 'mes_invalido',
                'mensagem': 'Mês deve estar entre 1 e 12'
            }), 400

        # Buscar concurso no banco e comparar
        from models.sorteio import Sorteio
        sorteio = Sorteio.query.filter_by(concurso=dados['concurso']).first()

        if not sorteio:
            return jsonify({
                'sucesso': False,
                'erro': 'concurso_nao_encontrado',
                'mensagem': f'Concurso {dados["concurso"]} não encontrado no banco'
            }), 404

        # Comparar com resultado oficial
        resultado = ConferenciaApostasOCRService.comparar_aposta_com_resultado(
            numeros,
            mes,
            sorteio
        )

        return jsonify({
            'sucesso': True,
            'valido': True,
            'resultado': resultado
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao validar dados: {str(e)}'
        }), 500


@conferencia_ocr_bp.route('/api/conferencia-ocr/exportar-relatorio/<int:concurso>', methods=['GET'])
def exportar_relatorio(concurso):
    """
    Exporta relatório de um concurso em formato JSON/CSV

    Query params:
        formato: 'json' (padrão) ou 'csv'

    Returns:
        Arquivo para download
    """
    try:
        formato = request.args.get('formato', 'json')

        # Processar concurso
        resultado = ConferenciaApostasOCRService.processar_concurso(concurso)

        if not resultado['sucesso']:
            return jsonify(resultado), 400

        if formato == 'csv':
            # Gerar CSV
            import io
            import csv
            from flask import send_file

            output = io.StringIO()
            writer = csv.writer(output)

            # Cabeçalho
            writer.writerow([
                'Aposta', 'Arquivo', 'Números Apostados', 'Mês Apostado',
                'Acertos', 'Acertou Mês', 'Faixa', 'Valor Ganho'
            ])

            # Dados
            for aposta in resultado['apostas']:
                if not aposta.get('erro_ocr') and not aposta.get('dados_incompletos'):
                    writer.writerow([
                        aposta['numero_aposta'],
                        aposta['arquivo'],
                        ' '.join(map(str, aposta['dados_extraidos']['numeros_apostados'])),
                        aposta['dados_extraidos']['mes_apostado'],
                        aposta['resultado']['acertos'],
                        'Sim' if aposta['resultado']['acertou_mes'] else 'Não',
                        aposta['resultado']['faixa'] or 'Sem prêmio',
                        f"R$ {aposta['valor_ganho']:.2f}"
                    ])

            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'concurso_{concurso}_relatorio.csv'
            )

        else:
            # Retornar JSON
            return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao exportar relatório: {str(e)}'
        }), 500


@conferencia_ocr_bp.route('/api/conferencia-ocr/ranking-global', methods=['POST'])
def iniciar_ranking_global():
    """
    Inicia o cálculo do ranking global de ABS em background
    """
    try:
        import uuid
        import threading
        
        task_id = str(uuid.uuid4())
        
        # Inicializa a task
        ConferenciaApostasOCRService.atualizar_progresso(task_id, 'iniciando', 0)
        
        # Inicia a thread
        thread = threading.Thread(
            target=ConferenciaApostasOCRService.processar_ranking_global_background,
            args=(task_id,)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'sucesso': True,
            'task_id': task_id,
            'mensagem': 'Processamento do ranking iniciado em background'
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao iniciar ranking: {str(e)}'
        }), 500

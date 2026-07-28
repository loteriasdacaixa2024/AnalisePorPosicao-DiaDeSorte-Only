"""
Routes para Central de Conferências - Dia de Sorte
Unifica conferência via OCR e conferência pós-apostas em um único serviço
"""

from flask import Blueprint, request, jsonify, render_template

# Criar blueprint unificado
central_conferencias_bp = Blueprint('central_conferencias', __name__)


# ============================================
# ROTA PRINCIPAL - PÁGINA CENTRAL
# ============================================

@central_conferencias_bp.route('/central-conferencias')
def pagina_central_conferencias():
    """Página principal da Central de Conferências (4 abas)"""
    return render_template('central_conferencias.html')


# ============================================
# ROTAS DE CONFERÊNCIA VIA OCR (Abas 1-3)
# ============================================

@central_conferencias_bp.route('/api/conferencia-ocr/concursos-disponiveis', methods=['GET'])
def listar_concursos_disponiveis_ocr():
    """Lista todos os concursos disponíveis na pasta mnt/conferencia_apostas/"""
    try:
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
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


@central_conferencias_bp.route('/api/conferencia-ocr/processar-concurso/<int:concurso>', methods=['POST'])
def processar_concurso_ocr(concurso):
    """Processa todos os screenshots de um concurso específico"""
    try:
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
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


@central_conferencias_bp.route('/api/conferencia-ocr/processar-multiplos', methods=['POST'])
def processar_multiplos_concursos_ocr():
    """Processa múltiplos concursos de uma vez"""
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

        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
        resultado = ConferenciaApostasOCRService.processar_multiplos_concursos(concursos)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao processar concursos: {str(e)}'
        }), 500


@central_conferencias_bp.route('/api/conferencia-ocr/testar-ocr', methods=['POST'])
def testar_ocr():
    """Testa o OCR em um screenshot específico"""
    try:
        dados = request.get_json()

        if not dados or 'concurso' not in dados or 'arquivo' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'dados_invalidos',
                'mensagem': 'É necessário fornecer concurso e arquivo'
            }), 400

        import os
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService

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


@central_conferencias_bp.route('/api/conferencia-ocr/validar-dados', methods=['POST'])
def validar_dados_extraidos_ocr():
    """Valida e permite correção manual dos dados extraídos via OCR"""
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

        # Validar números (7 a 15 dezenas permitidas)
        numeros = dados['numeros_apostados']
        if len(numeros) < 7 or len(numeros) > 15:
            return jsonify({
                'sucesso': False,
                'erro': 'quantidade_numeros',
                'mensagem': f'Deve ter entre 7 e 15 números (fornecido: {len(numeros)})'
            }), 400

        if any(n < 1 or n > 31 for n in numeros):
            return jsonify({
                'sucesso': False,
                'erro': 'numeros_invalidos',
                'mensagem': 'Números devem estar entre 1 e 31'
            }), 400

        if len(set(numeros)) != len(numeros):
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
        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService

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


@central_conferencias_bp.route('/api/conferencia-ocr/exportar-relatorio/<int:concurso>', methods=['GET'])
def exportar_relatorio_ocr(concurso):
    """Exporta relatório de um concurso em formato JSON/CSV"""
    try:
        formato = request.args.get('formato', 'json')

        from services.conferencia_apostas_ocr_service import ConferenciaApostasOCRService
        resultado = ConferenciaApostasOCRService.processar_concurso(concurso)

        if not resultado['sucesso']:
            return jsonify(resultado), 400

        if formato == 'csv':
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
            return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'mensagem': f'Erro ao exportar relatório: {str(e)}'
        }), 500


# ============================================
# ROTAS DE CONFERÊNCIA PÓS-APOSTAS (Aba 4)
# ============================================

@central_conferencias_bp.route('/api/conferencia/colunas', methods=['GET'])
def listar_colunas():
    """Lista colunas adicionais"""
    try:
        from services.conferencia_apostas_service import ConferenciaApostasService
        colunas = ConferenciaApostasService.listar_colunas_adicionais()
        return jsonify(colunas), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/colunas', methods=['POST'])
def adicionar_coluna():
    """Adiciona nova coluna adicional"""
    try:
        dados = request.get_json()

        if not dados or 'nome' not in dados:
            return jsonify({'erro': 'Campo "nome" é obrigatório'}), 400

        from services.conferencia_apostas_service import ConferenciaApostasService
        nova_coluna = ConferenciaApostasService.adicionar_coluna(
            dados['nome'],
            dados.get('tipo', 'text'),
            dados.get('descricao', '')
        )

        return jsonify(nova_coluna), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/colunas/<coluna_id>', methods=['DELETE'])
def remover_coluna(coluna_id):
    """Remove coluna adicional"""
    try:
        from services.conferencia_apostas_service import ConferenciaApostasService
        resultado = ConferenciaApostasService.remover_coluna(coluna_id)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/normalizar', methods=['POST'])
def normalizar_jogo():
    """Normaliza entrada de jogo com vários formatos"""
    try:
        dados = request.get_json()

        if not dados or 'texto' not in dados:
            return jsonify({'erro': 'Campo "texto" é obrigatório'}), 400

        from services.conferencia_apostas_service import ConferenciaApostasService
        resultado = ConferenciaApostasService.normalizar_combinacao(dados['texto'])

        if not resultado:
            return jsonify({'erro': 'Formato inválido'}), 400

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/validar-jogo', methods=['POST'])
def validar_jogo():
    """Valida um jogo"""
    try:
        dados = request.get_json()

        if not dados or 'numeros' not in dados:
            return jsonify({'erro': 'Campo "numeros" é obrigatório'}), 400

        from services.conferencia_apostas_service import ConferenciaApostasService
        resultado = ConferenciaApostasService.validar_jogo(
            dados['numeros'],
            dados.get('mes')
        )
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/analisar-jogo', methods=['POST'])
def analisar_jogo():
    """Analisa características de um jogo"""
    try:
        dados = request.get_json()

        if not dados or 'numeros' not in dados:
            return jsonify({'erro': 'Campo "numeros" é obrigatório'}), 400

        from services.conferencia_apostas_service import ConferenciaApostasService

        validacao = ConferenciaApostasService.validar_jogo(
            dados['numeros'],
            dados.get('mes')
        )
        if not validacao['valido']:
            return jsonify(validacao), 400

        analise = ConferenciaApostasService.analisar_jogo(
            dados['numeros'],
            dados.get('mes'),
            dados.get('concurso_numero')
        )
        return jsonify(analise), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/conferir', methods=['POST'])
def conferir_jogos():
    """
    Confere jogos com resultado de um concurso

    POST /api/conferencia/conferir
    Body: {
        jogos: [
            {numeros: [1,2,3,4,5,6,7], mes: 1},
            {numeros: [8,9,10,11,12,13,14], mes: 2},
            ...
        ],
        concurso: 1133,
        valor_aposta: 2.50
    }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        if 'jogos' not in dados or 'concurso' not in dados:
            return jsonify({'erro': 'Campos "jogos" e "concurso" são obrigatórios'}), 400

        jogos = dados['jogos']
        concurso = dados['concurso']
        valor_aposta = dados.get('valor_aposta', 2.50)

        from services.conferencia_apostas_service import ConferenciaApostasService

        for idx, jogo in enumerate(jogos):
            numeros = jogo.get('numeros', jogo) if isinstance(jogo, dict) else jogo
            mes = jogo.get('mes') if isinstance(jogo, dict) else None

            validacao = ConferenciaApostasService.validar_jogo(numeros, mes)
            if not validacao['valido']:
                return jsonify({
                    'erro': f"Jogo {idx + 1}: {validacao['erro']}"
                }), 400

        resultado = ConferenciaApostasService.conferir_multiplos_jogos(
            jogos,
            concurso,
            valor_aposta
        )

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@central_conferencias_bp.route('/api/conferencia/concursos', methods=['GET'])
def listar_concursos():
    """Lista concursos disponíveis para conferência (TODOS do primeiro ao último)"""
    try:
        from services.conferencia_apostas_service import ConferenciaApostasService
        concursos = ConferenciaApostasService.listar_concursos_disponiveis()
        return jsonify(concursos), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

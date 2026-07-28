"""
Routes para Monitoramento de Apostas
"""

from flask import Blueprint, render_template, request, jsonify
from services.monitoramento_apostas_service import MonitoramentoApostasService
import json

monitoramento_apostas_bp = Blueprint('monitoramento_apostas_bp', __name__, url_prefix='/monitoramento-apostas')



@monitoramento_apostas_bp.route('/')
def index():
    """Página principal de monitoramento de apostas"""
    return render_template('monitoramento_apostas.html')


@monitoramento_apostas_bp.route('/processar-json', methods=['POST'])
def processar_json():
    """
    Processa apostas de JSON
    Aceita: { "apostas_json": "..." }
    """
    try:
        data = request.get_json()
        apostas_json = data.get('apostas_json', '')

        if not apostas_json:
            return jsonify({
                'sucesso': False,
                'mensagem': 'JSON vazio'
            }), 400

        apostas_validas, erros = MonitoramentoApostasService.processar_apostas_json(apostas_json)

        return jsonify({
            'sucesso': True,
            'total_validas': len(apostas_validas),
            'total_erros': len(erros),
            'apostas': apostas_validas,
            'erros': erros
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao processar JSON: {str(e)}'
        }), 500


@monitoramento_apostas_bp.route('/processar-texto', methods=['POST'])
def processar_texto():
    """
    Processa apostas de texto
    Aceita: { "texto": "..." }
    """
    try:
        data = request.get_json()
        texto = data.get('texto', '')

        if not texto:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Texto vazio'
            }), 400

        apostas_validas, erros = MonitoramentoApostasService.processar_apostas_texto(texto)

        return jsonify({
            'sucesso': True,
            'total_validas': len(apostas_validas),
            'total_erros': len(erros),
            'apostas': apostas_validas,
            'erros': erros
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao processar texto: {str(e)}'
        }), 500


@monitoramento_apostas_bp.route('/analisar', methods=['POST'])
def analisar():
    """
    Analisa apostas contra resultados do banco
    Aceita: {
        "apostas": [...],
        "concurso_inicio": int (opcional),
        "concurso_fim": int (opcional),
        "data_inicio": "YYYY-MM-DD" (opcional),
        "data_fim": "YYYY-MM-DD" (opcional),
        "salvar": bool (opcional)
    }
    """
    try:
        data = request.get_json()
        apostas = data.get('apostas', [])

        if not apostas:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhuma aposta fornecida'
            }), 400

        # Parâmetros opcionais de filtro
        concurso_inicio = data.get('concurso_inicio')
        concurso_fim = data.get('concurso_fim')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        # Realizar análise
        resultado = MonitoramentoApostasService.analisar_apostas(
            apostas=apostas,
            concurso_inicio=concurso_inicio,
            concurso_fim=concurso_fim,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        if not resultado['sucesso']:
            return jsonify(resultado), 400

        # Salvar no banco se solicitado
        if data.get('salvar', False):
            try:
                tipo_upload = data.get('tipo_upload', 'json')
                usuario_id = data.get('usuario_id')  # Se houver autenticação

                analise_salva = MonitoramentoApostasService.salvar_analise(
                    analise_data=resultado,
                    tipo_upload=tipo_upload,
                    usuario_id=usuario_id
                )

                resultado['analise_id'] = analise_salva.id
                resultado['salvo'] = True

            except Exception as e:
                resultado['salvo'] = False
                resultado['erro_salvamento'] = str(e)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao analisar apostas: {str(e)}'
        }), 500


@monitoramento_apostas_bp.route('/historico')
def historico():
    """Lista histórico de análises"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        usuario_id = request.args.get('usuario_id', type=int)

        offset = (page - 1) * per_page

        analises = MonitoramentoApostasService.listar_analises(
            usuario_id=usuario_id,
            limit=per_page,
            offset=offset
        )

        return jsonify({
            'sucesso': True,
            'page': page,
            'per_page': per_page,
            'total': len(analises),
            'analises': [a.to_dict() for a in analises]
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao listar histórico: {str(e)}'
        }), 500


@monitoramento_apostas_bp.route('/analise/<int:analise_id>')
def obter_analise(analise_id):
    """Obtém uma análise específica"""
    try:
        analise = MonitoramentoApostasService.obter_analise(analise_id)

        if not analise:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Análise não encontrada'
            }), 404

        return jsonify({
            'sucesso': True,
            'analise': analise.to_dict()
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter análise: {str(e)}'
        }), 500


@monitoramento_apostas_bp.route('/analise/<int:analise_id>', methods=['DELETE'])
def deletar_analise(analise_id):
    """Deleta uma análise"""
    try:
        sucesso = MonitoramentoApostasService.deletar_analise(analise_id)

        if sucesso:
            return jsonify({
                'sucesso': True,
                'mensagem': 'Análise deletada com sucesso'
            })
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Análise não encontrada'
            }), 404

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao deletar análise: {str(e)}'
        }), 500


@monitoramento_apostas_bp.route('/estatisticas-historicas')
def estatisticas_historicas():
    """Obtém estatísticas históricas agregadas"""
    try:
        usuario_id = request.args.get('usuario_id', type=int)

        estatisticas = MonitoramentoApostasService.obter_estatisticas_historicas(usuario_id=usuario_id)

        return jsonify({
            'sucesso': True,
            'estatisticas': estatisticas
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao obter estatísticas: {str(e)}'
        }), 500


@monitoramento_apostas_bp.route('/upload-arquivo', methods=['POST'])
def upload_arquivo():
    """
    Faz upload de arquivo JSON com apostas
    """
    try:
        if 'arquivo' not in request.files:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nenhum arquivo enviado'
            }), 400

        arquivo = request.files['arquivo']

        if arquivo.filename == '':
            return jsonify({
                'sucesso': False,
                'mensagem': 'Nome de arquivo vazio'
            }), 400

        # Ler conteúdo do arquivo
        conteudo = arquivo.read().decode('utf-8')

        # Processar como JSON
        apostas_validas, erros = MonitoramentoApostasService.processar_apostas_json(conteudo)

        return jsonify({
            'sucesso': True,
            'nome_arquivo': arquivo.filename,
            'total_validas': len(apostas_validas),
            'total_erros': len(erros),
            'apostas': apostas_validas,
            'erros': erros
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao processar arquivo: {str(e)}'
        }), 500

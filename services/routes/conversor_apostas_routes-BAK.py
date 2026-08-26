"""
Routes para Conversor de Apostas - Dia de Sorte
Converte entre formatos TXT e JSON
"""

from flask import Blueprint, request, jsonify, render_template, send_file
from services.conversor_apostas_service import ConversorApostasService
import io
import json

# Criar blueprint
conversor_apostas_bp = Blueprint('conversor_apostas', __name__)


@conversor_apostas_bp.route('/conversor-apostas')
def pagina_conversor():
    """Página principal do conversor de apostas"""
    return render_template('conversor_apostas.html')


@conversor_apostas_bp.route('/api/conversor/upload', methods=['POST'])
def upload_arquivo():
    """
    Recebe upload de arquivo (.txt ou .json) e converte para JSON padrão

    Form data:
        - file: Arquivo enviado
        - concurso: Número do concurso
    """
    try:
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum arquivo enviado'
            }), 400

        arquivo = request.files['file']

        if arquivo.filename == '':
            return jsonify({
                'sucesso': False,
                'erro': 'Arquivo vazio'
            }), 400

        # Obter concurso
        concurso = request.form.get('concurso', 1139)
        try:
            concurso = int(concurso)
        except ValueError:
            concurso = 1139

        # Determinar tipo de arquivo
        tipo_arquivo = 'txt'
        if arquivo.filename.endswith('.json'):
            tipo_arquivo = 'json'

        # Ler conteúdo
        conteudo = arquivo.read().decode('utf-8')

        # Processar
        resultado = ConversorApostasService.processar_arquivo_upload(
            conteudo,
            tipo_arquivo,
            concurso
        )

        if resultado['sucesso']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao processar upload: {str(e)}'
        }), 500


@conversor_apostas_bp.route('/api/conversor/texto-para-json', methods=['POST'])
def texto_para_json():
    """
    Converte texto de apostas para JSON padrão

    JSON body:
        {
            "texto": "1 10 11 17 22 27 28 Jan\n...",
            "concurso": 1139
        }
    """
    try:
        dados = request.get_json()

        if not dados or 'texto' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "texto" obrigatório'
            }), 400

        texto = dados['texto']
        concurso = dados.get('concurso', 1139)

        # Converter
        resultado_json = ConversorApostasService.texto_para_json(texto, concurso)

        # Validar
        validacao = ConversorApostasService.validar_apostas(resultado_json)

        return jsonify({
            'sucesso': True,
            'dados': resultado_json,
            'validacao': validacao
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao converter: {str(e)}'
        }), 500


@conversor_apostas_bp.route('/api/conversor/json-para-texto', methods=['POST'])
def json_para_texto():
    """
    Converte JSON padrão para texto formato apostas.txt

    JSON body:
        {
            "concurso": 1139,
            "apostas": [...]
        }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'erro': 'JSON vazio'
            }), 400

        # Converter
        texto = ConversorApostasService.json_para_texto(dados)

        return jsonify({
            'sucesso': True,
            'texto': texto
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao converter: {str(e)}'
        }), 500


@conversor_apostas_bp.route('/api/conversor/validar', methods=['POST'])
def validar_apostas():
    """
    Valida JSON de apostas

    JSON body:
        {
            "concurso": 1139,
            "apostas": [...]
        }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'erro': 'JSON vazio'
            }), 400

        # Validar
        validacao = ConversorApostasService.validar_apostas(dados)

        return jsonify({
            'sucesso': True,
            'validacao': validacao
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao validar: {str(e)}'
        }), 500


@conversor_apostas_bp.route('/api/conversor/mes/serializar', methods=['POST'])
def serializar_mes():
    """
    Converte mês para formato específico

    JSON body:
        {
            "mes": "Janeiro",
            "formato": "numero"  // ou "abreviado" ou "extenso"
        }
    """
    try:
        dados = request.get_json()

        if not dados or 'mes' not in dados:
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "mes" obrigatório'
            }), 400

        mes = dados['mes']
        formato = dados.get('formato', 'abreviado')

        # Validar formato
        if formato not in ['numero', 'abreviado', 'extenso']:
            return jsonify({
                'sucesso': False,
                'erro': 'Formato deve ser "numero", "abreviado" ou "extenso"'
            }), 400

        # Serializar
        mes_serializado = ConversorApostasService.serializar_mes(mes, formato)

        return jsonify({
            'sucesso': True,
            'mes_original': mes,
            'mes_serializado': mes_serializado,
            'formato': formato
        }), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao serializar: {str(e)}'
        }), 500


@conversor_apostas_bp.route('/api/conversor/download/json', methods=['POST'])
def download_json():
    """
    Gera arquivo apostas.json para download

    JSON body:
        {
            "concurso": 1139,
            "apostas": [...]
        }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'erro': 'JSON vazio'
            }), 400

        # Gerar JSON formatado
        json_str = json.dumps(dados, indent=2, ensure_ascii=False)

        # Criar arquivo em memória
        buffer = io.BytesIO(json_str.encode('utf-8'))
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name='apostas.json'
        )

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao gerar download: {str(e)}'
        }), 500


@conversor_apostas_bp.route('/api/conversor/download/txt', methods=['POST'])
def download_txt():
    """
    Gera arquivo apostas.txt para download

    JSON body:
        {
            "concurso": 1139,
            "apostas": [...]
        }
    """
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({
                'sucesso': False,
                'erro': 'JSON vazio'
            }), 400

        # Converter para texto
        texto = ConversorApostasService.json_para_texto(dados)

        # Criar arquivo em memória
        buffer = io.BytesIO(texto.encode('utf-8'))
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='text/plain',
            as_attachment=True,
            download_name='apostas.txt'
        )

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao gerar download: {str(e)}'
        }), 500

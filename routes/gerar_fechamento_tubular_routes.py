from flask import Blueprint, jsonify, render_template, request, send_file, make_response
from services.gerar_fechamento_tubular_service import GerarFechamentoTubularService
import io
from datetime import datetime

gerar_fechamento_tubular_bp = Blueprint('gerar_fechamento_tubular', __name__)


@gerar_fechamento_tubular_bp.route('/ferramentas/gerar-fechamento-tubular')
def pagina_gerar_fechamento_tubular():
    """Página principal do gerador tubular"""
    return render_template('gerar_fechamento_tubular.html')


@gerar_fechamento_tubular_bp.route('/api/ferramentas/opcoes-fechamento-tubular')
def api_opcoes_fechamento():
    """Retorna opções de fechamento (TOP 3, recomendações, etc)"""
    try:
        opcoes = GerarFechamentoTubularService.obter_opcoes_para_fechamento()
        return jsonify(opcoes), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@gerar_fechamento_tubular_bp.route('/api/ferramentas/gerar-jogos-tubular', methods=['POST'])
def api_gerar_jogos():
    """
    🆕 MODIFICADO: Retorna formato completo com filtros aplicados

    Request JSON:
    {
        "quantidade": 15,
        "sequencia": "Sequência de 2 (63.44%)",
        "par_impar": "3P/4I",
        "mes": "Novembro",
        "digitos_unicos": "7 dígitos únicos",
        "excluir_numero": [11, 13],
        "fixar_numero": [7],
        "faixa_min": 1,
        "faixa_max": 31
    }

    Response JSON:
    {
        "ok": true,
        "total": 15,
        "jogos": [...],
        "apostas": [["01","02",...], ...],
        "filtros": {...}
    }
    """
    try:
        parametros = request.get_json()
        resultado = GerarFechamentoTubularService.gerar_jogos(parametros)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500


# ========================================================================
# 🆕 ROTA DE TESTE JSON
# ========================================================================

@gerar_fechamento_tubular_bp.route('/api/fechamento/teste', methods=['GET'])
def api_teste_fechamento():
    """
    Endpoint de teste para validar filtros e geração

    Retorna preview de como ficaria a geração com filtros padrão
    """
    try:
        # Gera 5 jogos de teste
        parametros_teste = {
            'quantidade': 5,
            'sequencia': 'Sequência de 2',
            'par_impar': '3P/4I',
            'mes': 'Março',
            'excluir_numero': [11, 13],
            'fixar_numero': [7]
        }

        resultado = GerarFechamentoTubularService.gerar_jogos(parametros_teste)

        # Monta preview em formato texto
        preview = []
        for jogo in resultado['jogos']:
            numeros_str = ' '.join([f"{n:02d}" for n in jogo['numeros']])
            mes_abrev = GerarFechamentoTubularService.MESES_ABREV[jogo['mes_sorte']]
            preview.append(f"{numeros_str} {mes_abrev}")

        return jsonify({
            'status': True,
            'filtros_ativos': resultado['filtros'],
            'qtd_apostas': resultado['total'],
            'preview': preview,
            'jogos_completos': resultado['jogos']
        }), 200

    except Exception as e:
        return jsonify({
            'status': False,
            'erro': str(e)
        }), 500


# ========================================================================
# 🆕 ROTAS DE EXPORTAÇÃO
# ========================================================================

@gerar_fechamento_tubular_bp.route('/api/fechamento/exportar/txt', methods=['POST'])
def api_exportar_txt():
    """
    Exporta palpites em formato TXT

    Request JSON:
    {
        "jogos": [...],  // Resultado do gerar_jogos()
    }

    Retorna: Arquivo .txt para download
    """
    try:
        dados = request.get_json()
        jogos_data = dados.get('jogos_data')

        if not jogos_data:
            return jsonify({'erro': 'Dados de jogos não fornecidos'}), 400

        # Gera conteúdo TXT
        conteudo_txt = GerarFechamentoTubularService.exportar_txt(jogos_data)

        # Cria arquivo para download
        output = io.BytesIO()
        output.write(conteudo_txt.encode('utf-8'))
        output.seek(0)

        filename = f"palpites_tubular_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        return send_file(
            output,
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@gerar_fechamento_tubular_bp.route('/api/fechamento/exportar/xls', methods=['POST'])
def api_exportar_xls():
    """
    Exporta palpites em formato Excel (.xlsx)

    Request JSON:
    {
        "jogos_data": {...}  // Resultado do gerar_jogos()
    }

    Retorna: Arquivo .xlsx para download
    """
    try:
        dados = request.get_json()
        jogos_data = dados.get('jogos_data')

        if not jogos_data:
            return jsonify({'erro': 'Dados de jogos não fornecidos'}), 400

        # Gera arquivo Excel
        excel_bytes = GerarFechamentoTubularService.exportar_xls(jogos_data)

        # Cria arquivo para download
        output = io.BytesIO(excel_bytes)
        output.seek(0)

        filename = f"palpites_tubular_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@gerar_fechamento_tubular_bp.route('/api/fechamento/exportar/html', methods=['POST'])
def api_exportar_html():
    """
    Exporta palpites em formato HTML completo

    Request JSON:
    {
        "jogos_data": {...},  // Resultado do gerar_jogos()
        "parametros": {...}   // Parâmetros usados na geração
    }

    Retorna: Arquivo .html para download
    """
    try:
        dados = request.get_json()
        jogos_data = dados.get('jogos_data')
        parametros = dados.get('parametros', {})

        if not jogos_data:
            return jsonify({'erro': 'Dados de jogos não fornecidos'}), 400

        # Gera HTML
        html_conteudo = GerarFechamentoTubularService.exportar_html(jogos_data, parametros)

        # Cria arquivo para download
        output = io.BytesIO()
        output.write(html_conteudo.encode('utf-8'))
        output.seek(0)

        filename = f"palpites_tubular_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        return send_file(
            output,
            mimetype='text/html',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ========================================================================
# 🆕 ROTAS AUXILIARES
# ========================================================================

@gerar_fechamento_tubular_bp.route('/api/fechamento/validar-filtros', methods=['POST'])
def api_validar_filtros():
    """
    Valida se os filtros são compatíveis entre si

    Request JSON:
    {
        "excluir_numero": [11, 13],
        "fixar_numero": [7],
        "par_impar": "3P/4I",
        "faixa_min": 1,
        "faixa_max": 31
    }

    Response:
    {
        "valido": true,
        "avisos": ["..."],
        "erros": ["..."]
    }
    """
    try:
        filtros = request.get_json()

        avisos = []
        erros = []

        # Validação 1: Números fixos não podem estar em excluídos
        fixos = set(filtros.get('fixar_numero', []))
        excluidos = set(filtros.get('excluir_numero', []))

        conflito = fixos.intersection(excluidos)
        if conflito:
            erros.append(f"Números {list(conflito)} estão tanto em FIXOS quanto em EXCLUÍDOS")

        # Validação 2: Números fixos devem estar dentro da faixa
        faixa_min = filtros.get('faixa_min', 1)
        faixa_max = filtros.get('faixa_max', 31)

        for num in fixos:
            if num < faixa_min or num > faixa_max:
                erros.append(f"Número fixo {num} está fora da faixa {faixa_min}-{faixa_max}")

        # Validação 3: Deve haver números suficientes disponíveis
        pool_disponivel = set(range(faixa_min, faixa_max + 1)) - excluidos

        if len(pool_disponivel) < 7:
            erros.append(f"Apenas {len(pool_disponivel)} números disponíveis. Necessário pelo menos 7.")

        # Validação 4: Par/Ímpar compatível com números fixos
        par_impar = filtros.get('par_impar')
        if par_impar:
            pares_necessarios = int(par_impar.split('P')[0])
            impares_necessarios = 7 - pares_necessarios

            pares_fixos = sum(1 for n in fixos if n % 2 == 0)
            impares_fixos = sum(1 for n in fixos if n % 2 != 0)

            if pares_fixos > pares_necessarios:
                avisos.append(f"Há {pares_fixos} pares fixos mas padrão exige apenas {pares_necessarios}")

            if impares_fixos > impares_necessarios:
                avisos.append(f"Há {impares_fixos} ímpares fixos mas padrão exige apenas {impares_necessarios}")

        return jsonify({
            'valido': len(erros) == 0,
            'avisos': avisos,
            'erros': erros
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@gerar_fechamento_tubular_bp.route('/api/fechamento/estatisticas', methods=['POST'])
def api_estatisticas_jogos():
    """
    Retorna estatísticas dos jogos gerados

    Request JSON:
    {
        "jogos": [...]
    }

    Response:
    {
        "total_jogos": 15,
        "soma_media": 98.5,
        "soma_min": 80,
        "soma_max": 115,
        "pares_medio": 3.2,
        "jogos_com_sequencia": 12
    }
    """
    try:
        dados = request.get_json()
        jogos = dados.get('jogos', [])

        if not jogos:
            return jsonify({'erro': 'Nenhum jogo fornecido'}), 400

        somas = [jogo['analise']['soma'] for jogo in jogos]
        pares = [jogo['analise']['pares'] for jogo in jogos]
        com_sequencia = sum(1 for jogo in jogos if jogo['analise']['tem_sequencia'])

        return jsonify({
            'total_jogos': len(jogos),
            'soma_media': sum(somas) / len(somas),
            'soma_min': min(somas),
            'soma_max': max(somas),
            'pares_medio': sum(pares) / len(pares),
            'jogos_com_sequencia': com_sequencia,
            'percentual_com_sequencia': (com_sequencia / len(jogos)) * 100
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

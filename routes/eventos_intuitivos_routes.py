# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Routes: Eventos Intuitivos COM AUTO-PREENCHIMENTO

"""
ESTE ARQUIVO VAI EM: routes/eventos_intuitivos_routes.py

IMPORTANTE: Adicione ao app.py:
    from routes.eventos_intuitivos_routes import eventos_bp
    app.register_blueprint(eventos_bp)
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from services.eventos_intuitivos_service import EventosIntuitivosService
from datetime import datetime

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos-intuitivos')


@eventos_bp.route('/')
def listar():
    """Lista todos os eventos"""
    try:
        eventos = EventosIntuitivosService.listar_eventos()
        return render_template('eventos_intuitivos/lista.html', eventos=eventos)
    except Exception as e:
        flash(f'Erro ao listar eventos: {str(e)}', 'error')
        return render_template('eventos_intuitivos/lista.html', eventos=[])


@eventos_bp.route('/novo')
def novo():
    """Mostra formulário para criar novo evento"""
    return render_template('eventos_intuitivos/form.html')


@eventos_bp.route('/criar', methods=['POST'])
def criar():
    """Cria novo evento"""
    try:
        dados = {
            'tipo': request.form.get('tipo'),
            'titulo': request.form.get('titulo'),
            'descricao': request.form.get('descricao'),
            'data_evento': request.form.get('data_evento')
        }

        # Validar dados obrigatórios
        if not all([dados['tipo'], dados['titulo'], dados['descricao'], dados['data_evento']]):
            flash('❌ Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('eventos.novo'))

        evento = EventosIntuitivosService.criar_evento(dados)

        # Verificar se evento foi criado com sucesso
        if evento and 'id' in evento:
            flash(f'✅ Evento "{evento["titulo"]}" criado com sucesso!', 'success')
            return redirect(url_for('eventos.detalhes', evento_id=evento['id']))
        else:
            flash('❌ Erro ao criar evento: ID não retornado', 'error')
            return redirect(url_for('eventos.novo'))

    except ValueError as e:
        flash(f'❌ Dados inválidos: {str(e)}', 'error')
        return redirect(url_for('eventos.novo'))
    except Exception as e:
        import traceback
        print(f"ERRO ao criar evento: {str(e)}")
        print(traceback.format_exc())
        flash(f'❌ Erro ao criar evento: {str(e)}', 'error')
        return redirect(url_for('eventos.novo'))


@eventos_bp.route('/<int:evento_id>')
def detalhes(evento_id):
    """Mostra detalhes de um evento"""
    try:
        evento = EventosIntuitivosService.obter_evento(evento_id)
        if not evento:
            flash('❌ Evento não encontrado!', 'error')
            return redirect(url_for('eventos.listar'))

        # Buscar lista de concursos disponíveis para o dropdown
        from models.sorteio import Sorteio
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(100).all()
        lista_concursos = [{'concurso': s.concurso, 'data': s.data_sorteio.strftime('%d/%m/%Y')} for s in concursos]

        return render_template('eventos_intuitivos/detalhes.html',
                               evento=evento,
                               concursos=lista_concursos)

    except Exception as e:
        flash(f'❌ Erro ao carregar evento: {str(e)}', 'error')
        return redirect(url_for('eventos.listar'))


@eventos_bp.route('/<int:evento_id>/adicionar-aposta', methods=['POST'])
def adicionar_aposta(evento_id):
    """Adiciona aposta a um evento"""
    try:
        # Converter números de string para lista de inteiros
        numeros_str = request.form.get('numeros', '')
        numeros = [int(n.strip()) for n in numeros_str.split(',') if n.strip()]

        dados = {
            'modalidade': request.form.get('modalidade'),
            'numeros': numeros,
            'mes_sorte': int(request.form.get('mes_sorte')) if request.form.get('mes_sorte') else None,
            'interpretacao': request.form.get('interpretacao')
        }

        aposta = EventosIntuitivosService.adicionar_aposta(evento_id, dados)
        flash(f'✅ Aposta para {dados["modalidade"]} adicionada!', 'success')

    except Exception as e:
        flash(f'❌ Erro ao adicionar aposta: {str(e)}', 'error')

    return redirect(url_for('eventos.detalhes', evento_id=evento_id))


@eventos_bp.route('/aposta/<int:aposta_id>/conferir', methods=['POST'])
def conferir_resultado(aposta_id):
    """Confere resultado de uma aposta"""
    try:
        # Converter números sorteados de string para lista
        numeros_str = request.form.get('numeros_sorteados', '')
        numeros_sorteados = [int(n.strip()) for n in numeros_str.split(',') if n.strip()]

        dados = {
            'concurso': int(request.form.get('concurso')),
            'data_sorteio': request.form.get('data_sorteio'),
            'numeros_sorteados': numeros_sorteados,
            'mes_sorteado': int(request.form.get('mes_sorteado')) if request.form.get('mes_sorteado') else None
        }

        conferencia = EventosIntuitivosService.conferir_resultado(aposta_id, dados)

        acertos = conferencia['acertos']
        if acertos > 0:
            flash(f'✅ Conferido! {acertos} acerto(s)!', 'success')
        else:
            flash('❌ Conferido! Nenhum acerto.', 'warning')

        # Redirecionar de volta para os detalhes do evento
        from models.eventos_intuitivos import ApostaIntuitiva
        aposta = ApostaIntuitiva.query.get(aposta_id)
        return redirect(url_for('eventos.detalhes', evento_id=aposta.evento_id))

    except Exception as e:
        flash(f'❌ Erro ao conferir resultado: {str(e)}', 'error')
        return redirect(url_for('eventos.listar'))


@eventos_bp.route('/conferencia/<int:conferencia_id>/analise', methods=['POST'])
def adicionar_analise(conferencia_id):
    """Adiciona análise retrospectiva"""
    try:
        analise_texto = request.form.get('analise_final')

        if not analise_texto or not analise_texto.strip():
            flash('❌ Digite uma análise!', 'error')
        else:
            conferencia = EventosIntuitivosService.adicionar_analise(conferencia_id, analise_texto)
            flash('✅ Análise adicionada!', 'success')

        # Redirecionar de volta
        from models.eventos_intuitivos import ConferenciaResultado, ApostaIntuitiva
        conf = ConferenciaResultado.query.get(conferencia_id)
        aposta = ApostaIntuitiva.query.get(conf.aposta_id)
        return redirect(url_for('eventos.detalhes', evento_id=aposta.evento_id))

    except Exception as e:
        flash(f'❌ Erro ao adicionar análise: {str(e)}', 'error')
        return redirect(url_for('eventos.listar'))


@eventos_bp.route('/<int:evento_id>/excluir', methods=['POST'])
def excluir(evento_id):
    """Exclui um evento"""
    try:
        EventosIntuitivosService.excluir_evento(evento_id)
        flash('✅ Evento excluído!', 'success')
    except Exception as e:
        flash(f'❌ Erro ao excluir: {str(e)}', 'error')

    return redirect(url_for('eventos.listar'))


# ============================================
# API Endpoints
# ============================================

@eventos_bp.route('/api/eventos')
def api_listar():
    """API: Lista eventos"""
    try:
        eventos = EventosIntuitivosService.listar_eventos()
        return jsonify({'success': True, 'eventos': eventos})
    except Exception as e:
        return jsonify({'success': False, 'erro': str(e)}), 500


@eventos_bp.route('/api/evento/<int:evento_id>')
def api_obter(evento_id):
    """API: Obtém evento específico"""
    try:
        evento = EventosIntuitivosService.obter_evento(evento_id)
        if not evento:
            return jsonify({'success': False, 'erro': 'Evento não encontrado'}), 404
        return jsonify({'success': True, 'evento': evento})
    except Exception as e:
        return jsonify({'success': False, 'erro': str(e)}), 500


@eventos_bp.route('/api/sorteio/<int:concurso>')
def api_buscar_sorteio(concurso):
    """
    API: Busca dados de um sorteio pelo número do concurso
    Usado para auto-preencher o formulário de conferência
    """
    try:
        from models.sorteio import Sorteio

        sorteio = Sorteio.query.filter_by(concurso=concurso).first()

        if not sorteio:
            return jsonify({
                'success': False,
                'erro': f'Concurso {concurso} não encontrado no banco de dados'
            }), 404

        # Obter números em ambas as ordens
        numeros_ordem_sorteio = sorteio.get_posicoes_lista()  # Ordem que foram sorteados
        numeros_ordem_crescente = sorted(numeros_ordem_sorteio)  # Ordem crescente

        # Retornar dados formatados para o formulário
        return jsonify({
            'success': True,
            'sorteio': {
                'concurso': sorteio.concurso,
                'data_sorteio': sorteio.data_sorteio.strftime('%Y-%m-%d'),  # Formato para input date
                'data_sorteio_br': sorteio.data_sorteio.strftime('%d/%m/%Y'),  # Formato BR para exibição
                # Ordem do Sorteio (como foram sorteados)
                'numeros_sorteio': numeros_ordem_sorteio,
                'numeros_sorteio_str': ' - '.join(map(str, numeros_ordem_sorteio)),
                # Ordem Crescente
                'numeros_crescente': numeros_ordem_crescente,
                'numeros_crescente_str': ' - '.join(map(str, numeros_ordem_crescente)),
                # Para o formulário (usar ordem crescente como padrão para conferência)
                'numeros': numeros_ordem_crescente,
                'numeros_str': ', '.join(map(str, numeros_ordem_crescente)),
                # Mês
                'mes_sorte': sorteio.mes_sorte,
                'mes_sorte_nome': sorteio.get_nome_mes()
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'erro': str(e)}), 500


@eventos_bp.route('/api/concursos')
def api_listar_concursos():
    """
    API: Lista todos os concursos disponíveis (para dropdown)
    """
    try:
        from models.sorteio import Sorteio

        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        lista = [{
            'concurso': s.concurso,
            'data': s.data_sorteio.strftime('%d/%m/%Y'),
            'label': f"Concurso {s.concurso} - {s.data_sorteio.strftime('%d/%m/%Y')}"
        } for s in concursos]

        return jsonify({'success': True, 'concursos': lista})

    except Exception as e:
        return jsonify({'success': False, 'erro': str(e)}), 500

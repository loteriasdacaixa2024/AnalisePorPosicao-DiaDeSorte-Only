# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint, request, jsonify, render_template
from models import Sorteio, db
from sqlalchemy import or_, and_

# Criar blueprint de sorteios
sorteio_bp = Blueprint('sorteio', __name__)

# Rota: Página principal (HTML)
@sorteio_bp.route('/')
def index():
    return render_template('index.html')

# Rota: Listar todos os sorteios com paginação
@sorteio_bp.route('/api/sorteios', methods=['GET'])
def listar_sorteios():
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        ordenar = request.args.get('ordenar', 'concurso')
        direcao = request.args.get('direcao', 'desc')
        
        if por_pagina > 100:
            por_pagina = 100
        
        query = Sorteio.query
        
        if hasattr(Sorteio, ordenar):
            coluna = getattr(Sorteio, ordenar)
            if direcao == 'asc':
                query = query.order_by(coluna.asc())
            else:
                query = query.order_by(coluna.desc())
        else:
            query = query.order_by(Sorteio.concurso.desc())
        
        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        return jsonify({
            'sorteios': [s.to_dict() for s in paginacao.items],
            'total': paginacao.total,
            'pagina': paginacao.page,
            'total_paginas': paginacao.pages,
            'por_pagina': por_pagina,
            'tem_proxima': paginacao.has_next,
            'tem_anterior': paginacao.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao listar sorteios: {str(e)}'}), 500

# Rota: Últimos N sorteios
@sorteio_bp.route('/api/sorteios/ultimos/<int:quantidade>', methods=['GET'])
def ultimos_sorteios(quantidade):
    try:
        if quantidade < 1:
            quantidade = 10
        if quantidade > 100:
            quantidade = 100
        
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(quantidade).all()
        
        # Se não houver sorteios, retornar lista vazia (não erro)
        if not sorteios:
            return jsonify({
                'quantidade': 0,
                'sorteios': [],
                'mensagem': 'Nenhum sorteio encontrado. Sincronize com a API da Caixa.'
            }), 200
        
        return jsonify({
            'quantidade': len(sorteios),
            'sorteios': [s.to_dict() for s in sorteios]
        }), 200
        
    except Exception as e:
        print(f"❌ ERRO em ultimos_sorteios: {str(e)}")
        return jsonify({'erro': f'Erro ao buscar últimos sorteios: {str(e)}'}), 500

# Rota: Buscar sorteio por concurso
@sorteio_bp.route('/api/sorteios/<int:concurso>', methods=['GET'])
def buscar_sorteio(concurso):
    try:
        sorteio = Sorteio.query.filter_by(concurso=concurso).first()
        
        if not sorteio:
            return jsonify({'erro': f'Sorteio {concurso} não encontrado'}), 404
        
        return jsonify(sorteio.to_dict()), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao buscar sorteio: {str(e)}'}), 500

# Rota: Filtrar por número
@sorteio_bp.route('/api/sorteios/filtrar/numero/<int:numero>', methods=['GET'])
def filtrar_por_numero(numero):
    try:
        if not Sorteio.validar_numero(numero):
            return jsonify({'erro': 'Número inválido. Deve estar entre 1 e 31'}), 400
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        
        if por_pagina > 100:
            por_pagina = 100
        
        query = Sorteio.query.filter(
            or_(
                Sorteio.posicao_1 == numero,
                Sorteio.posicao_2 == numero,
                Sorteio.posicao_3 == numero,
                Sorteio.posicao_4 == numero,
                Sorteio.posicao_5 == numero,
                Sorteio.posicao_6 == numero,
                Sorteio.posicao_7 == numero
            )
        ).order_by(Sorteio.concurso.desc())
        
        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        return jsonify({
            'numero': numero,
            'sorteios': [s.to_dict() for s in paginacao.items],
            'total': paginacao.total,
            'pagina': paginacao.page,
            'total_paginas': paginacao.pages
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao filtrar por número: {str(e)}'}), 500

# Rota: Filtrar por número E posição específica
@sorteio_bp.route('/api/sorteios/filtrar/posicao/<int:posicao>/numero/<int:numero>', methods=['GET'])
def filtrar_por_posicao_numero(posicao, numero):
    try:
        if posicao < 1 or posicao > 7:
            return jsonify({'erro': 'Posição inválida. Deve estar entre 1 e 7'}), 400
        
        if not Sorteio.validar_numero(numero):
            return jsonify({'erro': 'Número inválido. Deve estar entre 1 e 31'}), 400
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        
        if por_pagina > 100:
            por_pagina = 100
        
        coluna_posicao = getattr(Sorteio, f'posicao_{posicao}')
        query = Sorteio.query.filter(coluna_posicao == numero).order_by(Sorteio.concurso.desc())
        
        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        return jsonify({
            'posicao': posicao,
            'numero': numero,
            'sorteios': [s.to_dict() for s in paginacao.items],
            'total': paginacao.total,
            'pagina': paginacao.page,
            'total_paginas': paginacao.pages
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao filtrar por posição e número: {str(e)}'}), 500

# Rota: Filtrar por mês da sorte
@sorteio_bp.route('/api/sorteios/filtrar/mes/<int:mes>', methods=['GET'])
def filtrar_por_mes(mes):
    try:
        if not Sorteio.validar_mes(mes):
            return jsonify({'erro': 'Mês inválido. Deve estar entre 1 e 12'}), 400
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        
        if por_pagina > 100:
            por_pagina = 100
        
        query = Sorteio.query.filter_by(mes_sorte=mes).order_by(Sorteio.concurso.desc())
        
        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        return jsonify({
            'mes': mes,
            'sorteios': [s.to_dict() for s in paginacao.items],
            'total': paginacao.total,
            'pagina': paginacao.page,
            'total_paginas': paginacao.pages
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao filtrar por mês: {str(e)}'}), 500

# Rota: Filtrar por intervalo de concursos
@sorteio_bp.route('/api/sorteios/filtrar/intervalo', methods=['GET'])
def filtrar_por_intervalo():
    try:
        inicio = request.args.get('inicio', type=int)
        fim = request.args.get('fim', type=int)
        
        if not inicio or not fim:
            return jsonify({'erro': 'Parâmetros inicio e fim são obrigatórios'}), 400
        
        if inicio > fim:
            return jsonify({'erro': 'Concurso inicial não pode ser maior que o final'}), 400
        
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 50, type=int)
        
        if por_pagina > 100:
            por_pagina = 100
        
        query = Sorteio.query.filter(
            and_(
                Sorteio.concurso >= inicio,
                Sorteio.concurso <= fim
            )
        ).order_by(Sorteio.concurso.desc())
        
        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        return jsonify({
            'inicio': inicio,
            'fim': fim,
            'sorteios': [s.to_dict() for s in paginacao.items],
            'total': paginacao.total,
            'pagina': paginacao.page,
            'total_paginas': paginacao.pages
        }), 200
        
    except Exception as e:
        return jsonify({'erro': f'Erro ao filtrar por intervalo: {str(e)}'}), 500
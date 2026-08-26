# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import Usuario

def token_required(fn):
    """
    Decorator para rotas que exigem autenticação
    Verifica se o token JWT é válido
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'erro': 'Token inválido ou expirado', 'detalhes': str(e)}), 401
    return wrapper

def admin_required(fn):
    """
    Decorator para rotas que exigem privilégios de administrador
    Verifica se o usuário é admin
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            usuario_id = get_jwt_identity()
            usuario = Usuario.query.get(usuario_id)
            
            if not usuario:
                return jsonify({'erro': 'Usuário não encontrado'}), 404
            
            if not usuario.admin:
                return jsonify({'erro': 'Acesso negado. Apenas administradores.'}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'erro': 'Erro ao verificar permissões', 'detalhes': str(e)}), 401
    return wrapper

def usuario_ativo_required(fn):
    """
    Decorator para rotas que exigem usuário ativo
    Verifica se o usuário não foi desativado
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            usuario_id = get_jwt_identity()
            usuario = Usuario.query.get(usuario_id)
            
            if not usuario:
                return jsonify({'erro': 'Usuário não encontrado'}), 404
            
            if not usuario.ativo:
                return jsonify({'erro': 'Usuário desativado. Contate o administrador.'}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'erro': 'Erro ao verificar status do usuário', 'detalhes': str(e)}), 401
    return wrapper

def get_usuario_atual():
    """
    Retorna o usuário autenticado da requisição atual
    Retorna None se não houver usuário autenticado
    """
    try:
        verify_jwt_in_request()
        usuario_id = get_jwt_identity()
        return Usuario.query.get(usuario_id)
    except:
        return None

def verificar_propriedade_ou_admin(usuario_id_alvo):
    """
    Verifica se o usuário autenticado é o próprio ou é admin
    Útil para operações que podem ser feitas pelo próprio usuário ou por admin
    """
    try:
        verify_jwt_in_request()
        usuario_id_atual = get_jwt_identity()
        usuario_atual = Usuario.query.get(usuario_id_atual)
        
        if not usuario_atual:
            return False, jsonify({'erro': 'Usuário não encontrado'}), 404
        
        # Verifica se é o próprio usuário ou se é admin
        if usuario_atual.id == usuario_id_alvo or usuario_atual.admin:
            return True, None, None
        else:
            return False, jsonify({'erro': 'Acesso negado'}), 403
            
    except Exception as e:
        return False, jsonify({'erro': 'Erro ao verificar permissões', 'detalhes': str(e)}), 401
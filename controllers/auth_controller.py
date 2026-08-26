# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity
)
from models.sorteio import db
from models.usuario import Usuario
from datetime import datetime

class AuthController:
    """
    Controlador de autenticação
    Gerencia login, registro e validação de tokens JWT
    """
    
    @staticmethod
    def registrar():
        """
        Registra um novo usuário no sistema
        POST /api/auth/registrar
        Body: { "nome", "email", "senha" }
        """
        try:
            dados = request.get_json()
            
            # Validar dados obrigatórios
            if not dados:
                return jsonify({'erro': 'Dados não fornecidos'}), 400
            
            nome = dados.get('nome', '').strip()
            email = dados.get('email', '').strip().lower()
            senha = dados.get('senha', '')
            
            if not nome or not email or not senha:
                return jsonify({'erro': 'Nome, email e senha são obrigatórios'}), 400
            
            # Criar usuário usando método estático do modelo
            usuario, erro = Usuario.criar_usuario(nome, email, senha, admin=False)
            
            if erro:
                return jsonify({'erro': erro}), 400
            
            # Gerar tokens
            access_token = create_access_token(identity=usuario.id)
            refresh_token = create_refresh_token(identity=usuario.id)
            
            return jsonify({
                'mensagem': 'Usuário registrado com sucesso',
                'usuario': usuario.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 201
            
        except Exception as e:
            return jsonify({'erro': f'Erro ao registrar usuário: {str(e)}'}), 500
    
    @staticmethod
    def login():
        """
        Realiza login do usuário
        POST /api/auth/login
        Body: { "email", "senha" }
        """
        try:
            dados = request.get_json()
            
            # Validar dados obrigatórios
            if not dados:
                return jsonify({'erro': 'Dados não fornecidos'}), 400
            
            email = dados.get('email', '').strip().lower()
            senha = dados.get('senha', '')
            
            if not email or not senha:
                return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
            
            # Buscar usuário
            usuario = Usuario.buscar_por_email(email)
            
            if not usuario:
                return jsonify({'erro': 'Email ou senha incorretos'}), 401
            
            # Verificar se usuário está ativo
            if not usuario.ativo:
                return jsonify({'erro': 'Usuário desativado. Contate o administrador.'}), 403
            
            # Verificar senha
            if not usuario.verificar_senha(senha):
                return jsonify({'erro': 'Email ou senha incorretos'}), 401
            
            # Atualizar último acesso
            usuario.atualizar_ultimo_acesso()
            
            # Gerar tokens
            access_token = create_access_token(identity=usuario.id)
            refresh_token = create_refresh_token(identity=usuario.id)
            
            return jsonify({
                'mensagem': 'Login realizado com sucesso',
                'usuario': usuario.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 200
            
        except Exception as e:
            return jsonify({'erro': f'Erro ao fazer login: {str(e)}'}), 500
    
    @staticmethod
    @jwt_required()
    def perfil():
        """
        Retorna o perfil do usuário autenticado
        GET /api/auth/perfil
        Header: Authorization: Bearer <token>
        """
        try:
            # Obter ID do usuário do token
            usuario_id = get_jwt_identity()
            
            # Buscar usuário
            usuario = Usuario.query.get(usuario_id)
            
            if not usuario:
                return jsonify({'erro': 'Usuário não encontrado'}), 404
            
            return jsonify({
                'usuario': usuario.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({'erro': f'Erro ao buscar perfil: {str(e)}'}), 500
    
    @staticmethod
    @jwt_required()
    def atualizar_perfil():
        """
        Atualiza dados do perfil do usuário autenticado
        PUT /api/auth/perfil
        Header: Authorization: Bearer <token>
        Body: { "nome"?, "senha_atual"?, "senha_nova"? }
        """
        try:
            usuario_id = get_jwt_identity()
            usuario = Usuario.query.get(usuario_id)
            
            if not usuario:
                return jsonify({'erro': 'Usuário não encontrado'}), 404
            
            dados = request.get_json()
            
            if not dados:
                return jsonify({'erro': 'Dados não fornecidos'}), 400
            
            # Atualizar nome se fornecido
            if 'nome' in dados and dados['nome'].strip():
                usuario.nome = dados['nome'].strip()
            
            # Atualizar senha se fornecida
            if 'senha_atual' in dados and 'senha_nova' in dados:
                senha_atual = dados['senha_atual']
                senha_nova = dados['senha_nova']
                
                # Verificar senha atual
                if not usuario.verificar_senha(senha_atual):
                    return jsonify({'erro': 'Senha atual incorreta'}), 401
                
                # Validar nova senha
                senha_valida, mensagem = Usuario.validar_senha(senha_nova)
                if not senha_valida:
                    return jsonify({'erro': mensagem}), 400
                
                # Atualizar senha
                usuario.set_senha(senha_nova)
            
            db.session.commit()
            
            return jsonify({
                'mensagem': 'Perfil atualizado com sucesso',
                'usuario': usuario.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'erro': f'Erro ao atualizar perfil: {str(e)}'}), 500
    
    @staticmethod
    @jwt_required(refresh=True)
    def refresh():
        """
        Renova o token de acesso usando refresh token
        POST /api/auth/refresh
        Header: Authorization: Bearer <refresh_token>
        """
        try:
            usuario_id = get_jwt_identity()
            novo_token = create_access_token(identity=usuario_id)
            
            return jsonify({
                'access_token': novo_token
            }), 200
            
        except Exception as e:
            return jsonify({'erro': f'Erro ao renovar token: {str(e)}'}), 500
    
    @staticmethod
    @jwt_required()
    def verificar_admin():
        """
        Verifica se o usuário autenticado é administrador
        GET /api/auth/verificar-admin
        Header: Authorization: Bearer <token>
        """
        try:
            usuario_id = get_jwt_identity()
            usuario = Usuario.query.get(usuario_id)
            
            if not usuario:
                return jsonify({'erro': 'Usuário não encontrado'}), 404
            
            return jsonify({
                'admin': usuario.admin
            }), 200
            
        except Exception as e:
            return jsonify({'erro': f'Erro ao verificar admin: {str(e)}'}), 500
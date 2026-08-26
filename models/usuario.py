# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models.shared import db

class Usuario(db.Model):
    """
    Modelo para armazenar usuários do sistema
    """
    
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def atualizar_ultimo_acesso(self):
        self.ultimo_acesso = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, incluir_sensivel=False):
        dados = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'ativo': self.ativo,
            'admin': self.admin,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M:%S') if self.criado_em else None,
            'ultimo_acesso': self.ultimo_acesso.strftime('%d/%m/%Y %H:%M:%S') if self.ultimo_acesso else None
        }
        
        if incluir_sensivel:
            dados['senha_hash'] = self.senha_hash
        
        return dados
    
    def ativar(self):
        self.ativo = True
        db.session.commit()
    
    def desativar(self):
        self.ativo = False
        db.session.commit()
    
    def tornar_admin(self):
        self.admin = True
        db.session.commit()
    
    def remover_admin(self):
        self.admin = False
        db.session.commit()
    
    @staticmethod
    def validar_email(email):
        import re
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    @staticmethod
    def validar_senha(senha):
        if len(senha) < 6:
            return False, "A senha deve ter no mínimo 6 caracteres"
        return True, "Senha válida"
    
    @staticmethod
    def buscar_por_email(email):
        return Usuario.query.filter_by(email=email).first()
    
    @staticmethod
    def criar_usuario(nome, email, senha, admin=False):
        if not Usuario.validar_email(email):
            return None, "Email inválido"
        
        if Usuario.buscar_por_email(email):
            return None, "Email já cadastrado"
        
        senha_valida, mensagem = Usuario.validar_senha(senha)
        if not senha_valida:
            return None, mensagem
        
        usuario = Usuario(nome=nome, email=email, admin=admin)
        usuario.set_senha(senha)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            return usuario, None
        except Exception as e:
            db.session.rollback()
            return None, f"Erro ao criar usuário: {str(e)}"
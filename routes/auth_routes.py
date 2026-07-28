# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

from flask import Blueprint
from controllers.auth_controller import AuthController

# Criar blueprint de autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Rota: Registrar novo usuário
@auth_bp.route('/registrar', methods=['POST'])
def registrar():
    return AuthController.registrar()

# Rota: Login
@auth_bp.route('/login', methods=['POST'])
def login():
    return AuthController.login()

# Rota: Ver perfil do usuário autenticado
@auth_bp.route('/perfil', methods=['GET'])
def perfil():
    return AuthController.perfil()

# Rota: Atualizar perfil do usuário autenticado
@auth_bp.route('/perfil', methods=['PUT'])
def atualizar_perfil():
    return AuthController.atualizar_perfil()

# Rota: Renovar token de acesso
@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    return AuthController.refresh()

# Rota: Verificar se usuário é admin
@auth_bp.route('/verificar-admin', methods=['GET'])
def verificar_admin():
    return AuthController.verificar_admin()
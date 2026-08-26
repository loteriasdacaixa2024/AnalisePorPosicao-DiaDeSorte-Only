from flask import Blueprint, render_template

visualizacao_tubular_bp = Blueprint('visualizacao_tubular', __name__)

@visualizacao_tubular_bp.route('/visualizacao-tubular')
def pagina_visualizacao_tubular():
    return render_template('vizualizacao_tubular.html')
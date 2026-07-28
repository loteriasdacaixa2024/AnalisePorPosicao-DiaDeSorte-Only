"""
Rota exclusiva para o Índice Central de Análises
Apenas renderiza a tabela de sumário para organizar o acesso.
"""

from flask import Blueprint, render_template

indice_analises_bp = Blueprint('indice_analises', __name__)

@indice_analises_bp.route('/indice-analises')
def pagina_indice_analises():
    """
    Exibe a interface central de acesso às análises.
    O formato é uma tabela estruturada (Análise, O que faz, Acesso rápido).
    Nenhuma lógica de negócios é impactada.
    """
    return render_template('indice_analises.html')

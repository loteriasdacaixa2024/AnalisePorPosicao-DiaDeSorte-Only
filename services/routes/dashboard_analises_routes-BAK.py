"""
Rotas para Dashboard de Análises
Consolidação de todas as análises do sistema
"""

from flask import Blueprint, render_template, jsonify
from services.dashboard_analises_service import DashboardAnalisesService

dashboard_analises_bp = Blueprint('dashboard_analises', __name__)


@dashboard_analises_bp.route('/dashboard-analises')
def dashboard_analises():
    """Página do dashboard de análises"""
    return render_template('dashboard_analises.html')


@dashboard_analises_bp.route('/api/dashboard/analises')
def api_dashboard_analises():
    """API que retorna dados consolidados do dashboard"""
    try:
        dados = DashboardAnalisesService.obter_dashboard_completo()
        return jsonify(dados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

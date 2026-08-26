"""
================================================================================
ROUTES: Análises Sequenciais - DIA DE SORTE
================================================================================
Módulo ISOLADO para rotas de análises sequenciais.

URL BASE: http://localhost:5050/sequenciais

ENDPOINTS:
- GET  /dashboard              → Página principal
- GET  /api/analise            → Análise completa de sequências
- GET  /api/ultimo-concurso    → Último concurso (para auto-sync)
- GET  /api/status             → Status do serviço

Destino: routes/analises_sequenciais_routes.py
================================================================================
"""

from flask import Blueprint, render_template, jsonify
from services.analises_sequenciais_service import AnalisesSequenciaisService

# =============================================================================
# BLUEPRINT
# =============================================================================

sequenciais_bp = Blueprint('sequenciais', __name__, url_prefix='/sequenciais')

# =============================================================================
# PÁGINA PRINCIPAL
# =============================================================================

@sequenciais_bp.route('/dashboard')
def dashboard():
    """Página principal do dashboard de análises sequenciais"""
    return render_template('dashboard_sequenciais.html')

# =============================================================================
# API - ANÁLISE COMPLETA
# =============================================================================

@sequenciais_bp.route('/api/analise')
def api_analise():
    """API: Análise completa de sequências consecutivas"""
    try:
        dados = AnalisesSequenciaisService.analisar_sequencias()
        status = 200 if dados.get('sucesso') else 500
        return jsonify(dados), status
    except Exception as e:
        import traceback
        erro_detalhado = traceback.format_exc()
        print(f"[ERRO API ANALISE] {erro_detalhado}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'detalhes': erro_detalhado
        }), 500

# =============================================================================
# API - ÚLTIMO CONCURSO (para auto-sync)
# =============================================================================

@sequenciais_bp.route('/api/ultimo-concurso')
def api_ultimo_concurso():
    """API: Retorna o número do último concurso para verificar atualizações"""
    ultimo = AnalisesSequenciaisService.obter_ultimo_concurso()
    return jsonify({
        'ultimo_concurso': ultimo
    }), 200

# =============================================================================
# API - STATUS
# =============================================================================

@sequenciais_bp.route('/api/status')
def api_status():
    """API: Status do serviço de análises sequenciais"""
    status = AnalisesSequenciaisService.obter_status()
    return jsonify(status), 200

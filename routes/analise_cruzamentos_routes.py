"""
================================================================================
ROUTES: Análise de Cruzamentos - DIA DE SORTE
================================================================================
Módulo ISOLADO para rotas de cruzamentos estatísticos.

URL BASE: http://localhost:5050/cruzamentos

ENDPOINTS:
- GET  /dashboard            → Página principal
- GET  /api/coluna-x-linha   → Análise #1: Coluna × Linha
- GET  /api/status           → Status de todas as análises

Destino: routes/analise_cruzamentos_routes.py
================================================================================
"""

from flask import Blueprint, render_template, jsonify
from services.analise_cruzamentos_service import AnaliseCruzamentosService

# =============================================================================
# BLUEPRINT
# =============================================================================

cruzamentos_bp = Blueprint('cruzamentos', __name__, url_prefix='/cruzamentos')

# =============================================================================
# PÁGINA PRINCIPAL
# =============================================================================

@cruzamentos_bp.route('/dashboard')
def dashboard():
    """Página principal do dashboard de cruzamentos"""
    return render_template('dashboard_cruzamentos.html')

# =============================================================================
# ✅ API - ANÁLISE 1: COLUNA × LINHA
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-linha')
def api_coluna_x_linha():
    """API: Análise Coluna × Linha (Mapa de Calor 2D)"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_linha()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# ✅ API - ANÁLISE 2: COLUNA × PARES/ÍMPARES
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-pares-impares')
def api_coluna_x_pares_impares():
    """API: Análise Coluna × Pares/Ímpares"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_pares_impares()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# ✅ API - ANÁLISE 3: COLUNA × QUENTES/FRIAS
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-quentes-frias')
def api_coluna_x_quentes_frias():
    """API: Análise Coluna × Quentes/Frias/Atrasadas"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_quentes_frias()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# ✅ API - ANÁLISE 4: COLUNA × PADRÃO DÍGITOS
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-padrao-digitos')
def api_coluna_x_padrao_digitos():
    """API: Análise Coluna × Padrão de Dígitos"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_padrao_digitos()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# ✅ API - ANÁLISE 5: COLUNA × SEQUÊNCIAS
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-sequencias')
def api_coluna_x_sequencias():
    """API: Análise Coluna × Sequências/Finais"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_sequencias()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# ✅ API - ANÁLISE 6: COLUNA × NÚMEROS JUNTOS
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-numeros-juntos')
def api_coluna_x_numeros_juntos():
    """API: Análise Coluna × Números Juntos"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_numeros_juntos()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# ✅ API - ANÁLISE 7: COLUNA × SOMA
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-soma')
def api_coluna_x_soma():
    """API: Análise Coluna × Soma Total"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_soma()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# ✅ API - ANÁLISE 8: COLUNA × DIA SEMANA
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-dia-semana')
def api_coluna_x_dia_semana():
    """API: Análise Coluna × Dia da Semana"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_dia_semana()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# ✅ API - ANÁLISE 9: COLUNA × MÊS
# =============================================================================

@cruzamentos_bp.route('/api/coluna-x-mes')
def api_coluna_x_mes():
    """API: Análise Coluna × Mês da Sorte"""
    dados = AnaliseCruzamentosService.analisar_coluna_x_mes()
    status = 200 if dados.get('sucesso') else 500
    return jsonify(dados), status

# =============================================================================
# STATUS DE TODAS AS ANÁLISES
# =============================================================================

@cruzamentos_bp.route('/api/status')
def api_status():
    """API: Status de todas as análises disponíveis"""
    status = AnaliseCruzamentosService.obter_status_analises()
    return jsonify(status), 200

from flask import Blueprint, jsonify, render_template
from services.analise_repeticao_concurso_anterior_service import AnaliseRepeticaoConcursoAnteriorService

analise_repeticao_concurso_anterior_bp = Blueprint('analise_repeticao_concurso_anterior', __name__)


@analise_repeticao_concurso_anterior_bp.route('/analises/repeticao-concurso-anterior')
def pagina_repeticao():
    """Página HTML de visualização da análise"""
    return render_template('analise_repeticao_concurso_anterior.html')


@analise_repeticao_concurso_anterior_bp.route('/api/analises/repeticao-concurso-anterior', methods=['GET'])
def api_repeticao():
    """
    API JSON para análise de repetição do concurso anterior
    Retorna Top 3, insights e recomendações
    """
    resultado = AnaliseRepeticaoConcursoAnteriorService.analisar_repeticoes()
    return jsonify(resultado), 200

from app import app
from services.gerador_atraso_posicao_service import GeradorAtrasoPosicaoService

with app.app_context():
    res = GeradorAtrasoPosicaoService.gerar_apostas_atraso_posicao('ultimo', 0, 7, 'aleatorio')
    print("Result:", res)

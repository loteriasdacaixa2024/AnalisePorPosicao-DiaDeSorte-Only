from app import create_app
from models.sorteio import Sorteio
app = create_app()
with app.app_context():
    s = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
    if s:
        print(f'Concurso: {s.concurso}')
        print(f'Dezenas: {s.posicao_1}, {s.posicao_2}, {s.posicao_3}, {s.posicao_4}, {s.posicao_5}, {s.posicao_6}, {s.posicao_7}')
        print(f'Mes: {s.mes_sorte}')
    else:
        print('Nenhum sorteio encontrado.')


from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte
from sqlalchemy import func, desc

app = create_app()
with app.app_context():
    # Top lotérica geral por total de prêmios
    top_loterica_geral = db.session.query(
        LocaisSorte.unidade_loterica,
        LocaisSorte.cidade,
        func.count(LocaisSorte.id).label('total_apostas'),
        func.sum(LocaisSorte.valor_premio).label('total_premios')
    ).filter_by(modalidade="Dia de Sorte").group_by(LocaisSorte.unidade_loterica, LocaisSorte.cidade).order_by(desc('total_premios')).first()
    
    if top_loterica_geral:
        loterica, cidade, total_apostas, total_premios = top_loterica_geral
        print("\nTop lotérica GERAL por total de prêmios:")
        print(f"  Lotérica: {loterica}")
        print(f"  Cidade: {cidade}")
        print(f"  Total apostas: {total_apostas}")
        print(f"  Total prêmios: R$ {total_premios:.2f}")

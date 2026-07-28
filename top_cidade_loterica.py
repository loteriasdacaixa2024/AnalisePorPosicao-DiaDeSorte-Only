
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte
from sqlalchemy import func, desc

app = create_app()
with app.app_context():
    # Step 1: Find the top cidade by total_premios
    top_cidade_stats = db.session.query(
        LocaisSorte.cidade,
        func.count(LocaisSorte.id).label('total_apostas'),
        func.sum(LocaisSorte.valor_premio).label('total_premios')
    ).filter_by(modalidade="Dia de Sorte").group_by(LocaisSorte.cidade).order_by(desc('total_premios')).first()
    
    if top_cidade_stats:
        top_cidade, total_apostas_cidade, total_premios_cidade = top_cidade_stats
        print(f"Top cidade por total de prêmios:")
        print(f"  Cidade: {top_cidade}")
        print(f"  Total apostas: {total_apostas_cidade}")
        print(f"  Total prêmios: R$ {total_premios_cidade:.2f}\n")
        
        # Step 2: Find top lotérica in that cidade
        top_loterica_stats = db.session.query(
            LocaisSorte.unidade_loterica,
            func.count(LocaisSorte.id).label('total_apostas'),
            func.sum(LocaisSorte.valor_premio).label('total_premios')
        ).filter_by(
            modalidade="Dia de Sorte",
            cidade=top_cidade
        ).group_by(LocaisSorte.unidade_loterica).order_by(desc('total_premios')).first()
        
        if top_loterica_stats:
            top_loterica, total_apostas_loterica, total_premios_loterica = top_loterica_stats
            print(f"Top lotérica na cidade {top_cidade}:")
            print(f"  Lotérica: {top_loterica}")
            print(f"  Total apostas: {total_apostas_loterica}")
            print(f"  Total prêmios: R$ {total_premios_loterica:.2f}")

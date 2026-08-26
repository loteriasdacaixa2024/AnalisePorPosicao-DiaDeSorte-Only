
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte
from sqlalchemy import func

app = create_app()
with app.app_context():
    # Get stats grouped by tipo_aposta
    stats = db.session.query(
        LocaisSorte.tipo_aposta,
        func.count(LocaisSorte.id).label('total_apostas'),
        func.sum(LocaisSorte.valor_premio).label('total_premios'),
        func.avg(LocaisSorte.valor_premio).label('premio_medio')
    ).filter_by(modalidade="Dia de Sorte").group_by(LocaisSorte.tipo_aposta).all()
    
    print("Stats grouped by tipo_aposta:")
    for tipo, total, soma, media in stats:
        print(f"  - {repr(tipo)}:")
        print(f"    Total apostas: {total}")
        print(f"    Total prêmios: R$ {soma:.2f}")
        print(f"    Média prêmio: R$ {media:.2f}")

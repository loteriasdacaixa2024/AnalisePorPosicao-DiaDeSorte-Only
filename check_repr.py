
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte

app = create_app()
with app.app_context():
    # Get first 10 Bolão records
    records = db.session.query(
        LocaisSorte.id,
        LocaisSorte.tipo_aposta
    ).filter(
        LocaisSorte.modalidade == "Dia de Sorte",
        LocaisSorte.tipo_aposta != "Simples"
    ).limit(10).all()
    
    print("First 10 non-Simples records:")
    for rec_id, tipo in records:
        print(f"  ID {rec_id}: repr(tipo) = {repr(tipo)}, hex = {''.join(f'{ord(c):04X}' for c in tipo)}")

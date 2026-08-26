
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte

app = create_app()
with app.app_context():
    # Get all distinct tipo_aposta and also show their hex representation
    tipos = db.session.query(LocaisSorte.tipo_aposta).filter_by(modalidade="Dia de Sorte").distinct().all()
    print("Distinct tipo_aposta values:")
    for t in tipos:
        val = t[0]
        if val:
            hex_repr = ' '.join(f'{ord(c):04X}' for c in val)
        else:
            hex_repr = 'None'
        print(f"  - '{val}' (length: {len(val) if val else 0}, repr: {repr(val)}, hex: {hex_repr})")
        
    # Also check the counts
    print("\nCounts per tipo_aposta:")
    counts = db.session.query(
        LocaisSorte.tipo_aposta,
        db.func.count(LocaisSorte.id)
    ).filter_by(modalidade="Dia de Sorte").group_by(LocaisSorte.tipo_aposta).all()
    for t, cnt in counts:
        print(f"  - '{t}': {cnt}")

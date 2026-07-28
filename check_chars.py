
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte
import sys
import io

# Force UTF-8 for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = create_app()
with app.app_context():
    # Get all tipo_aposta with id
    records = db.session.query(
        LocaisSorte.id,
        LocaisSorte.tipo_aposta
    ).filter(
        LocaisSorte.modalidade == "Dia de Sorte",
        LocaisSorte.tipo_aposta.isnot(None)
    ).limit(10).all()
    
    print("First 10 records:")
    for rec_id, tipo in records:
        print(f"  ID: {rec_id}, tipo_aposta:")
        for i, c in enumerate(tipo):
            print(f"    char {i}: '{c}', ord: {ord(c):04X}")
            
    # Get counts grouped by tipo_aposta's stripped value
    print("\nCounts by stripped tipo_aposta:")
    all_records = db.session.query(LocaisSorte).filter_by(modalidade="Dia de Sorte").all()
    count_map = {}
    for rec in all_records:
        t = rec.tipo_aposta
        key = t.strip() if t else 'None'
        if key not in count_map:
            count_map[key] = 0
        count_map[key] += 1
        
    for k, cnt in count_map.items():
        hex_str = ' '.join(f'{ord(c):04X}' for c in k)
        print(f"  '{k}': {cnt} (hex: {hex_str})")


from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte

app = create_app()
with app.app_context():
    # Get ALL records
    all_records = LocaisSorte.query.filter(
        LocaisSorte.modalidade == "Dia de Sorte"
    ).all()
    
    print(f"Total records: {len(all_records)}")
    
    fixed_count = 0
    for rec in all_records:
        original = rec.tipo_aposta
        if original:
            # Check if it's any type of "Bolão" (starts with Bol, ends with o)
            original_upper = original.upper()
            if original_upper.startswith('BOL') and original_upper.endswith('O'):
                if original != 'Bolão':
                    rec.tipo_aposta = 'Bolão'
                    fixed_count += 1
                    # Print minimal info to avoid encoding issues
                    print(f"Fixed record {rec.id}")
    
    db.session.commit()
    print(f"\nFixed {fixed_count} records total!")

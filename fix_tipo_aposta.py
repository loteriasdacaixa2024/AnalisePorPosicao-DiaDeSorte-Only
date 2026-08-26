
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte

app = create_app()
with app.app_context():
    # Find all records that are not "Simples" or "Bolão"
    all_records = LocaisSorte.query.filter(
        LocaisSorte.modalidade == "Dia de Sorte"
    ).all()
    
    print(f"Found {len(all_records)} total records")
    
    fixed_count = 0
    for rec in all_records:
        original = rec.tipo_aposta
        if original:
            original_stripped = original.strip()
            # Check if it's any variation of Bolão (case-insensitive, with whitespace, etc.)
            if original_stripped.lower().startswith('bol') and original_stripped.lower().endswith('o'):
                rec.tipo_aposta = 'Bolão'
                if original != 'Bolão':
                    fixed_count += 1
    
    db.session.commit()
    print(f"Fixed {fixed_count} records!")

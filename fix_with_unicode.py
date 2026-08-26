
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte

app = create_app()
with app.app_context():
    # Use Unicode escape sequence for ã to avoid encoding issues
    correct_tipo = "Bol\u00E3o"  # This is "Bolão"
    
    # Update ALL records that are NOT "Simples" to "Bolão"
    updated = db.session.query(LocaisSorte).filter(
        LocaisSorte.modalidade == "Dia de Sorte",
        LocaisSorte.tipo_aposta != "Simples"
    ).update(
        {LocaisSorte.tipo_aposta: correct_tipo},
        synchronize_session=False
    )
    
    db.session.commit()
    print(f"Updated {updated} records to {repr(correct_tipo)}!")

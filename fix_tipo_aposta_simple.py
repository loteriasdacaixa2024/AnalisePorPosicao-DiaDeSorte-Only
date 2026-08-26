
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte

app = create_app()
with app.app_context():
    # Update ALL records that are NOT "Simples" to "Bolão"
    updated = db.session.query(LocaisSorte).filter(
        LocaisSorte.modalidade == "Dia de Sorte",
        LocaisSorte.tipo_aposta != "Simples"
    ).update(
        {LocaisSorte.tipo_aposta: "Bolão"},
        synchronize_session=False
    )
    
    db.session.commit()
    print(f"Updated {updated} records to 'Bolão'!")

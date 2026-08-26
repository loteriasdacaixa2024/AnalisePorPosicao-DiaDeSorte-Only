
from app import create_app
from models.shared import db
from models.locais_sorte import LocaisSorte

app = create_app()
with app.app_context():
    # Get sample records where unidade_loterica contains "CANAIS ELETRONICOS"
    samples = db.session.query(LocaisSorte).filter(
        LocaisSorte.modalidade == "Dia de Sorte",
        LocaisSorte.unidade_loterica.like("%CANAIS ELETRONICOS%")
    ).limit(5).all()
    
    print("Amostra de registros 'LOTERIAS EM CANAIS ELETRONICOS':")
    for rec in samples:
        print(f"\n  ID: {rec.id}")
        print(f"  Concurso: {rec.concurso}")
        print(f"  Cidade: {rec.cidade}")
        print(f"  Unidade lotérica: {rec.unidade_loterica}")
        print(f"  Razão social: {rec.razao_social}")
        print(f"  Tipo aposta: {rec.tipo_aposta}")
        print(f"  Valor prêmio: R$ {rec.valor_premio:.2f}")

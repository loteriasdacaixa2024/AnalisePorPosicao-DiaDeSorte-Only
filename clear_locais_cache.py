
from app import create_app
from services.locais_sorte_service import LocaisSorteService

app = create_app()
with app.app_context():
    # Clear the cache
    LocaisSorteService._cache_comparativo = {'dados': None, 'ts': 0}
    print("Cache cleared successfully!")

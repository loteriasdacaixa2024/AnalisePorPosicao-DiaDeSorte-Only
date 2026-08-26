
from app import create_app
from services.locais_sorte_service import LocaisSorteService

app = create_app()
with app.app_context():
    # Clear cache completely
    LocaisSorteService._cache_comparativo = {'dados': None, 'ts': 0}
    print("Cache cleared!")
    
    # Let's call obter_comparativo_estratificacao to see what it returns
    result = LocaisSorteService.obter_comparativo_estratificacao(usar_cache=False)
    print("\nComparativo result:")
    for item in result['comparador_aposta']:
        print(f"  - {repr(item)}")

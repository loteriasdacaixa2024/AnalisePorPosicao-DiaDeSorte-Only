
from services.locais_sorte_service import LocaisSorteService

# Clear the cache
LocaisSorteService._cache_comparativo = {'dados': None, 'ts': 0}
print("Cache cleared!")

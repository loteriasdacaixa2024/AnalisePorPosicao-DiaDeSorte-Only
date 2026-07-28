from app import app
from services.analise_soma_dezenas_service import AnaliseSomaDezenasService
from services.analise_digitos_unicos_service import AnaliseDigitosUnicosService

with app.app_context():
    soma_data = AnaliseSomaDezenasService.analisar_somas()
    digito_data = AnaliseDigitosUnicosService.analisar_digitos_unicos()
    
    print(f"SOMA - Min: {soma_data.get('soma_minima')}, Max: {soma_data.get('soma_maxima')}")
    print(f"DIGITOS - Min: {digito_data.get('quantidade_minima')}, Max: {digito_data.get('quantidade_maxima')}")

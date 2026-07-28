import os
import sys
from collections import defaultdict
from itertools import combinations

# Add the project root to sys.path so we can import services
sys.path.append(r'd:\Loterias\AnalisePorPosicao-DiaDeSorte-Only')

from services.analise_digitos_unicos_service import AnaliseDigitosUnicosService
from flask import Flask
from models.sorteio import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///d:/Loterias/AnalisePorPosicao-DiaDeSorte-Only/analise_por_posicao.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("Analisando histórico para obter os Top 10 padrões...")
    resultado = AnaliseDigitosUnicosService.analisar_digitos_unicos()
    top10 = resultado['top_relacoes_soma'][:10]
    relacoes_alvo = [t['relacao'] for t in top10]
    
    print(f"Top 10 relações: {relacoes_alvo}")
    print("Gerando as matrizes (pode demorar alguns segundos)...")
    
    matriz = AnaliseDigitosUnicosService.gerar_matriz_elite(relacoes_alvo)
    
    output_dir = r"d:\Loterias\AnalisePorPosicao-DiaDeSorte-Only\Exportacoes_SimuladorElite"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for i, rel in enumerate(relacoes_alvo):
        # Format the relation string to avoid invalid filename characters like '/'
        safe_rel = rel.replace('/', '_')
        filename = f"Top_{i+1}_Padrao_{safe_rel}.txt"
        filepath = os.path.join(output_dir, filename)
        
        combinacoes = matriz.get(rel, [])
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"PADRÃO: {rel} (Dígitos / Soma)\n")
            f.write(f"TOTAL DE COMBINAÇÕES INÉDITAS ENCONTRADAS: {len(combinacoes)}\n")
            f.write("-" * 50 + "\n")
            for combo in combinacoes:
                combo_str = " ".join([f"{n:02d}" for n in sorted(combo)])
                f.write(combo_str + "\n")
                
        print(f"[{i+1}/10] Arquivo salvo: {filename} com {len(combinacoes)} apostas.")
        
    print(f"\nTodos os 10 arquivos foram gerados com sucesso na pasta:\n{output_dir}")

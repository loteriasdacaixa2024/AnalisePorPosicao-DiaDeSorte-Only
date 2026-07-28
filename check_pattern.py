import sqlite3
import json

db = sqlite3.connect('analise_por_posicao.db')
concursos = db.execute('SELECT concurso, posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7 FROM sorteios ORDER BY concurso ASC').fetchall()

encontrados_3_pares = []
encontrados_3_pares_exato_u = []

for row in concursos:
    conc = row[0]
    nums = sorted(list(row[1:]))
    
    # Check for consecutive pairs
    pares = []
    for i in range(len(nums) - 1):
        if nums[i+1] == nums[i] + 1:
            pares.append((nums[i], nums[i+1]))
            
    # Pattern: "07 08 17 18 27 28" (3 pairs with the exact same units)
    # Check if there are at least 3 consecutive pairs
    if len(pares) >= 3:
        encontrados_3_pares.append((conc, nums, pares))
        
        # Check if the 3 pairs share the exact same units
        unidades = {}
        for p in pares:
            u1, u2 = p[0] % 10, p[1] % 10
            key = f"{u1}-{u2}"
            if key not in unidades:
                unidades[key] = []
            unidades[key].append(p)
            
        for k, v in unidades.items():
            if len(v) >= 3:
                encontrados_3_pares_exato_u.append((conc, nums, v))

print(f"Total de concursos com pelo menos 3 pares consecutivos: {len(encontrados_3_pares)}")
print(f"Total de concursos com 3 pares consecutivos com as MESMAS terminações (Padrão Exato): {len(encontrados_3_pares_exato_u)}")

if len(encontrados_3_pares_exato_u) > 0:
    print("\nConcursos com o PADRÃO EXATO (3 colunas iguais):")
    for e in encontrados_3_pares_exato_u:
        print(f"Concurso {e[0]}: {e[1]} -> Pares: {e[2]}")
else:
    print("\nNenhum concurso teve o padrão EXATO de 3 pares nas mesmas unidades.")
    print("Últimos com apenas 3 pares soltos:")
    for e in encontrados_3_pares[-5:]:
        print(f"Concurso {e[0]}: {e[1]} -> Pares: {e[2]}")

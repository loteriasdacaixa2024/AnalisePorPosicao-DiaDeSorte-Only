import sqlite3

db = sqlite3.connect('analise_por_posicao.db')
concursos = db.execute('SELECT concurso, posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7 FROM sorteios ORDER BY concurso ASC').fetchall()

encontrados_2_pares_exato_u = []

for row in concursos:
    conc = row[0]
    nums = sorted(list(row[1:]))
    
    pares = []
    for i in range(len(nums) - 1):
        if nums[i+1] == nums[i] + 1:
            pares.append((nums[i], nums[i+1]))
            
    if len(pares) >= 2:
        unidades = {}
        for p in pares:
            u1, u2 = p[0] % 10, p[1] % 10
            key = f"{u1}-{u2}"
            if key not in unidades:
                unidades[key] = []
            unidades[key].append(p)
            
        for k, v in unidades.items():
            if len(v) >= 2:
                encontrados_2_pares_exato_u.append((conc, nums, v))

print(f"Total de concursos com 2 pares consecutivos com as MESMAS terminações: {len(encontrados_2_pares_exato_u)}")
for e in encontrados_2_pares_exato_u[-5:]:
    print(f"Concurso {e[0]}: {e[1]} -> Pares Identicos: {e[2]}")

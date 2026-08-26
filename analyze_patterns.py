import sqlite3
from collections import Counter

conn = sqlite3.connect('analise_por_posicao.db')
cursor = conn.cursor()

def count_digits(nums):
    d = set()
    for n in nums:
        d.add(n // 10)
        d.add(n % 10)
    return len(d)

def get_max_seq(nums):
    nums = sorted(nums)
    max_s = 1
    curr = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1] + 1:
            curr += 1
            max_s = max(max_s, curr)
        else:
            curr = 1
    return max_s

cursor.execute("SELECT posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7 FROM sorteios")
rows = cursor.fetchall()

somas = []
digitos = []
sequencias = []

for row in rows:
    if all(row):
        somas.append(sum(row))
        digitos.append(count_digits(row))
        sequencias.append(get_max_seq(row))

if somas:
    print(f"--- SOMA ---")
    print(f"Média: {sum(somas)/len(somas):.2f}")
    print(f"Padrão mais frequente: {Counter(somas).most_common(1)[0][0]}")
    
    print(f"\n--- DÍGITOS ---")
    print(f"Média: {sum(digitos)/len(digitos):.2f}")
    print(f"Padrão mais frequente (MODA): {Counter(digitos).most_common(1)[0][0]} dígitos")
    
    print(f"\n--- SEQUÊNCIAS ---")
    print(f"Média: {sum(sequencias)/len(sequencias):.2f}")
    print(f"Padrão mais frequente (MODA): {Counter(sequencias).most_common(1)[0][0]} números consecutivos")
    
    # Check frequency of seq=2
    seq_counts = Counter(sequencias)
    print(f"Frequência de Sequência=2: {seq_counts[2]} ({seq_counts[2]/len(sequencias)*100:.2f}%)")
    print(f"Frequência de SEM Sequência (1): {seq_counts[1]} ({seq_counts[1]/len(sequencias)*100:.2f}%)")

conn.close()

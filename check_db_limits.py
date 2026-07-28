import sqlite3

conn = sqlite3.connect('analise_por_posicao.db')
cursor = conn.cursor()

# Get sum limits
cursor.execute("SELECT MIN(posicao_1 + posicao_2 + posicao_3 + posicao_4 + posicao_5 + posicao_6 + posicao_7), MAX(posicao_1 + posicao_2 + posicao_3 + posicao_4 + posicao_5 + posicao_6 + posicao_7) FROM sorteios")
min_soma, max_soma = cursor.fetchone()

print(f"Database Sum Limits: {min_soma} to {max_soma}")

# Get digits limits - this is complex in SQL, but let's try to get a sample
cursor.execute("SELECT posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7 FROM sorteios LIMIT 10")
rows = cursor.fetchall()

def count_digits(nums):
    d = set()
    for n in nums:
        d.add(n // 10)
        d.add(n % 10)
    return len(d)

digitos_counts = []
cursor.execute("SELECT posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7 FROM sorteios")
for row in cursor.fetchall():
    if all(row):
        digitos_counts.append(count_digits(row))

if digitos_counts:
    print(f"Database Digits Limits: {min(digitos_counts)} to {max(digitos_counts)}")

conn.close()

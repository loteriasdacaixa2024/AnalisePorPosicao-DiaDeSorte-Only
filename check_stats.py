import sqlite3

def get_stats():
    import os
    # Obter o caminho relativo dinamicamente para suportar execução de outras letras de disco ou Google Drive
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analise_por_posicao.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT concurso, posicao_1, posicao_2, posicao_3, posicao_4, posicao_5, posicao_6, posicao_7 FROM sorteios ORDER BY concurso ASC')
    draws = cursor.fetchall()
    
    if not draws:
        print("No draws found")
        return
    
    last_concurso = draws[-1][0]
    
    delays = {i: 0 for i in range(1, 32)}
    last_seen = {i: 0 for i in range(1, 32)}
    
    for draw in draws:
        concurso = draw[0]
        nums = draw[1:8]
        for num in nums:
            if num is not None and 1 <= num <= 31:
                last_seen[num] = concurso
                
    for i in range(1, 32):
        if last_seen[i] > 0:
            delays[i] = last_concurso - last_seen[i]
        else:
            delays[i] = len(draws)
            
    # Calculate frequency in last 30 draws
    last_30 = draws[-30:]
    freq_30 = {i: 0 for i in range(1, 32)}
    for draw in last_30:
        nums = draw[1:8]
        for num in nums:
            if num is not None and 1 <= num <= 31:
                freq_30[num] += 1
                
    sorted_delay = sorted(delays.items(), key=lambda x: x[1], reverse=True)
    sorted_freq = sorted(freq_30.items(), key=lambda x: x[1], reverse=True)
    
    print("TOTAL DRAWS:", len(draws))
    print("LAST CONCURSO:", last_concurso)
    print("ATRASADAS (Top 10):", sorted_delay[:10])
    print("QUENTES_LAST_30 (Top 10):", sorted_freq[:10])
    
get_stats()

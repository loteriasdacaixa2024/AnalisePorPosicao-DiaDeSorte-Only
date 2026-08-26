import sqlite3
db = sqlite3.connect('analise_por_posicao.db')
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", tables)

try:
    cols = db.execute("PRAGMA table_info(resultados)").fetchall()
    print("Cols resultados:", cols)
except Exception as e:
    pass

try:
    cols = db.execute("PRAGMA table_info(concursos)").fetchall()
    print("Cols concursos:", cols)
except Exception as e:
    pass

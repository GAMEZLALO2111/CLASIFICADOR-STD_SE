from app.database.db import Base, engine
import sqlite3

# Crear tablas
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas/actualizadas")

# Listar tablas
conn = sqlite3.connect('clasificador.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = [t[0] for t in cursor.fetchall()]
print(f"\nTablas en BD: {len(tablas)}")
for tabla in tablas:
    print(f"  - {tabla}")
conn.close()

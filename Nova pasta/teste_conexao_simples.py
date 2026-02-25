from sqlalchemy import create_engine, text
import psycopg2

# Conexão direta
try:
    conn = psycopg2.connect(
        host="localhost",
        database="fitlog_db",
        user="postgres",
        password="D2806"
    )
    print("✅ Conexão estabelecida!")
    
    # Testar query simples
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("✅ Query simples executada")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
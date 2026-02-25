# diagnostic.py
import os
from dotenv import load_dotenv

print("1. Carregando .env...")
load_dotenv()

db_url = os.getenv('DATABASE_URL')
print(f"2. DATABASE_URL lida: '{db_url}'")

print(f"3. Tipo da variável: {type(db_url)}")
print(f"4. Bytes da string: {db_url.encode('utf-8') if db_url else 'None'}")

if db_url:
    print("5. Tentando conectar...")
    import psycopg2
    try:
        conn = psycopg2.connect(db_url)
        print("✅ Sucesso!")
        conn.close()
    except Exception as e:
        print(f"❌ Erro: {e}")
else:
    print("❌ DATABASE_URL não encontrada no .env")
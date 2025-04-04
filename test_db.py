import psycopg2

try:
    conn = psycopg2.connect(
        dbname="loja",
        user="postgres",
        password="FSA171612",
        host="localhost",
        port="5432"
    )
    print("Conexão bem sucedida!")
    conn.close()
except Exception as e:
    print(f"Erro na conexão: {e}")

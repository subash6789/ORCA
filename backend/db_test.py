import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="orca_db",
        user="postgres",
        password=input("Enter PostgreSQL password: ")
    )

    print("ORCA PostgreSQL connection: SUCCESS")

    conn.close()

except Exception as e:
    print("Connection failed:")
    print(e)
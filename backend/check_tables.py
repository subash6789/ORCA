import getpass
import psycopg2

password = getpass.getpass("Enter PostgreSQL password: ")

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="orca_db",
        user="postgres",
        password=password
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    print("\nORCA database tables:")
    for table in cursor.fetchall():
        print("-", table[0])

    cursor.close()
    conn.close()

except Exception as e:
    print("\nDatabase check failed:")
    print(e)

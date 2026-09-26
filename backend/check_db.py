from db_connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT region, COUNT(*)
FROM ocean_observation
GROUP BY region
ORDER BY region;
""")

print("RECORD COUNT BY REGION:")

for row in cursor.fetchall():
    print("-", row[0], "|", row[1], "records")

cursor.close()
conn.close()
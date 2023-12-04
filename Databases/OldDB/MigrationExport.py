import sqlite3

db_path = 'database.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table in tables:

    table_name = table[0]

    with open(f"Tables/{table_name}.txt", "a+") as file:

        print(f"Table: {table_name}")
        print("-" * 40)

        # Получение и вывод всех данных из таблицы
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            file.write(str([i for i in row])+"\n")

        print("\n")

# Закрытие соединения с базой данных
conn.close()
# tests/test_db_smoke.py
def test_db_connection_works(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES LIMIT 1")
    row = cursor.fetchone()
    assert row is not None, "Нет доступа к INFORMATION_SCHEMA"
    print("Пример таблицы из INFORMATION_SCHEMA:", row)

    # Попробуй перечислить все таблицы
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'PUBLIC'")
    tables = [r[0] for r in cursor.fetchall()]
    print("Таблицы в схеме PUBLIC:", tables)
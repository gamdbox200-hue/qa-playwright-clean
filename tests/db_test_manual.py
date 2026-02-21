# db_test_manual.py — запусти как python db_test_manual.py
import os
import jaydebeapi

# Настройки (скопируй из conftest.py)
JAR_PATH = r"C:\Users\gamdb\drivers\hsqldb-2.7.3.jar"  # ← свой реальный путь!
DRIVER   = "org.hsqldb.jdbc.JDBCDriver"
URL      = "jdbc:hsqldb:hsql://localhost:9001/parabank"
USER     = "sa"
PASS     = ""

print("Пытаюсь подключиться...")

try:
    conn = jaydebeapi.connect(
        DRIVER,
        URL,
        [USER, PASS],
        jars=JAR_PATH
    )
    print("Подключение УСПЕШНО!")

    cursor = conn.cursor()

    # Самый безопасный запрос — к системной схеме
    cursor.execute("""
    SELECT TABLE_SCHEMA, TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA, TABLE_NAME""")
    tables = cursor.fetchall()
    print("Все таблицы в БД:")
    for schema, name in tables:
        print (f"  {schema}.{name}")

    # Если CUSTOMER есть — попробуем посчитать
    try:
        cursor.execute("SELECT COUNT(*) FROM CUSTOMER")
        count = cursor.fetchone()[0]
        print(f"В таблице CUSTOMER {count} записей")
    except Exception as sub_e:
        print("CUSTOMER не удалось запросить:", sub_e)

    cursor.close()
    conn.close()
    print("Соединение закрыто")

except Exception as e:
    print("Ошибка подключения:", e)
    print("\nЧто проверить:")
    print("1. Docker запущен? → docker ps")
    print("2. Порт 9001 открыт? → netstat -ano | findstr 9001")
    print("3. JAR существует? →", os.path.exists(JAR_PATH))
    print("4. JAVA_HOME установлен? → echo %JAVA_HOME%")

# tests/conftest.py
import os
import pytest
from dotenv import load_dotenv
import requests
from xml.etree import ElementTree as ET
import jaydebeapi

load_dotenv()

# ======================== НАСТРОЙКИ ========================

BASE_URL = "http://localhost:8080/parabank"

# Настройки HSQLDB (ParaBank в Docker)
HSQLDB_JAR_DIR  = "drivers"                     # папка в корне проекта
HSQLDB_JAR_NAME = "hsqldb-2.7.3.jar"
HSQLDB_JAR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # tests/ → корень проекта
    HSQLDB_JAR_DIR,
    HSQLDB_JAR_NAME
)

HSQLDB_DRIVER   = "org.hsqldb.jdbc.JDBCDriver"  # актуальное имя
HSQLDB_HOST     = "localhost"
HSQLDB_PORT     = 9001                          # должен быть проброшен в docker run -p 9001:9001
HSQLDB_DB_NAME  = "parabank"
HSQLDB_URL      = f"jdbc:hsqldb:hsql://{HSQLDB_HOST}:{HSQLDB_PORT}/{HSQLDB_DB_NAME}"
HSQLDB_USER     = "sa"
HSQLDB_PASS     = ""

# ======================== ФИКСТУРЫ ========================

@pytest.fixture(scope="session")
def base_url():
    """Базовый URL приложения ParaBank"""
    return BASE_URL


@pytest.fixture(scope="session")
def auth_session(base_url):
    """
    Авторизованная сессия requests после логина john/demo.
    Сохраняет customer_id в pytest.customer_id
    """
    session = requests.Session()
    login_url = f"{base_url}/services/bank/login/john/demo"

    response = session.get(login_url)

    if response.status_code != 200:
        pytest.fail(
            f"Логин не удался: {response.status_code} — {response.text[:300]}"
        )

    try:
        root = ET.fromstring(response.text)
        customer_id_elem = root.find(".//id")

        if customer_id_elem is None or not customer_id_elem.text:
            pytest.fail(
                f"Не нашли <id> в XML-ответе логина:\n{response.text[:600]}"
            )

        if not customer_id_elem.text.isdigit():
            pytest.fail(f"customer_id не является числом: {customer_id_elem.text}")

        pytest.customer_id = customer_id_elem.text

    except ET.ParseError as e:
        pytest.fail(f"Ответ логина не является валидным XML: {e}\nТекст: {response.text[:300]}")

    yield session
    session.close()


@pytest.fixture(scope="session")
def db_conn():
    """
    Подключение к HSQLDB ParaBank через JayDeBeApi (синхронная версия).
    """
    if not os.path.isfile(HSQLDB_JAR_PATH):
        pytest.fail(
            f"HSQLDB драйвер не найден!\n"
            f"Ожидаемый путь: {HSQLDB_JAR_PATH}\n"
            f"Скачай: https://repo1.maven.org/maven2/org/hsqldb/hsqldb/2.7.3/hsqldb-2.7.3.jar\n"
            f"Положи в папку: ./drivers/\n"
            f"Затем перезапусти pytest"
        )

    conn = None
    try:
        conn = jaydebeapi.connect(
            HSQLDB_DRIVER,                  # 1. driver class (позиционный)
            HSQLDB_URL,                     # 2. jdbc url (позиционный)
            [HSQLDB_USER, HSQLDB_PASS],     # 3. [user, password] (позиционный)
            jars=HSQLDB_JAR_PATH            # 4. jars (keyword)
        )
        print(f"Успешно подключено к HSQLDB: {HSQLDB_URL}")
        yield conn

    except Exception as e:
        pytest.fail(
            f"Ошибка подключения к HSQLDB:\n{str(e)}\n\n"
            f"Возможные причины и как проверить:\n"
            f"  • Контейнер не запущен → docker ps\n"
            f"  • Порт 9001 не проброшен → docker run ... -p 9001:9001\n"
            f"  • JAR-файл не найден или путь неверный: {HSQLDB_JAR_PATH}\n"
            f"  • Порт 9001 занят → netstat -ano | findstr 9001\n"
            f"  • jaydebeapi / jpype1 не установлены → pip install jaydebeapi jpype1\n"
            f"Логи контейнера: docker logs parabank"
        )

    finally:
        if conn is not None:
            try:
                conn.close()
                print("Соединение с HSQLDB закрыто")
            except:
                pass

# ======================== ПРИМЕР ИСПОЛЬЗОВАНИЯ ========================
"""
def test_db_smoke(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT 1")
    assert cursor.fetchone() == (1,), "База не отвечает"
    print("База отвечает")
"""
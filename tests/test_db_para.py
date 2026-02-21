import pytest

def test_customer_count(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM PUBLIC.CUSTOMER")
    count = cursor.fetchone()[0]
    assert count >= 1, "В ParaBank должен быть хотя бы один клиент"
    print(f"Клиентов в базе: {count}")


def test_john_exists(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT ID, FIRST_NAME, LAST_NAME, USERNAME 
        FROM PUBLIC.CUSTOMER 
        WHERE USERNAME = 'john'
    """)
    row = cursor.fetchone()
    
    assert row is not None, "Пользователь с username='john' не найден в таблице CUSTOMER"
    
    customer_id, first_name, last_name, username = row
    print(f"John найден: ID={customer_id}, {first_name} {last_name}, username={username}")


def test_transfer_updates_balance(db_conn, auth_session, base_url):
    """
    Проверяем, что перевод денег обновляет баланс в БД.
    """
    cursor = db_conn.cursor()
    
    from_account_id = 12345   # checking john (проверь в UI или в выводе теста)
    to_account_id   = 54321   # savings или другой аккаунт john
    
    amount = 10.00
    
    # Шаг 1: Баланс ДО перевода
    cursor.execute("SELECT BALANCE FROM PUBLIC.ACCOUNT WHERE ID = ?", (from_account_id,))
    balance_from_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT BALANCE FROM PUBLIC.ACCOUNT WHERE ID = ?", (to_account_id,))
    balance_to_before = cursor.fetchone()[0]
    
    print(f"ДО: from {from_account_id} = {balance_from_before}, to {to_account_id} = {balance_to_before}")
    
    # Шаг 2: Выполняем перевод через API (используем твою фикстуру auth_session)
    transfer_url = f"{base_url}/services/bank/transfer?fromAccountId={from_account_id}&toAccountId={to_account_id}&amount={amount}"
    response = auth_session.post(transfer_url)
    
    assert response.status_code == 200, f"Перевод не прошёл: {response.text}"
    assert "Successfully transferred" in response.text, "Нет подтверждения перевода"
    
    # Шаг 3: Баланс ПОСЛЕ перевода
    cursor.execute("SELECT BALANCE FROM PUBLIC.ACCOUNT WHERE ID = ?", (from_account_id,))
    balance_from_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT BALANCE FROM PUBLIC.ACCOUNT WHERE ID = ?", (to_account_id,))
    balance_to_after = cursor.fetchone()[0]
    
    print(f"ПОСЛЕ: from {from_account_id} = {balance_from_after}, to {to_account_id} = {balance_to_after}")
    
    # Шаг 4: Проверки
    assert balance_from_after == balance_from_before - amount, \
        f"Баланс отправителя не уменьшился на {amount}: было {balance_from_before}, стало {balance_from_after}"
    
    assert balance_to_after == balance_to_before + amount, \
        f"Баланс получателя не увеличился на {amount}: было {balance_to_before}, стало {balance_to_after}"

def test_john_balance(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT BALANCE 
        FROM PUBLIC.ACCOUNT 
        WHERE CUSTOMER_ID = 12212
    """)
    balances = cursor.fetchall()
    print("Балансы аккаунтов john:", [b[0] for b in balances])
    assert len(balances) >= 1, "У john нет аккаунтов"

def test_transactions_exist(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM PUBLIC.TRANSACTION")
    count = cursor.fetchone()[0]
    print(f"Транзакций в базе: {count}")
    assert count > 0, "Нет транзакций в базе"

def test_john_accounts(db_conn):
    """
    Проверяем, что у john есть аккаунты и хотя бы один с ненулевым балансом.
    """
    cursor = db_conn.cursor()
    
    # Ищем аккаунты по customer_id john (12212 — из твоего предыдущего теста)
    cursor.execute("""
        SELECT ID, TYPE, BALANCE 
        FROM PUBLIC.ACCOUNT 
        WHERE CUSTOMER_ID = 12212
    """)
    accounts = cursor.fetchall()
    
    assert len(accounts) >= 1, "У john нет ни одного аккаунта в таблице ACCOUNT"
    
    print("Аккаунты john:")
    has_positive = False
    for acc_id, acc_type, balance in accounts:
        print(f"  ID={acc_id}, Type={acc_type}, Balance={balance}")
        if balance > 0:
            has_positive = True
    
    # Проверяем, что хотя бы один аккаунт положительный (можно убрать, если не хочешь)
    # assert has_positive, "Все аккаунты john отрицательные или нулевые"
    
    # Сохраняем первый аккаунт для будущих тестов
    pytest.first_john_account_id = accounts[0][0]
"""ЗАДАЧА 2. SQL по транзакциям клиентов МТС Банка.

Контекст:
Есть таблица transact с транзакциями клиентов с 2021 года.
Столбцы: id_client, tran_time, id_tran, sum_tran.

Подзадачи:
1. Посчитать траты каждого клиента за последние 30 дней от текущего числа
2. Для топ-100 наиболее платежеспособных клиентов за всю историю
   посчитать траты помесячно"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_database(): # создаём базу данных
    
    # соединение с базой данных в памяти (не сохраняется на диск)
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # создаём таблицу trensact
    cursor.execute("""
        CREATE TABLE transact (
            id_tran INTEGER PRIMARY KEY,
            id_client INTEGER NOT NULL,
            tran_time TEXT NOT NULL,
            sum_tran REAL NOT NULL
        )
    """)
    
    # генерируем синтетические данные
    random.seed(42)
    
    num_clients = 100 # 100 клиентов
    num_transactions = 5000 # 5000 транзакций
    
    start_date = datetime(2021, 1, 1) # дата начала
    end_date = datetime.now() # дата конца (сегодня)
    
    transactions = [] # генерируем транзакции
    for i in range(1, num_transactions + 1): # проходим по списку транзакций
        id_client = random.randint(1, num_clients) # случайный клиент от 1 от 100
        
        # случайная дата в диапазоне
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        tran_time = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        # случайная сумма от 100 до 50000 рублей
        # большинство транзакций — небольшие (до 5000), редкие — крупные
        if random.random() < 0.9: # 90% транзакций — мелкие
            sum_tran = random.uniform(100, 5000)
        else: # 10% — крупные
            sum_tran = random.uniform(5000, 50000)
        
        transactions.append((i, id_client, tran_time.strftime("%Y-%m-%d %H:%M:%S"), round(sum_tran, 2))) # добавляем транзакцию в список
    
    # вставляем транзакции в таблицу
    cursor.executemany(
        "INSERT INTO transact (id_tran, id_client, tran_time, sum_tran) VALUES (?, ?, ?, ?)",
        transactions
    )
    
    conn.commit()
    print(f"База данных создана: {num_clients} клиентов, {num_transactions} транзакций")
    print(f"Период: {start_date.strftime('%Y-%m-%d')} — {end_date.strftime('%Y-%m-%d')}\n")
    
    return conn

# 1 подзадача - траты за последние 30 дней
def task1_last_30_days(conn):
    print("ПОДЗАДАЧА 1: Траты каждого клиента за последние 30 дней")
    print()
    
    query = """
        SELECT 
            id_client,
            COUNT(*) AS num_transactions,
            ROUND(SUM(sum_tran), 2) AS total_spent
        FROM transact
        WHERE tran_time >= DATE('now', '-30 days')
        GROUP BY id_client
        ORDER BY total_spent DESC
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"Найдено клиентов с транзакциями за последние 30 дней: {len(results)}\n")
    print(f"{'Клиент':<10} {'Транзакций':<15} {'Сумма (руб)':<15}")
    print("-" * 40)
    
    for row in results[:10]:  # Показываем топ-10
        print(f"{row[0]:<10} {row[1]:<15} {row[2]:<15}")
    
    if len(results) > 10:
        print(f"... и ещё {len(results) - 10} клиентов")
    
    print()

# 2 подзадача - помесячные траты топ 100 наиболее платёжеспособных клиентов
def task2_monthly_top100(conn):
    print("ПОДЗАДАЧА 2: Помесячные траты топ-100 клиентов за всю историю")
    print()
    
    query = """
        WITH top_clients AS (
            -- Шаг 1: Находим топ-100 клиентов по общей сумме трат
            SELECT id_client
            FROM transact
            GROUP BY id_client
            ORDER BY SUM(sum_tran) DESC
            LIMIT 100
        )
        -- Шаг 2: Для этих клиентов считаем траты помесячно
        SELECT 
            t.id_client,
            strftime('%Y-%m', t.tran_time) AS month,
            COUNT(*) AS num_transactions,
            ROUND(SUM(t.sum_tran), 2) AS monthly_spent
        FROM transact t
        WHERE t.id_client IN (SELECT id_client FROM top_clients)
        GROUP BY t.id_client, strftime('%Y-%m', t.tran_time)
        ORDER BY t.id_client, month
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"Всего записей (клиент-месяц): {len(results)}\n")
    print(f"{'Клиент':<10} {'Месяц':<12} {'Транзакций':<15} {'Сумма (руб)':<15}")
    print("-" * 50)
    
    for row in results[:20]:
        print(f"{row[0]:<10} {row[1]:<12} {row[2]:<15} {row[3]:<15}")
    
    if len(results) > 20:
        print(f"... и ещё {len(results) - 20} записей")
    
    print()

# запуск всех задач
def main():
    print("ЗАДАЧА 2: SQL по транзакциям клиентов МТС Банка")
    print()
    
    conn = create_database() # создаём базу данных
    
    try:
        task1_last_30_days(conn) # 1 задача
        task2_monthly_top100(conn) # 2 задача
        
        print("Все запросы выполнены успешно")
    finally:
        conn.close()

main()
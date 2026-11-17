"""ЗАДАЧА 3. Расчёт Retention (удержания) клиентов МТС Банка

Контекст:
Продукт просит посчитать retention на основе таблицы transact из Задачи 2

ШАГ 1: Вопросы продукту (что мы должны уточнить перед началом)
1. Что считается "когортой"? (Дата регистрации или дата первой транзакции?)
2. Что считается "удержанием"? (Любая транзакция, или транзакция > 0 руб, или конкретное действие?)
3. Какой период удержания нас интересует? (Day 1, Week 1, Month 1?)

ШАГ 2: Наши предположения (так как продукт не ответил, мы фиксируем допущения)
1. Когорта = месяц первой транзакции клиента (так как таблицы регистраций у нас нет)
2. Удержание = наличие хотя бы одной транзакции в целевом месяце
3. Период = помесячный (Month 0, Month 1, Month 2...), так как это стандарт для финтеха 
   и соответствует агрегации из Задачи 2

ШАГ 3: Действия (алгоритм)
1. Для каждого клиента находим месяц его первой транзакции (cohort_month)
2. Для каждого клиента находим все месяцы, когда он совершал транзакции (activity_month)
3. Соединяем эти данные и считаем количество уникальных клиентов для каждой пары 
   (cohort_month, activity_month)
4. В Python рассчитываем размер когорты и процент удержания для каждого периода"""

import sqlite3
import random
from datetime import datetime, timedelta


def create_database(): # создаём базу данных
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE transact (
            id_tran INTEGER PRIMARY KEY,
            id_client INTEGER NOT NULL,
            tran_time TEXT NOT NULL,
            sum_tran REAL NOT NULL
        )
    """)
    
    random.seed(42)
    num_clients = 100
    num_transactions = 5000
    start_date = datetime(2021, 1, 1)
    end_date = datetime.now()
    
    transactions = []
    for i in range(1, num_transactions + 1):
        id_client = random.randint(1, num_clients)
        days_range = (end_date - start_date).days
        random_days = random.randint(0, days_range)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        tran_time = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        if random.random() < 0.9:
            sum_tran = random.uniform(100, 5000)
        else:
            sum_tran = random.uniform(5000, 50000)
            
        transactions.append((i, id_client, tran_time.strftime("%Y-%m-%d %H:%M:%S"), round(sum_tran, 2)))
    
    cursor.executemany(
        "INSERT INTO transact (id_tran, id_client, tran_time, sum_tran) VALUES (?, ?, ?, ?)",
        transactions
    )
    conn.commit()
    return conn

# считаем retention
def calculate_retention(conn):
    print("ЗАДАЧА 3: Расчёт Retention (удержания) клиентов")
    print()
    print("[Допущения]: Когорта = месяц первой транзакции. Удержание = любая транзакция в месяце")
    print()

    query = """
        WITH user_cohorts AS (
            -- 1. Находим месяц первой транзакции для каждого клиента (это его когорта)
            SELECT 
                id_client,
                strftime('%Y-%m', MIN(tran_time)) AS cohort_month
            FROM transact
            GROUP BY id_client
        ),
        user_activity AS (
            -- 2. Находим все уникальные месяцы, когда клиент совершал транзакции
            SELECT 
                id_client,
                strftime('%Y-%m', tran_time) AS activity_month
            FROM transact
            GROUP BY id_client, strftime('%Y-%m', tran_time)
        ),
        retention_raw AS (
            -- 3. Соединяем когорты с активностью и считаем пользователей
            SELECT 
                c.cohort_month,
                a.activity_month,
                COUNT(DISTINCT a.id_client) AS retained_users
            FROM user_cohorts c
            JOIN user_activity a ON c.id_client = a.id_client
            GROUP BY c.cohort_month, a.activity_month
        )
        -- 4. Добавляем общий размер когорты для расчёта процентов
        SELECT 
            r.cohort_month,
            r.activity_month,
            r.retained_users,
            (SELECT COUNT(DISTINCT id_client) FROM user_cohorts c2 WHERE c2.cohort_month = r.cohort_month) AS cohort_size
        FROM retention_raw r
        ORDER BY r.cohort_month, r.activity_month
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    raw_data = cursor.fetchall()
    
    cohorts = {} # словарь для хранения данных
    
    for row in raw_data:
        cohort_month = row[0]
        activity_month = row[1]
        retained_users = row[2]
        cohort_size = row[3]
        
        if cohort_month not in cohorts:
            cohorts[cohort_month] = {'size': cohort_size}
            
        c_year, c_month = map(int, cohort_month.split('-'))
        a_year, a_month = map(int, activity_month.split('-'))
        period_index = (a_year - c_year) * 12 + (a_month - c_month)
        
        cohorts[cohort_month][period_index] = retained_users

    # выводим таблицу
    print(f"{'Когорта':<10} | {'Размер':<6} | {'M0':<5} | {'M1':<5} | {'M2':<5} | {'M3':<5} | ...")
    print("-" * 65)
    print()
    
    # сортируем когорты по времени
    for cohort_month in sorted(cohorts.keys())[:10]: # показываем первые 10 когорт для наглядности
        data = cohorts[cohort_month]
        size = data['size']
        
        # формируем строку с процентами удержания
        row_str = f"{cohort_month:<10} | {size:<6} | "
        for period in range(4): # показываем периоды M0, M1, M2, M3
            if period in data:
                pct = (data[period] / size) * 100
                row_str += f"{pct:>4.1f}% | "
            else:
                row_str += f"{'-':>5} | "
        
        print(row_str)
        
    print("(Показаны первые 10 когорт. M0 = месяц первой транзакции, M1 = следующий месяц и т.д.)")
    print()

def main():
    conn = create_database()
    try:
        calculate_retention(conn)
    finally:
        conn.close()

main()
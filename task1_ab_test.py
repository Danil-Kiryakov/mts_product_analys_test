"""Задача 1. A/B-тест баннера на странице оформления карты МТС Банка
Вариант A: 2574 клиента зашли, 350 нажали на баннер
Вариант B: 2855 клиентов зашли, 375 нажали на баннер

Вопрос: какой вариант баннера предложить продукту и почему?"""

import math
from scipy import stats

n_a = 2574  # клтенты группы а
clicks_a = 350  # клики группы а

n_b = 2855  # клиенты группы б
clicks_b = 375  # клики группы б

if n_a == 0 or n_b == 0:
    print("Ошибка: количество клиентов в одной из групп равно 0. Проверьте данные.")
    exit()
if clicks_a < 0 or clicks_b < 0:
    print("Ошибка: количество кликов не может быть отрицательным.")
    exit()

conversion_a = clicks_a / n_a # конверсия а
conversion_b = clicks_b / n_b # конверсия б

print("ЗАДАЧА 1: A/B-тест баннера МТС Банка")
print()
print(f"Вариант A: {clicks_a} / {n_a} = {conversion_a:.4f} ({conversion_a*100:.2f}%)")
print(f"Вариант B: {clicks_b} / {n_b} = {conversion_b:.4f} ({conversion_b*100:.2f}%)")
print(f"Разница: {(conversion_b - conversion_a)*100:.2f} п.п.")
print()

# z-тест, нулевая гипотеза(H0) - конверсии равны, альтернативная гипотеза(H1) - конверсии различаются
p_pooled = (clicks_a + clicks_b) / (n_a + n_b) # объединённая пропорция
se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_a + 1/n_b)) # стандартная ошибка (погрешность)
z_stat = (conversion_a - conversion_b) / se # z-статистика
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat))) # двусторонний p-value

print("СТАТИСТИЧЕСКАЯ ПРОВЕРКА")
print()
print(f"Z-статистика: {z_stat:.4f}")
print(f"P-value (двусторонний): {p_value:.4f}")
print(f"Уровень значимости α: 0.05")
print()

# доверительный интервал для разницы пропорций (95%)
diff = conversion_a - conversion_b
se_diff = math.sqrt(
    conversion_a * (1 - conversion_a) / n_a + 
    conversion_b * (1 - conversion_b) / n_b
)
ci_lower = diff - 1.96 * se_diff # нижняя граница интервала
ci_upper = diff + 1.96 * se_diff # верхняя граница интервала

print(f"95% доверительный интервал разницы: [{ci_lower:.4f}, {ci_upper:.4f}]")
print(f"В процентных пунктах: [{ci_lower*100:.2f}, {ci_upper*100:.2f}]")

print()
print("ВЫВОД")
print()

if p_value < 0.05:
    print(f"P-value ({p_value:.4f}) < 0.05 -> отвергаем H0")
    print("Разница статистически значима")
    if conversion_a > conversion_b:
        print("Рекомендация: выбрать ВАРИАНТ A")
        print()
    else:
        print("Рекомендация: выбрать ВАРИАНТ B")
        print()
else:
    print(f"P-value ({p_value:.4f}) ≥ 0.05 -> не отвергаем H0")
    print("Разница статистически не значима")
    print("Рекомендация: оба варианта равнозначны, можно оставить A или провести тест на большей выборке")
    print()

print("БИЗНЕС-РЕКОМЕНДАЦИЯ ДЛЯ ПРОДУКТА")
print()
if conversion_a > conversion_b:
    lift = (conversion_a - conversion_b) / conversion_b * 100
    print(f"Вариант A показывает конверсию выше на {lift:.1f}% относительно B")
    print(f"При сохранении текущего трафика это даст ~{(conversion_a - conversion_b) * 1000:.0f} дополнительных кликов на 1000 посетителей")
else:
    print("Варианты статистически неразличимы. Решение можно принять по другим критериям:")
    print("- стоимость производства баннера")
    print("- соответствие бренд-буку")
    print("- результаты качественного исследования (интервью с пользователями)")
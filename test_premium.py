# test_premium.py
from premium_manager import SubscriptionManager


def test_premium():
    print("=== ТЕСТ ПРЕМИУМ МЕНЕДЖЕРА ===")

    # Создаем менеджер
    pm = SubscriptionManager()

    # Проверяем статус
    print(f"1. Премиум активен? {pm.is_premium()}")

    # Активируем на 1 месяц
    print("2. Активируем премиум на 1 месяц...")
    pm.activate_premium(1)

    # Проверяем статус
    print(f"3. Премиум активен? {pm.is_premium()}")
    print(f"4. Истекает: {pm.get_expiration_date()}")

    # Сохраняем тестовые данные
    test_user = {
        'name': 'Тест',
        'birth_time': '15:30',
        'birth_place': 'Москва'
    }
    pm.save_user_data(test_user)
    print(f"5. Данные пользователя: {pm.get_user_data()}")

    print("=== ТЕСТ ЗАВЕРШЕН ===")


if __name__ == "__main__":
    test_premium()
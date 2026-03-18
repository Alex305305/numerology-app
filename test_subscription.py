# test_subscription.py
from premium_manager import SubscriptionManager


def test_subscription():
    print("=== ТЕСТ ПОДПИСКИ ===")

    # Создаем менеджер
    sm = SubscriptionManager()

    # Проверяем статус
    print(f"1. Премиум активен? {sm.is_premium()}")

    # Активируем на 1 месяц
    print("2. Активируем премиум на 1 месяц...")
    sm.activate_premium(1)

    # Проверяем статус
    print(f"3. Премиум активен? {sm.is_premium()}")
    print(f"4. Истекает: {sm.data.get('expires')}")

    print("=== ТЕСТ ЗАВЕРШЕН ===")


if __name__ == "__main__":
    test_subscription()
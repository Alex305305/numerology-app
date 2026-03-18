# subscription.py
import json
import os
from datetime import datetime, timedelta


class SubscriptionManager:
    def __init__(self, filename="subscription.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'is_premium': False, 'expires': None}
        return {'is_premium': False, 'expires': None}

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def is_premium(self):
        """Проверяет, активна ли подписка"""
        if not self.data.get('is_premium'):
            return False

        expires = self.data.get('expires')
        if expires:
            expire_date = datetime.strptime(expires, "%Y-%m-%d").date()
            if expire_date < datetime.now().date():
                self.data['is_premium'] = False
                self.save()
                return False

        return True

    def activate_premium(self, months=1):
        """Активирует премиум на указанное количество месяцев"""
        if self.is_premium():
            # Продлеваем существующую подписку
            expires = datetime.strptime(self.data['expires'], "%Y-%m-%d").date()
            new_expires = expires + timedelta(days=30 * months)
        else:
            # Новая подписка
            new_expires = datetime.now().date() + timedelta(days=30 * months)

        self.data['is_premium'] = True
        self.data['expires'] = new_expires.strftime("%Y-%m-%d")
        self.save()
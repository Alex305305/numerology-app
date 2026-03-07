import json
import os
from datetime import datetime


class HistoryManager:
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        """Загружает историю из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save(self):
        """Сохраняет историю в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add(self, name, birth_date, report):
        """Добавляет новый расчёт в историю"""
        entry = {
            'name': name,
            'birth_date': birth_date,
            'report': report,
            'timestamp': datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        self.data.insert(0, entry)  # добавляем в начало
        # Ограничим историю 20 записями
        self.data = self.data[:20]
        self.save()

    def get_all(self):
        """Возвращает всю историю"""
        return self.data

    def clear(self):
        """Очищает историю"""
        self.data = []
        self.save()
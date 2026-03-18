# predictions.py
import json
import os
from datetime import datetime, date, timedelta
from core import reduce_to_number, calculate_life_path


class PredictionManager:
    def __init__(self, filename="predictions.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_daily_prediction(self, user_id, life_path, target_date=None):
        """Возвращает прогноз на указанную дату"""
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%Y-%m-%d")

        # Проверяем, есть ли уже прогноз в кэше
        if user_id in self.data and date_str in self.data[user_id]:
            return self.data[user_id][date_str]

        # Рассчитываем новый прогноз
        prediction = self._calculate_daily_prediction(life_path, target_date)

        # Сохраняем
        if user_id not in self.data:
            self.data[user_id] = {}
        self.data[user_id][date_str] = prediction
        self.save()

        return prediction

    def _calculate_daily_prediction(self, life_path, target_date):
        """Математика ежедневного прогноза"""
        day = target_date.day
        month = target_date.month
        year = target_date.year

        # Суммируем числа
        day_num = sum(int(d) for d in str(day) if d.isdigit())
        month_num = sum(int(d) for d in str(month) if d.isdigit())
        year_num = sum(int(d) for d in str(year) if d.isdigit())

        # Сворачиваем
        day_num = reduce_to_number(day_num, keep_master=False)
        month_num = reduce_to_number(month_num, keep_master=False)
        year_num = reduce_to_number(year_num, keep_master=False)

        # Число дня
        total = life_path + day_num + month_num + year_num
        day_number = reduce_to_number(total, keep_master=False)

        # Получаем описание
        description = self._get_day_description(day_number)

        # Благоприятные/неблагоприятные направления
        favorable = self._get_favorable_directions(day_number)

        return {
            'date': target_date.strftime("%d.%m.%Y"),
            'number': day_number,
            'description': description,
            'favorable': favorable,
            'unfavorable': self._get_unfavorable_directions(day_number)
        }

    def _get_day_description(self, number):
        """Описание энергии дня"""
        descriptions = {
            1: "День лидерства и инициативы. Начинайте новые проекты, проявляйте себя.",
            2: "День сотрудничества и дипломатии. Улаживайте конфликты, ищите компромиссы.",
            3: "День творчества и общения. Встречайтесь с друзьями, творите, веселитесь.",
            4: "День труда и порядка. Работайте, планируйте, наводите порядок.",
            5: "День свободы и перемен. Пробуйте новое, путешествуйте, рискуйте.",
            6: "День любви и заботы. Уделите время семье, помогайте близким.",
            7: "День анализа и уединения. Размышляйте, медитируйте, учитесь.",
            8: "День успеха и денег. Заключайте сделки, решайте финансовые вопросы.",
            9: "День завершения. Заканчивайте старые дела, отпускайте прошлое."
        }
        return descriptions.get(number, "Нейтральный день. Прислушивайтесь к интуиции.")

    def _get_favorable_directions(self, number):
        """Благоприятные занятия в этот день"""
        fav = {
            1: ["начало новых дел", "публичные выступления", "принятие решений"],
            2: ["переговоры", "консультации", "работа в паре"],
            3: ["творчество", "общение", "презентации"],
            4: ["работа", "планирование", "спорт"],
            5: ["путешествия", "обучение", "эксперименты"],
            6: ["семья", "домашние дела", "помощь другим"],
            7: ["исследования", "медитация", "одиночество"],
            8: ["финансы", "бизнес", "инвестиции"],
            9: ["завершение", "благотворительность", "отпускание"]
        }
        return fav.get(number, ["обычные дела"])

    def _get_unfavorable_directions(self, number):
        """Неблагоприятные занятия"""
        unfav = {
            1: ["подчинение", "ожидание", "пассивность"],
            2: ["конфликты", "одиночество", "резкие решения"],
            3: ["рутина", "ограничения", "критика"],
            4: ["риск", "импульсивность", "хаос"],
            5: ["обязательства", "рутина", "ограничения"],
            6: ["конфликты в семье", "эгоизм", "работа"],
            7: ["шумные компании", "суета", "пустые разговоры"],
            8: ["рискованные траты", "азарт", "конфликты"],
            9: ["новые начинания", "эгоизм", "цепляние за прошлое"]
        }
        return unfav.get(number, ["рискованные действия"])
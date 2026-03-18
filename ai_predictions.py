# ai_predictions.py
import requests
import json
from datetime import datetime, date, timedelta
from core import calculate_life_path, calculate_soul_number, calculate_mind_number, get_zodiac_sign


class AIPredictionEngine:
    def __init__(self, api_key, model="deepseek"):  # или "openai", "qwen"
        self.api_key = api_key
        self.model = model
        self.base_url = self._get_base_url()

    def _get_base_url(self):
        """Выбор API в зависимости от модели"""
        urls = {
            "deepseek": "https://api.deepseek.com/v1/chat/completions",
            "openai": "https://api.openai.com/v1/chat/completions",
            "qwen": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        }
        return urls.get(self.model, urls["deepseek"])

    def _get_headers(self):
        """Заголовки для API"""
        if self.model == "deepseek":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        elif self.model == "openai":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        elif self.model == "qwen":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        return {}

    def _calculate_numerology(self, birth_date, birth_time=None):
        """Рассчитываем все нумерологические числа"""
        life_path = calculate_life_path(birth_date)
        soul = calculate_soul_number(birth_date)  # упрощенно
        mind = calculate_mind_number(birth_date)

        # Разбираем дату
        parts = birth_date.split('.')
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        zodiac = get_zodiac_sign(day, month)[0]

        # Персональный год
        current_year = datetime.now().year
        personal_year = life_path + current_year
        while personal_year > 9:
            personal_year = sum(int(d) for d in str(personal_year))

        return {
            'life_path': life_path,
            'soul': soul,
            'mind': mind,
            'zodiac': zodiac,
            'personal_year': personal_year,
            'birth_day': day,
            'birth_month': month,
            'birth_year': year
        }

    def _build_prompt(self, user_data, prediction_type, target_date):
        """Строим промпт для ИИ"""

        # Рассчитываем нумерологию
        numerology = self._calculate_numerology(
            user_data['birth_date'],
            user_data.get('birth_time')
        )

        # Формируем контекст
        context = f"""
        Ты профессиональный астролог и нумеролог с 20-летним опытом.
        Составь персональный {prediction_type} прогноз для пользователя.

        ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
        - Имя: {user_data['name']}
        - Пол: {user_data.get('gender', 'не указан')}
        - Дата рождения: {user_data['birth_date']}
        - Время рождения: {user_data.get('birth_time', 'не указано')}
        - Место рождения: {user_data.get('birth_place', 'не указано')}
        - Профессия: {user_data.get('profession', 'не указана')}
        - Семейное положение: {user_data.get('relationship_status', 'не указано')}
        - Интересы: {', '.join(user_data.get('interests', ['общее']))}

        НУМЕРОЛОГИЧЕСКИЕ ДАННЫЕ:
        - Число жизненного пути: {numerology['life_path']}
        - Число души: {numerology['soul']}
        - Число ума: {numerology['mind']}
        - Знак зодиака: {numerology['zodiac']}
        - Персональный год: {numerology['personal_year']}

        ДАТА ПРОГНОЗА: {target_date.strftime('%d.%m.%Y')}
        ТИП ПРОГНОЗА: {prediction_type}

        ТРЕБОВАНИЯ К ПРОГНОЗУ:
        1. Обязательно учитывай профессию пользователя
        2. Дай конкретные советы, привязанные к реальной жизни
        3. Укажи благоприятные и неблагоприятные часы
        4. Сделай прогноз живым, человеческим языком
        5. Добавь персональные рекомендации

        ФОРМАТ ОТВЕТА (JSON):
        {{
            "short": "Краткий прогноз (1 предложение)",
            "full": "Полный прогноз (5-7 предложений)",
            "favorable_times": ["11:00-13:00"],
            "advice": ["конкретный совет 1", "совет 2"],
            "mood": "positive/neutral/cautious"
        }}
        """

        return context

    def get_prediction(self, user_data, prediction_type="daily", target_date=None):
        """Получаем прогноз от ИИ"""

        if target_date is None:
            target_date = date.today()

        # Строим промпт
        prompt = self._build_prompt(user_data, prediction_type, target_date)

        # Формируем запрос к API
        if self.model == "deepseek":
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Ты профессиональный астролог и нумеролог."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 1000
            }
        elif self.model == "openai":
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "Ты профессиональный астролог и нумеролог."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 1000
            }

        try:
            response = requests.post(
                self.base_url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            # Парсим ответ в зависимости от модели
            if self.model == "deepseek":
                content = response.json()['choices'][0]['message']['content']
            elif self.model == "openai":
                content = response.json()['choices'][0]['message']['content']

            # Извлекаем JSON из ответа
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Если не нашли JSON, возвращаем текст как есть
                return {
                    "short": "Ваш прогноз готов",
                    "full": content,
                    "favorable_times": [],
                    "advice": [],
                    "mood": "neutral"
                }

        except Exception as e:
            print(f"Ошибка при запросе к ИИ: {e}")
            return self._get_fallback_prediction(user_data, prediction_type, target_date)

    def _get_fallback_prediction(self, user_data, prediction_type, target_date):
        """Резервный прогноз, если ИИ недоступен"""
        # Здесь используем наши статические расчеты
        from predictions import PredictionManager
        pm = PredictionManager()
        numerology = self._calculate_numerology(user_data['birth_date'])

        # Получаем базовый прогноз
        daily = pm._calculate_daily_prediction(numerology['life_path'], target_date)

        return {
            "short": f"День числа {daily['number']}: {daily['description'][:50]}...",
            "full": daily['description'] + "\n\n" + "\n".join(daily['favorable']),
            "favorable_times": [],
            "advice": daily['favorable'],
            "mood": "neutral"
        }
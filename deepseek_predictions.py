# deepseek_predictions.py
import os
import json
from datetime import date, datetime, timedelta
from openai import OpenAI
from typing import Dict, List, Optional
import hashlib


class DeepSeekPredictionEngine:
    def __init__(self, api_key=None):
        """
        Инициализация движка DeepSeek API

        Args:
            api_key: API ключ DeepSeek (если None, берется из переменной окружения)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API ключ не найден. Укажите api_key или установите DEEPSEEK_API_KEY\n"
                "Получить ключ: https://platform.deepseek.com/api_keys"
            )

        # Создаем клиент OpenAI (DeepSeek совместим с OpenAI SDK) [citation:4]
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.proxyapi.ru/openai/v1"  # Важно: именно /v1 на конце
        )

        self.cache = {}  # Кэш для бесплатных прогнозов

    def _get_cache_key(self, user_id, pred_type, target_date):
        """Генерирует ключ для кэша"""
        date_str = target_date.strftime("%Y%m%d")
        return f"{user_id}_{pred_type}_{date_str}"

    def _build_prediction_prompt(self, user_data, numerology, pred_type, target_date, is_premium=False):
        """Строит промпт для прогноза на основе данных пользователя"""

        period_names = {
            "daily": "на сегодня",
            "weekly": "на неделю",
            "monthly": "на месяц"
        }
        period = period_names.get(pred_type, "на сегодня")

        # Базовая информация
        base_info = f"""
        Ты профессиональный нумеролог и астролог с 20-летним опытом.
        Составь персональный прогноз {period} для пользователя.

        Данные пользователя:
        - Имя: {user_data.get('name', 'Пользователь')}
        - Дата рождения: {user_data.get('birth_date', 'не указана')}
        - Профессия: {user_data.get('profession', 'не указана')}
        """

        # Добавляем время рождения только для премиум
        if is_premium and user_data.get('birth_time'):
            base_info += f"- Время рождения: {user_data.get('birth_time')}\n"
        if is_premium and user_data.get('birth_place'):
            base_info += f"- Место рождения: {user_data.get('birth_place')}\n"

        # Нумерологические данные
        numerology_info = f"""
        Нумерологические данные (рассчитаны по дате рождения):
        - Число жизненного пути: {numerology.get('life_path', '?')}
        - Число души: {numerology.get('soul', '?')}
        - Число ума: {numerology.get('mind', '?')}
        - Знак зодиака: {numerology.get('zodiac', '?')}
        - Персональный год: {numerology.get('personal_year', '?')}
        - Кармический хвост: {numerology.get('karmic_tail', '?')}
        """

        if is_premium:
            # Детальный промпт для премиум
            prompt = base_info + numerology_info + f"""
            Дата прогноза: {target_date.strftime('%d.%m.%Y')}

            Требования к прогнозу:
            1. Дай подробный прогноз по трем сферам: карьера, любовь, здоровье
            2. Укажи благоприятные часы (если есть данные о времени рождения)
            3. Дай 3 конкретных совета на {period}
            4. Учти профессию пользователя в рекомендациях
            5. Укажи, чего лучше избегать
            6. Прогноз должен быть персонализированным и практичным

            Формат ответа (только JSON, без лишнего текста):
            {{
                "short": "Краткое резюме (1 предложение)",
                "career": "Прогноз по карьере с учетом профессии",
                "love": "Прогноз по любви/отношениям",
                "health": "Прогноз по здоровью",
                "favorable_hours": ["час1", "час2"],
                "avoid": ["чего избегать 1", "чего избегать 2"],
                "advice": ["совет 1", "совет 2", "совет 3"],
                "mood": "positive/neutral/cautious"
            }}
            """
        else:
            # Простой промпт для бесплатной версии
            prompt = base_info + numerology_info + f"""
            Дата прогноза: {target_date.strftime('%d.%m.%Y')}

            Требования:
            1. Дай краткий прогноз на {period}
            2. Укажи 2 благоприятных дела и 2 вещи, которых лучше избегать
            3. Дай один главный совет

            Формат ответа (только JSON, без лишнего текста):
            {{
                "short": "Краткое резюме (1-2 предложения)",
                "full": "Полный прогноз (3-4 предложения)",
                "favorable": ["дело 1", "дело 2"],
                "avoid": ["избегать 1", "избегать 2"],
                "advice": ["главный совет"]
            }}
            """

        return prompt

    def get_prediction(self, user_data, numerology, pred_type="daily", target_date=None, is_premium=False):
        """Получает прогноз от DeepSeek API"""

        if target_date is None:
            target_date = date.today()

        # Проверяем кэш для бесплатной версии
        if not is_premium:
            cache_key = self._get_cache_key(
                user_data.get('user_id', 'default'),
                pred_type,
                target_date
            )
            if cache_key in self.cache:
                print("✅ Использован кэшированный прогноз")
                return self.cache[cache_key]

        # Строим промпт
        prompt = self._build_prediction_prompt(
            user_data, numerology, pred_type, target_date, is_premium
        )

        try:
            # 👇 ВОТ СЮДА ВСТАВЛЯЕМ ВЫБОР МОДЕЛИ
            if is_premium:
                model = "gpt-4.1-nano"  # или "o4-mini"
            else:
                model = "o4-mini"  # или "o3-mini"

            # Отправляем запрос
            completion_params = {
                "model": model,
                "messages": [
                    {"role": "system",
                     "content": "Ты профессиональный нумеролог и астролог. Отвечай только в формате JSON."},
                    {"role": "user", "content": prompt}
                ],
                "max_completion_tokens": 2000,
                "response_format": {"type": "json_object"}
            }

            # Temperature только для премиум
            if is_premium:
                completion_params["temperature"] = 0.7

            # Отправляем запрос
            response = self.client.chat.completions.create(**completion_params)

            # Получаем ответ
            content = response.choices[0].message.content

            # Парсим JSON
            try:
                # Иногда API может вернуть JSON с пояснениями, пытаемся извлечь
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    prediction = json.loads(json_match.group())
                else:
                    prediction = json.loads(content)
            except Exception as e:
                print(f"⚠️ Ошибка парсинга JSON: {e}")
                prediction = self._get_fallback_prediction(user_data, numerology, pred_type, is_premium)

            # Сохраняем в кэш для бесплатной версии
            if not is_premium:
                cache_key = self._get_cache_key(
                    user_data.get('user_id', 'default'),
                    pred_type,
                    target_date
                )
                self.cache[cache_key] = prediction
                # Ограничиваем размер кэша
                if len(self.cache) > 50:
                    oldest = min(self.cache.keys(), key=lambda k: k.split('_')[-1])
                    del self.cache[oldest]

            return prediction

        except Exception as e:
            print(f"❌ Ошибка DeepSeek API: {e}")
            return self._get_fallback_prediction(user_data, numerology, pred_type, is_premium)

    def _get_fallback_prediction(self, user_data, numerology, pred_type, is_premium):
        """Резервный прогноз на случай ошибки API"""

        life_path = numerology.get('life_path', 1)
        name = user_data.get('name', '')

        if is_premium:
            return {
                "short": f"🌟 День числа {life_path} для {name}",
                "career": "Благоприятный день для профессионального роста. Ваша инициативность будет замечена.",
                "love": "В отношениях возможны приятные сюрпризы. Будьте открыты к общению.",
                "health": "Обратите внимание на режим сна и питание.",
                "favorable_hours": ["10:00-12:00", "15:00-17:00"],
                "avoid": ["конфликты", "рискованные решения"],
                "advice": [
                    "Доверяйте своей интуиции",
                    "Уделите время близким",
                    "Планируйте важные дела на первую половину дня"
                ],
                "mood": "positive"
            }
        else:
            return {
                "short": f"Сегодня день числа {life_path}",
                "full": "Хороший день для новых начинаний. Будьте внимательны к знакам судьбы. Энергия дня благоприятствует общению и творчеству.",
                "favorable": ["общение", "планирование", "творчество"],
                "avoid": ["спешка", "конфликты", "импульсивные решения"],
                "advice": ["Прислушайтесь к интуиции и доверяйте своему внутреннему голосу"]
            }

    def check_balance(self):
        """Проверяет остаток токенов (для мониторинга)"""
        try:
            # DeepSeek API пока не имеет метода для проверки баланса,
            # но можно отслеживать через веб-интерфейс
            return "Проверьте баланс на platform.deepseek.com/usage"
        except:
            return "Не удалось проверить баланс"
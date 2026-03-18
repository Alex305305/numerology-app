# premium_predictions.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from datetime import datetime, date
from deepseek_predictions import DeepSeekPredictionEngine
from premium_manager import SubscriptionManager
from core import calculate_life_path, calculate_soul_number, calculate_mind_number, get_zodiac_sign, get_karmic_tail


class PremiumPredictionsScreen(Screen):
    def __init__(self, user_data, **kwargs):
        super().__init__(**kwargs)
        self.user_data = user_data
        self.sub_manager = SubscriptionManager()

        # Создаем движок для прогнозов (ключ берется из переменной окружения)
        self.ai_engine = DeepSeekPredictionEngine()

        # Рассчитываем нумерологию для пользователя
        self.numerology = self._calculate_user_numerology()

        # Создаем интерфейс
        self.build_ui()

    def on_enter(self):
        """Вызывается при входе на экран"""
        if self.user_data and self.user_data.get('name'):
            # Пересчитываем нумерологию с новыми данными
            self.numerology = self._calculate_user_numerology()
            # Загружаем прогноз
            self.load_prediction("daily")
        else:
            # Если данных нет, показываем сообщение
            self.prediction_label.text = "Сначала введите данные в профиле"

    def _calculate_user_numerology(self):
        """Рассчитывает все нумерологические данные пользователя"""
        birth_date = self.user_data.get('birth_date', '01.01.2000')
        name = self.user_data.get('name', '')

        # Разбираем дату для знака зодиака
        try:
            parts = birth_date.split('.')
            day, month = int(parts[0]), int(parts[1])
            zodiac = get_zodiac_sign(day, month)[0]
        except:
            zodiac = "Не определен"

        return {
            'life_path': calculate_life_path(birth_date),
            'soul': calculate_soul_number(name),
            'mind': calculate_mind_number(name),
            'zodiac': zodiac,
            'personal_year': self._calculate_personal_year(birth_date),
            'karmic_tail': get_karmic_tail(birth_date)
        }

    def _calculate_personal_year(self, birth_date):
        """Рассчитывает персональный год"""
        from core import calculate_life_path
        from datetime import datetime

        life_path = calculate_life_path(birth_date)
        current_year = datetime.now().year
        total = life_path + current_year
        while total > 9:
            total = sum(int(d) for d in str(total))
        return total

    def load_prediction(self, pred_type="daily"):
        """Загружает прогноз от ИИ"""

        # Проверяем подписку
        is_premium = self.sub_manager.is_premium()

        # Показываем загрузку
        self.loading_label.text = "🔮 ИИ составляет прогноз..."
        self.prediction_label.text = ""

        def \
                load_thread(dt):
            target_date = date.today()

            # Получаем прогноз
            prediction = self.ai_engine.get_prediction(
                self.user_data,
                self.numerology,
                pred_type=pred_type,
                target_date=target_date,
                is_premium=is_premium
            )

            # Обновляем UI
            self.update_prediction_ui(prediction, pred_type, is_premium)

        Clock.schedule_once(load_thread, 0.1)

    def show_premium_required(self, layout):
        """Показывает экран для неподписанных пользователей"""
        layout.add_widget(Label(
            text="🔒 Премиум доступ",
            font_size=36,
            size_hint_y=None,
            height=80,
            color=(1, 0.9, 0.6, 1)
        ))

        layout.add_widget(Label(
            text="Этот раздел доступен только\nдля премиум подписчиков",
            font_size=20,
            size_hint_y=None,
            height=100,
            color=(1, 1, 1, 1)
        ))

        features = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        features.add_widget(Label(text="✅ Ежедневные прогнозы"))
        features.add_widget(Label(text="✅ Время рождения"))
        features.add_widget(Label(text="✅ Карьера, любовь, здоровье"))
        features.add_widget(Label(text="✅ Благоприятные часы"))
        features.add_widget(Label(text="✅ Еженедельные прогнозы"))
        layout.add_widget(features)

        subscribe_btn = Button(
            text="Подписаться за 199₽/мес",
            size_hint_y=None,
            height=70,
            background_color=(0.3, 0.6, 0.3, 1),
            font_size=18
        )
        subscribe_btn.bind(on_press=self.go_to_subscription)
        layout.add_widget(subscribe_btn)

        back_btn = Button(
            text="Назад",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.1, 0.3, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

    def show_premium_content(self, layout):
        """Показывает контент для премиум пользователей"""
        # Вкладки
        tabs = BoxLayout(size_hint_y=None, height=50, spacing=5)

        self.btn_day = Button(text="День", background_color=(0.4, 0.3, 0.6, 1))
        self.btn_week = Button(text="Неделя", background_color=(0.3, 0.2, 0.5, 1))
        self.btn_month = Button(text="Месяц", background_color=(0.3, 0.2, 0.5, 1))

        tabs.add_widget(self.btn_day)
        tabs.add_widget(self.btn_week)
        tabs.add_widget(self.btn_month)
        layout.add_widget(tabs)

        # Информация о подписке
        expires = self.sub_manager.data.get('expires', 'неизвестно')
        layout.add_widget(Label(
            text=f"✅ Премиум активен до {expires}",
            size_hint_y=None,
            height=40,
            color=(0.3, 1, 0.3, 1)
        ))

        # Область прогноза
        scroll = ScrollView()
        self.prediction_label = Label(
            text="Загружаем ваш персональный прогноз...",
            font_size=16,
            halign='left',
            valign='top',
            size_hint_y=None,
            color=(1, 1, 1, 1)
        )
        self.prediction_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )
        scroll.add_widget(self.prediction_label)
        layout.add_widget(scroll)

        # Кнопка назад
        back_btn = Button(
            text="Назад",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.1, 0.3, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

        # Загружаем прогноз
        Clock.schedule_once(lambda dt: self.load_prediction("daily"), 0.1)

    def go_to_subscription(self, instance):
        """Переход к оформлению подписки"""
        from subscription_screen import SubscriptionScreen
        self.manager.current = 'subscription'

    def update_prediction_ui(self, prediction, pred_type, is_premium):
        """Обновляет интерфейс с прогнозом"""
        self.loading_label.text = ""

        if is_premium and pred_type == "daily":
            # Премиум формат
            text = f"[b]{prediction.get('short', '')}[/b]\n\n"
            text += f"💼 КАРЬЕРА:\n{prediction.get('career', '')}\n\n"
            text += f"❤️ ЛЮБОВЬ:\n{prediction.get('love', '')}\n\n"
            text += f"🏃 ЗДОРОВЬЕ:\n{prediction.get('health', '')}\n\n"

            if prediction.get('favorable_hours'):
                text += "⏰ БЛАГОПРИЯТНЫЕ ЧАСЫ:\n"
                for hour in prediction['favorable_hours']:
                    text += f"   {hour}\n"
                text += "\n"

            if prediction.get('advice'):
                text += "💡 СОВЕТЫ:\n"
                for advice in prediction['advice']:
                    text += f"   • {advice}\n"
        else:
            # Бесплатный формат
            text = f"[b]{prediction.get('short', '')}[/b]\n\n"
            text += f"{prediction.get('full', '')}\n\n"

            if prediction.get('favorable'):
                text += "✅ БЛАГОПРИЯТНО:\n"
                for item in prediction['favorable']:
                    text += f"   • {item}\n"
                text += "\n"

            if prediction.get('avoid'):
                text += "⚠️ ИЗБЕГАТЬ:\n"
                for item in prediction['avoid']:
                    text += f"   • {item}\n"
                text += "\n"

            if prediction.get('advice'):
                text += "💡 СОВЕТ:\n"
                text += f"   {prediction['advice'][0]}\n"

        self.prediction_label.text = text

        # Принудительно обновляем размер текста под текущую ширину
        self.prediction_label.text_size = (self.prediction_label.width * 0.9, None)

    def build_ui(self):
        """Создает интерфейс экрана"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Заголовок
        title = "🔮 Ваш прогноз"
        if not self.sub_manager.is_premium():
            title += " (бесплатно)"

        layout.add_widget(Label(
            text=title,
            font_size=36,
            size_hint_y=None,
            height=60,
            color=(1, 0.9, 0.6, 1)
        ))

        # Вкладки
        tabs = BoxLayout(size_hint_y=None, height=50, spacing=5)

        self.btn_day = Button(text="День", background_color=(0.4, 0.3, 0.6, 1))
        self.btn_day.bind(on_press=lambda x: self.load_prediction("daily"))

        self.btn_week = Button(text="Неделя", background_color=(0.3, 0.2, 0.5, 1))
        self.btn_week.bind(on_press=lambda x: self.load_prediction("weekly"))

        self.btn_month = Button(text="Месяц", background_color=(0.3, 0.2, 0.5, 1))
        self.btn_month.bind(on_press=lambda x: self.load_prediction("monthly"))

        tabs.add_widget(self.btn_day)
        tabs.add_widget(self.btn_week)
        tabs.add_widget(self.btn_month)
        layout.add_widget(tabs)

        # Индикатор загрузки
        self.loading_label = Label(
            text="",
            size_hint_y=None,
            height=40,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.loading_label)

        # Область прогноза
        scroll = ScrollView()
        # Стало:
        self.prediction_label = Label(
            text="",
            font_size=16,
            halign='left',
            valign='top',
            size_hint_y=None,
            size_hint_x=1,  # Растягиваем по ширине
            text_size=(self.width * 0.9, None),  # Ширина 90% от родителя
            color=(1, 1, 1, 1),
            markup=True
        )
        # Добавь привязку для обновления text_size при изменении размера окна
        self.prediction_label.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value * 0.9, None))
        )
        scroll.add_widget(self.prediction_label)
        layout.add_widget(scroll)

        # Кнопка назад
        back_btn = Button(
            text="Назад",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.1, 0.3, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

        self.add_widget(layout)

        # Загружаем дневной прогноз при старте
        Clock.schedule_once(lambda dt: self.load_prediction("daily"), 0.1)

    def on_size(self, *args):
        """Вызывается при изменении размера окна"""
        if hasattr(self, 'prediction_label'):
            self.prediction_label.text_size = (self.prediction_label.width * 0.9, None)


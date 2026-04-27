from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from datetime import date
from deepseek_predictions import DeepSeekPredictionEngine
from premium_manager import SubscriptionManager
from core import calculate_life_path, calculate_soul_number, calculate_mind_number, get_zodiac_sign, get_karmic_tail

class PremiumPredictionsScreen(Screen):
    def __init__(self, user_data, **kwargs):
        super().__init__(**kwargs)
        self.user_data = user_data
        self.sub_manager = SubscriptionManager()
        self.ai_engine = DeepSeekPredictionEngine()
        self.numerology = self._calculate_user_numerology() if user_data else None
        self.build_ui()

    def _calculate_user_numerology(self):
        birth_date = self.user_data.get('birth_date', '01.01.2000')
        name = self.user_data.get('name', '')
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
        from core import calculate_life_path
        from datetime import datetime
        life_path = calculate_life_path(birth_date)
        current_year = datetime.now().year
        total = life_path + current_year
        while total > 9:
            total = sum(int(d) for d in str(total))
        return total

    def on_enter(self):
        if hasattr(self, 'user_data') and self.user_data and self.user_data.get('name'):
            self.numerology = self._calculate_user_numerology()
        self.build_ui()
        if self.user_data and self.user_data.get('name') and self.sub_manager.is_premium():
            Clock.schedule_once(lambda dt: self.load_prediction("daily"), 0.2)
        elif not self.user_data or not self.user_data.get('name'):
            if hasattr(self, 'prediction_label'):
                self.prediction_label.text = "👤 Сначала введите данные в профиле"

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        if not self.sub_manager.is_premium():
            self.show_premium_required(layout)
        else:
            self.show_premium_content(layout)
        self.add_widget(layout)

    def show_premium_required(self, layout):
        layout.clear_widgets()
        layout.add_widget(Label(
            text="🔒 Премиум доступ",
            font_size=36,
            size_hint_y=None,
            height=80,
            color=(1, 0.9, 0.6, 1)
        ))
        layout.add_widget(Label(
            text="Ежедневные, еженедельные и ежемесячные прогнозы\nдоступны только по подписке",
            font_size=20,
            size_hint_y=None,
            height=100,
            color=(1, 1, 1, 1)
        ))
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

    def go_to_subscription(self, instance):
        self.manager.current = 'subscription'

    def show_premium_content(self, layout):
        layout.clear_widgets()
        layout.add_widget(Label(
            text="🔮 Ваш прогноз (премиум)",
            font_size=36,
            size_hint_y=None,
            height=60,
            color=(1, 0.9, 0.6, 1)
        ))
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

        expires = self.sub_manager.data.get('expires', 'неизвестно')
        layout.add_widget(Label(
            text=f"✅ Премиум активен до {expires}",
            size_hint_y=None,
            height=40,
            color=(0.3, 1, 0.3, 1)
        ))

        self.loading_label = Label(text="", size_hint_y=None, height=40, color=(1,1,1,1))
        layout.add_widget(self.loading_label)

        scroll = ScrollView()
        self.prediction_label = Label(
            text="",
            font_size=16,
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(scroll.width, None),
            color=(1,1,1,1),
            markup=True
        )
        self.prediction_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1]),
            width=lambda instance, value: setattr(instance, 'text_size', (value, None))
        )
        scroll.add_widget(self.prediction_label)
        layout.add_widget(scroll)

        back_btn = Button(
            text="Назад",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.1, 0.3, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

    def load_prediction(self, pred_type="daily"):
        is_premium = self.sub_manager.is_premium()
        if not is_premium:
            self.build_ui()
            return
        self.loading_label.text = "🔮 ИИ составляет прогноз..."
        self.prediction_label.text = ""

        def load_thread(dt):
            target_date = date.today()
            prediction = self.ai_engine.get_prediction(
                self.user_data,
                self.numerology,
                pred_type=pred_type,
                target_date=target_date,
                is_premium=True
            )
            self.update_prediction_ui(prediction, pred_type)

        Clock.schedule_once(load_thread, 0.1)

    def update_prediction_ui(self, prediction, pred_type):
        self.loading_label.text = ""
        text = f"[b]{prediction.get('short', '')}[/b]\n\n"
        text += f"💼 КАРЬЕРА:\n{prediction.get('career', '')}\n\n"
        text += f"❤️ ЛЮБОВЬ:\n{prediction.get('love', '')}\n\n"
        text += f"🏃 ЗДОРОВЬЕ:\n{prediction.get('health', '')}\n\n"
        if prediction.get('favorable_hours'):
            text += "⏰ БЛАГОПРИЯТНЫЕ ЧАСЫ:\n"
            for hour in prediction['favorable_hours']:
                text += f"   {hour}\n"
            text += "\n"
        if prediction.get('avoid'):
            text += "⚠️ ИЗБЕГАТЬ:\n"
            for item in prediction['avoid']:
                text += f"   • {item}\n"
            text += "\n"
        if prediction.get('advice'):
            text += "💡 СОВЕТЫ:\n"
            for advice in prediction['advice']:
                text += f"   • {advice}\n"
        if prediction.get('daily_breakdown'):
            text += f"\n📅 ДЕТАЛЬНЫЙ РАЗБОР:\n{prediction['daily_breakdown']}\n"
        self.prediction_label.text = text
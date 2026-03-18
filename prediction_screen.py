# prediction_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from datetime import datetime, timedelta
from deepseek_predictions import QwenPredictionEngine
import json


class PredictionScreen(Screen):
    def __init__(self, user_data, api_key, **kwargs):
        super().__init__(**kwargs)
        self.user_data = user_data
        self.is_premium = user_data.get('is_premium', False)  # Проверяем подписку
        self.ai_engine = QwenPredictionEngine(api_key)

        # Основной layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Заголовок
        title_text = "🔮 Ваш прогноз"
        if not self.is_premium:
            title_text += " (Бесплатно)"

        layout.add_widget(Label(
            text=title_text,
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

        # Информация о премиум (если не куплено)
        if not self.is_premium:
            premium_info = BoxLayout(size_hint_y=None, height=80, spacing=10)
            premium_info.add_widget(Label(
                text="✨ Для прогнозов с временем рождения\nи расширенного анализа -",
                color=(1, 1, 0.8, 1),
                font_size=14
            ))
            premium_btn = Button(
                text="Премиум",
                size_hint_x=0.3,
                background_color=(0.5, 0.3, 0.7, 1)
            )
            premium_btn.bind(on_press=self.show_premium_popup)
            premium_info.add_widget(premium_btn)
            layout.add_widget(premium_info)

        # Индикатор загрузки
        self.loading_label = Label(
            text="✨ Загружаем прогноз...",
            size_hint_y=None,
            height=50,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.loading_label)

        # Область для текста прогноза
        scroll = ScrollView()
        self.prediction_label = Label(
            text="",
            font_size=16,
            halign='left',
            valign='top',
            size_hint_y=None,
            color=(1, 1, 1, 1),
            markup=True
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

        self.add_widget(layout)

        # Загружаем дневной прогноз
        Clock.schedule_once(lambda dt: self.load_prediction("daily"), 0.1)

    def show_premium_popup(self, instance):
        """Показывает окно с предложением премиум"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(Label(
            text="✨ Премиум прогнозы ✨",
            font_size=24,
            color=(1, 0.9, 0.6, 1)
        ))
        content.add_widget(Label(
            text="• Прогнозы с учетом времени рождения\n"
                 "• Детальный анализ карьеры и отношений\n"
                 "• Благоприятные часы\n"
                 "• Предупреждения о трудностях",
            halign='left',
            color=(1, 1, 1, 1)
        ))

        buttons = BoxLayout(size_hint_y=None, height=100, spacing=10)

        subscribe_btn = Button(
            text="Подписаться\n199₽/мес",
            background_color=(0.3, 0.6, 0.3, 1)
        )
        subscribe_btn.bind(on_press=self.subscribe)

        cancel_btn = Button(
            text="Позже",
            background_color=(0.5, 0.2, 0.2, 1)
        )

        buttons.add_widget(subscribe_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.8, 0.6)
        )
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def subscribe(self, instance):
        """Обработка подписки"""
        # Здесь будет интеграция с платежами
        self.is_premium = True
        self.user_data['is_premium'] = True
        self.manager.current = 'prediction'  # перезагружаем экран

    def load_prediction(self, pred_type):
        """Загружает прогноз"""

        # Подсветка вкладок
        self.btn_day.background_color = (0.4, 0.3, 0.6, 1) if pred_type == "daily" else (0.3, 0.2, 0.5, 1)
        self.btn_week.background_color = (0.4, 0.3, 0.6, 1) if pred_type == "weekly" else (0.3, 0.2, 0.5, 1)
        self.btn_month.background_color = (0.4, 0.3, 0.6, 1) if pred_type == "monthly" else (0.3, 0.2, 0.5, 1)

        self.loading_label.text = "🔮 ИИ составляет прогноз..."
        self.prediction_label.text = ""

        def load_thread(dt):
            target_date = datetime.now()
            prediction = self.ai_engine.get_prediction(
                self.user_data,
                is_premium=self.is_premium,
                pred_type=pred_type,
                target_date=target_date
            )

            # Обновляем UI
            self.update_prediction_ui(prediction, pred_type)

        Clock.schedule_once(load_thread, 0.1)

    def update_prediction_ui(self, prediction, pred_type):
        """Обновляет интерфейс с прогнозом"""
        self.loading_label.text = ""

        if self.is_premium:
            # Формат для премиум
            text = f"[b]{prediction.get('short', '')}[/b]\n\n"
            text += f"💼 КАРЬЕРА:\n{prediction.get('career', '')}\n\n"
            text += f"❤️ ОТНОШЕНИЯ:\n{prediction.get('love', '')}\n\n"
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
            # Формат для бесплатного
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
                text += "💡 ГЛАВНЫЙ СОВЕТ:\n"
                text += f"   {prediction['advice'][0]}\n"

        self.prediction_label.text = text
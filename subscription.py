# subscription.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup


class SubscriptionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Заголовок
        layout.add_widget(Label(
            text="🔮 Премиум прогнозы",
            font_size=32,
            size_hint_y=None,
            height=60,
            color=(1, 0.9, 0.6, 1)
        ))

        # Описание
        layout.add_widget(Label(
            text="Получайте персональные прогнозы\nна каждый день!",
            font_size=20,
            size_hint_y=None,
            height=80,
            color=(1, 1, 1, 1)
        ))

        # Тарифы
        tariffs = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=300)

        # Ежедневный
        daily = Button(
            text="🌅 Ежедневный\n149 ₽/месяц",
            size_hint_y=None,
            height=80,
            background_color=(0.3, 0.2, 0.5, 1)
        )
        daily.bind(on_press=lambda x: self.subscribe('daily'))
        tariffs.add_widget(daily)

        # Еженедельный
        weekly = Button(
            text="📅 Еженедельный\n299 ₽/месяц",
            size_hint_y=None,
            height=80,
            background_color=(0.4, 0.3, 0.6, 1)
        )
        weekly.bind(on_press=lambda x: self.subscribe('weekly'))
        tariffs.add_widget(weekly)

        # Годовой
        yearly = Button(
            text="🎆 Годовой\n1990 ₽/год",
            size_hint_y=None,
            height=80,
            background_color=(0.5, 0.4, 0.7, 1)
        )
        yearly.bind(on_press=lambda x: self.subscribe('yearly'))
        tariffs.add_widget(yearly)

        layout.add_widget(tariffs)

        # Кнопка назад
        back = Button(
            text="Назад",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.1, 0.3, 1)
        )
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back)

        self.add_widget(layout)

    def subscribe(self, plan):
        """Обработка подписки"""
        # Здесь будет интеграция с Google Play Billing
        popup = Popup(
            title="Тестовый режим",
            content=Label(text=f"Вы выбрали тариф: {plan}\n\nВ реальном приложении\nздесь будет оплата"),
            size_hint=(0.8, 0.5)
        )
        popup.open()
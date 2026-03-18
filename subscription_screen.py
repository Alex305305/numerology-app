# subscription_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from premium_manager import SubscriptionManager



class SubscriptionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Заголовок
        layout.add_widget(Label(
            text="🌟 Премиум подписка",
            font_size=36,
            size_hint_y=None,
            height=80,
            color=(1, 0.9, 0.6, 1)
        ))

        # Тарифы
        plans = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=300)

        # Месячный
        monthly = Button(
            text="1 месяц — 199 ₽",
            size_hint_y=None,
            height=70,
            background_color=(0.3, 0.2, 0.5, 1),
            font_size=20
        )
        monthly.bind(on_press=lambda x: self.subscribe(1))
        plans.add_widget(monthly)

        # Квартальный (со скидкой)
        quarterly = Button(
            text="3 месяца — 499 ₽ (166 ₽/мес)",
            size_hint_y=None,
            height=70,
            background_color=(0.4, 0.3, 0.6, 1),
            font_size=20
        )
        quarterly.bind(on_press=lambda x: self.subscribe(3))
        plans.add_widget(quarterly)

        # Годовой (макс скидка)
        yearly = Button(
            text="12 месяцев — 1490 ₽ (124 ₽/мес)",
            size_hint_y=None,
            height=70,
            background_color=(0.5, 0.4, 0.7, 1),
            font_size=20
        )
        yearly.bind(on_press=lambda x: self.subscribe(12))
        plans.add_widget(yearly)

        layout.add_widget(plans)

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

    def subscribe(self, months):
        """Обработка подписки"""
        from premium_manager import SubscriptionManager
        sub = SubscriptionManager()
        sub.activate_premium(months)

        # Показываем успех
        popup = Popup(
            title="Успешно!",
            content=Label(text=f"Премиум активирован на {months} мес."),
            size_hint=(0.6, 0.4)
        )
        popup.open()

        # Возвращаемся в меню
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'main'), 2)
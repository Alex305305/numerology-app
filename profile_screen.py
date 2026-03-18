# profile_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Поля для ввода
        self.name_input = TextInput(hint_text="Имя", multiline=False)
        self.date_input = TextInput(hint_text="Дата рождения (дд.мм.гггг)", multiline=False)
        self.time_input = TextInput(hint_text="Время рождения (чч:мм)", multiline=False)
        self.place_input = TextInput(hint_text="Место рождения", multiline=False)
        self.profession_input = TextInput(hint_text="Профессия", multiline=False)
        self.status_input = TextInput(hint_text="Семейное положение", multiline=False)

        # Добавляем поля в layout
        layout.add_widget(Label(text="Заполните анкету для точных прогнозов"))
        layout.add_widget(self.name_input)
        layout.add_widget(self.date_input)
        layout.add_widget(self.time_input)
        layout.add_widget(self.place_input)
        layout.add_widget(self.profession_input)
        layout.add_widget(self.status_input)

        # Кнопка для получения прогноза
        btn = Button(text="🔮 Получить прогноз", size_hint_y=None, height=50)
        btn.bind(on_press=self.get_prediction)
        layout.add_widget(btn)

        # Кнопка назад
        back_btn = Button(text="Назад", size_hint_y=None, height=50)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def get_prediction(self, instance):
        """Собирает данные и переходит к прогнозу"""
        # Проверяем, заполнены ли обязательные поля
        if not self.name_input.text or not self.date_input.text:
            # Можно показать всплывающее окно с ошибкой
            return

        # Собираем данные пользователя
        user_data = {
            'name': self.name_input.text,
            'birth_date': self.date_input.text,
            'birth_time': self.time_input.text if self.time_input.text else None,
            'birth_place': self.place_input.text if self.place_input.text else None,
            'profession': self.profession_input.text if self.profession_input.text else "не указана",
            'relationship_status': self.status_input.text if self.status_input.text else "не указано"
        }

        # Передаем данные на экран прогнозов
        predictions_screen = self.manager.get_screen('premium_predictions')
        predictions_screen.user_data = user_data

        # Переходим к прогнозу
        self.manager.current = 'premium_predictions'

    def save_profile(self, instance):
        # Сохраняем в JSON
        user_data = {
            'name': self.name_input.text,
            'birth_date': self.date_input.text,
            'birth_time': self.time_input.text,
            'birth_place': self.place_input.text,
            'profession': self.profession_input.text,
            'relationship_status': self.status_input.text,
            'interests': ['карьера', 'здоровье']  # можно добавить выбор
        }

        with open('user_profile.json', 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)

        self.manager.current = 'main'
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.app import App
from core import validate_date, generate_full_report
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.uix.scrollview import ScrollView
from space_background import SpaceBackground


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = SpaceBackground()
        self.add_widget(self.background)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        # Заголовок с эффектом свечения (используем markup)
        title = Label(
            text='[color=ffd966]🔮[/color] [color=ffffff]Нумеролог[/color]',
            font_size=48,
            markup=True,
            size_hint_y=None,
            height=120,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title)
        # Стиль для кнопок
        btn_style = {
            'size_hint_y': None,
            'height': 70,
            'font_size': 24,
            'background_color': get_color_from_hex('#4a2c5c'),
            'color': get_color_from_hex('#ffd966'),
            'background_normal': ''
        }
        # Кнопка "Полный расчёт"
        btn_calc = Button(text='✨ Полный расчёт', **btn_style)
        btn_calc.bind(on_press=lambda x: setattr(self.manager, 'current', 'report'))

        # Кнопка "Выход"
        btn_exit = Button(text='🚪 Выход', **btn_style)
        btn_exit.bind(on_press=lambda x: App.get_running_app().stop())

        layout.add_widget(btn_calc)
        layout.add_widget(btn_exit)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_press(self, action):
        if action == "exit":
            App.get_running_app().stop()
        else:
            self.manager.current = action



class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#4A0E5C')  # фиолетовый
        self.color = get_color_from_hex('#FFD966')            # золотой
        self.font_size = 22
        self.size_hint_y = None
        self.height = 70

# Затем в MainMenu вместо обычных Button используй StyledButton

class BaseScreen(Screen):
    def show_popup(self, title, text):
        scroll = ScrollView()
        label = Label(
            text=text,
            font_size=14,
            halign='left',
            valign='top',
            text_size=(self.width * 0.8, None),
            size_hint_y=None,
            color=(1, 1, 1, 1)
        )
        label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        scroll.add_widget(label)
        content = BoxLayout(orientation='vertical')
        content.add_widget(scroll)
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.9),
            background_color=get_color_from_hex('#2A0B3A')
        )
        popup.scale = 0.5
        popup.open()
        # Анимация
        anim = Animation(scale=1, duration=0.3) + Animation(scale=1, duration=0.1)

        anim.start(popup)


from space_background import SpaceBackground


class ReportScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 1. Космический фон
        self.background = SpaceBackground()
        self.add_widget(self.background)

        # 2. Основной контейнер для виджетов (поверх фона)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)

        # Заголовок
        layout.add_widget(Label(
            text="🌌 Введите данные",
            font_size=36,
            size_hint_y=None,
            height=80,
            color=(1, 1, 0.8, 1)
        ))

        # Поле для имени
        layout.add_widget(Label(
            text="Имя:",
            font_size=20,
            halign='left',
            size_hint_y=None,
            height=30,
            color=(1, 1, 0.8, 1)
        ))
        self.name_input = TextInput(
            multiline=False,
            font_size=22,
            height=50,
            size_hint_y=None,
            hint_text="Например: Юрий",
            background_color=(0.2, 0.1, 0.3, 0.8),
            foreground_color=(1, 1, 1, 1)
        )
        layout.add_widget(self.name_input)

        # Поле для даты
        layout.add_widget(Label(
            text="Дата рождения:",
            font_size=20,
            halign='left',
            size_hint_y=None,
            height=30,
            color=(1, 1, 0.8, 1)
        ))
        self.date_input = TextInput(
            multiline=False,
            font_size=22,
            height=50,
            size_hint_y=None,
            hint_text="дд.мм.гггг",
            background_color=(0.2, 0.1, 0.3, 0.8),
            foreground_color=(1, 1, 1, 1)
        )
        layout.add_widget(self.date_input)

        # Кнопка расчёта
        btn_calc = Button(
            text="🔮 Рассчитать",
            size_hint_y=None,
            height=70,
            font_size=24,
            background_color=(0.3, 0.1, 0.5, 0.9),
            color=(1, 1, 0.8, 1)
        )
        btn_calc.bind(on_press=self.calculate)
        layout.add_widget(btn_calc)

        # Кнопка назад
        btn_back = Button(
            text="Назад",
            size_hint_y=None,
            height=60,
            font_size=20,
            background_color=(0.2, 0.05, 0.3, 0.8),
            color=(1, 1, 0.8, 1)
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_size(self, *args):
        """Обновляем размер фона при изменении окна"""
        if hasattr(self, 'background'):
            self.background.size = self.size

    def calculate(self, instance):
        name = self.name_input.text.strip()
        date = self.date_input.text.strip()
        if not name or not validate_date(date):
            self.show_popup("❌ Ошибка", "Введите имя и корректную дату (дд.мм.гггг)")
            return
        report = generate_full_report(date, name)
        self.show_popup("🌟 Ваш нумерологический портрет", report)




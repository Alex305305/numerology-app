from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.app import App
from core import validate_date, generate_full_report, calculate_life_path, get_compatibility_description
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from space_background import SpaceBackground


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = SpaceBackground()
        self.add_widget(self.background)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        # Заголовок с эффектом свечения (используем markup)
        title = Label(
            text='[color=ffd966] [/color] [color=ffffff]Нумеролог[/color]',
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
        btn_calc = Button(text=' Полный расчёт', **btn_style)
        btn_calc.bind(on_press=lambda x: setattr(self.manager, 'current', 'report'))
        layout.add_widget(btn_calc)

        btn_compat = Button(text=' Совместимость', **btn_style)
        btn_compat.bind(on_press=lambda x: setattr(self.manager, 'current', 'compatibility'))
        layout.add_widget(btn_compat)

        # Кнопка "Выход"
        btn_exit = Button(text=' Выход', **btn_style)
        btn_exit.bind(on_press=lambda x: App.get_running_app().stop())
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
        popup = Popup(
            title=title,
            content=Label(
                text=text,
                font_size=14,
                halign='left',
                valign='top',
                text_size=(450, None)
            ),
            size_hint=(0.9, 0.9)
        )
        popup.open()


    def _update_bg(self, instance, value):
        """Обновляет позицию и размер фона при изменении контейнера"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_sep(self, instance, value):
        """Обновляет позицию и размер разделителя"""
        self.sep_rect.pos = instance.pos
        self.sep_rect.size = instance.size


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
            text=" Введите данные",
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
            text=" Рассчитать",
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

        # Строка с чекбоксом
        box_master = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        box_master.add_widget(Label(
            text="Учитывать мастер-числа (11,22,33):",
            color=(1, 1, 0.8, 1),
            size_hint_x=0.7
        ))
        self.master_check = CheckBox(active=True, size_hint_x=0.3)
        box_master.add_widget(self.master_check)
        layout.add_widget(box_master)

        self.add_widget(layout)

    def on_size(self, *args):
        """Обновляем размер фона при изменении окна"""
        if hasattr(self, 'background'):
            self.background.size = self.size

    def calculate(self, instance):
        name = self.name_input.text.strip()
        date = self.date_input.text.strip()
        if not name or not validate_date(date):
            self.show_popup(" Ошибка", "Введите имя и корректную дату (дд.мм.гггг)")
            return
        keep_master = self.master_check.active  # True или False
        report = generate_full_report(date, name, keep_master=keep_master)
        self.show_popup(" Ваш нумерологический портрет", report)

class CompatibilityScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = SpaceBackground()
        self.add_widget(self.background)

        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)

        layout.add_widget(Label(
            text=" Совместимость",
            font_size=36,
            size_hint_y=None,
            height=80,
            color=(1, 0.9, 0.8, 1)
        ))

        # Данные первого человека
        layout.add_widget(Label(text="Первый человек:", font_size=20, size_hint_y=None, height=30, color=(1,1,0.8,1)))
        self.name1_input = TextInput(hint_text="Имя", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.name1_input)
        self.date1_input = TextInput(hint_text="дд.мм.гггг", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.date1_input)

        # Данные второго человека
        layout.add_widget(Label(text="Второй человек:", font_size=20, size_hint_y=None, height=30, color=(1,1,0.8,1)))
        self.name2_input = TextInput(hint_text="Имя", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.name2_input)
        self.date2_input = TextInput(hint_text="дд.мм.гггг", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.date2_input)

        # Кнопка расчёта
        btn = Button(text=" Рассчитать совместимость", size_hint_y=None, height=70,
                     background_color=(0.3,0.1,0.5,0.9), color=(1,1,0.8,1))
        btn.bind(on_press=self.calculate_compatibility)
        layout.add_widget(btn)

        # Кнопка назад
        back_btn = Button(text="Назад", size_hint_y=None, height=60,
                          background_color=(0.2,0.05,0.3,0.8), color=(1,1,0.8,1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

        # Строка с чекбоксом для выбора учёта мастер-чисел
        box_master = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        box_master.add_widget(Label(
            text="Учитывать мастер-числа (11,22,33):",
            color=(1, 1, 0.8, 1),
            size_hint_x=0.7
        ))
        self.master_check = CheckBox(active=True, size_hint_x=0.3)
        box_master.add_widget(self.master_check)

        # Добавляем эту панель в основной layout
        layout.add_widget(box_master)

        self.add_widget(layout)

    def calculate_compatibility(self, instance):
        name1 = self.name1_input.text.strip()
        date1 = self.date1_input.text.strip()
        name2 = self.name2_input.text.strip()
        date2 = self.date2_input.text.strip()

        if not all([name1, date1, name2, date2]) or not validate_date(date1) or not validate_date(date2):
            self.show_popup("Ошибка", "Заполните все поля корректно!")
            return

        # Рассчитываем числа жизненного пути (с мастер-числами)
        from core import calculate_life_path, get_compatibility_description
        num1 = calculate_life_path(date1, keep_master=True)
        num2 = calculate_life_path(date2, keep_master=True)
        desc = get_compatibility_description(num1, num2)

        report = f"Первый: {name1} (число пути {num1})\nВторой: {name2} (число пути {num2})\n\nСовместимость:\n{desc}"
        self.show_popup("Результат совместимости", report)


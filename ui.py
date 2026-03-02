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


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.1, 0.1, 0.2, 1)  # тёмно-синий фон
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
            layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
            layout.add_widget(Label(
                text="🔮 Нумеролог", font_size=48, color=get_color_from_hex('#FFD966'),
                size_hint_y=None, height=100
            ))
            # Используем StyledButton
            for text, screen in [("Полный расчёт", "report"), ("Выход", "exit")]:
                btn = StyledButton(text=text)
                btn.bind(on_press=lambda i, s=screen: self.on_press(s))
                layout.add_widget(btn)
            self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_press(self, action):
        if action == "exit":
            App.get_running_app().stop()
        else:
            self.manager.current = action


class ReportScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)

        layout.add_widget(Label(text="Имя:", font_size=20, size_hint_y=None, height=40))
        self.name_input = TextInput(multiline=False, font_size=22, height=50, size_hint_y=None,
                                    hint_text="Например: Алексей")
        layout.add_widget(self.name_input)

        layout.add_widget(Label(text="Дата рождения:", font_size=20, size_hint_y=None, height=40))
        self.date_input = TextInput(multiline=False, font_size=22, height=50, size_hint_y=None, hint_text="дд.мм.гггг")
        layout.add_widget(self.date_input)

        btn = Button(text="✨ Рассчитать", size_hint_y=None, height=70, font_size=24)
        btn.bind(on_press=self.calculate)
        layout.add_widget(btn)

        back = Button(text="Назад", size_hint_y=None, height=60, font_size=20, background_color=(0.4, 0.4, 0.4, 1))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back)

        self.add_widget(layout)

    def calculate(self, instance):
        name = self.name_input.text.strip()
        date = self.date_input.text.strip()
        if not name or not validate_date(date):
            self.show_popup("❌ Ошибка", "Введите имя и корректную дату (дд.мм.гггг)")
            return
        report = generate_full_report(date, name)
        self.show_popup("🌟 Ваш нумерологический портрет", report)


# # Пустые заглушки для других экранов (можно расширить позже)
# class LifePathScreen(BaseScreen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
#         layout.add_widget(Label(text="Экран 'Число жизненного пути'\n(в разработке)", font_size=24))
#         back = Button(text="Назад", size_hint_y=None, height=60, font_size=20)
#         back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
#         layout.add_widget(back)
#         self.add_widget(layout)
#
#
# class SoulNumberScreen(BaseScreen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
#         layout.add_widget(Label(text="Экран 'Число души'\n(в разработке)", font_size=24))
#         back = Button(text="Назад", size_hint_y=None, height=60, font_size=20)
#         back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
#         layout.add_widget(back)
#         self.add_widget(layout)
#
#
# class MindNumberScreen(BaseScreen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
#         layout.add_widget(Label(text="Экран 'Число ума'\n(в разработке)", font_size=24))
#         back = Button(text="Назад", size_hint_y=None, height=60, font_size=20)
#         back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
#         layout.add_widget(back)
#         self.add_widget(layout)



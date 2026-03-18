from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from premium_manager import SubscriptionManager # добавить эту строку

from core import validate_date, generate_full_report


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Космический фон
        self.background = SpaceBackground()
        self.add_widget(self.background)

        # Затемняющий слой для читаемости кнопок
        with self.canvas.after:
            Color(0, 0, 0, 0.3)  # полупрозрачный чёрный
            self.dim = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_dim, pos=self._update_dim)

        # Главный контейнер - растягивается на весь экран
        main_layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        main_layout.size_hint = (1, 1)  # Растягиваем на весь экран

        # Пустое пространство сверху для центрирования
        main_layout.add_widget(Widget(size_hint_y=1))

        # Контейнер для кнопок (центрированный)
        button_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint=(None, None),
            size=(400, 400)  # Фиксированный размер контейнера
        )
        button_container.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Заголовок
        title = Label(
            text='[color=ffd966]🔮[/color] [color=ffffff]Нумеролог[/color]',
            font_size=48,
            markup=True,
            size_hint=(None, None),
            size=(400, 80)
        )
        button_container.add_widget(title)

        # Кнопки
        buttons = [
            ("✨ Полный расчёт", "report"),
            ("💞 Совместимость", "compatibility"),
            ("📜 История", "history"),
            ("🔮 Прогнозы", "profile"),  # Новая кнопка
            ("🌠 Выход", "exit")
        ]

        for text, screen in buttons:
            btn = Button(
                text=text,
                size_hint=(None, None),
                size=(400, 60),
                font_size=24,
                background_normal='',
                background_color=(0.2, 0.1, 0.3, 0.8),
                color=(1, 1, 0.9, 1)
            )
            btn.bind(on_press=lambda x, s=screen: self.on_press(s))
            button_container.add_widget(btn)

        main_layout.add_widget(button_container)

        # Пустое пространство снизу для центрирования
        main_layout.add_widget(Widget(size_hint_y=1))

        self.add_widget(main_layout)

        # Принудительное обновление макета через небольшую задержку
        Clock.schedule_once(lambda dt: self.do_layout(), 0.1)

    def _update_dim(self, *args):
        self.dim.pos = self.pos
        self.dim.size = self.size

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
        popup.open()
        # Анимация
        anim = Animation(scale=1, duration=0.3) + Animation(scale=1, duration=0.1)
        popup.scale = 0.5
        anim.start(popup)

    def _update_bg(self, instance, value):
        """Обновляет позицию и размер фона при изменении контейнера"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_sep(self, instance, value):
        """Обновляет позицию и размер разделителя"""
        self.sep_rect.pos = instance.pos
        self.sep_rect.size = instance.size


class HistoryScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Фон
        self.background = SpaceBackground()
        self.add_widget(self.background)

        # Основной контейнер
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        main_layout.size_hint = (1, 1)

        # Заголовок с эффектом
        title_layout = BoxLayout(size_hint_y=None, height=80, spacing=10)
        title_label = Label(
            text="📜 История расчётов",
            font_size=36,
            color=(1, 0.9, 0.6, 1),  # тёплый золотой
            bold=True,
            halign='center',
            valign='middle'
        )
        title_layout.add_widget(title_label)
        main_layout.add_widget(title_layout)

        # Контейнер для списка истории с красивым фоном
        scroll = ScrollView()
        self.history_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15,
            padding=[15, 15, 15, 15]
        )
        self.history_container.bind(minimum_height=self.history_container.setter('height'))
        scroll.add_widget(self.history_container)
        main_layout.add_widget(scroll)

        # Кнопки внизу
        buttons_layout = BoxLayout(size_hint_y=None, height=60, spacing=15)

        # Кнопка очистки истории
        clear_btn = Button(
            text="🗑️ Очистить",
            size_hint_x=0.5,
            background_color=(0.6, 0.2, 0.2, 0.9),
            color=(1, 1, 1, 1),
            font_size=18,
            background_normal=''
        )
        clear_btn.bind(on_press=self.clear_history)
        buttons_layout.add_widget(clear_btn)

        # Кнопка назад
        back_btn = Button(
            text="◀ Назад",
            size_hint_x=0.5,
            background_color=(0.3, 0.2, 0.5, 0.9),
            color=(1, 1, 0.8, 1),
            font_size=18,
            background_normal=''
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        buttons_layout.add_widget(back_btn)

        main_layout.add_widget(buttons_layout)
        self.add_widget(main_layout)

    def on_enter(self):
        """Вызывается при входе на экран"""
        self.load_history()

    def create_beautiful_card(self, entry):
        """Создаёт красивую карточку для записи истории"""

        # Основная карточка с закруглёнными углами
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=130,
            spacing=5,
            padding=[15, 10, 15, 10]
        )

        # Рисуем красивый фон с градиентом через canvas
        with card.canvas.before:
            # Градиентный фон (тёмно-фиолетовый с переходом)
            Color(0.25, 0.15, 0.35, 0.95)
            card.rect_bg = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[15]
            )

            # Верхняя полоска-акцент
            Color(1, 0.8, 0.4, 0.8)  # золотая
            card.rect_accent = RoundedRectangle(
                pos=(card.x, card.y + card.height - 5),
                size=(card.width, 5),
                radius=[15, 15, 0, 0]
            )

        # Обновляем позиции при изменении размеров
        def update_rects(instance, value):
            card.rect_bg.pos = instance.pos
            card.rect_bg.size = instance.size
            card.rect_accent.pos = (instance.x, instance.y + instance.height - 5)
            card.rect_accent.size = (instance.width, 5)

        card.bind(pos=update_rects, size=update_rects)

        # Верхняя строка с именем и датой
        top_row = BoxLayout(size_hint_y=None, height=35, spacing=10)

        # Имя с иконкой
        name_label = Label(
            text=f"👤 [b]{entry.get('name', '???')}[/b]",
            markup=True,
            font_size=18,
            color=(1, 0.9, 0.6, 1),
            halign='left',
            size_hint_x=0.5
        )
        name_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        top_row.add_widget(name_label)

        # Дата с иконкой
        date_label = Label(
            text=f"📅 {entry.get('birth_date', '???')}",
            font_size=16,
            color=(0.9, 0.9, 0.9, 1),
            halign='right',
            size_hint_x=0.5
        )
        date_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        top_row.add_widget(date_label)

        card.add_widget(top_row)

        # Время расчёта
        time_label = Label(
            text=f"⏱️ {entry.get('timestamp', '???')}",
            font_size=14,
            color=(0.8, 0.8, 0.8, 0.9),
            halign='left',
            size_hint_y=None,
            height=25
        )
        time_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        card.add_widget(time_label)

        # Кнопка просмотра с эффектом при наведении
        view_btn = Button(
            text="👁️ Просмотреть",
            size_hint_y=None,
            height=40,
            background_color=(0.4, 0.25, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=16,
            background_normal=''
        )
        view_btn.bind(
            on_press=lambda btn, r=entry.get('report', ''): self.show_report(r),
            on_enter=lambda btn: setattr(btn, 'background_color', (0.5, 0.35, 0.7, 1)),
            on_leave=lambda btn: setattr(btn, 'background_color', (0.4, 0.25, 0.6, 1))
        )
        card.add_widget(view_btn)

        return card

    def load_history(self):
        """Загружает и отображает историю"""
        self.history_container.clear_widgets()

        from history import HistoryManager
        history = HistoryManager()
        entries = history.get_all()

        if not entries:
            # Красивое сообщение о пустой истории
            empty_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=300,
                padding=30
            )

            with empty_layout.canvas.before:
                Color(0.2, 0.1, 0.3, 0.7)
                RoundedRectangle(pos=empty_layout.pos, size=empty_layout.size, radius=[20])

            empty_label = Label(
                text="📭 История пока пуста\n\nСделайте первый расчёт,\nчтобы он появился здесь!",
                font_size=20,
                color=(1, 1, 1, 0.9),
                halign='center'
            )
            empty_layout.add_widget(empty_label)
            self.history_container.add_widget(empty_layout)
            return

        for entry in entries:
            card = self.create_beautiful_card(entry)
            self.history_container.add_widget(card)

    def show_report(self, report):
        """Показывает сохранённый отчёт"""
        self.show_popup("📜 Сохранённый расчёт", report)

    def clear_history(self, instance):
        """Очищает историю"""
        from history import HistoryManager
        history = HistoryManager()
        history.clear()
        self.load_history()

from space_background import SpaceBackground


class ReportScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Проверяем подписку
        self.premium = SubscriptionManager()

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
        btn_calc.bind(on_press=self.calculate_with_loading)
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

        # Премиум блок (если нет подписки)
        if not self.premium.is_premium():
            premium_box = BoxLayout(size_hint_y=None, height=60, spacing=10)
            premium_box.add_widget(Label(
                text="🔮 Хотите прогнозы на каждый день?",
                color=(1, 1, 0.8, 1),
                font_size=16
            ))
            premium_btn = Button(
                text="Премиум",
                size_hint_x=0.3,
                background_color=(0.5, 0.3, 0.7, 1),
                color=(1, 1, 1, 1)
            )
            premium_btn.bind(on_press=self.show_premium_popup)
            premium_box.add_widget(premium_btn)
            layout.add_widget(premium_box)

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

    def show_premium_popup(self, instance):
        """Показывает окно с преимуществами премиум"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        content = BoxLayout(orientation='vertical', padding=20, spacing=15)

        content.add_widget(Label(
            text="✨ Премиум прогнозы ✨",
            font_size=24,
            color=(1, 0.9, 0.6, 1),
            size_hint_y=None,
            height=50
        ))

        features = BoxLayout(orientation='vertical', size_hint_y=None, height=200, spacing=10)

        features.add_widget(Label(
            text="✅ Ежедневные прогнозы",
            halign='left',
            color=(1, 1, 1, 1)
        ))
        features.add_widget(Label(
            text="✅ Учет времени рождения",
            halign='left',
            color=(1, 1, 1, 1)
        ))
        features.add_widget(Label(
            text="✅ Карьера, любовь, здоровье",
            halign='left',
            color=(1, 1, 1, 1)
        ))
        features.add_widget(Label(
            text="✅ Благоприятные часы",
            halign='left',
            color=(1, 1, 1, 1)
        ))
        features.add_widget(Label(
            text="✅ Еженедельные прогнозы",
            halign='left',
            color=(1, 1, 1, 1)
        ))

        content.add_widget(features)

        price_label = Label(
            text="199 ₽/месяц",
            font_size=20,
            color=(1, 0.8, 0.4, 1),
            size_hint_y=None,
            height=40
        )
        content.add_widget(price_label)

        buttons = BoxLayout(size_hint_y=None, height=100, spacing=10)

        subscribe_btn = Button(
            text="Подписаться",
            background_color=(0.3, 0.6, 0.3, 1),
            size_hint_x=0.5
        )
        subscribe_btn.bind(on_press=self.activate_premium)

        cancel_btn = Button(
            text="Позже",
            background_color=(0.5, 0.2, 0.2, 1),
            size_hint_x=0.5
        )

        buttons.add_widget(subscribe_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.8, 0.7)
        )
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def activate_premium(self, instance):
        """Активация премиум подписки"""
        from premium_manager import SubscriptionManager
        pm = SubscriptionManager()
        pm.activate_premium(1)

        # Закрываем текущий попап
        instance.parent.parent.parent.dismiss()

        # Показываем успех
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        success_popup = Popup(
            title="Успешно!",
            content=Label(text="Премиум активирован!\nТеперь вам доступны прогнозы."),
            size_hint=(0.6, 0.4)
        )
        success_popup.open()

        # Обновляем интерфейс
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.update_premium_ui(), 0.5)

    def update_premium_ui(self):
        """Обновляет интерфейс после активации премиум"""
        # Перезагружаем экран
        self.manager.current = 'report'


    def calculate_with_loading(self, instance):
        """Показывает индикатор загрузки и выполняет расчёт"""

        # Создаём попап с индикатором
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        content.add_widget(Label(
            text="🔮 Вычисляем...",
            font_size=24,
            color=(1, 1, 0.8, 1)
        ))

        progress = ProgressBar(max=100, value=0, size_hint_y=None, height=30)
        content.add_widget(progress)

        loading_popup = Popup(
            title='',
            content=content,
            size_hint=(0.5, 0.3),
            background_color=(0.1, 0.05, 0.2, 1)
        )
        loading_popup.open()

        # Анимируем прогресс
        from kivy.animation import Animation
        anim = Animation(value=100, duration=1.5)
        anim.start(progress)

        # Выполняем расчёт с задержкой
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.do_calculation(loading_popup), 1.5)

    def do_calculation(self, loading_popup):
        """Реальный расчёт"""
        name = self.name_input.text.strip()
        date = self.date_input.text.strip()

        if not name or not validate_date(date):
            loading_popup.dismiss()
            self.show_popup("❌ Ошибка", "Введите имя и корректную дату")
            return

        keep_master = self.master_check.active if hasattr(self, 'master_check') else True
        report = generate_full_report(date, name, keep_master=keep_master)

        # Сохраняем в историю
        from history import HistoryManager
        history = HistoryManager()
        history.add(name, date, report)

        loading_popup.dismiss()
        self.show_popup("🌟 Ваш нумерологический портрет", report)

    def on_size(self, *args):
        """Обновляем размер фона при изменении окна"""
        if hasattr(self, 'background'):
            self.background.size = self.size

    def calculate(self, instance):
        name = self.name_input.text.strip()
        date = self.date_input.text.strip()
        if not name or not validate_date(date):
            self.show_popup("Ошибка", "Введите имя и корректную дату (дд.мм.гггг)")
            return

        keep_master = self.master_check.active if hasattr(self, 'master_check') else True
        report = generate_full_report(date, name, keep_master=keep_master)

        # Сохраняем в историю
        from history import HistoryManager
        history = HistoryManager()
        history.add(name, date, report)

        self.show_popup("Ваш нумерологический портрет", report)

        # Добавляем блок с премиум предложением внизу
        premium_box = BoxLayout(size_hint_y=None, height=60, spacing=10)
        premium_box.add_widget(Label(
            text="🔮 Хотите прогнозы на каждый день?",
            color=(1, 1, 0.8, 1),
            font_size=16
        ))
        premium_btn = Button(
            text="Премиум",
            size_hint_x=0.3,
            background_color=(0.5, 0.3, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        premium_btn.bind(on_press=self.show_premium_popup)
        premium_box.add_widget(premium_btn)

        # Добавляем после кнопки "Назад"
        layout.add_widget(premium_box)


    def show_premium_popup(self, instance):
        """Показывает окно с преимуществами премиум"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)

        content.add_widget(Label(
            text="✨ Премиум прогнозы ✨",
            font_size=24,
            color=(1, 0.9, 0.6, 1),
            size_hint_y=None,
            height=50
        ))

        features = BoxLayout(orientation='vertical', size_hint_y=None, height=200, spacing=10)

        features.add_widget(Label(
            text="✅ Ежедневные прогнозы с учетом времени рождения",
            halign='left',
            color=(1, 1, 1, 1)
        ))
        features.add_widget(Label(
            text="✅ Детальный разбор карьеры, любви, здоровья",
            halign='left',
            color=(1, 1, 1, 1)
        ))
        features.add_widget(Label(
            text="✅ Благоприятные часы для важных дел",
            halign='left',
            color=(1, 1, 1, 1)
        ))
        features.add_widget(Label(
            text="✅ Еженедельные и ежемесячные прогнозы",
            halign='left',
            color=(1, 1, 1, 1)
        ))
        features.add_widget(Label(
            text="✅ Push-уведомления с прогнозом на день",
            halign='left',
            color=(1, 1, 1, 1)
        ))

        content.add_widget(features)

        price_label = Label(
            text="199 ₽/месяц",
            font_size=20,
            color=(1, 0.8, 0.4, 1),
            size_hint_y=None,
            height=40
        )
        content.add_widget(price_label)

        buttons = BoxLayout(size_hint_y=None, height=100, spacing=10)

        subscribe_btn = Button(
            text="Подписаться",
            background_color=(0.3, 0.6, 0.3, 1),
            size_hint_x=0.5
        )
        subscribe_btn.bind(on_press=self.activate_premium)

        cancel_btn = Button(
            text="Позже",
            background_color=(0.5, 0.2, 0.2, 1),
            size_hint_x=0.5
        )

        buttons.add_widget(subscribe_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.8, 0.7)
        )
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()


    def activate_premium(self, instance):
        """Активация премиум подписки"""
        from premium_manager import SubscriptionManager
        sub = SubscriptionManager()
        sub.activate_premium()

        # Закрываем текущий попап
        instance.parent.parent.parent.dismiss()

        # Показываем успех
        success_popup = Popup(
            title="Успешно!",
            content=Label(text="Премиум активирован!\nТеперь вам доступны прогнозы."),
            size_hint=(0.6, 0.4)
        )
        success_popup.open()

        # Обновляем интерфейс
        Clock.schedule_once(lambda dt: self.update_premium_ui(), 0.5)


    def update_premium_ui(self):
        """Обновляет интерфейс после активации премиум"""
        # Здесь можно добавить обновление кнопок и т.д.
        pass



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


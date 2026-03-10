# Шаг 4: Файл main.py (точка входа)
# numerology_app/
# ├── venv/          # виртуальное окружение (уже есть)
# ├── main.py        # точка входа (только запуск)
# ├── core.py        # все расчёты и данные (нумерология + зодиак)
# └── ui.py          # интерфейс Kivy (экраны, кнопки)

from kivy.app import App
from ui import MainMenu, ReportScreen, CompatibilityScreen, HistoryScreen
from kivy.uix.screenmanager import ScreenManager, FadeTransition, SlideTransition, WipeTransition
from kivy.clock import Clock
from kivy.core.window import Window


class NumerologyApp(App):
    def build(self):
        # Устанавливаем минимальный размер окна
        Window.minimum_width = 400
        Window.minimum_height = 600

        # Можно выбрать любой переход:
        # FadeTransition - плавное затухание
        # SlideTransition - скольжение (можно задать direction)
        # WipeTransition - вытеснение
        # CardTransition - эффект карты

        sm = ScreenManager(transition=SlideTransition(duration=0.3))

        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(ReportScreen(name="report"))
        sm.add_widget(CompatibilityScreen(name="compatibility"))
        sm.add_widget(HistoryScreen(name="history"))

        # Принудительное обновление макета
        Clock.schedule_once(lambda dt: self.fix_layout(sm), 0.2)

        return sm

    def fix_layout(self, sm):
        sm.do_layout()
        for screen in sm.screens:
            screen.do_layout()
        Window.update_viewport()


if __name__ == "__main__":
    NumerologyApp().run()



"""
Какие бывают переходы?
WipeTransition – экран вытесняет предыдущий, как шторка.
SlideTransition – экран заезжает сбоку (можно указать направление:
SlideTransition(direction='left')).
FadeTransition – плавное появление/исчезновение.
CardTransition – эффект, похожий на перелистывание карт.
NoTransition – без анимации (по умолчанию).
"""
#
# cd /home/stalin/EGOROV/numerology_app
# source venv/bin/activate
# python main.py

"""Красивое оформление карточек в истории (сделать их более приятными глазу)

Анимации при переходах между экранами (уже есть FadeTransition, можно добавить эффекты)

Иконки для кнопок (добавить эмодзи или картинки)

Тёмная тема для всех экранов (единый стиль)

Индикатор загрузки при расчёте (если будет долго)"""















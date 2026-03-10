# Шаг 4: Файл main.py (точка входа)
# numerology_app/
# ├── venv/          # виртуальное окружение (уже есть)
# ├── main.py        # точка входа (только запуск)
# ├── core.py        # все расчёты и данные (нумерология + зодиак)
# └── ui.py          # интерфейс Kivy (экраны, кнопки)

from kivy.app import App
from ui import MainMenu, ReportScreen, CompatibilityScreen, HistoryScreen
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.clock import Clock
from kivy.core.window import Window


class NumerologyApp(App):
    def build(self):
        # Устанавливаем минимальный размер окна для корректного отображения
        Window.minimum_width = 400
        Window.minimum_height = 600

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(ReportScreen(name="report"))
        sm.add_widget(CompatibilityScreen(name="compatibility"))
        sm.add_widget(HistoryScreen(name="history"))

        # Принудительное обновление макета через небольшую задержку
        Clock.schedule_once(lambda dt: self.fix_layout(sm), 0.2)

        return sm

    def fix_layout(self, sm):
        """Принудительно обновляет размеры всех экранов"""
        sm.do_layout()
        for screen in sm.screens:
            screen.do_layout()
        # Принудительно обновляем окно
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

















# Шаг 4: Файл main.py (точка входа)
# numerology_app/
# ├── venv/          # виртуальное окружение (уже есть)
# ├── main.py        # точка входа (только запуск)
# ├── core.py        # все расчёты и данные (нумерология + зодиак)
# └── ui.py          # интерфейс Kivy (экраны, кнопки)

from kivy.app import App
from ui import MainMenu, ReportScreen, CompatibilityScreen
from kivy.uix.screenmanager import ScreenManager, WipeTransition, SlideTransition, FadeTransition, CardTransition

class NumerologyApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.5))
        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(ReportScreen(name="report"))
        sm.add_widget(CompatibilityScreen(name="compatibility"))
        return sm

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


















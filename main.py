# main.py

from kivy.app import App
from ui import MainMenu, ReportScreen, CompatibilityScreen, HistoryScreen
from premium_predictions import PremiumPredictionsScreen
from subscription_screen import SubscriptionScreen
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.clock import Clock
from kivy.core.window import Window
from profile_screen import ProfileScreen


class NumerologyApp(App):
    def build(self):
        Window.minimum_width = 400
        Window.minimum_height = 600

        sm = ScreenManager(transition=SlideTransition(duration=0.3))

        # Основные экраны
        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(ReportScreen(name="report"))
        sm.add_widget(CompatibilityScreen(name="compatibility"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(ProfileScreen(name="profile"))


        # Премиум экраны
        sm.add_widget(PremiumPredictionsScreen(user_data={}, name="premium_predictions"))
        sm.add_widget(SubscriptionScreen(name="subscription"))

        Clock.schedule_once(lambda dt: self.fix_layout(sm), 0.2)
        return sm

    def fix_layout(self, sm):
        sm.do_layout()
        for screen in sm.screens:
            screen.do_layout()
        Window.update_viewport()


if __name__ == "__main__":
    NumerologyApp().run()



# cd /home/stalin/EGOROV/numerology_app
# source venv/bin/activate
# export DEEPSEEK_API_KEY='твой_ключ'
# python main.py
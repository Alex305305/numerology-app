from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.animation import Animation
from random import randint, uniform

class Star(Widget):
    def __init__(self, x, y, size, **kwargs):
        super().__init__(**kwargs)
        self.size = (size, size)
        self.pos = (x, y)
        self.opacity = uniform(0.5, 1.0)

        with self.canvas:
            Color(1, 1, 1, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

        # Бесконечное мерцание
        anim = Animation(opacity=1.0, duration=uniform(1.5, 2.5)) + \
               Animation(opacity=0.3, duration=uniform(1.5, 2.5))
        anim.repeat = True
        anim.start(self)

class SpaceBackground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stars = []
        self.bind(size=self.on_size)

    def on_size(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Фон (градиент можно сделать через несколько прямоугольников)
            Color(0.05, 0.02, 0.15, 1)
            Ellipse(pos=self.pos, size=self.size)  # или Rectangle
            # Можно добавить туманности...
        self.create_stars()

    def create_stars(self):
        self.clear_widgets()
        self.stars.clear()
        for _ in range(150):
            x = randint(0, int(self.width))
            y = randint(0, int(self.height))
            size = uniform(1.0, 3.5)
            star = Star(x, y, size)
            self.add_widget(star)
            self.stars.append(star)
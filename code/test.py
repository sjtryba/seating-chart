from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.progressbar import ProgressBar
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner

from kivy.lang import Builder

Builder.load_string('''
<Intro>:
    BoxLayout:
        orientation: "vertical"

        BoxLayout:
            size_hint_y: 0.1

            BoxLayout:
                orientation: "vertical"
                size_hint_x: 0.2

                ToggleButton:
                    id: optimize_button
                    text: "Optimize"
                    on_state:
                        if self.state == "down": self.text = "Working..."
                        if self.state == "normal": self.text = "Optimize"

                ProgressBar:
                    id: progress
                    size_hint_y: 0.1

            Label:
                text: ""

            Button:
                id: student_button
                text: 'Students'
                size_hint_x: 0.2
                on_text:
                    if self.text == "New Student": root.manager.transition.direction = 'left'
                    if self.text == "New Student": root.manager.current = 'SecondScreen'
                    if self.text == "New Student": self.text = 'Students'


        FloatLayout:

<SecondScreen>:
    BoxLayout:
        Label:
            text: "working?"
            font_size: '20px'
        Button:
            text: "Back"
            on_press:
                root.parent.new_student()
                root.manager.transition.direction = "right"
                root.manager.current = "Intro"
''')


class TestApp(App):
    def build(self):
        return CustomScreenManager()


class CustomScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super(CustomScreenManager, self).__init__(*args, **kwargs)
        self.intro = Intro(name='Intro')
        self.second_screen = SecondScreen(name='SecondScreen')
        self.add_widget(self.intro)
        self.add_widget(self.second_screen)

    def new_student(self):
        btn = Button(text="Spencer", size_hint_y=None, height=40)
        btn.bind(on_release=lambda btn: self.intro.dropdown.select(btn.text))
        self.intro.dropdown.add_widget(btn)


class Intro(Screen):
    def __init__(self, *args, **kwargs):
        super(Intro, self).__init__(*args, **kwargs)
        self.dropdown = DropDown()
        btn = Button(text="New Student", size_hint_y=None, height=40)
        btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
        self.dropdown.add_widget(btn)
        self.ids.student_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.ids.student_button, 'text', x))


class SecondScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(SecondScreen, self).__init__(*args, **kwargs)

TestApp().run()

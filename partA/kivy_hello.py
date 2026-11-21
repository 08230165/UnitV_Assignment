
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

# Window configuration
Window.size = (450, 320)
Window.clearcolor = (0.96, 0.97, 0.99, 1)


class GreetingApp(App):

    def build(self):
        self.title = "Welcome App | Kivy"

        # Main vertical layout
        layout = BoxLayout(
            orientation="vertical",
            padding=[35, 30, 35, 30],
            spacing=10
        )

        # Heading
        heading = Label(
            text="Welcome!",
            font_size=30,
            bold=True,
            color=(0.12, 0.23, 0.54, 1)
        )

        # Instruction
        instruction = Label(
            text="Press the button to receive a greeting.",
            font_size=15,
            color=(0.28, 0.34, 0.41, 1)
        )

        # Greeting message
        self.message = Label(
            font_size=17,
            color=(0.15, 0.39, 0.92, 1)
        )

        # Action button
        self.greet_button = Button(
            text="Say Hello",
            font_size=16,
            bold=True,
            size_hint=(1, None),
            height=50,
            background_normal="",
            background_color=(0.15, 0.39, 0.92, 1)
        )

        # Bind button event
        self.greet_button.bind(on_press=self.say_hello)

        # Add widgets to layout
        layout.add_widget(heading)
        layout.add_widget(instruction)
        layout.add_widget(self.message)
        layout.add_widget(self.greet_button)

        return layout

    def say_hello(self, instance):
        """Update the greeting when the button is pressed."""
        self.message.text = "Hello! Have a wonderful day."
        instance.text = "Greeted!"


if __name__ == "__main__":
    GreetingApp().run()

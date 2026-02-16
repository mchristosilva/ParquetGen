from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel
from pygments.lexers.sql import SqlLexer
from kivy.clock import Clock

true_type_font = "fonts/consola.ttf"


class SQLTextEditor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", **kwargs)

        self.placeholder = "Digite ou importe uma query SQL..."

        self.text_input = CodeInput(
            lexer=SqlLexer(),
            font_name=true_type_font,
            font_size=9,
            tab_width=4,
            auto_indent=True,
            multiline=True,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0, 0, 1),
            padding=(10, 8, 10, 8),
        )

        self.text_input.bind(text=self._update_placeholder)
        self.text_input.bind(size=self._update_placeholder)
        self.text_input.bind(pos=self._update_placeholder)

        self.add_widget(self.text_input)

        Clock.schedule_once(lambda dt: self._update_placeholder())

    def _update_placeholder(self, *args):
        self.text_input.canvas.after.clear()

        if self.text_input.text.strip():
            return  # tem texto → não desenha placeholder

        with self.text_input.canvas.after:
            Color(0.6, 0.6, 0.6, 0.6)  # cinza suave

            label = CoreLabel(
                text=self.placeholder,
                font_size=self.text_input.font_size,
                font_name=true_type_font,
                color=(0.6, 0.6, 0.6, 0.6)
            )
            label.refresh()

            Rectangle(
                texture=label.texture,
                size=label.texture.size,
                pos=(
                    self.text_input.x + self.text_input.padding[0],
                    self.text_input.y + self.text_input.height -
                    self.text_input.padding[1] - label.texture.size[1]
                )
            )

    # API pública
    def get_text(self):
        return self.text_input.text

    def set_text(self, txt):
        self.text_input.text = txt
        self._update_placeholder()

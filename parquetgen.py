import os
import json
import threading
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from sql_query_editor import SQLTextEditor
from kivy.uix.filechooser import FileChooserIconView
from formatter.main import formatar_sql_de_arquivo
from log import CAMINHO as CAMINHO_PADRAO
from consulta import roda_consulta
from listar_unidades import listar_unidades

true_type_font = "fonts/consola.ttf"


def show_popup(title, message):
    popup = Popup(
        title=title,
        content=Label(text=message),
        size_hint=(0.6, 0.4)
    )
    popup.open()


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.last_output_folder = None

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        with layout.canvas.before:
            Color(0.75, 0.75, 0.75, 1)  # #C0C0C0
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda w, v: setattr(self.bg_rect, "pos", w.pos))
        layout.bind(size=lambda w, v: setattr(self.bg_rect, "size", w.size))

        self.path_label = Label(
            text=f"Pasta padrão: {CAMINHO_PADRAO}",
            size_hint_y=None,
            height=30,
            color=(0, 0, 0, 1)
        )
        layout.add_widget(self.path_label)

        self.folder_input = self.make_input(
            "Subpasta que será criada dentro da pasta padrão (ex: Beira_leito\\2025)")
        layout.add_widget(self.folder_input)

        self.file_input = self.make_input(
            "Nome dos arquivos a serem gerados (log e parquet), sem a extensão")
        layout.add_widget(self.file_input)

        editor_box = BoxLayout(size_hint_y=1)
        self.query_input = SQLTextEditor()
        editor_box.add_widget(self.query_input)
        layout.add_widget(editor_box)

        self.log_output = TextInput(
            text="",
            readonly=True,
            size_hint_y=0.4,
            font_name=true_type_font,
            font_size=12,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 1),
            foreground_color=(0, 1, 0, 1),
            cursor_color=(0, 1, 0, 1),
            disabled_foreground_color=(0, 1, 0, 1),
        )

        self.add_border(self.log_output)
        layout.add_widget(self.log_output)

        self.progress = ProgressBar(
            max=1,
            value=0,
            opacity=0,
            size_hint_y=None,
            height=6
        )
        layout.add_widget(self.progress)

        with self.progress.canvas.before:
            Color(0, 1, 0, 1)
            self._pb_rect = Rectangle(
                pos=self.progress.pos, size=self.progress.size)

        self.progress.bind(pos=lambda w, v: setattr(
            self._pb_rect, "pos", w.pos))
        self.progress.bind(size=lambda w, v: setattr(
            self._pb_rect, "size", w.size))

        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=10)

        self.btn_exec = self.make_button(
            " Executar", self.execute)
        btn_box.add_widget(self.btn_exec)

        self.btn_import = self.make_button(
            "Importar Query", lambda x: self.import_query())
        btn_box.add_widget(self.btn_import)

        self.btn_clear = self.make_button(
            "Limpar", lambda x: self.clear_logs())
        btn_box.add_widget(self.btn_clear)

        self.btn_copy = self.make_button(
            "Copiar Query", lambda x: self.copy_query())
        btn_box.add_widget(self.btn_copy)

        self.btn_open = self.make_button(
            "Abrir Pasta", lambda x: self.open_folder())
        btn_box.add_widget(self.btn_open)

        # Botões começam desabilitados
        self.btn_clear.disabled = True
        self.btn_copy.disabled = True
        self.btn_open.disabled = True

        layout.add_widget(btn_box)

        self.add_widget(layout)

        self.hover_buttons = [
            self.btn_exec,
            self.btn_clear,
            self.btn_copy,
            self.btn_open,
            self.btn_import,
        ]

        Window.bind(mouse_pos=self.on_mouse_pos)

    def import_query(self):
        chooser = FileChooserIconView(filters=["*.sql"])

        box = BoxLayout(orientation="vertical", spacing=5)

        drives_box = BoxLayout(size_hint_y=None, height=40, spacing=5)

        for drive in listar_unidades():
            btn = Button(text=drive, size_hint_x=None, width=70)

            def abrir_drive(instance, caminho=drive):
                chooser.path = caminho

            btn.bind(on_release=abrir_drive)
            drives_box.add_widget(btn)

        box.add_widget(drives_box)

        box.add_widget(chooser)

        btn_load = Button(text="Carregar", size_hint_y=None, height=40)

        def carregar(*_):
            if chooser.selection:
                self._load_sql_file(chooser.selection[0])
                popup.dismiss()

        btn_load.bind(on_release=carregar)
        box.add_widget(btn_load)

        popup = Popup(
            title="Importar Query",
            content=box,
            size_hint=(0.9, 0.9)
        )
        popup.open()

    def _load_sql_file(self, caminho):
        try:
            texto = formatar_sql_de_arquivo(caminho)

            self.query_input.set_text(texto)
            self.add_log(f"Arquivo importado: {caminho}")

        except Exception as e:
            self.add_log(f"Erro ao importar: {e}")

    def make_input(self, hint):
        ti = TextInput(
            hint_text=hint,
            multiline=False,
            size_hint_y=None,
            height=35,
            font_name=true_type_font,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0, 0, 1)
        )
        self.add_border(ti)
        return ti

    def make_button(self, text, callback, icon_path=None):
        btn = Button(
            text=text,
            background_normal="",
            background_color=(0.88, 0.88, 0.88, 1),
            color=(0, 0, 0, 1),
            font_name=true_type_font,
            halign="left",
            valign="middle",
            padding=(28, 10)
        )

        if icon_path:
            with btn.canvas.after:
                btn._icon = Rectangle(
                    source=icon_path,
                    size=(20, 20),
                    pos=(0, 0)
                )

            def update_icon(*args):
                btn._icon.pos = (
                    btn.x + 6,
                    btn.center_y - btn._icon.size[1] / 2
                )

            btn.bind(pos=update_icon, size=update_icon)

        self.add_border(btn)
        btn.bind(on_release=callback)
        return btn

    def add_border(self, widget):
        with widget.canvas.after:
            Color(0, 0, 0, 1)

            widget._top = Rectangle(size=(0, 1), pos=(0, 0))
            widget._bottom = Rectangle(size=(0, 1), pos=(0, 0))
            widget._left = Rectangle(size=(1, 0), pos=(0, 0))
            widget._right = Rectangle(size=(1, 0), pos=(0, 0))

        def update(*args):
            x, y = widget.pos
            w, h = widget.size

            widget._top.pos = (x, y + h - 1)
            widget._top.size = (w, 1)

            widget._bottom.pos = (x, y)
            widget._bottom.size = (w, 1)

            widget._left.pos = (x, y)
            widget._left.size = (1, h)

            widget._right.pos = (x + w - 1, y)
            widget._right.size = (1, h)

        widget.bind(pos=update, size=update)

    def on_mouse_pos(self, window, pos):
        for btn in self.hover_buttons:
            if btn.collide_point(*btn.to_widget(*pos)):
                btn.background_color = (1, 1, 1, 1)
            else:
                btn.background_color = (0.88, 0.88, 0.88, 1)

    def add_log(self, msg):
        self.log_output.text += msg + "\n"
        self.log_output.cursor = (0, len(self.log_output.text))

    def clear_logs(self):
        self.log_output.text = ""

        self.folder_input.text = ""
        self.file_input.text = ""
        self.query_input.set_text("")

        self.log_output.cursor = (0, 0)

        self.btn_exec.disabled = False
        self.btn_import.disabled = False
        self.btn_clear.disabled = True
        self.btn_copy.disabled = True
        self.btn_open.disabled = True

    def copy_query(self):
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(self.query_input.get_text())
        self.add_log("Query copiada.")

    def open_folder(self):
        if not self.last_output_folder:
            show_popup("Aviso", "Nenhum arquivo gerado ainda.")
            return
        subprocess.Popen(f'explorer "{self.last_output_folder}"')

    def lock_ui(self):
        self.btn_exec.disabled = True

    def unlock_ui(self):
        self.btn_exec.disabled = False

    def start_progress(self):
        self.progress.value = 0
        self.progress.opacity = 1

    def stop_progress(self):
        self.progress.value = 1
        self.progress.opacity = 0

    def enable_post_exec_buttons(self):
        self.btn_exec.disabled = True
        self.btn_import.disabled = True
        self.btn_clear.disabled = False
        self.btn_copy.disabled = False
        self.btn_open.disabled = False

    def execute(self, instance):
        folder = self.folder_input.text.strip()
        file_name = self.file_input.text.strip()
        query = self.query_input.get_text().strip()

        if not file_name or not folder or not query:
            show_popup("Erro", "Preencha todos os campos.")
            return

        if not query.lower().startswith("select"):
            show_popup("Erro", "Somente SELECT é permitido.")
            return

        caminho_relativo = os.path.join(folder, file_name + ".parquet")

        self.lock_ui()
        self.start_progress()
        self.add_log("Iniciando execução...")

        threading.Thread(
            target=self.run_query_thread,
            args=(query, caminho_relativo),
            daemon=True
        ).start()

    def run_query_thread(self, query, caminho_relativo):
        try:
            resultado = roda_consulta(query, caminho_relativo)

            # Se houve erro de sintaxe ou comando proibido
            if resultado is None or "erro" in resultado:
                Clock.schedule_once(lambda dt: self.add_log(
                    resultado.get("erro", "Falha na consulta.")
                ))
                return

            # Se a sintaxe foi validada, mostrar no log da interface
            if resultado.get("sintaxe_valida"):
                Clock.schedule_once(lambda dt: self.add_log("Sintaxe válida."))

            self.last_output_folder = os.path.dirname(resultado["parquet"])

            Clock.schedule_once(
                lambda dt: self.add_log("Consulta finalizada.")
            )

            Clock.schedule_once(lambda dt: self.save_history(
                query,
                resultado["parquet"],
                resultado["log"]
            ))

            Clock.schedule_once(lambda dt: show_popup(
                "Sucesso",
                f"Arquivo gerado:\n{resultado['parquet']}"
            ))

            Clock.schedule_once(lambda dt: self.enable_post_exec_buttons())

        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_log(f"Erro: {str(e)}"))
            Clock.schedule_once(lambda dt: show_popup("Erro", str(e)))

        finally:
            self.unlock_ui()
            Clock.schedule_once(lambda dt: self.stop_progress())

    def save_history(self, query, parquet_path, log_path):
        hist_file = "historico.json"

        # Carrega histórico existente
        if os.path.exists(hist_file):
            with open(hist_file, "r", encoding="utf-8") as f:
                hist = json.load(f)
        else:
            hist = []

        # Adiciona novo registro
        hist.append({
            "query": query.strip(),        # query real
            "arquivo": parquet_path,       # caminho do parquet
            "log": log_path                # caminho do log
        })

        # Salva JSON com barras normais
        with open(hist_file, "w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2, ensure_ascii=False)


class MyApp(App):

    title = "RedeSC - Gerador de arquivos Parquet"
    icon = "img/icon.png"

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main_screen"))
        return sm


if __name__ == "__main__":
    MyApp().run()

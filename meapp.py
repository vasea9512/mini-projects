import tkinter as tk
from tkinter import filedialog
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
import re

# -----------------------------
#  Топ‑100 слов для автодополнения
# -----------------------------
PY_COMMON_WORDS = [
    "def", "class", "return", "import", "from", "as", "if", "elif", "else",
    "for", "while", "break", "continue", "try", "except", "finally", "with",
    "lambda", "yield", "global", "nonlocal", "assert", "pass", "raise",
    "in", "is", "not", "and", "or", "True", "False", "None",

    "print", "len", "range", "open", "input", "type", "dir", "id", "sum",
    "min", "max", "abs", "round", "sorted", "map", "filter", "zip",
    "enumerate", "isinstance", "issubclass", "all", "any",

    "int", "float", "str", "list", "dict", "set", "tuple", "bool", "bytes",

    "split", "join", "replace", "lower", "upper", "strip", "startswith",
    "endswith", "format",

    "append", "extend", "insert", "pop", "remove", "clear", "sort", "reverse",

    "keys", "values", "items", "get", "update",

    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
    "ImportError", "RuntimeError", "AttributeError",

    "os", "sys", "math", "random", "json", "time", "datetime", "re",

    "self", "__init__", "__str__", "__repr__", "__name__", "__main__"
]

# -----------------------------
#  Класс автодополнения
# -----------------------------
class AutoComplete:
    def __init__(self, text_widget):
        self.text = text_widget
        self.listbox = None
        self.words = PY_COMMON_WORDS

        self.text.bind("<KeyRelease>", self.on_key_release, add="+")
        self.text.bind("<Button-1>", lambda e: self.hide_listbox(), add="+")
        self.text.bind("<Return>", self.on_enter, add="+")
        self.text.bind("<Tab>", self.on_tab, add="+")

    def on_enter(self, event):
        if self.listbox:
            self.insert_selection()
            return "break"  # Блокируем перенос строки

    def on_tab(self, event):
        if self.listbox:
            self.insert_selection()
            return "break"  # Блокируем табуляцию

    def on_key_release(self, event):
        if event.keysym in ("Up", "Down"):
            return

        if event.keysym in ("Return", "Tab"):
            return "break"

        word = self.get_current_word()
        if not word:
            self.hide_listbox()
            return

        matches = [w for w in self.words if w.startswith(word)]
        if matches:
            self.show_listbox(matches)
        else:
            self.hide_listbox()

    def get_current_word(self):
        pos = self.text.index("insert")
        line = self.text.get(f"{pos} linestart", pos)
        word = ""
        for ch in reversed(line):
            if ch.isalnum() or ch == "_":
                word = ch + word
            else:
                break
        return word

    def show_listbox(self, matches):
        if self.listbox:
            self.listbox.destroy()

        bbox = self.text.bbox("insert")
        if not bbox:
            return

        x, y, width, height = bbox
        x += self.text.winfo_rootx()
        y += self.text.winfo_rooty() + height

        self.listbox = tk.Listbox(
            height=min(6, len(matches)),
            bg="#2d2d2d",
            fg="white",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#555555"
        )
        self.listbox.place(x=x, y=y)

        for m in matches:
            self.listbox.insert(tk.END, m)

        self.listbox.select_set(0)
        self.listbox.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.insert_selection()
        return "break"

    def hide_listbox(self):
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None

    def insert_selection(self):
        if not self.listbox:
            return

        word = self.listbox.get(tk.ACTIVE)
        cur = self.text.index("insert")

        w = self.get_current_word()
        self.text.delete(f"{cur} - {len(w)}c", cur)

        self.text.insert("insert", word)
        self.hide_listbox()


# -----------------------------
#  Основное окно редактора
# -----------------------------
root = tk.Tk()
root.title("Dark Python Editor")
root.geometry("900x600")

BG = "#1e1e1e"
FG = "#ffffff"

text = tk.Text(
    root,
    bg=BG,
    fg=FG,
    insertbackground="white",
    font=("Consolas", 12),
    undo=True
)
text.pack(fill="both", expand=True)

# -----------------------------
#  Подсветка синтаксиса
# -----------------------------
style = get_style_by_name("monokai")

for token, style_def in style.styles.items():
    if not style_def:
        continue

    match = re.search(r"#([0-9a-fA-F]{6})", style_def)
    if not match:
        continue

    color = match.group(0)
    if color.startswith("##"):
        color = "#" + color[2:]

    text.tag_configure(str(token), foreground=color)

def highlight(event=None):
    code = text.get("1.0", tk.END)
    text.mark_set("range_start", "1.0")

    for tag in text.tag_names():
        if tag.startswith("Token."):
            text.tag_remove(tag, "1.0", tk.END)

    for token, content in lex(code, PythonLexer()):
        if content == "\n":
            text.mark_set("range_start", "range_start + 1c")
            continue
        text.mark_set("range_end", f"range_start + {len(content)}c")
        text.tag_add(str(token), "range_start", "range_end")
        text.mark_set("range_start", "range_end")

text.bind("<KeyRelease>", highlight, add="+")

# -----------------------------
#  Открытие и сохранение файлов
# -----------------------------
def open_file():
    path = filedialog.askopenfilename()
    if not path:
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    text.delete("1.0", tk.END)
    text.insert("1.0", content)
    highlight()

def save_file():
    path = filedialog.asksaveasfilename(defaultextension=".py")
    if not path:
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.get("1.0", tk.END))

menu = tk.Menu(root)
file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
menu.add_cascade(label="File", menu=file_menu)
root.config(menu=menu)

autocomplete = AutoComplete(text)

root.mainloop()

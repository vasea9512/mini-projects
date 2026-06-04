import tkinter as tk
from tkinter import filedialog
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
import re
import inspect
import builtins
import os, sys, json, math, random, time, datetime, re as re_mod

# -----------------------------
#  СЛОВА ДЛЯ АВТОДОПОЛНЕНИЯ
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

MODULE_WORDS = (
    dir(os) + dir(sys) + dir(json) + dir(math) +
    dir(random) + dir(time) + dir(datetime) + dir(re_mod)
)
PY_COMMON_WORDS += [w for w in MODULE_WORDS if w.isidentifier()]
PY_COMMON_WORDS += [w for w in dir(builtins) if w.isidentifier()]

PY_COMMON_WORDS = sorted(set(PY_COMMON_WORDS))


# -----------------------------
#  НУМЕРАЦИЯ СТРОК
# -----------------------------
class LineNumbers(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=40, bg="#1e1e1e", highlightthickness=0, **kwargs)
        self.text = text_widget
        self.text.bind("<KeyRelease>", self.redraw, add="+")
        self.text.bind("<MouseWheel>", self.redraw, add="+")
        self.text.bind("<Button-1>", self.redraw, add="+")
        self.text.bind("<Configure>", self.redraw, add="+")
        self.redraw()

    def redraw(self, event=None):
        self.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(35, y, anchor="ne", text=linenum,
                             fill="#555555", font=("Consolas", 11))
            i = self.text.index(f"{i}+1line")


# -----------------------------
#  МИНИ-КАРТА КОДА
# -----------------------------
class CodeMinimap(tk.Text):
    def __init__(self, master, source_text, **kwargs):
        super().__init__(master, width=20, bg="#111111", fg="#777777",
                         font=("Consolas", 6), state="disabled",
                         highlightthickness=0, **kwargs)
        self.source = source_text
        self.source.bind("<KeyRelease>", self.update_map, add="+")
        self.source.bind("<MouseWheel>", self.update_map, add="+")
        self.source.bind("<Configure>", self.update_map, add="+")
        self.update_map()

    def update_map(self, event=None):
        self.config(state="normal")
        self.delete("1.0", tk.END)
        content = self.source.get("1.0", tk.END)
        self.insert("1.0", content)
        self.config(state="disabled")


# -----------------------------
#  ПОПАП ПОДПИСИ ФУНКЦИИ
# -----------------------------
class SignaturePopup(tk.Toplevel):
    def __init__(self, master, text, func):
        super().__init__(master)
        self.overrideredirect(True)
        self.config(bg="#222222")
        try:
            sig = str(inspect.signature(func))
        except Exception:
            sig = "()"
        label = tk.Label(self, text=f"{func.__name__}{sig}",
                         bg="#222222", fg="#00ff99", font=("Consolas", 10))
        label.pack()
        bbox = text.bbox("insert")
        if bbox:
            x, y, _, h = bbox
            x += text.winfo_rootx()
            y += text.winfo_rooty() + h
            self.geometry(f"+{x}+{y}")
        else:
            self.geometry("+100+100")


# -----------------------------
#  АВТОДОПОЛНЕНИЕ
# -----------------------------
class AutoComplete:
    def __init__(self, text_widget):
        self.text = text_widget
        self.listbox = None
        self.words = PY_COMMON_WORDS
        self.sig_popup = None

        self.text.bind("<KeyRelease>", self.on_key_release, add="+")
        self.text.bind("<Button-1>", lambda e: self.hide_listbox(), add="+")
        self.text.bind("<Return>", self.on_enter, add="+")
        self.text.bind("<Tab>", self.on_tab, add="+")
        self.text.bind("(", self.on_open_paren, add="+")

    def on_open_paren(self, event):
        self.text.insert("insert", ")")
        self.text.mark_set("insert", "insert-1c")
        self.show_signature()
        return "break"

    def show_signature(self):
        word = self.get_current_word()
        func = None

        if word in globals():
            obj = globals()[word]
            if callable(obj):
                func = obj
        elif hasattr(builtins, word):
            obj = getattr(builtins, word)
            if callable(obj):
                func = obj

        if func:
            if self.sig_popup:
                self.sig_popup.destroy()
            self.sig_popup = SignaturePopup(self.text.master, self.text, func)

    def on_enter(self, event):
        if self.listbox:
            self.insert_selection()
            return "break"

    def on_tab(self, event):
        if self.listbox:
            self.insert_selection()
            return "break"

    def on_key_release(self, event):
        if event.keysym in ("Up", "Down", "Return", "Tab"):
            return

        if event.keysym == "BackSpace":
            if self.sig_popup:
                self.sig_popup.destroy()
                self.sig_popup = None

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
            height=min(8, len(matches)),
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
#  УПРОЩЕНИЕ СИНТАКСИСА
# -----------------------------
def on_colon(event, text):
    pos = text.index("insert")
    text.insert(pos, ":")
    text.insert(f"{pos} + 1c", "\n    ")
    return "break"

def on_quote(event, text, char):
    text.insert("insert", char + char)
    text.mark_set("insert", "insert-1c")
    return "break"

def on_backspace(event, text):
    pos = text.index("insert")
    line_start = text.index(f"{pos} linestart")
    before = text.get(line_start, pos)
    if before.endswith("    "):
        text.delete(f"{pos} - 4c", pos)
        return "break"


# -----------------------------
#  ОСНОВНОЕ ОКНО
# -----------------------------
root = tk.Tk()
root.title("Python Mini IDE")
root.geometry("1100x700")

BG = "#1e1e1e"
FG = "#ffffff"

main_frame = tk.Frame(root, bg=BG)
main_frame.pack(fill="both", expand=True)

text = tk.Text(
    main_frame,
    bg=BG,
    fg=FG,
    insertbackground="white",
    font=("Consolas", 12),
    undo=True
)

line_numbers = LineNumbers(main_frame, text)
line_numbers.pack(side="left", fill="y")

text.pack(side="left", fill="both", expand=True)

minimap = CodeMinimap(main_frame, text)
minimap.pack(side="right", fill="y")

# -----------------------------
#  ПОДСВЕТКА СИНТАКСИСА
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
#  ОТКРЫТИЕ / СОХРАНЕНИЕ
# -----------------------------
def open_file():
    path = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
    if not path:
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    text.delete("1.0", tk.END)
    text.insert("1.0", content)
    highlight()

def save_file():
    path = filedialog.asksaveasfilename(defaultextension=".py",
                                        filetypes=[("Python files", "*.py"), ("All files", "*.*")])
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

# -----------------------------
#  ПОДКЛЮЧАЕМ АВТОДОПОЛНЕНИЕ И СИНТАКС-ПОМОЩЬ
# -----------------------------
autocomplete = AutoComplete(text)

text.bind(":", lambda e: on_colon(e, text), add="+")
text.bind('"', lambda e: on_quote(e, text, '"'), add="+")
text.bind("'", lambda e: on_quote(e, text, "'"), add="+")
text.bind("<BackSpace>", lambda e: on_backspace(e, text), add="+")

root.mainloop()

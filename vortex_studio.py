#!/usr/bin/env python3
"""
===============================================================================
VORTEX STUDIO - Visual Studio Style IDE for Vortex3D
- Visual Studio Theme & Layout (Activity Bar, Explorer, Tabs, Breadcrumbs, Terminal)
- Automatic Windows System Light / Dark Theme Detection
- On-the-fly Light / Dark Mode Toggle
- Full Vortex3D Syntax Highlighting, Line Numbers & Auto-indentation
- Integrated 1-Click Native Compilation (F6) & Playtesting (F5)
===============================================================================
"""

import sys
import os
import re
import subprocess
import threading
import winreg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

COMPILER_SCRIPT = os.path.join(SCRIPT_DIR, "vortex.py")

# Visual Studio Themes Definition
THEMES = {
    "dark": {
        "bg_editor": "#1e1e1e",
        "fg_editor": "#d4d4d4",
        "bg_sidebar": "#252526",
        "fg_sidebar": "#cccccc",
        "bg_activity": "#333333",
        "fg_activity": "#ffffff",
        "bg_tab_active": "#1e1e1e",
        "fg_tab_active": "#ffffff",
        "bg_tab_inactive": "#2d2d2d",
        "fg_tab_inactive": "#969696",
        "bg_breadcrumbs": "#1e1e1e",
        "fg_breadcrumbs": "#a6a6a6",
        "bg_terminal": "#181818",
        "fg_terminal": "#cccccc",
        "bg_statusbar": "#007acc",
        "fg_statusbar": "#ffffff",
        "bg_toolbar": "#2d2d2d",
        "fg_toolbar": "#cccccc",
        "bg_lineno": "#1e1e1e",
        "fg_lineno": "#858585",
        "accent": "#007acc",
        "border": "#3f3f46",
        "select_bg": "#264f78",
        # Syntax Colors (VS Dark)
        "syntax_keyword": "#569cd6",
        "syntax_event": "#dcdcaa",
        "syntax_engine": "#4ec9b0",
        "syntax_type": "#4ec9b0",
        "syntax_string": "#ce9178",
        "syntax_number": "#b5cea8",
        "syntax_comment": "#6a9955",
        "btn_run": "#388a34",
        "btn_build": "#0e639c",
    },
    "light": {
        "bg_editor": "#ffffff",
        "fg_editor": "#000000",
        "bg_sidebar": "#f3f3f3",
        "fg_sidebar": "#333333",
        "bg_activity": "#2c2c2c",
        "fg_activity": "#ffffff",
        "bg_tab_active": "#ffffff",
        "fg_tab_active": "#333333",
        "bg_tab_inactive": "#ececec",
        "fg_tab_inactive": "#717171",
        "bg_breadcrumbs": "#f8f8f8",
        "fg_breadcrumbs": "#616161",
        "bg_terminal": "#f8f9fa",
        "fg_terminal": "#212529",
        "bg_statusbar": "#007acc",
        "fg_statusbar": "#ffffff",
        "bg_toolbar": "#f3f3f3",
        "fg_toolbar": "#333333",
        "bg_lineno": "#ffffff",
        "fg_lineno": "#a0a0a0",
        "accent": "#007acc",
        "border": "#e5e5e5",
        "select_bg": "#add6ff",
        # Syntax Colors (VS Light)
        "syntax_keyword": "#0000ff",
        "syntax_event": "#795e26",
        "syntax_engine": "#267f99",
        "syntax_type": "#267f99",
        "syntax_string": "#a31515",
        "syntax_number": "#098658",
        "syntax_comment": "#008000",
        "btn_run": "#237804",
        "btn_build": "#005a9e",
    }
}

def detect_windows_system_theme():
    """Detects whether Windows is currently in Dark or Light mode via registry."""
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return "light" if val == 1 else "dark"
    except Exception:
        return "dark"

DEFAULT_CODE = """# ============================================================================
# GAME: NEON BREACH - SCI-FI ARENA 3D
# LANGUAGE: Vortex3D (Pythonic Easy Mode)
# ============================================================================

environment:
    volumetric_fog: true
    fog_color: color.rgb(0.04, 0.05, 0.09)
    bloom: true
    pbr: true

player_speed = 14.0
jump_force = 11.0
player_health = 100.0
score = 0.0
game_over = false

mat_player = material:
    albedo: color.rgb(0.10, 0.90, 0.70)
    metallic: 0.85

player = mesh.create_cube(mat_player)

on_start:
    player.position = vec3(0.0, 1.5, 0.0)
    player.tag = "player"
    rigidbody.attach(player):
        gravity: true
        mass: 1.0

on_update(dt):
    if is_key_down("W"):
        player.position.z -= player_speed * dt
    if is_key_down("S"):
        player.position.z += player_speed * dt
    if is_key_down("A"):
        player.position.x -= player_speed * dt
    if is_key_down("D"):
        player.position.x += player_speed * dt

    if is_key_pressed("SPACE") and player.is_grounded:
        player.velocity.y = jump_force

    main_cam.follow(player.position)
    hud.set_health(player_health)
    hud.set_score(score)
"""

class VortexStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visual Studio - Vortex3D Studio")
        self.geometry("1280x820")
        self.minsize(960, 600)

        # Detect System Theme (Dark or Light)
        self.current_theme = detect_windows_system_theme()
        self.current_filepath = None
        self.is_dirty = False

        self.setup_ui()
        self.apply_theme()
        self.bind_events()

        # Load initial sample code (Vortex Block 3D Sandbox)
        sample_path = os.path.join(SCRIPT_DIR, "games", "vortex_block.vx")
        if not os.path.exists(sample_path):
            sample_path = os.path.join(SCRIPT_DIR, "games", "sci_fi_arena_pythonic.vx")
        if os.path.exists(sample_path):
            self.load_file(sample_path)
        else:
            self.editor.insert("1.0", DEFAULT_CODE)
            self.update_line_numbers()
            self.highlight_syntax()

    def setup_ui(self):
        # 1. Top Menu Bar (Visual Studio Style)
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New File", accelerator="Ctrl+N", command=self.action_new)
        file_menu.add_command(label="Open File...", accelerator="Ctrl+O", command=self.action_open)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.action_save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        build_menu = tk.Menu(menubar, tearoff=0)
        build_menu.add_command(label="Run Game", accelerator="F5", command=self.action_run)
        build_menu.add_command(label="Build .EXE", accelerator="F6", command=self.action_compile)
        build_menu.add_command(label="Check Syntax", accelerator="F7", command=self.action_check)
        menubar.add_cascade(label="Run & Build", menu=build_menu)

        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label="Use System Theme", command=self.set_system_theme)
        theme_menu.add_command(label="Dark Theme", command=lambda: self.switch_theme("dark"))
        theme_menu.add_command(label="Light Theme", command=lambda: self.switch_theme("light"))
        menubar.add_cascade(label="Themes", menu=theme_menu)

        # 2. Main Horizontal Container
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 2A. Activity Bar (Leftmost vertical ribbon)
        self.activity_bar = tk.Frame(self.main_container, width=48)
        self.activity_bar.pack(side=tk.LEFT, fill=tk.Y)
        self.activity_bar.pack_propagate(False)

        self.btn_act_files = tk.Button(self.activity_bar, text="📁", font=("Segoe UI", 14), bd=0, relief="flat", command=self.toggle_sidebar)
        self.btn_act_files.pack(fill=tk.X, pady=(10, 4))

        self.btn_act_run = tk.Button(self.activity_bar, text="▶", font=("Segoe UI", 12, "bold"), bd=0, relief="flat", command=self.action_run)
        self.btn_act_run.pack(fill=tk.X, pady=4)

        self.btn_act_theme = tk.Button(self.activity_bar, text="🌓", font=("Segoe UI", 12), bd=0, relief="flat", command=self.toggle_theme)
        self.btn_act_theme.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # 2B. Explorer Sidebar
        self.sidebar = tk.Frame(self.main_container, width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.lbl_explorer = tk.Label(self.sidebar, text="  EXPLORER: VORTEX3D", font=("Segoe UI", 8, "bold"), anchor="w", pady=8)
        self.lbl_explorer.pack(fill=tk.X)

        self.listbox_files = tk.Listbox(self.sidebar, bd=0, highlightthickness=0, font=("Segoe UI", 9), selectmode=tk.SINGLE)
        self.listbox_files.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.listbox_files.bind("<<ListboxSelect>>", self.on_select_project_file)
        self.refresh_file_list()

        # 2C. Center Work Area
        self.center_area = tk.Frame(self.main_container)
        self.center_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Top Fast Action Ribbon / Toolbar
        self.toolbar = tk.Frame(self.center_area, height=36)
        self.toolbar.pack(fill=tk.X)

        self.btn_tb_run = tk.Button(self.toolbar, text="▶ Run (F5)", font=("Segoe UI", 9, "bold"), bd=0, padx=14, pady=4, command=self.action_run)
        self.btn_tb_run.pack(side=tk.LEFT, padx=(8, 4), pady=4)

        self.btn_tb_build = tk.Button(self.toolbar, text="⚙ Build .exe (F6)", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=4, command=self.action_compile)
        self.btn_tb_build.pack(side=tk.LEFT, padx=4, pady=4)

        self.btn_tb_check = tk.Button(self.toolbar, text="✓ Check (F7)", font=("Segoe UI", 9), bd=0, padx=10, pady=4, command=self.action_check)
        self.btn_tb_check.pack(side=tk.LEFT, padx=4, pady=4)

        self.var_release = tk.BooleanVar(value=True)
        self.chk_release = tk.Checkbutton(self.toolbar, text="Release (-O3)", variable=self.var_release, bd=0)
        self.chk_release.pack(side=tk.RIGHT, padx=10)

        self.lbl_fps = tk.Label(self.toolbar, text="FPS Cap:", font=("Segoe UI", 9))
        self.lbl_fps.pack(side=tk.RIGHT, padx=4)

        self.combo_fps = ttk.Combobox(self.toolbar, values=["60", "120", "144", "240"], width=5)
        self.combo_fps.set("120")
        self.combo_fps.pack(side=tk.RIGHT, padx=6)

        # Tab Strip (Visual Studio Style Active Tab)
        self.tab_strip = tk.Frame(self.center_area, height=30)
        self.tab_strip.pack(fill=tk.X)

        self.active_tab = tk.Label(self.tab_strip, text=" sci_fi_arena_pythonic.vx  ✕ ", font=("Segoe UI", 9), padx=12, pady=4)
        self.active_tab.pack(side=tk.LEFT)

        # Breadcrumbs bar
        self.breadcrumbs = tk.Label(self.center_area, text=" games  >  sci_fi_arena_pythonic.vx  >  on_update(dt)", font=("Segoe UI", 8), anchor="w", padx=10, pady=2)
        self.breadcrumbs.pack(fill=tk.X)

        # Main Paned Editor & Terminal
        self.paned = tk.PanedWindow(self.center_area, orient=tk.VERTICAL, sashwidth=4, bd=0)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Editor Frame
        self.editor_frame = tk.Frame(self.paned)
        self.paned.add(self.editor_frame, minsize=300)

        self.line_numbers = tk.Text(self.editor_frame, width=4, bd=0, highlightthickness=0, font=("Consolas", 11), state="disabled", cursor="arrow")
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.editor = tk.Text(self.editor_frame, bd=0, highlightthickness=0, font=("Consolas", 11), undo=True, wrap="none")
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_y = tk.Scrollbar(self.editor_frame, command=self.on_scroll_y)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=self.scroll_y.set)

        # Bottom Panel (VS Terminal / Output)
        self.terminal_frame = tk.Frame(self.paned, height=180)
        self.paned.add(self.terminal_frame, minsize=120)

        self.term_header = tk.Frame(self.terminal_frame, height=26)
        self.term_header.pack(fill=tk.X)

        self.lbl_term_title = tk.Label(self.term_header, text="  TERMINAL: BUILD & EXECUTION", font=("Segoe UI", 8, "bold"))
        self.lbl_term_title.pack(side=tk.LEFT, pady=2)

        self.btn_clear_term = tk.Button(self.term_header, text="Clear", font=("Segoe UI", 8), bd=0, padx=6, command=self.clear_console)
        self.btn_clear_term.pack(side=tk.RIGHT, padx=6, pady=2)

        self.terminal = tk.Text(self.terminal_frame, bd=0, highlightthickness=0, font=("Consolas", 9), wrap="word")
        self.terminal.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 3. Bottom Visual Studio Status Bar (Blue Bar)
        self.statusbar = tk.Frame(self, height=24)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status_left = tk.Label(self.statusbar, text="  ✓ Vortex3D: Ready", font=("Segoe UI", 8, "bold"))
        self.lbl_status_left.pack(side=tk.LEFT, pady=2)

        self.btn_theme_indicator = tk.Button(self.statusbar, text=f"Theme: {self.current_theme.upper()}", font=("Segoe UI", 8), bd=0, command=self.toggle_theme)
        self.btn_theme_indicator.pack(side=tk.RIGHT, padx=8)

        self.lbl_status_lang = tk.Label(self.statusbar, text="Vortex3D (Pythonic)", font=("Segoe UI", 8))
        self.lbl_status_lang.pack(side=tk.RIGHT, padx=8)

        self.lbl_status_enc = tk.Label(self.statusbar, text="UTF-8", font=("Segoe UI", 8))
        self.lbl_status_enc.pack(side=tk.RIGHT, padx=8)

        self.lbl_status_pos = tk.Label(self.statusbar, text="Ln 1, Col 1", font=("Segoe UI", 8))
        self.lbl_status_pos.pack(side=tk.RIGHT, padx=8)

    def apply_theme(self):
        t = THEMES[self.current_theme]
        self.configure(bg=t["bg_editor"])

        # Activity Bar
        self.activity_bar.config(bg=t["bg_activity"])
        for btn in [self.btn_act_files, self.btn_act_run, self.btn_act_theme]:
            btn.config(bg=t["bg_activity"], fg=t["fg_activity"], activebackground=t["bg_sidebar"], activeforeground=t["fg_activity"])

        # Sidebar
        self.sidebar.config(bg=t["bg_sidebar"])
        self.lbl_explorer.config(bg=t["bg_sidebar"], fg=t["fg_sidebar"])
        self.listbox_files.config(bg=t["bg_sidebar"], fg=t["fg_sidebar"], selectbackground=t["accent"], selectforeground="#ffffff")

        # Toolbar
        self.toolbar.config(bg=t["bg_toolbar"])
        self.btn_tb_run.config(bg=t["btn_run"], fg="#ffffff", activebackground="#2ea043")
        self.btn_tb_build.config(bg=t["btn_build"], fg="#ffffff", activebackground="#007acc")
        self.btn_tb_check.config(bg=t["bg_sidebar"], fg=t["fg_sidebar"])
        self.chk_release.config(bg=t["bg_toolbar"], fg=t["fg_toolbar"], selectcolor=t["bg_sidebar"], activebackground=t["bg_toolbar"])
        self.lbl_fps.config(bg=t["bg_toolbar"], fg=t["fg_toolbar"])

        # Tab Strip & Breadcrumbs
        self.tab_strip.config(bg=t["bg_tab_inactive"])
        self.active_tab.config(bg=t["bg_tab_active"], fg=t["fg_tab_active"])
        self.breadcrumbs.config(bg=t["bg_breadcrumbs"], fg=t["fg_breadcrumbs"])

        # Editor & Line Numbers
        self.line_numbers.config(bg=t["bg_lineno"], fg=t["fg_lineno"])
        self.editor.config(bg=t["bg_editor"], fg=t["fg_editor"], insertbackground=t["fg_editor"], selectbackground=t["select_bg"])

        # Terminal
        self.terminal_frame.config(bg=t["bg_terminal"])
        self.term_header.config(bg=t["bg_tab_inactive"])
        self.lbl_term_title.config(bg=t["bg_tab_inactive"], fg=t["fg_sidebar"])
        self.btn_clear_term.config(bg=t["bg_sidebar"], fg=t["fg_sidebar"])
        self.terminal.config(bg=t["bg_terminal"], fg=t["fg_terminal"], insertbackground=t["fg_terminal"])

        # Status Bar
        self.statusbar.config(bg=t["bg_statusbar"])
        self.lbl_status_left.config(bg=t["bg_statusbar"], fg=t["fg_statusbar"])
        self.lbl_status_pos.config(bg=t["bg_statusbar"], fg=t["fg_statusbar"])
        self.lbl_status_enc.config(bg=t["bg_statusbar"], fg=t["fg_statusbar"])
        self.lbl_status_lang.config(bg=t["bg_statusbar"], fg=t["fg_statusbar"])
        self.btn_theme_indicator.config(bg=t["bg_statusbar"], fg=t["fg_statusbar"], text=f"Theme: {self.current_theme.upper()}")

        # Update syntax tags
        self.editor.tag_configure("keyword", foreground=t["syntax_keyword"], font=("Consolas", 11, "bold"))
        self.editor.tag_configure("event_hook", foreground=t["syntax_event"], font=("Consolas", 11, "bold"))
        self.editor.tag_configure("engine_obj", foreground=t["syntax_engine"], font=("Consolas", 11, "bold"))
        self.editor.tag_configure("math_type", foreground=t["syntax_type"])
        self.editor.tag_configure("string", foreground=t["syntax_string"])
        self.editor.tag_configure("number", foreground=t["syntax_number"])
        self.editor.tag_configure("comment", foreground=t["syntax_comment"], font=("Consolas", 11, "italic"))

        self.highlight_syntax()

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()

    def switch_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme()

    def set_system_theme(self):
        self.current_theme = detect_windows_system_theme()
        self.apply_theme()

    def toggle_sidebar(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y, after=self.activity_bar)

    def on_scroll_y(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def bind_events(self):
        self.editor.bind("<KeyRelease>", self.on_key_release)
        self.editor.bind("<Return>", self.on_return_key)
        self.bind("<Control-s>", lambda e: self.action_save())
        self.bind("<Control-n>", lambda e: self.action_new())
        self.bind("<Control-o>", lambda e: self.action_open())
        self.bind("<F5>", lambda e: self.action_run())
        self.bind("<F6>", lambda e: self.action_compile())
        self.bind("<F7>", lambda e: self.action_check())

    def on_key_release(self, event=None):
        self.update_line_numbers()
        self.highlight_syntax()
        self.update_cursor_info()

    def update_cursor_info(self):
        idx = self.editor.index(tk.INSERT)
        row, col = idx.split('.')
        self.lbl_status_pos.config(text=f"Ln {row}, Col {int(col) + 1}")

    def on_return_key(self, event):
        idx = self.editor.index(tk.INSERT)
        line_num = int(idx.split('.')[0])
        prev_line = self.editor.get(f"{line_num}.0", f"{line_num}.end")
        indent = len(prev_line) - len(prev_line.lstrip())
        extra = 4 if prev_line.strip().endswith(":") or prev_line.strip().endswith("{") else 0
        self.editor.insert(tk.INSERT, "\n" + " " * (indent + extra))
        self.update_line_numbers()
        self.update_cursor_info()
        return "break"

    def update_line_numbers(self):
        count = int(self.editor.index('end-1c').split('.')[0])
        lines = "\n".join(str(i) for i in range(1, count + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", lines)
        self.line_numbers.config(state="disabled")

    def highlight_syntax(self):
        text = self.editor.get("1.0", tk.END)
        for tag in ["keyword", "event_hook", "engine_obj", "math_type", "string", "number", "comment"]:
            self.editor.tag_remove(tag, "1.0", tk.END)

        keywords = [r'\bif\b', r'\belse\b', r'\brepeat\b', r'\btimes\b', r'\bevery\b', r'\bseconds\b',
                    r'\bfor\b', r'\beach\b', r'\bin\b', r'\btrue\b', r'\bfalse\b', r'\band\b', r'\bor\b',
                    r'\bnot\b', r'\bdef\b', r'\bfunction\b', r'\breturn\b', r'\benvironment\b']
        events = [r'\bon_start\b', r'\bon_update\b', r'\bon_collision\b', r'\bon_key_press\b', r'\bon_mouse_click\b']
        engine_objs = [r'\bmesh\b', r'\bcamera\b', r'\blight\b', r'\bmaterial\b', r'\brigidbody\b', r'\bparticle_emitter\b', r'\bhud\b', r'\bsound3d\b']
        math_types = [r'\bvec3\b', r'\bcolor\b', r'\btransform\b', r'\bnumber\b', r'\btext\b', r'\bboolean\b']

        for kw in keywords:
            for match in re.finditer(kw, text):
                self.editor.tag_add("keyword", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for ev in events:
            for match in re.finditer(ev, text):
                self.editor.tag_add("event_hook", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for eng in engine_objs:
            for match in re.finditer(eng, text):
                self.editor.tag_add("engine_obj", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for mt in math_types:
            for match in re.finditer(mt, text):
                self.editor.tag_add("math_type", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(r'"[^"\\]*(\\.[^"\\]*)*"', text):
            self.editor.tag_add("string", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(r'\b\d+(\.\d+)?\b', text):
            self.editor.tag_add("number", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(r'(//|#).*', text):
            self.editor.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def log(self, text):
        self.terminal.insert(tk.END, text + "\n")
        self.terminal.see(tk.END)

    def clear_console(self):
        self.terminal.delete("1.0", tk.END)

    def action_new(self):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", DEFAULT_CODE)
        self.current_filepath = None
        self.active_tab.config(text=" Untitled.vx  ✕ ")
        self.breadcrumbs.config(text=" workspace  >  Untitled.vx")
        self.update_line_numbers()
        self.highlight_syntax()

    def action_open(self):
        fp = filedialog.askopenfilename(filetypes=[("Vortex3D Files", "*.vx"), ("All Files", "*.*")])
        if fp:
            self.load_file(fp)

    def load_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", code)
            self.current_filepath = filepath
            fname = os.path.basename(filepath)
            self.active_tab.config(text=f" {fname}  ✕ ")
            self.breadcrumbs.config(text=f" games  >  {fname}")
            self.lbl_status_left.config(text=f"  ✓ {fname} loaded")
            self.update_line_numbers()
            self.highlight_syntax()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def action_save(self):
        if not self.current_filepath:
            fp = filedialog.asksaveasfilename(defaultextension=".vx", filetypes=[("Vortex3D Files", "*.vx")])
            if not fp:
                return False
            self.current_filepath = fp
        with open(self.current_filepath, "w", encoding="utf-8") as f:
            f.write(self.editor.get("1.0", tk.END))
        fname = os.path.basename(self.current_filepath)
        self.active_tab.config(text=f" {fname}  ✕ ")
        self.lbl_status_left.config(text=f"  ✓ Saved {fname}")
        self.log(f"[+] Saved: {self.current_filepath}")
        self.refresh_file_list()
        return True

    def refresh_file_list(self):
        self.listbox_files.delete(0, tk.END)
        games_dir = os.path.join(SCRIPT_DIR, "games")
        if os.path.exists(games_dir):
            for f in os.listdir(games_dir):
                if f.endswith(".vx"):
                    self.listbox_files.insert(tk.END, f"  📄 {f}")

    def on_select_project_file(self, event):
        sel = self.listbox_files.curselection()
        if sel:
            raw = self.listbox_files.get(sel[0]).replace("📄", "").strip()
            full = os.path.join(SCRIPT_DIR, "games", raw)
            self.load_file(full)

    def action_check(self):
        if not self.action_save():
            return
        self.log(f"[*] Checking syntax: {os.path.basename(self.current_filepath)}...")
        cmd = [sys.executable, COMPILER_SCRIPT, "check", self.current_filepath]
        threading.Thread(target=self.run_process, args=(cmd, False)).start()

    def action_compile(self):
        if not self.action_save():
            return
        self.log(f"[*] Building native .exe for {os.path.basename(self.current_filepath)}...")
        cmd = [sys.executable, COMPILER_SCRIPT, "build", self.current_filepath, "--fps-cap", self.combo_fps.get()]
        if self.var_release.get():
            cmd.append("--release")
        threading.Thread(target=self.run_process, args=(cmd, False)).start()

    def action_run(self):
        if not self.action_save():
            return
        self.log(f"[*] Compiling & Launching {os.path.basename(self.current_filepath)}...")
        cmd = [sys.executable, COMPILER_SCRIPT, "run", self.current_filepath, "--fps-cap", self.combo_fps.get()]
        if self.var_release.get():
            cmd.append("--release")
        threading.Thread(target=self.run_process, args=(cmd, True)).start()

    def run_process(self, cmd, is_launch=False):
        self.lbl_status_left.config(text="  ⚙ Compiling...")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            self.log(line.strip())
        p.wait()
        if p.returncode == 0:
            status = "▶ Running 3D Game" if is_launch else "✓ Build Succeeded"
            self.lbl_status_left.config(text=f"  {status}")
        else:
            self.lbl_status_left.config(text=f"  ✕ Build Failed (Code {p.returncode})")

if __name__ == "__main__":
    app = VortexStudio()
    app.mainloop()

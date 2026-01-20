# Description: Interface graphique Tkinter pour le jeu d'aventure

"""Module d'interface graphique pour le jeu d'aventure textuel.

Contient les classes `_StdoutRedirector` et `GameGUI` pour l'affichage
graphique du jeu avec Tkinter.
"""

import sys
import platform
from pathlib import Path

# Détection de l'OS pour adapter l'interface
IS_WINDOWS = platform.system() == 'Windows'
IS_MAC = platform.system() == 'Darwin'

# Optional: import Tkinter for GUI. If unavailable, GUI will be skipped.
try:
    import tkinter as tk
    from tkinter import ttk, simpledialog, messagebox
except Exception:
    tk = None

# Optional: import PIL for image resizing. If unavailable, images won't be scaled.
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class _StdoutRedirector:
    """Redirect sys.stdout writes into a Tkinter Text widget."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, msg):
        """Write message to the Text widget."""
        if msg:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")

    def flush(self):
        """Flush method required by sys.stdout interface (no-op for Text widget)."""


class GameGUI(tk.Tk):
    """Tkinter GUI for the text-based adventure game.

    Layout - Style Cluedo Victorien:
    ┌─────────────────────────────────────────────────────────────┐
    │  [Image 800x450]     │  [Info Panel compact]               │
    ├─────────────────────────────────────────────────────────────┤
    │  [Terminal Output - Scrollable]    │  [Boutons Actions]    │
    ├─────────────────────────────────────────────────────────────┤
    │  [Inventaire]                      │  [Entry + Send]       │
    └─────────────────────────────────────────────────────────────┘
    """

    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 450
    
    # Police cross-platform: Georgia sur Mac, Palatino Linotype ou Times New Roman sur Windows
    FONT_FAMILY = 'Palatino Linotype' if IS_WINDOWS else 'Georgia'
    FONT_MONO = 'Consolas' if IS_WINDOWS else 'Georgia'
    
    # Palette de couleurs victoriennes Cluedo
    COLORS = {
        'bg_dark': '#1a0f0f',           # Brun très foncé (fond principal)
        'bg_medium': '#2d1f1f',         # Brun moyen
        'bg_light': '#3d2b2b',          # Brun clair
        'accent_gold': '#c9a227',       # Or victorien
        'accent_burgundy': '#722f37',   # Bordeaux
        'accent_burgundy_light': '#8b3a3a',  # Bordeaux clair
        'text_cream': '#f5e6d3',        # Crème/ivoire
        'text_gold': '#d4af37',         # Or pour titres
        'text_muted': '#a89080',        # Texte secondaire
        'terminal_bg': '#0d0907',       # Fond terminal (presque noir)
        'terminal_fg': '#c9a227',       # Texte terminal (or)
        'highlight': '#8b0000',         # Rouge foncé pour sélection
    }

    def __init__(self):
        super().__init__()
        # Import Game ici pour éviter les imports circulaires
        from game import Game
        
        # Titre sans emoji sur Windows (affichage problématique)
        if IS_WINDOWS:
            self.title("Mystere au Manoir - Enquete Victorienne")
        else:
            self.title("🔍 Mystère au Manoir - Enquête Victorienne")
        self.configure(bg=self.COLORS['bg_dark'])
        
        # Plein écran au lancement - méthode différente selon l'OS
        if IS_WINDOWS:
            # Sur Windows, utiliser state('zoomed') pour un meilleur comportement
            self.state('zoomed')
        else:
            self.attributes('-fullscreen', True)
        
        # Touche Escape pour quitter le jeu
        self.bind('<Escape>', lambda e: self._on_close())

        # Underlying game logic instance
        self.game = Game()

        # Cache d'images pour éviter le garbage collection et améliorer les performances
        self.image_cache = {}
        
        # Configurer le style ttk pour le thème victorien
        self._setup_victorian_style()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Afficher l'écran d'accueil en premier
        self._show_splash_screen()

    def _show_splash_screen(self):
        """Affiche l'écran d'accueil avec l'image d'introduction et le bouton Nouvelle Partie."""
        # Créer le frame principal du splash screen
        self.splash_frame = tk.Frame(self, bg=self.COLORS['bg_dark'])
        self.splash_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Container central pour centrer le contenu
        center_container = tk.Frame(self.splash_frame, bg=self.COLORS['bg_dark'])
        center_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Cadre décoratif victorien autour de l'image
        image_border = tk.Frame(center_container, bg=self.COLORS['accent_gold'], padx=4, pady=4)
        image_border.pack(pady=(0, 30))
        
        inner_border = tk.Frame(image_border, bg=self.COLORS['bg_medium'], padx=3, pady=3)
        inner_border.pack()
        
        # Canvas pour l'image d'introduction
        splash_width = 900
        splash_height = 550
        self.splash_canvas = tk.Canvas(inner_border,
                                       width=splash_width,
                                       height=splash_height,
                                       bg=self.COLORS['bg_dark'],
                                       highlightthickness=0)
        self.splash_canvas.pack()
        
        # Charger l'image d'introduction
        assets_dir = Path(__file__).parent / 'assets'
        splash_image_path = assets_dir / 'splash_intro.png'
        
        if splash_image_path.exists():
            self._splash_image = self._load_image(splash_image_path, 
                                                   resize_to=(splash_width, splash_height), 
                                                   fill=True)
            if self._splash_image:
                self.splash_canvas.create_image(splash_width // 2, splash_height // 2, 
                                               image=self._splash_image, anchor="center")
        else:
            # Si pas d'image, afficher un texte de remplacement stylisé
            self.splash_canvas.create_text(splash_width // 2, splash_height // 2 - 50,
                                           text="MYSTERE AU MANOIR",
                                           font=(self.FONT_FAMILY, 36, "bold"),
                                           fill=self.COLORS['text_gold'])
            self.splash_canvas.create_text(splash_width // 2, splash_height // 2 + 20,
                                           text="Une Enquête Victorienne",
                                           font=(self.FONT_FAMILY, 20, "italic"),
                                           fill=self.COLORS['text_cream'])
            self.splash_canvas.create_text(splash_width // 2, splash_height // 2 + 80,
                                           text="Placez votre image 'splash_intro.png' dans le dossier assets",
                                           font=(self.FONT_FAMILY, 12),
                                           fill=self.COLORS['text_muted'])
        
        # Container pour les boutons
        button_container = tk.Frame(center_container, bg=self.COLORS['bg_dark'])
        button_container.pack(pady=20)
        
        # Bouton "Nouvelle Partie" - Style victorien élégant
        self.new_game_btn = tk.Button(
            button_container,
            text="NOUVELLE ENQUETE" if IS_WINDOWS else "⚜  NOUVELLE ENQUÊTE  ⚜",
            font=(self.FONT_FAMILY, 16, "bold"),
            bg=self.COLORS['accent_burgundy'],
            fg=self.COLORS['text_gold'],
            activebackground=self.COLORS['accent_burgundy_light'],
            activeforeground=self.COLORS['text_cream'],
            relief="raised",
            borderwidth=3,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self._start_new_game
        )
        self.new_game_btn.pack(pady=10)
        
        # Effet hover sur le bouton
        self.new_game_btn.bind("<Enter>", lambda e: self.new_game_btn.config(
            bg=self.COLORS['accent_burgundy_light'],
            fg=self.COLORS['text_cream']
        ))
        self.new_game_btn.bind("<Leave>", lambda e: self.new_game_btn.config(
            bg=self.COLORS['accent_burgundy'],
            fg=self.COLORS['text_gold']
        ))
        
        # Bouton "Quitter" - Plus discret
        self.quit_splash_btn = tk.Button(
            button_container,
            text="Quitter",
            font=(self.FONT_FAMILY, 11),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_muted'],
            activebackground=self.COLORS['bg_light'],
            activeforeground=self.COLORS['text_cream'],
            relief="flat",
            borderwidth=1,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._on_close
        )
        self.quit_splash_btn.pack(pady=(5, 0))
        
        # Texte décoratif en bas
        footer_text = tk.Label(
            center_container,
            text="Un mystere vous attend dans les ombres du manoir" if IS_WINDOWS else "─────  Un mystère vous attend dans les ombres du manoir  ─────",
            font=(self.FONT_FAMILY, 10, "italic"),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_muted']
        )
        footer_text.pack(pady=(30, 0))

    def _start_new_game(self):
        """Lance une nouvelle partie après l'écran d'accueil."""
        # Créer un dialogue personnalisé pour le nom du détective
        self._show_name_dialog()

    def _show_name_dialog(self):
        """Affiche un dialogue stylisé pour entrer le nom du détective."""
        # Créer une fenêtre de dialogue personnalisée
        dialog = tk.Toplevel(self)
        dialog.title("Identité du Détective")
        dialog.geometry("500x300")
        dialog.configure(bg=self.COLORS['bg_dark'])
        dialog.resizable(False, False)
        dialog.transient(self)
        
        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Variable pour stocker le nom
        self._detective_name = "Détective"
        self._dialog_confirmed = False
        
        # Cadre décoratif
        main_frame = tk.Frame(dialog, bg=self.COLORS['bg_dark'], padx=30, pady=30)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title_label = tk.Label(
            main_frame,
            text="ENQUETEUR" if IS_WINDOWS else "⚜ ENQUÊTEUR ⚜",
            font=(self.FONT_FAMILY, 18, "bold"),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_gold']
        )
        title_label.pack(pady=(0, 20))
        
        # Question
        question_label = tk.Label(
            main_frame,
            text="Quel est votre nom, detective ?" if IS_WINDOWS else "Quel est votre nom, détective ?",
            font=(self.FONT_FAMILY, 12),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_cream']
        )
        question_label.pack(pady=(0, 15))
        
        # Champ de saisie stylisé
        entry_frame = tk.Frame(main_frame, bg=self.COLORS['accent_gold'], padx=2, pady=2)
        entry_frame.pack(pady=10)
        
        name_entry = tk.Entry(
            entry_frame,
            font=(self.FONT_FAMILY, 14),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_cream'],
            insertbackground=self.COLORS['accent_gold'],
            relief="flat",
            width=25,
            justify="center"
        )
        name_entry.pack(ipady=8)
        name_entry.focus_set()
        
        def on_confirm():
            name = name_entry.get().strip()
            if not name:
                name = "Détective"
            self._detective_name = name
            self._dialog_confirmed = True
            dialog.destroy()
        
        def on_key(event):
            if event.keysym == "Return":
                on_confirm()
        
        def on_dialog_close():
            self._dialog_confirmed = True  # Permet de continuer même si fermé
            dialog.destroy()
        
        name_entry.bind("<Key>", on_key)
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Bouton de confirmation
        confirm_btn = tk.Button(
            main_frame,
            text="Commencer l'Enquete" if IS_WINDOWS else "Commencer l'Enquête",
            font=(self.FONT_FAMILY, 12, "bold"),
            bg=self.COLORS['accent_burgundy'],
            fg=self.COLORS['text_gold'],
            activebackground=self.COLORS['accent_burgundy_light'],
            activeforeground=self.COLORS['text_cream'],
            relief="raised",
            borderwidth=2,
            padx=25,
            pady=8,
            cursor="hand2",
            command=on_confirm
        )
        confirm_btn.pack(pady=(20, 0))
        
        # Effet hover
        confirm_btn.bind("<Enter>", lambda e: confirm_btn.config(
            bg=self.COLORS['accent_burgundy_light']
        ))
        confirm_btn.bind("<Leave>", lambda e: confirm_btn.config(
            bg=self.COLORS['accent_burgundy']
        ))
        
        # Attendre que le dialogue soit fermé
        dialog.grab_set()
        self.wait_window(dialog)
        
        # Initialiser le jeu après fermeture du dialogue
        self._initialize_game()

    def _initialize_game(self):
        """Initialise le jeu après la saisie du nom."""
        # Détruire l'écran d'accueil
        self.splash_frame.destroy()
        
        # Configurer le jeu avec le nom du joueur
        self.game.setup(player_name=self._detective_name)

        # Build UI layers
        self._build_layout()
        
        # Raccourcis clavier pour la navigation
        self.bind('<Up>', lambda e: self._send_command('go N'))
        self.bind('<Down>', lambda e: self._send_command('go S'))
        self.bind('<Left>', lambda e: self._send_command('go O'))
        self.bind('<Right>', lambda e: self._send_command('go E'))
        self.bind('<Key-u>', lambda e: self._send_command('go U') if not self._entry_has_focus() else None)
        self.bind('<Key-d>', lambda e: self._send_command('go D') if not self._entry_has_focus() else None)
        self.bind('<Key-b>', lambda e: self._send_command('back') if not self._entry_has_focus() else None)

        # Redirect stdout so game prints appear in terminal output area
        self.original_stdout = sys.stdout
        sys.stdout = _StdoutRedirector(self.text_output)

        # Print welcome text in GUI
        self.game.print_welcome()

        # Update all panels
        self._update_all_panels()

    def _setup_victorian_style(self):
        """Configure le style ttk pour un thème victorien."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style général
        style.configure('.',
                       background=self.COLORS['bg_dark'],
                       foreground=self.COLORS['text_cream'],
                       font=(self.FONT_FAMILY, 14))
        
        # Frames
        style.configure('TFrame', background=self.COLORS['bg_dark'])
        
        # LabelFrames avec bordure dorée
        style.configure('TLabelframe',
                       background=self.COLORS['bg_dark'],
                       bordercolor=self.COLORS['accent_gold'],
                       relief='ridge',
                       borderwidth=2)
        style.configure('TLabelframe.Label',
                       background=self.COLORS['bg_dark'],
                       foreground=self.COLORS['text_gold'],
                       font=(self.FONT_FAMILY, 14, 'bold'))
        
        # Scrollbar
        style.configure('TScrollbar',
                       background=self.COLORS['bg_medium'],
                       troughcolor=self.COLORS['bg_dark'],
                       arrowcolor=self.COLORS['accent_gold'])
        
        # Entry
        style.configure('TEntry',
                       fieldbackground=self.COLORS['bg_medium'],
                       foreground=self.COLORS['text_cream'],
                       insertcolor=self.COLORS['accent_gold'])

    # -------- Layout construction --------
    def _build_layout(self):
        """Construire l'interface avec tous les panneaux - Style Victorien."""
        # Configure root grid: 3 rows, 2 columns
        self.grid_rowconfigure(0, weight=0)  # Top: Image + Info
        self.grid_rowconfigure(1, weight=1)  # Middle: Terminal + Actions
        self.grid_rowconfigure(2, weight=0)  # Bottom: Inventory + Entry
        self.grid_columnconfigure(0, weight=1)  # Left side expands
        self.grid_columnconfigure(1, weight=0)  # Right side fixed

        # Load button images
        assets_dir = Path(__file__).parent / 'assets'
        # Charger et redimensionner l'image help avec PIL (en conservant les proportions)
        self._btn_help = None
        help_path = assets_dir / 'help.png'
        if help_path.exists() and PIL_AVAILABLE:
            try:
                help_img = Image.open(help_path)
                # Redimensionner en conservant les proportions pour la largeur des boutons
                target_width = 140
                ratio = target_width / help_img.width
                new_height = int(help_img.height * ratio)
                # Utiliser LANCZOS ou ANTIALIAS selon la version de PIL
                try:
                    resample_method = Image.Resampling.LANCZOS
                except AttributeError:
                    # Anciennes versions de PIL utilisent ANTIALIAS
                    resample_method = Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS
                help_img = help_img.resize((target_width, new_height), resample_method)
                self._btn_help = ImageTk.PhotoImage(help_img)
            except Exception as e:
                print(f"[DEBUG] Erreur chargement image help: {e}")
                self._btn_help = None
        elif not help_path.exists():
            print(f"[DEBUG] Image help non trouvée: {help_path}")
        elif not PIL_AVAILABLE:
            print("[DEBUG] PIL non disponible - bouton help sera en texte")

        # ============ ROW 0: TOP - Image + Room Info ============
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=6, pady=(6, 3))
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)

        # Image area (left) - Style parchemin victorien
        image_frame = ttk.LabelFrame(top_frame, text="Scene du Crime" if IS_WINDOWS else "⚜ Scène du Crime ⚜")
        image_frame.grid(row=0, column=0, sticky="nw", padx=(0, 6))
        
        canvas_container = ttk.Frame(image_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        canvas_container.pack(padx=5, pady=5)
        canvas_container.pack_propagate(False)
        
        self.canvas = tk.Canvas(canvas_container,
                                width=self.IMAGE_WIDTH,
                                height=self.IMAGE_HEIGHT,
                                bg=self.COLORS['bg_dark'],
                                highlightbackground=self.COLORS['accent_gold'],
                                highlightthickness=2)
        self.canvas.pack(fill="both", expand=True)
        self._image_ref = None

        # Room info panel (right of image) - compact, style victorien
        info_frame = ttk.Frame(top_frame, width=280)
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        info_frame.grid_propagate(False)
        info_frame.grid_rowconfigure(0, weight=0)
        info_frame.grid_rowconfigure(1, weight=1)
        info_frame.grid_rowconfigure(2, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)

        # Room name and description
        room_frame = ttk.LabelFrame(info_frame, text="Lieu d'Investigation" if IS_WINDOWS else "⚜ Lieu d'Investigation ⚜")
        room_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.room_label = tk.Label(room_frame, text="", font=(self.FONT_FAMILY, 16, "bold"),
                                   bg=self.COLORS['bg_medium'], fg=self.COLORS['text_gold'], 
                                   anchor="w")
        self.room_label.pack(fill="x", padx=5, pady=3)
        self.exits_label = tk.Label(room_frame, text="", font=(self.FONT_FAMILY, 12),
                                    bg=self.COLORS['bg_light'], fg=self.COLORS['text_muted'], 
                                    anchor="w")
        self.exits_label.pack(fill="x", padx=5, pady=(0, 3))

        # Objects in room - style indices
        objects_frame = ttk.LabelFrame(info_frame, text="Indices & Objets" if IS_WINDOWS else "🔍 Indices & Objets")
        objects_frame.grid(row=1, column=0, sticky="nsew", pady=4)
        self.objects_listbox = tk.Listbox(objects_frame, height=3, 
                                          bg=self.COLORS['bg_medium'], 
                                          fg=self.COLORS['text_cream'],
                                          selectbackground=self.COLORS['highlight'],
                                          selectforeground=self.COLORS['text_gold'],
                                          font=(self.FONT_FAMILY, 14),
                                          highlightbackground=self.COLORS['accent_gold'],
                                          highlightthickness=1)
        self.objects_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.objects_listbox.bind("<Double-1>", lambda e: self._take_selected())

        # Characters in room - style suspects
        chars_frame = ttk.LabelFrame(info_frame, text="Suspects Presents" if IS_WINDOWS else "🎭 Suspects Présents")
        chars_frame.grid(row=2, column=0, sticky="nsew", pady=4)
        self.chars_listbox = tk.Listbox(chars_frame, height=2, 
                                        bg=self.COLORS['bg_medium'], 
                                        fg=self.COLORS['text_cream'],
                                        selectbackground=self.COLORS['highlight'],
                                        selectforeground=self.COLORS['text_gold'],
                                        font=(self.FONT_FAMILY, 14),
                                        highlightbackground=self.COLORS['accent_gold'],
                                        highlightthickness=1)
        self.chars_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.chars_listbox.bind("<Double-1>", lambda e: self._talk_selected())

        # ============ ROW 1: MIDDLE - Terminal + Actions ============
        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=3)
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(1, weight=0)
        middle_frame.grid_rowconfigure(0, weight=1)

        # Terminal output (left) - Style carnet d'enquête
        terminal_frame = ttk.LabelFrame(middle_frame, text="Carnet d'Enquete" if IS_WINDOWS else "📜 Carnet d'Enquête")
        terminal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        terminal_frame.grid_rowconfigure(0, weight=1)
        terminal_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(terminal_frame, orient="vertical")
        self.text_output = tk.Text(terminal_frame,
                                   wrap="word",
                                   yscrollcommand=scrollbar.set,
                                   state="disabled",
                                   bg=self.COLORS['terminal_bg'],
                                   fg=self.COLORS['terminal_fg'],
                                   font=(self.FONT_FAMILY, 16),
                                   height=12,
                                   insertbackground=self.COLORS['accent_gold'],
                                   highlightbackground=self.COLORS['accent_gold'],
                                   highlightthickness=1)
        scrollbar.config(command=self.text_output.yview)
        self.text_output.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        # Actions panel (right) - Style victorien
        actions_panel = ttk.Frame(middle_frame)
        actions_panel.grid(row=0, column=1, sticky="nsew")
        actions_panel.grid_rowconfigure(2, weight=1)  # Investigation frame can expand

        # Style de boutons victoriens - texte doré sur fond sombre
        btn_style = {
            "width": 12, 
            "pady": 2, 
            "font": (self.FONT_FAMILY, 13),
            "bg": self.COLORS['bg_dark'],
            "fg": self.COLORS['text_gold'],
            "activebackground": self.COLORS['accent_burgundy'],
            "activeforeground": self.COLORS['text_cream'],
            "relief": "raised",
            "bd": 2
        }

        # Help button - utiliser un Label cliquable pour éviter les bordures
        if self._btn_help:
            help_btn = tk.Label(actions_panel,
                      image=self._btn_help,
                      bg=self.COLORS['bg_dark'],
                      cursor="hand2")
            help_btn.bind("<Button-1>", lambda e: self._send_command("help"))
        else:
            help_btn = tk.Button(actions_panel,
                      text="? Aide" if IS_WINDOWS else "❓ Aide",
                      command=lambda: self._send_command("help"),
                      **btn_style)
        help_btn.grid(row=0, column=0, sticky="ew", pady=2)

        # Panneau de raccourcis clavier
        move_frame = ttk.LabelFrame(actions_panel, text="Navigation (Clavier)" if IS_WINDOWS else "🧭 Navigation (Clavier)")
        move_frame.grid(row=1, column=0, sticky="ew", pady=2)
        
        # Indication des contrôles clavier
        controls_info = tk.Label(move_frame, 
                                  text="Fleches: N/S/O/E\nU: Monter | D: Descendre | B: Retour" if IS_WINDOWS else "⬆⬇⬅➡ Flèches: N/S/O/E\nU: Monter | D: Descendre | B: Retour",
                                  font=(self.FONT_FAMILY, 10),
                                  bg=self.COLORS['bg_dark'],
                                  fg=self.COLORS['text_gold'],
                                  justify="left")
        controls_info.pack(pady=4, padx=5, anchor="w")

        # ===== Investigation - Menu déroulant =====
        act_frame = ttk.LabelFrame(actions_panel, text="Investigation" if IS_WINDOWS else "🔍 Investigation")
        act_frame.grid(row=2, column=0, sticky="ew", pady=2)
        act_frame.grid_columnconfigure(0, weight=1)
        
        # Actions d'investigation disponibles (sans emojis sur Windows)
        if IS_WINDOWS:
            self.investigation_actions = {
                "Observer": lambda: self._send_command("look"),
                "Memoire": lambda: self._send_command("history"),
                "Saisir": self._prompt_take,
                "Deposer": self._prompt_drop,
                "Interroger": self._prompt_talk,
                "Inspecter": self._prompt_inspect,
            }
            self.inv_action_var = tk.StringVar(value="Observer")
        else:
            self.investigation_actions = {
                "👁 Observer": lambda: self._send_command("look"),
                "📜 Mémoire": lambda: self._send_command("history"),
                "✋ Saisir": self._prompt_take,
                "📦 Déposer": self._prompt_drop,
                "💬 Interroger": self._prompt_talk,
                "🔍 Inspecter": self._prompt_inspect,
            }
            self.inv_action_var = tk.StringVar(value="👁 Observer")
        
        # Menu déroulant Investigation
        inv_dropdown = tk.OptionMenu(act_frame, self.inv_action_var, 
                                      *list(self.investigation_actions.keys()))
        inv_dropdown.config(
            font=(self.FONT_FAMILY, 12),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_gold'],
            activebackground=self.COLORS['accent_burgundy'],
            activeforeground=self.COLORS['text_cream'],
            highlightthickness=1,
            highlightbackground=self.COLORS['accent_gold'],
            width=14
        )
        inv_dropdown["menu"].config(
            font=(self.FONT_FAMILY, 12),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_gold'],
            activebackground=self.COLORS['accent_burgundy'],
            activeforeground=self.COLORS['text_cream']
        )
        inv_dropdown.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        
        # Style bouton GO
        go_btn_style = {
            "width": 6, 
            "pady": 3, 
            "font": (self.FONT_FAMILY, 12, "bold"),
            "bg": self.COLORS['accent_burgundy'],
            "fg": self.COLORS['text_gold'],
            "activebackground": self.COLORS['accent_burgundy_light'],
            "activeforeground": self.COLORS['text_cream'],
            "relief": "raised",
            "bd": 2
        }
        
        tk.Button(act_frame, text="GO" if IS_WINDOWS else "▶ GO", 
                  command=self._execute_investigation,
                  **go_btn_style).grid(row=0, column=1, padx=4, pady=4)

        # ===== Missions - Menu déroulant =====
        quest_frame = ttk.LabelFrame(actions_panel, text="Missions" if IS_WINDOWS else "📋 Missions")
        quest_frame.grid(row=3, column=0, sticky="ew", pady=2)
        quest_frame.grid_columnconfigure(0, weight=1)
        
        # Actions de missions disponibles (sans emojis sur Windows)
        if IS_WINDOWS:
            self.mission_actions = {
                "Objectifs": lambda: self._send_command("quests"),
                "Decouvertes": lambda: self._send_command("rewards"),
                "Deverrouiller": self._prompt_unlock,
            }
            self.mission_action_var = tk.StringVar(value="Objectifs")
        else:
            self.mission_actions = {
                "📋 Objectifs": lambda: self._send_command("quests"),
                "🏆 Découvertes": lambda: self._send_command("rewards"),
                "🔓 Déverrouiller": self._prompt_unlock,
            }
            self.mission_action_var = tk.StringVar(value="📋 Objectifs")
        
        # Utiliser tk.OptionMenu pour un meilleur contrôle du style
        mission_dropdown = tk.OptionMenu(quest_frame, self.mission_action_var, 
                                          *list(self.mission_actions.keys()))
        mission_dropdown.config(
            font=(self.FONT_FAMILY, 12),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_gold'],
            activebackground=self.COLORS['accent_burgundy'],
            activeforeground=self.COLORS['text_cream'],
            highlightthickness=1,
            highlightbackground=self.COLORS['accent_gold'],
            width=16
        )
        mission_dropdown["menu"].config(
            font=(self.FONT_FAMILY, 12),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_gold'],
            activebackground=self.COLORS['accent_burgundy'],
            activeforeground=self.COLORS['text_cream']
        )
        mission_dropdown.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        
        tk.Button(quest_frame, text="GO" if IS_WINDOWS else "▶ GO", 
                  command=self._execute_mission,
                  **go_btn_style).grid(row=0, column=1, padx=4, pady=4)

        # Note: Bouton Quitter retiré - utiliser Escape pour quitter

        # ============ ROW 2: BOTTOM - Inventory + Entry ============
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=(3, 6))
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=2)

        # Inventory panel (left) - Style sacoche de détective
        inv_frame = ttk.LabelFrame(bottom_frame, text="Sacoche du Detective" if IS_WINDOWS else "🎒 Sacoche du Détective")
        inv_frame.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        
        self.inventory_listbox = tk.Listbox(inv_frame, height=3, 
                                            bg=self.COLORS['bg_medium'], 
                                            fg=self.COLORS['text_cream'],
                                            selectbackground=self.COLORS['highlight'],
                                            selectforeground=self.COLORS['text_gold'],
                                            font=(self.FONT_FAMILY, 10),
                                            highlightbackground=self.COLORS['accent_gold'],
                                            highlightthickness=1)
        self.inventory_listbox.pack(fill="x", padx=5, pady=5)
        self.inventory_listbox.bind("<Double-1>", lambda e: self._drop_selected())

        # Command entry (right) - Style télégramme victorien
        entry_frame = ttk.LabelFrame(bottom_frame, text="Ordres du Detective" if IS_WINDOWS else "✒️ Ordres du Détective")
        entry_frame.grid(row=0, column=1, sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        entry_container = ttk.Frame(entry_frame)
        entry_container.pack(fill="x", padx=5, pady=5)
        entry_container.grid_columnconfigure(0, weight=1)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(entry_container, 
                              textvariable=self.entry_var, 
                              font=(self.FONT_FAMILY, 16),
                              bg=self.COLORS['bg_medium'],
                              fg=self.COLORS['text_cream'],
                              insertbackground=self.COLORS['accent_gold'],
                              highlightbackground=self.COLORS['accent_gold'],
                              highlightthickness=1)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

        send_btn = tk.Button(entry_container, text="Executer" if IS_WINDOWS else "Exécuter", command=self._on_enter,
                             bg=self.COLORS['accent_burgundy'], 
                             fg=self.COLORS['text_cream'],
                             activebackground=self.COLORS['accent_burgundy_light'],
                             activeforeground=self.COLORS['text_gold'],
                             font=(self.FONT_FAMILY, 15, "bold"),
                             relief="raised",
                             bd=2)
        send_btn.grid(row=0, column=1)


    # -------- Panel updates --------
    def _update_all_panels(self):
        """Mettre à jour tous les panneaux d'information."""
        self._update_room_image()
        self._update_room_info()
        self._update_objects_list()
        self._update_characters_list()
        self._update_inventory_list()

    def _update_room_info(self):
        """Mettre à jour les informations sur la pièce actuelle."""
        if not self.game.player or not self.game.player.current_room:
            return
        room = self.game.player.current_room
        room_name = room.name.replace("_", " ")
        self.room_label.config(text=f"📍 {room_name}")
        self.exits_label.config(text=room.get_exit_string())

    def _update_objects_list(self):
        """Mettre à jour la liste des objets dans la pièce."""
        self.objects_listbox.delete(0, tk.END)
        if self.game.player and self.game.player.current_room:
            for item_name, item in self.game.player.current_room.inventory.items():
                # Afficher le nom et la description courte de l'objet
                desc = getattr(item, 'description', '')
                if desc:
                    self.objects_listbox.insert(tk.END, f"  {item_name} - {desc}")
                else:
                    self.objects_listbox.insert(tk.END, f"  {item_name}")

    def _update_characters_list(self):
        """Mettre à jour la liste des personnages dans la pièce."""
        self.chars_listbox.delete(0, tk.END)
        if self.game.player and self.game.player.current_room:
            for char_name, char in self.game.player.current_room.characters.items():
                # Afficher le nom et la description courte du personnage
                desc = getattr(char, 'description', '')
                if desc:
                    self.chars_listbox.insert(tk.END, f"  {char_name} - {desc}")
                else:
                    self.chars_listbox.insert(tk.END, f"  {char_name}")

    def _update_inventory_list(self):
        """Mettre à jour la liste de l'inventaire du joueur."""
        self.inventory_listbox.delete(0, tk.END)
        if not self.game.player or not self.game.player.inventory:
            self.inventory_listbox.insert(tk.END, "  (vide)")
        else:
            for item_name, item in self.game.player.inventory.items():
                self.inventory_listbox.insert(tk.END, f"  {item_name} ({item.weight} kg)")

    # -------- Image update --------
    def _load_image(self, image_path, resize_to=None, fill=True):
        """Charge une image depuis le cache ou depuis le fichier.
        
        Utilise un cache pour éviter de recharger les images et prévenir
        le garbage collection des PhotoImage par Python.
        
        Args:
            image_path: Chemin vers l'image
            resize_to: Tuple (width, height) pour redimensionner l'image
            fill: Si True, remplit tout le cadre (peut couper l'image). Si False, conserve les proportions.
        """
        # Créer une clé de cache unique incluant la taille et le mode
        cache_key = f"{image_path}_{resize_to}_{fill}" if resize_to else str(image_path)
        
        # Méthode de resampling compatible avec toutes les versions de PIL
        def get_resample_method():
            try:
                return Image.Resampling.LANCZOS
            except AttributeError:
                return Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS
        
        if cache_key not in self.image_cache:
            try:
                if PIL_AVAILABLE and resize_to:
                    # Utiliser PIL pour redimensionner l'image
                    pil_image = Image.open(image_path)
                    resample = get_resample_method()
                    
                    if fill:
                        # Mode FILL: redimensionner pour couvrir tout le cadre (crop si nécessaire)
                        target_w, target_h = resize_to
                        img_w, img_h = pil_image.size
                        
                        # Calculer le ratio pour couvrir tout le cadre
                        ratio_w = target_w / img_w
                        ratio_h = target_h / img_h
                        ratio = max(ratio_w, ratio_h)  # Prendre le plus grand pour couvrir tout
                        
                        # Nouvelle taille après mise à l'échelle
                        new_w = int(img_w * ratio)
                        new_h = int(img_h * ratio)
                        
                        # Redimensionner
                        pil_image = pil_image.resize((new_w, new_h), resample)
                        
                        # Centrer et découper pour avoir exactement la taille voulue
                        left = (new_w - target_w) // 2
                        top = (new_h - target_h) // 2
                        right = left + target_w
                        bottom = top + target_h
                        pil_image = pil_image.crop((left, top, right, bottom))
                        
                        self.image_cache[cache_key] = ImageTk.PhotoImage(pil_image)
                    else:
                        # Mode FIT: conserver les proportions avec bordures
                        pil_image.thumbnail(resize_to, resample)
                        final_image = Image.new('RGBA', resize_to, (0, 0, 0, 0))
                        x_offset = (resize_to[0] - pil_image.width) // 2
                        y_offset = (resize_to[1] - pil_image.height) // 2
                        if pil_image.mode != 'RGBA':
                            pil_image = pil_image.convert('RGBA')
                        final_image.paste(pil_image, (x_offset, y_offset))
                        self.image_cache[cache_key] = ImageTk.PhotoImage(final_image)
                else:
                    # Fallback sans PIL: charger l'image et essayer de l'adapter si resize_to est fourni
                    img = tk.PhotoImage(file=image_path)
                    if resize_to:
                        try:
                            target_w, target_h = resize_to
                            w, h = img.width(), img.height()
                            # Ne réduire que si l'image est plus grande que la cible
                            if w > target_w or h > target_h:
                                factor_w = max(1, int(round(w / target_w)))
                                factor_h = max(1, int(round(h / target_h)))
                                factor = max(factor_w, factor_h)
                                # subsample ne prend que des entiers; on prend le plus grand facteur pour garantir que
                                # l'image devienne plus petite que la cible (approximation)
                                if factor > 1:
                                    img = img.subsample(factor, factor)
                        except Exception:
                            # En cas d'erreur, revenir à l'image d'origine
                            pass
                    self.image_cache[cache_key] = img
            except Exception as e:
                print(f"Erreur chargement image {image_path}: {e}")
                return None
        return self.image_cache[cache_key]

    def _update_room_image(self):
        """Update the canvas with layered rendering: background, items, characters."""
        if not self.game.player or not self.game.player.current_room:
            return

        room = self.game.player.current_room
        assets_dir = Path(__file__).parent / 'assets'

        # Calque 0 : Nettoyage complet du canvas
        self.canvas.delete("all")

        # Calque 1 : Image de fond de la pièce (redimensionnée pour s'adapter)
        if room.image:
            bg_path = assets_dir / room.image
        else:
            bg_path = assets_dir / 'scene.png'

        # Charger l'image avec redimensionnement à la taille du canvas
        bg_image = self._load_image(bg_path, resize_to=(self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
        if bg_image:
            self.canvas.create_image(
                self.IMAGE_WIDTH / 2,
                self.IMAGE_HEIGHT / 2,
                image=bg_image,
                anchor="center",
                tags="background"
            )
        else:
            # Fallback victorien: afficher le nom de la pièce avec style
            self.canvas.create_rectangle(0, 0, self.IMAGE_WIDTH, self.IMAGE_HEIGHT, 
                                        fill=self.COLORS['bg_dark'],
                                        outline=self.COLORS['accent_gold'],
                                        width=2)
            # Cadre décoratif
            self.canvas.create_rectangle(10, 10, self.IMAGE_WIDTH-10, self.IMAGE_HEIGHT-10, 
                                        outline=self.COLORS['accent_gold'],
                                        width=1)
            self.canvas.create_text(
                self.IMAGE_WIDTH / 2,
                self.IMAGE_HEIGHT / 2,
                text=room.name.replace('_', ' ') if IS_WINDOWS else f"⚜ {room.name.replace('_', ' ')} ⚜",
                fill=self.COLORS['text_gold'],
                font=(self.FONT_FAMILY, 20, "italic")
            )

        # Calque 2 : Objets présents dans la pièce
        for item_name, item in room.inventory.items():
            if item.image:
                item_path = assets_dir / item.image
                if item_path.exists():
                    item_image = self._load_image(item_path)
                    if item_image:
                        # Utiliser la position définie dans sprite_positions ou une position par défaut
                        pos = room.sprite_positions.get(item_name, (self.IMAGE_WIDTH // 2, self.IMAGE_HEIGHT - 50))
                        self.canvas.create_image(
                            pos[0], pos[1],
                            image=item_image,
                            anchor="center",
                            tags="item"
                        )

        # Calque 3 : Personnages présents dans la pièce
        for char_name, char in room.characters.items():
            if char.image:
                char_path = assets_dir / char.image
                if char_path.exists():
                    # Redimensionner les sprites PNJ pour tenir dans la scène (proportions dynamiques)
                    # Taille plus grande pour une meilleure visibilité : largeur 30% et hauteur 55% du canvas
                    npc_max_w = max(80, int(self.IMAGE_WIDTH * 0.30))
                    npc_max_h = max(120, int(self.IMAGE_HEIGHT * 0.55))
                    char_image = self._load_image(char_path, resize_to=(npc_max_w, npc_max_h), fill=False)
                    if char_image:
                        # Position aléatoire : gauche ou droite (symétrique), aligné au bas de l'image
                        import random
                        if random.choice([True, False]):
                            # Position bas-gauche
                            x_pos = 0
                            anchor = "sw"
                        else:
                            # Position bas-droite (symétrique)
                            x_pos = self.IMAGE_WIDTH
                            anchor = "se"
                        
                        self.canvas.create_image(
                            x_pos, self.IMAGE_HEIGHT,
                            image=char_image,
                            anchor=anchor,
                            tags="character"
                        )


    # -------- Event handlers --------
    def _entry_has_focus(self):
        """Vérifie si le champ de saisie a le focus."""
        return self.focus_get() == self.entry

    def _on_enter(self, _event=None):
        """Handle Enter key press in the entry field."""
        value = self.entry_var.get().strip()
        if value:
            self._send_command(value)
        self.entry_var.set("")


    def _send_command(self, command):
        if self.game.finished:
            return
        # Echo the command in output area
        print(f"> {command}\n")
        self.game.process_command(command)
        # Update all panels after command
        self._update_all_panels()
        if self.game.finished:
            # Disable further input and schedule close (brief delay to show farewell)
            self.entry.configure(state="disabled")
            self.after(600, self._on_close)

    def _take_selected(self):
        """Prendre l'objet sélectionné dans la liste."""
        selection = self.objects_listbox.curselection()
        if selection:
            item_text = self.objects_listbox.get(selection[0])
            item_name = item_text.strip().split(" - ")[0].strip()
            if item_name:
                self._send_command(f"take {item_name}")

    def _drop_selected(self):
        """Déposer l'objet sélectionné de l'inventaire."""
        selection = self.inventory_listbox.curselection()
        if selection:
            item_text = self.inventory_listbox.get(selection[0])
            if "(vide)" not in item_text:
                item_name = item_text.strip().split(" (")[0].strip()
                if item_name:
                    self._send_command(f"drop {item_name}")

    def _talk_selected(self):
        """Parler au personnage sélectionné."""
        selection = self.chars_listbox.curselection()
        if selection:
            char_text = self.chars_listbox.get(selection[0])
            char_name = char_text.strip().split(" - ")[0].strip()
            if char_name:
                self._send_command(f"talk {char_name}")

    def _prompt_talk(self):
        """Affiche une liste des personnages présents et permet de parler à l'un d'eux."""
        room = self.game.player.current_room
        if not room.characters:
            print("Il n'y a personne à qui parler ici.\n")
            return
        
        # Créer une fenêtre de sélection
        chars = list(room.characters.keys())
        if len(chars) == 1:
            self._send_command(f"talk {chars[0]}")
        else:
            choice = simpledialog.askstring(
                "Parler",
                f"À qui voulez-vous parler?\n({', '.join(chars)})",
                parent=self
            )
            if choice:
                self._send_command(f"talk {choice}")


    def _prompt_take(self):
        """Affiche une liste des objets présents et permet d'en prendre un."""
        room = self.game.player.current_room
        if not room.inventory:
            print("Il n'y a rien à prendre ici.\n")
            return
        
        items = list(room.inventory.keys())
        if len(items) == 1:
            self._send_command(f"take {items[0]}")
        else:
            choice = simpledialog.askstring(
                "Prendre",
                f"Que voulez-vous prendre?\n({', '.join(items)})",
                parent=self
            )
            if choice:
                self._send_command(f"take {choice}")

    def _prompt_inspect(self):
        """Affiche une liste des objets et permet d'en inspecter un."""
        current = self.game.player.current_room
        room_items = list(current.inventory.keys()) if current else []
        player_items = list(self.game.player.inventory.keys())
        all_items = room_items + player_items
        
        if not all_items:
            print("Il n'y a rien à inspecter ici.\n")
            return
        
        if len(all_items) == 1:
            self._send_command(f"inspect {all_items[0]}")
        else:
            choice = simpledialog.askstring(
                "Inspecter",
                f"Que voulez-vous inspecter?\n({', '.join(all_items)})",
                parent=self
            )
            if choice:
                self._send_command(f"inspect {choice}")

    def _prompt_unlock(self):
        """Affiche une liste des objets verrouillés et permet d'en déverrouiller un."""
        current = self.game.player.current_room
        if not current:
            print("Vous n'êtes dans aucune pièce.\n")
            return
        
        # Chercher les objets qui peuvent être déverrouillés
        locked_items = [name for name, item in current.inventory.items() 
                       if 'fermé' in name.lower() or 'verrouillé' in name.lower() or 'locked' in name.lower()]
        
        if not locked_items:
            print("Il n'y a rien à déverrouiller ici.\n")
            return
        
        if len(locked_items) == 1:
            self._send_command(f"unlock {locked_items[0]}")
        else:
            choice = simpledialog.askstring(
                "Déverrouiller",
                f"Que voulez-vous déverrouiller?\n({', '.join(locked_items)})",
                parent=self
            )
            if choice:
                self._send_command(f"unlock {choice}")

    def _execute_investigation(self):
        """Exécute l'action d'investigation sélectionnée dans le menu déroulant."""
        action_name = self.inv_action_var.get()
        if action_name in self.investigation_actions:
            self.investigation_actions[action_name]()

    def _execute_mission(self):
        """Exécute l'action de mission sélectionnée dans le menu déroulant."""
        action_name = self.mission_action_var.get()
        if action_name in self.mission_actions:
            self.mission_actions[action_name]()

    def _prompt_drop(self):
        """Affiche une liste des objets dans l'inventaire et permet d'en déposer un."""
        player_inv = self.game.player.inventory
        if not player_inv:
            print("Votre inventaire est vide.\n")
            return
        
        items = list(player_inv.keys())
        if len(items) == 1:
            self._send_command(f"drop {items[0]}")
        else:
            choice = simpledialog.askstring(
                "Déposer",
                f"Que voulez-vous déposer?\n({', '.join(items)})",
                parent=self
            )
            if choice:
                self._send_command(f"drop {choice}")


    def _on_close(self):
        # Restore stdout and destroy window
        if hasattr(self, 'original_stdout'):
            sys.stdout = self.original_stdout
        self.destroy()

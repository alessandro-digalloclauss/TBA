# Description: Game class

"""Module principal du jeu d'aventure textuel.

Contient la classe `Game` qui assemble les pièces, les commandes et le
joueur, et exécute la boucle principale du jeu.
"""

# Import des modules

from pathlib import Path
import sys

# Optional: import Tkinter for GUI. If unavailable, GUI will be skipped.
try:
    import tkinter as tk
    from tkinter import ttk, simpledialog
except Exception:
    tk = None

from room import Room
from player import Player
from command import Command
from actions import Actions
from item import Item
from character import Character
from quest import Quest

# Activer pour afficher les messages de débogage dans les autres modules
# Importable via `from game import DEBUG`
DEBUG = False


class Game:
    """Conteneur principal du jeu : pièces, commandes et état du joueur."""

    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        # Initialiser les directions et alias tôt pour qu'ils existent
        # même si _create_world() est appelé directement dans des tests.
        self.directions = set(["N", "E", "S", "O", "U", "D"])  # nord, est, sud, ouest, haut, bas
        self.direction_aliases = {
            "N": "N",
            "NORD": "N",
            "E": "E",
            "EST": "E",
            "S": "S",
            "SUD": "S",
            "O": "O",
            "0": "O",
            "OUEST": "O",
            "U": "U",
            "HAUT": "U",
            "UP": "U",
            "D": "D",
            "BAS": "D",
            "DOWN": "D",
        }

    # Configuration du jeu
    def setup(self, player_name=None):
        """Créer les pièces, déclarer les commandes et placer le joueur dans la pièce de départ.

        Si `player_name` est fourni, il est utilisé sans demander à l'utilisateur
        (utile pour l'interface graphique qui demande le nom via un dialogue).
        """

        # Déclaration des commandes

        cmd_help = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["help"] = cmd_help
        cmd_quit = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["quit"] = cmd_quit
        go = Command(
            "go",
            " <direction> : se déplacer dans une direction cardinale "
            "(N, E, S, O, U, D)",
            Actions.go,
            1,
        )
        self.commands["go"] = go
        cmd_back = Command("back", " : revenir en arrière", Actions.back, 0)
        self.commands["back"] = cmd_back
        cmd_history = Command("history", " : afficher l'historique", Actions.history, 0)
        self.commands["history"] = cmd_history
        cmd_look = Command("look", " : regarder la pièce", Actions.look, 0)
        self.commands["look"] = cmd_look
        cmd_check = Command("check", " : afficher l'inventaire", Actions.check, 0)
        self.commands["check"] = cmd_check
        cmd_inspect = Command("inspect", " <objet> : examiner un objet en détail (nécessite une loupe)", Actions.inspect, 1)
        self.commands["inspect"] = cmd_inspect
        cmd_talk = Command("talk", " <person> : parler à un personnage présent", Actions.talk, 1)
        self.commands["talk"] = cmd_talk
        cmd_take = Command(
            "take",
            " <item> : prendre un objet présent dans la pièce",
            Actions.take,
            1,
        )
        self.commands["take"] = cmd_take
        cmd_drop = Command(
            "drop",
            " <item> : reposer un objet dans la pièce",
            Actions.drop,
            1,
        )
        self.commands["drop"] = cmd_drop
        cmd_quests = Command("quests", " : afficher la liste des quêtes", Actions.quests, 0)
        self.commands["quests"] = cmd_quests
        cmd_quest = Command(
            "quest", " <titre> : afficher les détails d'une quête", Actions.quest, 1
        )
        self.commands["quest"] = cmd_quest
        cmd_activate = Command(
            "activate", " <titre> : activer une quête", Actions.activate, 1
        )
        self.commands["activate"] = cmd_activate
        cmd_rewards = Command("rewards", " : afficher vos récompenses", Actions.rewards, 0)
        self.commands["rewards"] = cmd_rewards
        # Directions utilisées dans le jeu (codes canoniques d'une lettre)
        # et table d'alias qui mappe différentes entrées utilisateur vers
        # le code canonique.
        self.directions = set(["N", "E", "S", "O", "U", "D"])  # nord, est, sud, ouest, haut, bas
        # Mappe mots/variants usuels (insensibles à la casse) vers les lettres canoniques.
        self.direction_aliases = {
            "N": "N",
            "NORD": "N",
            "E": "E",
            "EST": "E",
            "S": "S",
            "SUD": "S",
            "O": "O",
            "0": "O",
            "OUEST": "O",
            "OUEST": "O",
            "U": "U",
            "HAUT": "U",
            "UP": "U",
            "D": "D",
            "BAS": "D",
            "DOWN": "D",
        }
        # Création du monde (pièces, inventaires, sorties)
        start_room = self._create_world()

        # Configuration du joueur et pièce de départ
        if player_name is None:
            name = input("\nEntrez votre nom: ")
        else:
            name = player_name

        self.player = Player(name)
        # Placer le joueur dans la salle de départ
        self.player.current_room = start_room

        # Donner un outil d'investigation au joueur
        self.player.inventory['loupe'] = Item('loupe', "une loupe d'inspection, utile pour examiner les indices", 0.2)

        # Initialiser les quêtes
        self._setup_quests()

    def _setup_quests(self):
        """Initialiser les quêtes du jeu."""
        # Quête d'exploration du manoir
        exploration_quest = Quest(
            title="Explorateur du Manoir",
            description="Explorez les différentes pièces du manoir mystérieux.",
            objectives=[
                "Visiter Hall",
                "Visiter Salon_Victorien",
                "Visiter Bibliotheque",
                "Visiter Bureau",
                "Visiter Chambre",
            ],
            reward="Titre de Grand Explorateur",
        )

        # Quête de déplacement
        travel_quest = Quest(
            title="Grand Voyageur",
            description="Déplacez-vous 10 fois à travers le manoir.",
            objectives=["Se déplacer 10 fois"],
            reward="Bottes de voyageur",
        )

        # Quête des lieux secrets
        secrets_quest = Quest(
            title="Découvreur de Secrets",
            description="Découvrez les lieux les plus mystérieux du manoir.",
            objectives=[
                "Visiter Pièce_cachée",
                "Visiter Cave_a_vin",
                "Visiter Atelier",
            ],
            reward="Clé dorée",
        )

        # Quête de rencontre avec les PNJ
        pnj_quest = Quest(
            title="Rencontres Mystérieuses",
            description="Parlez aux habitants du manoir.",
            objectives=[
                "parler avec Gandalf",
                "parler avec Archiviste",
            ],
            reward="Connaissance ancienne",
        )

        # Ajouter les quêtes au gestionnaire du joueur
        self.player.quest_manager.add_quest(exploration_quest)
        self.player.quest_manager.add_quest(travel_quest)
        self.player.quest_manager.add_quest(secrets_quest)
        self.player.quest_manager.add_quest(pnj_quest)

    def _create_world(self):
        """Créer les pièces, peupler les inventaires et relier les sorties.

        Retourne la pièce de départ (hall).
        """
        # Créer toutes les pièces et les stocker dans un dict pour y référer facilement
        rooms = {}
        rooms['jardin_hiver'] = Room(
            'Jardin_hiver',
            '🌿 Jardin d’hiver',
            'Des plantes exotiques sont en désordre sous une vitre brisée.'
        )
        rooms['hall'] = Room(
            'Hall',
            'Hall',
            "Le vaste hall est dominé par un grand lustre immobile. L'horloge s'est arrêtée à 22:30.",
        )
        rooms['salon_victorien'] = Room(
            'Salon_Victorien',
            'Salon victorien',
            'On voit des fauteuils usés, une cheminée froide et une horloge ancienne.'
        )
        rooms['cuisine'] = Room(
            'Cuisine',
            '🍲 Cuisine',
            "On y trouve un chaudron fumant et des couteaux alignés, l’un manque."
        )
        rooms['bureau'] = Room(
            'Bureau',
            'Bureau',
            'C’EST L’HORREUR ! Un corps gît au sol dans le bureau, entouré de sang et de papiers éparpillés.'
            'Les vieux fauteuils ne sont pas à leur place, ils ont visiblement été bousculés'
        )
        rooms['couloir'] = Room(
            'Couloir',
            '🚪 Couloir',
            'Le long couloir est sombre et le parquet grince sous vos pas.'
            'Des traces de pas boueuses mènent vers la bibliothèque.'
        )
        rooms['chambre'] = Room(
            'Chambre',
            '🛏️ Chambre',
            'Le lit est défait et la fenêtre est entrouverte.'
        )
        rooms['bibliotheque'] = Room(
            'Bibliotheque',
            '📖 Bibliothèque',
            'De hauts rayonnages remplis de livres anciens couvrent les murs.'
            'Tous sont soigneusement alignés, sauf un vieux livre mal rangé qui dépasse de l’étagère.'
        )
        rooms['piece_cachee'] = Room(
            'Pièce_cachée',
            '🕯️ Pièce cachée',
            'Une petite pièce secrète est faiblement éclairée par une lanterne.'
            'Des parchemins en évidence sur le bureau retiennent l\'attention'
        )
        rooms['cave_a_vin'] = Room(
            'Cave_a_vin',
            '🍷 Cave à vin',
            'La cave est fraîche et humide, remplie de bouteilles anciennes.'
        )
        rooms['atelier'] = Room(
            'Atelier',
            '🛠️ Atelier',
            "Des outils et des plans froissés sont éparpillés sur l’établi."
        )

        # Collecter les pièces dans la liste du jeu
        self.rooms = list(rooms.values())

        # Ajout d'items dans certaines pièces (nom -> Item)
        # Jardin d'hiver
        rooms['jardin_hiver'].inventory['plantes renversées'] = Item(
            'plantes renversées', 'des plantes renversées, terre et feuilles éparpillées', 3.0
        )
        rooms['jardin_hiver'].inventory['gants de jardinage propres'] = Item(
            'gants de jardinage propres', "une paire de gants de jardinage propres", 0.2,
            detail="Des gants propres mais légèrement humides, sans trace de sang ni de terre incrustée."
        )

        # Hall
        rooms['hall'].inventory['cle'] = Item('cle', 'une petite clé rouillée', 0.5)
        rooms['hall'].inventory['manteau'] = Item('manteau', "un manteau élégant, peut-être appartenant à un invité", 1.5)

        # Cuisine
        rooms['cuisine'].inventory['couteau'] = Item('couteau', 'un couteau émoussé', 0.5)
        rooms['cuisine'].inventory['livre'] = Item(
            'livre', 'un livre laissé sur la table, pages ouvertes', 0.8
        )

        # Salon victorien
        rooms['salon_victorien'].inventory['lettre'] = Item(
            'lettre', "une lettre à moitié brûlée; l'encre est encore à demi lisible", 0.05
        )

        # Bureau
        rooms['bureau'].inventory['note froissée'] = Item('note froissée', "une note couverte de taches de sang", 0.03)
        rooms['bureau'].inventory['corps'] = Item(
            'corps',
            "le corps sans vie du maître de maison, Armand de Valenbourg, étendu au sol, entouré de sang",
            80.0,
            detail="À en juger par les marques sur le corps, il semble que le maître ait été poignardé."
        )

        # Chambre
        rooms['chambre'].inventory['pistolet'] = Item(
            'pistolet', 'un petit pistolet trouvé caché dans un tiroir', 1.2
        )
        rooms['chambre'].inventory['bijoux'] = Item('bijoux', 'un écrin contenant des bijoux précieux', 0.3)

        # Bibliothèque
        rooms['bibliotheque'].inventory['grimoire'] = Item(
            'grimoire', 'un vieux grimoire relié de cuir', 1.2
        )
        rooms['bibliotheque'].inventory['livre étrange'] = Item(
            'livre étrange', 'un livre à la reliure étrange, dépasse de l\'une des étagères', 1.1,
            detail="La reliure cache un petit mécanisme; des marques d'usure montrent qu'il a déjà été manipulé récemment."
        )
        rooms['bibliotheque'].inventory['échelle déplacée'] = Item('échelle déplacée', 'une échelle roulante déplacée', 5.0)
        rooms['bibliotheque'].inventory['bougie éteinte'] = Item('bougie éteinte', 'une bougie éteinte, cire froide', 0.1)

        # Pièce cachée
        rooms['piece_cachee'].inventory['clé secrète'] = Item('clé secrète', 'une clé petite et finement ciselée', 0.1,
            detail="Très fine, pourrait ouvrir un petit coffret ou un tiroir discret."
        )
        rooms['piece_cachee'].inventory['lettre de chantage'] = Item('lettre de chantage', 'une lettre menaçante, écrite à la main', 0.05,
            detail="La lettre mentionne une dette et le nom 'Delcourt' dans une phrase partiellement effacée."
        )

        # Cave à vin
        rooms['cave_a_vin'].inventory['bouteille brisée'] = Item('bouteille brisée', 'des éclats de bouteille et du vin renversé', 0.2)
        rooms['cave_a_vin'].inventory['traces effacées'] = Item('traces effacées', "des marques nettoyées, comme si on avait tenté d'effacer des indices", 0.0)
        rooms['cave_a_vin'].inventory['tonneau déplacé'] = Item('tonneau déplacé', 'un tonneau déplacé laissant un espace vide', 20.0)

        # Atelier
        # Indices importants
        rooms['atelier'].inventory['gants tachés de sang'] = Item(
            'gants tachés de sang', "une paire de gants tachés de sang, indice potentiel", 0.1,
            detail="De petites éclaboussures et des fibres noircies indiquent une lutte; des traces de saleté sont incrustées, peut-être transférées récemment."
        )
        rooms['atelier'].inventory['plans froissés'] = Item('plans froissés', 'des plans froissés couverts de notes et de ratures', 0.2,
            detail="On distingue des annotations techniques et une mention barrée : 'Ne pas laisser Armand lire'."
        )
        rooms['atelier'].inventory['outils lourds'] = Item('outils lourds', "une caisse d'outils lourds", 15.0)

        # Ajouter les personnages non joueurs dans les pièces
        rooms['jardin_hiver'].characters['Émile'] = Character(
            'Émile',
            "le jardinier taciturne qui connaît les passages secrets",
            rooms['jardin_hiver'],
            ["Je préfère rester discret... Ces passages cachés, peu les connaissent."]
        )
        rooms['cuisine'].characters['Clara Beaumont'] = Character(
            'Clara Beaumont',
            "la lectrice mystérieuse, invitée cultivée, toujours un livre à la main (était dans la cuisine lors du drame)",
            rooms['cuisine'],
            ["Les livres disent parfois plus que les gens. J'étais dans la cuisine cette nuit-là."]
        )
        rooms['atelier'].characters['Victor Lenoir'] = Character(
            'Victor Lenoir',
            "l'ingénieur, passe son temps à l'atelier; sait manipuler des mécanismes complexes",
            rooms['atelier'],
            ["Les mécanismes peuvent être trompeurs. Je conçois des dispositifs, pas des crimes."]
        )
        rooms['salon_victorien'].characters['Hélène de Valenbourg'] = Character(
            'Hélène de Valenbourg',
            "l'épouse, froide et distante (possède une arme à feu)",
            rooms['salon_victorien'],
            ["Je suis encore sous le choc. Armand avait beaucoup d'ennemis... Je n'ai rien à cacher."]
        )
        rooms['bibliotheque'].characters['Maurice Delcourt'] = Character(
            'Maurice Delcourt',
            "l'archiviste, obsédé par les livres anciens; fréquente la bibliothèque",
            rooms['bibliotheque'],
            ["Les vieux manuscrits ont des secrets que certains paieraient cher pour découvrir."]
        )

        # Create exits for rooms
        rooms['jardin_hiver'].exits = {
            'N': None,
            'E': rooms['hall'],
            'S': None,
            'O': None,
            'U': None,
            'D': None,
        }
        rooms['hall'].exits = {
            'N': None,
            'E': rooms['salon_victorien'],
            'S': rooms['cuisine'],
            'O': rooms['jardin_hiver'],
            'U': rooms['couloir'],
            'D': None,
        }
        rooms['salon_victorien'].exits = {
            'N': None,
            'E': None,
            'S': rooms['bureau'],
            'O': rooms['hall'],
            'U': None,
            'D': None,
        }
        rooms['cuisine'].exits = {
            'N': rooms['hall'],
            'E': rooms['bureau'],
            'S': None,
            'O': rooms['salon_victorien'],
            'U': None,
            'D': rooms['cave_a_vin'],
        }
        rooms['bureau'].exits = {
            'N': rooms['salon_victorien'],
            'E': None,
            'S': None,
            'O': rooms['cuisine'],
            'U': None,
            'D': None,
        }
        rooms['cave_a_vin'].exits = {
            'N': None,
            'E': rooms['atelier'],
            'S': None,
            'O': None,
            'U': rooms['cuisine'],
            'D': None,
        }
        rooms['atelier'].exits = {
            'N': None,
            'E': None,
            'S': None,
            'O': rooms['cave_a_vin'],
            'U': None,
            'D': None,
        }
        rooms['couloir'].exits = {
            'N': rooms['chambre'],
            'E': rooms['bibliotheque'],
            'S': None,
            'O': None,
            'U': None,
            'D': rooms['cuisine'],
        }
        rooms['chambre'].exits = {
            'N': None,
            'E': None,
            'S': rooms['couloir'],
            'O': None,
            'U': None,
            'D': None,
        }
        # L'accès est initialement verrouillé vers la pièce cachée (s'ouvrira en prenant un livre particulier)
        rooms['bibliotheque'].exits = {
            'N': None,
            'E': None,  # verrouillé jusqu'à activation
            'S': None,
            'O': rooms['couloir'],
            'U': None,
            'D': None,
        }
        # Pièce cachée isolée initialement (sortie O verrouillée)
        rooms['piece_cachee'].exits = {
            'N': None,
            'E': None,
            'S': None,
            'O': None,  # verrouillé jusqu'à activation depuis la bibliothèque
            'U': None,
            'D': None,
        }

        # Return the starting room (hall)
        return rooms['hall']

    # Play the game
    def play(self):
        """Run the main game loop until the player quits."""
        self.setup()
        self.print_welcome()
        # Loop until the game is finished
        while not self.finished:
            # Get the command from the player
            self.process_command(input("> "))

    # Process the command entered by the player
    def process_command(self, command_string) -> None:
        """Parse a command string and execute the corresponding action.

        The first token is the command word; the rest are parameters.
        """

        # Split the command string into a list of words
        list_of_words = command_string.split(" ")

        command_word = list_of_words[0]

        # If the command is not recognized, print an error message
        if command_word not in self.commands:
            print(
                f"\nCommande '{command_word}' non reconnue. Entrez 'help' "
                "pour voir la liste des commandes disponibles.\n"
            )
            # Also remind the player of their current location
            current = getattr(self.player, 'current_room', None)
            if current is not None:
                room_name = getattr(current, 'name', 'inconnue').replace('_', ' ')
                print(f"Vous êtes toujours dans {room_name}.\n")
        # If the command is recognized, execute it
        else:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)

        # Avancer le monde d'un tour : tenter de déplacer les PNJ
        # (appelé à la fin de chaque commande, reconnue ou non)
        self.tick_npcs()

    # Print the welcome message
    def print_welcome(self):
        """Show a short welcome and the current room description."""
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("Entrez 'help' si vous avez besoin d'aide.")
        # Contexte introductif ajouté: mystère du manoir
        print(
            "Le manoir d’Hiver accueille plusieurs invités pour une soirée privée.\n"
            "Au petit matin, le maître des lieux est retrouvé mort dans son bureau, une flaque de sang autour de lui.\n"
            "Les portes étaient verrouillées. Le meurtrier est forcément dans la maison.\n"
            "La victime ? Armand de Valenbourg, propriétaire du manoir, homme riche et secret, détenteur de documents compromettants.\n"
        )
        print(self.player.current_room.get_long_description())

    def tick_npcs(self):
        """Avance d'un tour les personnages non joueurs en appelant leur méthode `move()`.

        Parcourt toutes les pièces et appelle `move()` pour chaque personnage
        listé dans `room.characters`. On itère sur une copie pour éviter les
        modifications durant l'itération.
        """
        # Pour chaque pièce, faire tenter le déplacement de chaque PNJ présent
        for room in self.rooms:
            # Copier la liste des personnages pour parcourir en sécurité
            chars = list(room.characters.values())
            for char in chars:
                try:
                    # Ne pas déplacer un PNJ si le joueur est dans la même pièce
                    # (évite qu'un PNJ disparaisse immédiatement après qu'on lui a parlé).
                    player_room = getattr(self.player, 'current_room', None)
                    if player_room is not None and player_room is room:
                        # Skip moving this NPC this tick
                        continue

                    char.move()
                except Exception:
                    # Ne pas interrompre le jeu pour une erreur de PNJ
                    pass


##############################
# Tkinter GUI Implementation #
##############################


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

    Layout:
    ┌─────────────────────────────────────────────────────────────┐
    │  [Image 400x300]     │  [Info Panel: Lieu, Objets, PNJ]    │
    ├─────────────────────────────────────────────────────────────┤
    │  [Terminal Output - Scrollable]    │  [Boutons Actions]    │
    ├─────────────────────────────────────────────────────────────┤
    │  [Inventaire]                      │  [Entry + Send]       │
    └─────────────────────────────────────────────────────────────┘
    """

    IMAGE_WIDTH = 400
    IMAGE_HEIGHT = 300

    def __init__(self):
        super().__init__()
        self.title("TBA - Aventure Textuelle")
        self.geometry("1100x750")  # Plus large pour tout afficher
        self.minsize(1000, 700)

        # Underlying game logic instance
        self.game = Game()

        # Ask player name via dialog (fallback to 'Joueur')
        name = simpledialog.askstring("Nom", "Entrez votre nom:", parent=self)
        if not name:
            name = "Joueur"
        self.game.setup(player_name=name)  # Pass name to avoid double prompt

        # Build UI layers
        self._build_layout()

        # Redirect stdout so game prints appear in terminal output area
        self.original_stdout = sys.stdout
        sys.stdout = _StdoutRedirector(self.text_output)

        # Print welcome text in GUI
        self.game.print_welcome()

        # Update all panels
        self._update_all_panels()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # -------- Layout construction --------
    def _build_layout(self):
        """Construire l'interface avec tous les panneaux."""
        # Configure root grid: 3 rows, 2 columns
        self.grid_rowconfigure(0, weight=0)  # Top: Image + Info
        self.grid_rowconfigure(1, weight=1)  # Middle: Terminal + Actions
        self.grid_rowconfigure(2, weight=0)  # Bottom: Inventory + Entry
        self.grid_columnconfigure(0, weight=1)  # Left side expands
        self.grid_columnconfigure(1, weight=0)  # Right side fixed

        # Load button images
        assets_dir = Path(__file__).parent / 'assets'
        self._btn_help = tk.PhotoImage(file=assets_dir / 'help-50.png') if (assets_dir / 'help-50.png').exists() else None
        self._btn_up = tk.PhotoImage(file=assets_dir / 'up-arrow-50.png') if (assets_dir / 'up-arrow-50.png').exists() else None
        self._btn_down = tk.PhotoImage(file=assets_dir / 'down-arrow-50.png') if (assets_dir / 'down-arrow-50.png').exists() else None
        self._btn_left = tk.PhotoImage(file=assets_dir / 'left-arrow-50.png') if (assets_dir / 'left-arrow-50.png').exists() else None
        self._btn_right = tk.PhotoImage(file=assets_dir / 'right-arrow-50.png') if (assets_dir / 'right-arrow-50.png').exists() else None
        self._btn_quit = tk.PhotoImage(file=assets_dir / 'quit-50.png') if (assets_dir / 'quit-50.png').exists() else None

        # ============ ROW 0: TOP - Image + Room Info ============
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=6, pady=(6, 3))
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)

        # Image area (left)
        image_frame = ttk.LabelFrame(top_frame, text="🗺️ Lieu")
        image_frame.grid(row=0, column=0, sticky="nw", padx=(0, 6))
        
        canvas_container = ttk.Frame(image_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        canvas_container.pack(padx=5, pady=5)
        canvas_container.pack_propagate(False)
        
        self.canvas = tk.Canvas(canvas_container,
                                width=self.IMAGE_WIDTH,
                                height=self.IMAGE_HEIGHT,
                                bg="#1a1a2e")
        self.canvas.pack(fill="both", expand=True)
        self._image_ref = None

        # Room info panel (right of image)
        info_frame = ttk.Frame(top_frame)
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        info_frame.grid_rowconfigure(0, weight=0)
        info_frame.grid_rowconfigure(1, weight=1)
        info_frame.grid_rowconfigure(2, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)

        # Room name and description
        room_frame = ttk.LabelFrame(info_frame, text="📍 Lieu actuel")
        room_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.room_label = tk.Label(room_frame, text="", font=("Helvetica", 12, "bold"),
                                   bg="#1a1a2e", fg="#eee", anchor="w", wraplength=350)
        self.room_label.pack(fill="x", padx=5, pady=3)
        self.exits_label = tk.Label(room_frame, text="", font=("Helvetica", 10),
                                    bg="#16213e", fg="#aaa", anchor="w")
        self.exits_label.pack(fill="x", padx=5, pady=(0, 3))

        # Objects in room
        objects_frame = ttk.LabelFrame(info_frame, text="📦 Objets dans la pièce")
        objects_frame.grid(row=1, column=0, sticky="nsew", pady=4)
        self.objects_listbox = tk.Listbox(objects_frame, height=4, bg="#16213e", fg="#eee",
                                          selectbackground="#e94560", font=("Helvetica", 10))
        self.objects_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.objects_listbox.bind("<Double-1>", lambda e: self._take_selected())

        # Characters in room
        chars_frame = ttk.LabelFrame(info_frame, text="👥 Personnages présents")
        chars_frame.grid(row=2, column=0, sticky="nsew", pady=4)
        self.chars_listbox = tk.Listbox(chars_frame, height=3, bg="#16213e", fg="#eee",
                                        selectbackground="#e94560", font=("Helvetica", 10))
        self.chars_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.chars_listbox.bind("<Double-1>", lambda e: self._talk_selected())

        # ============ ROW 1: MIDDLE - Terminal + Actions ============
        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=3)
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(1, weight=0)
        middle_frame.grid_rowconfigure(0, weight=1)

        # Terminal output (left)
        terminal_frame = ttk.LabelFrame(middle_frame, text="📜 Terminal")
        terminal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        terminal_frame.grid_rowconfigure(0, weight=1)
        terminal_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(terminal_frame, orient="vertical")
        self.text_output = tk.Text(terminal_frame,
                                   wrap="word",
                                   yscrollcommand=scrollbar.set,
                                   state="disabled",
                                   bg="#0f0f23", fg="#00ff00",
                                   font=("Courier", 11),
                                   height=12)
        scrollbar.config(command=self.text_output.yview)
        self.text_output.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        # Actions panel (right)
        actions_panel = ttk.Frame(middle_frame)
        actions_panel.grid(row=0, column=1, sticky="ns")

        btn_style = {"width": 12, "pady": 2, "font": ("Helvetica", 9)}

        # Help button
        tk.Button(actions_panel,
                  image=self._btn_help if self._btn_help else None,
                  text="❓ Aide" if self._btn_help is None else "",
                  command=lambda: self._send_command("help"),
                  **btn_style if self._btn_help is None else {"bd": 0}).grid(row=0, column=0, sticky="ew", pady=2)

        # Movement buttons
        move_frame = ttk.LabelFrame(actions_panel, text="🧭 Déplacements")
        move_frame.grid(row=1, column=0, sticky="ew", pady=4)
        
        tk.Button(move_frame, text="⬆ Haut", command=lambda: self._send_command("go U"),
                  width=8).grid(row=0, column=0, columnspan=3, sticky="ew")
        tk.Button(move_frame, image=self._btn_up if self._btn_up else None,
                  text="N" if not self._btn_up else "",
                  command=lambda: self._send_command("go N"), bd=0).grid(row=1, column=1)
        tk.Button(move_frame, image=self._btn_left if self._btn_left else None,
                  text="O" if not self._btn_left else "",
                  command=lambda: self._send_command("go O"), bd=0).grid(row=2, column=0)
        tk.Button(move_frame, image=self._btn_right if self._btn_right else None,
                  text="E" if not self._btn_right else "",
                  command=lambda: self._send_command("go E"), bd=0).grid(row=2, column=2)
        tk.Button(move_frame, image=self._btn_down if self._btn_down else None,
                  text="S" if not self._btn_down else "",
                  command=lambda: self._send_command("go S"), bd=0).grid(row=3, column=1)
        tk.Button(move_frame, text="⬇ Bas", command=lambda: self._send_command("go D"),
                  width=8).grid(row=4, column=0, columnspan=3, sticky="ew")
        tk.Button(move_frame, text="↩ Retour", command=lambda: self._send_command("back"),
                  width=8).grid(row=5, column=0, columnspan=3, sticky="ew", pady=(4, 0))

        # Actions buttons
        act_frame = ttk.LabelFrame(actions_panel, text="⚡ Actions")
        act_frame.grid(row=2, column=0, sticky="ew", pady=4)
        
        tk.Button(act_frame, text="👁 Regarder", command=lambda: self._send_command("look"),
                  **btn_style).grid(row=0, column=0, sticky="ew", pady=1)
        tk.Button(act_frame, text="📜 Historique", command=lambda: self._send_command("history"),
                  **btn_style).grid(row=1, column=0, sticky="ew", pady=1)
        tk.Button(act_frame, text="✋ Prendre", command=self._prompt_take,
                  **btn_style).grid(row=2, column=0, sticky="ew", pady=1)
        tk.Button(act_frame, text="📦 Déposer", command=self._prompt_drop,
                  **btn_style).grid(row=3, column=0, sticky="ew", pady=1)
        tk.Button(act_frame, text="💬 Parler", command=self._prompt_talk,
                  **btn_style).grid(row=4, column=0, sticky="ew", pady=1)

        # Quests buttons
        quest_frame = ttk.LabelFrame(actions_panel, text="📋 Quêtes")
        quest_frame.grid(row=3, column=0, sticky="ew", pady=4)
        
        tk.Button(quest_frame, text="📋 Voir quêtes", command=lambda: self._send_command("quests"),
                  **btn_style).grid(row=0, column=0, sticky="ew", pady=1)
        tk.Button(quest_frame, text="🏆 Récompenses", command=lambda: self._send_command("rewards"),
                  **btn_style).grid(row=1, column=0, sticky="ew", pady=1)

        # Quit button
        tk.Button(actions_panel,
                  image=self._btn_quit if self._btn_quit else None,
                  text="🚪 Quitter" if self._btn_quit is None else "",
                  command=lambda: self._send_command("quit"),
                  **btn_style if self._btn_quit is None else {"bd": 0}).grid(row=4, column=0, sticky="ew", pady=(8, 2))

        # ============ ROW 2: BOTTOM - Inventory + Entry ============
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=(3, 6))
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=2)

        # Inventory panel (left)
        inv_frame = ttk.LabelFrame(bottom_frame, text="🎒 Inventaire")
        inv_frame.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        
        self.inventory_listbox = tk.Listbox(inv_frame, height=3, bg="#16213e", fg="#eee",
                                            selectbackground="#e94560", font=("Helvetica", 10))
        self.inventory_listbox.pack(fill="x", padx=5, pady=5)
        self.inventory_listbox.bind("<Double-1>", lambda e: self._drop_selected())

        # Command entry (right)
        entry_frame = ttk.LabelFrame(bottom_frame, text="⌨️ Commande")
        entry_frame.grid(row=0, column=1, sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        entry_container = ttk.Frame(entry_frame)
        entry_container.pack(fill="x", padx=5, pady=5)
        entry_container.grid_columnconfigure(0, weight=1)

        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(entry_container, textvariable=self.entry_var, font=("Courier", 11))
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

        send_btn = tk.Button(entry_container, text="Envoyer", command=self._on_enter,
                             bg="#e94560", fg="white", font=("Helvetica", 10, "bold"))
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
        if not self.game.player or not self.game.player.current_room:
            return
        room = self.game.player.current_room
        for item_name, item in room.inventory.items():
            self.objects_listbox.insert(tk.END, f"  {item_name} - {item.description}")

    def _update_characters_list(self):
        """Mettre à jour la liste des personnages présents."""
        self.chars_listbox.delete(0, tk.END)
        if not self.game.player or not self.game.player.current_room:
            return
        room = self.game.player.current_room
        for char_name, char in room.characters.items():
            self.chars_listbox.insert(tk.END, f"  {char_name} - {char.description}")

    def _update_inventory_list(self):
        """Mettre à jour l'inventaire du joueur."""
        self.inventory_listbox.delete(0, tk.END)
        if not self.game.player:
            return
        if not self.game.player.inventory:
            self.inventory_listbox.insert(tk.END, "  (vide)")
        else:
            for item_name, item in self.game.player.inventory.items():
                self.inventory_listbox.insert(tk.END, f"  {item_name} ({item.weight} kg)")

    # -------- Image update --------
    def _update_room_image(self):
        """Update the canvas image based on the current room."""
        if not self.game.player or not self.game.player.current_room:
            return

        room = self.game.player.current_room
        assets_dir = Path(__file__).parent / 'assets'

        # Use room-specific image if available, otherwise fallback
        if room.image:
            image_path = assets_dir / room.image
        else:
            image_path = assets_dir / 'scene.png'

        try:
            # Load new image
            self._image_ref = tk.PhotoImage(file=image_path)
            # Clear canvas and redraw image
            self.canvas.delete("all")
            self.canvas.create_image(
                self.IMAGE_WIDTH/2,
                self.IMAGE_HEIGHT/2,
                image=self._image_ref
            )
        except Exception:
            # Fallback to text if image not found or cannot be loaded
            self.canvas.delete("all")
            self.canvas.create_text(
                self.IMAGE_WIDTH/2,
                self.IMAGE_HEIGHT/2,
                text=f"Image: {room.name}",
                fill="white",
                font=("Helvetica", 18)
            )


    # -------- Event handlers --------
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
        sys.stdout = self.original_stdout
        self.destroy()


def main():
    """Module entry point: create and run the game."""
    # Create a game object and play the game
    args = __import__('sys').argv[1:]
    # If user asked for CLI explicitly, use console mode
    if '--cli' in args:
        Game().play()
        return

    # If Tkinter is available, try to launch GUI, otherwise fallback to CLI
    if tk is not None:
        try:
            app = GameGUI()
            app.mainloop()
            return
        except tk.TclError as e:
            print(f"GUI indisponible ({e}). Passage en mode console.")

    # Fallback to console mode
    Game().play()


if __name__ == "__main__":
    main()

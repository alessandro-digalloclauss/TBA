# Description: Game class

"""Module principal du jeu d'aventure textuel.

Contient la classe `Game` qui assemble les pièces, les commandes et le
joueur, et exécute la boucle principale du jeu.
"""

# Import des modules

from pathlib import Path

# Optional: import Tkinter for GUI. If unavailable, GUI will be skipped.
try:
    import tkinter as tk
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
        cmd_unlock = Command(
            "déverrouiller",
            " <objet> : déverrouiller un objet avec une clé",
            Actions.unlock,
            1,
        )
        self.commands["déverrouiller"] = cmd_unlock
        # Alias anglais pour unlock
        cmd_unlock_en = Command(
            "unlock",
            " <object> : unlock an object with a key",
            Actions.unlock,
            1,
        )
        self.commands["unlock"] = cmd_unlock_en
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
                "Visiter Cuisine",
                "Visiter Bureau",
                "Visiter Jardin_hiver",
            ],
            reward="Exploration du rez-de chaussée",
            completion_message="Bravo ! Vous avez exploré les pièces principales du manoir. Votre sens de l'observation sera précieux pour résoudre cette enquête.",
        )

        # Quête de déplacement
        travel_quest = Quest(
            title="Grand Voyageur",
            description="Déplacez-vous 10 fois à travers le manoir.",
            objectives=["Se déplacer 10 fois"],
            reward="Pistes d'investigations",
            completion_message="Félicitations ! Vous avez exploré le manoir en profondeur. Ces pistes d'investigations vous aideront à résoudre le mystère.",
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
            reward="Clé du Mystère",
            completion_message="Félicitations ! Vous avez découvert tous les secrets du manoir. La Clé du Mystère vous est remise : elle pourrait bien ouvrir la vérité sur cette sombre affaire...",
        )

        # Quête de rencontre avec les PNJ
        pnj_quest = Quest(
            title="Rencontres Mystérieuses",
            description="Interrogez tous les suspects présents dans le manoir.",
            objectives=[
                "Parler avec Emile",
                "Parler avec Clara Beaumont",
                "Parler avec Victor Lenoir",
                "Parler avec Hélène de Valenbourg",
                "Parler avec Maurice Delcourt",
            ],
            reward="Pistes d'investigations",
            completion_message="Félicitations ! Vous avez interrogé tous les suspects du manoir. Chacun semble cacher quelque chose... mais un seul est le coupable.",
        )

        # Quête du livre étrange
        livre_quest = Quest(
            title="Le Livre Étrange",
            description="Trouvez et prenez le mystérieux livre étrange caché dans le manoir.",
            objectives=[
                "Prendre livre étrange",
            ],
            reward="Récompenses mystérieuses inconnues",
            completion_message="Vous avez trouvé le livre étrange ! En l'ouvrant, vous découvrez des pages couvertes de symboles anciens... Quelque chose de mystérieux se révèle à vous.",
        )

        # Ajouter les quêtes au gestionnaire du joueur
        self.player.quest_manager.add_quest(exploration_quest)
        self.player.quest_manager.add_quest(travel_quest)
        self.player.quest_manager.add_quest(secrets_quest)
        self.player.quest_manager.add_quest(pnj_quest)
        self.player.quest_manager.add_quest(livre_quest)

        # Activer automatiquement toutes les quêtes au démarrage
        self.player.quest_manager.activate_quest("Explorateur du Manoir")
        self.player.quest_manager.activate_quest("Grand Voyageur")
        self.player.quest_manager.activate_quest("Découvreur de Secrets")
        self.player.quest_manager.activate_quest("Rencontres Mystérieuses")
        self.player.quest_manager.activate_quest("Le Livre Étrange")

    def _create_world(self):
        """Créer les pièces, peupler les inventaires et relier les sorties.

        Retourne la pièce de départ (hall).
        """
        # Créer toutes les pièces et les stocker dans un dict pour y référer facilement
        rooms = {}
        rooms['jardin_hiver'] = Room(
            'Jardin_hiver',
            "🌿 Jardin d'hiver",
            'Des plantes exotiques sont en désordre sous une vitre brisée.'
        )
        rooms['hall'] = Room(
            'Hall',
            'Hall',
            "Le vaste hall est dominé par un grand lustre immobile. L'horloge s'est arrêtée à 22:30."
        )
        rooms['salon_victorien'] = Room(
            'Salon_Victorien',
            'Salon victorien',
            'On voit des fauteuils usés et une cheminée froide.'
        )
        rooms['cuisine'] = Room(
            'Cuisine',
            '🍲 Cuisine',
            "On y trouve un chaudron fumant et des couteaux alignés, l'un manque."
        )
        rooms['bureau'] = Room(
            'Bureau',
            'Bureau',
            "C'EST L'HORREUR ! Un corps gît au sol, entouré de sang et de papiers éparpillés."
        )
        rooms['couloir'] = Room(
            'Couloir',
            '🚪 Couloir',
            "Le long couloir est sombre et le parquet grince sous vos pas. Des traces de pas boueuses mènent vers la bibliothèque."
        )
        rooms['chambre'] = Room(
            'Chambre',
            '🛏️ Chambre',
            'Le lit est défait et la fenêtre est entrouverte.'
        )
        rooms['bibliotheque'] = Room(
            'Bibliotheque',
            '📖 Bibliothèque',
            "De hauts rayonnages remplis de livres anciens couvrent les murs. Un vieux livre mal rangé dépasse de l'étagère."
        )
        rooms['piece_cachee'] = Room(
            'Pièce_cachée',
            '🕯️ Pièce cachée',
            "Une petite pièce secrète est faiblement éclairée par une lanterne. Un vieux tiroir du bureau retient l'attention."
        )
        rooms['cave_a_vin'] = Room(
            'Cave_a_vin',
            '🍷 Cave à vin',
            'La cave est fraîche et humide, remplie de bouteilles anciennes.'
        )
        rooms['atelier'] = Room(
            'Atelier',
            '🛠️ Atelier',
            "Des outils et des plans froissés sont éparpillés sur l'établi."
        )

        # Collecter les pièces dans la liste du jeu
        self.rooms = list(rooms.values())

        # Configuration des images de fond pour chaque pièce
        rooms['hall'].image = 'bg_hall.png'
        rooms['jardin_hiver'].image = 'bg_jardin.png'
        rooms['salon_victorien'].image = 'bg_salon.png'
        rooms['cuisine'].image = 'bg_cuisine.png'
        rooms['bureau'].image = 'bg_bureau.png'
        rooms['couloir'].image = 'bg_couloir.png'
        rooms['chambre'].image = 'bg_chambre.png'
        rooms['bibliotheque'].image = 'bg_bibliotheque.png'
        rooms['piece_cachee'].image = 'bg_piece_cachee.png'
        rooms['cave_a_vin'].image = 'bg_cave.png'
        rooms['atelier'].image = 'bg_atelier.png'

        # Configuration des positions des sprites pour le Hall
        rooms['hall'].sprite_positions = {
            'cle': (100, 250),
            'manteau': (300, 200),
            'registre des invités': (200, 260),
        }

        # Configuration des positions des sprites pour le Jardin d'hiver
        rooms['jardin_hiver'].sprite_positions = {
            'plantes renversées': (150, 220),
            'gants de jardinage propres': (280, 180),
            'Émile': (80, 150),  # Position du personnage Émile
        }

        # Configuration des positions des sprites pour le Bureau (placer le corps, la montre et le carnet)
        rooms['bureau'].sprite_positions = {
            'corps': (420, 320),
            'montre cassée': (460, 320),  # au poignet droit du corps
            "carnet de rdv d'Armand": (380, 330),  # posé près du bureau
        }

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
        rooms['hall'].inventory['manteau'] = Item('manteau', "un manteau élégant, peut-être appartenant à un invité", 1.5, image='item_manteau.png')
        # Registre des invités 
        rooms['hall'].inventory['registre des invités'] = Item(
            'registre des invités',
            "un registre à couverture épaisse où sont notés les noms des invités",
            0.6,
            detail=(
                "Registre des invités, à la date d'hier soir) :\n"
                "- Hélène de Valenbourg : épouse, présence silencieuse\n"
                "- Victor Lenoir : ingénieur, invité de l'atelier\n"
                "- Maurice Delcourt : archiviste, visiteur studieux\n"
                "- Clara Beaumont : invitée, lectrice reconnue\n"
                "- Emile : jardinier, employé du manoir\n\n"
                "Note: Ce registre recense les présents pour la soirée — pourrait contenir des indices sur les rencontres de la veille."
            )
        )

        # Cuisine
        rooms['cuisine'].inventory['couteau'] = Item('couteau', 'un couteau émoussé', 0.5)
        rooms['cuisine'].inventory['livre'] = Item(
            'livre', "un livre appartenant à Clara, laissé sur la table, pages ouvertes", 0.8,
            detail="Le livre porte le nom 'Clara Beaumont' inscrit à l'intérieur de la couverture."
        )

        # Salon victorien
        rooms['salon_victorien'].inventory['lettre'] = Item(
            'lettre', "une lettre à moitié brûlée; l'encre est encore à demi lisible", 0.05,
            detail="La lettre est partiellement consumée, mais on peut encore lire :\n\"Ma chère Clara,\nRetrouvez-moi dans la cuisine à 22h. Je voudrais discuter avec vous de ce dernier livre que vous m'avez passé, je viendrai avec Emile qui commence à s'intéresser à la lecture.\n- H.\"\nCette lettre semble prouver qu'Hélène, Clara et Emile étaient probablement ensemble au moment du drame..."
        )

        # Bureau
        rooms['bureau'].inventory['corps'] = Item(
            'corps',
            "le corps sans vie du maître de maison, Armand de Valenbourg, étendu au sol, entouré de sang",
            80.0,
            detail="À en juger par les marques sur le corps, il semble que le maître ait été poignardé. Une montre cassée est arrêtée à 22h30 au poignet."
        )
        # Montre cassée retrouvée au poignet du corps
        rooms['bureau'].inventory['montre cassée'] = Item(
            'montre cassée',
            "une montre cassée, au verre fissuré; l'aiguille est figée et l'affichage indique 22:30, comme arrêtée au moment du drame",
            0.05,
            detail="La montre est arrêtée à 22:30; Elle est encore attachée au bracelet qui entoure le poignet du corps. L'heure du crime était alors probablement aux alentours de 22h."
        )
        # Carnet de rendez-vous d'Armand déplacé ici depuis le Hall
        rooms['bureau'].inventory["carnet de rdv d'Armand"] = Item(
            "carnet de rdv d'Armand",
            "un petit carnet de rendez-vous en cuir usé; des heures et des notes griffonnées à la hâte y figurent",
            0.2,
            detail="Le carnet semble appartenir à Armand de Valenbourg, à la date d'hier : 22h - discussion privée à propos du manuscrit"
        )

        # Chambre
        rooms['chambre'].inventory['pistolet'] = Item(
            'pistolet', 'un petit pistolet trouvé caché dans un tiroir', 1.2
        )
        rooms['chambre'].inventory['bijoux'] = Item('bijoux', 'un écrin contenant des bijoux précieux', 0.3)

        # Couloir
        rooms['couloir'].inventory['empreintes de pas'] = Item(
            'empreintes de pas', "des traces de pas boueuses sur le parquet", 0.0,
            detail="Les empreintes semblent provenir de bottes de jardinage. Elles mènent de l'escalier vers la bibliothèque, puis reviennent... la boue peut dater d'hier."
        )

        # Bibliothèque
        rooms['bibliotheque'].inventory['grimoire'] = Item(
            'grimoire', 'un vieux grimoire relié de cuir', 1.2
        )
        rooms['bibliotheque'].inventory['livre étrange'] = Item(
            'livre étrange', 'un livre à la reliure étrange, dépasse de l\'une des étagères', 1.1,
            detail="La reliure cache un petit mécanisme; des marques d'usure montrent qu'il a déjà été manipulé récemment."
        )
        rooms['bibliotheque'].inventory['échelle déplacée'] = Item('échelle déplacée', 'une échelle roulante déplacée', 5.0)

        # Pièce cachée - la clé et le tiroir fermé sont visibles au début
        rooms['piece_cachee'].inventory['clé secrète'] = Item('clé secrète', 'une clé petite et finement ciselée', 0.1,
            detail="Très fine, cette clé semble correspondre au tiroir dans le coin de la pièce..."
        )
        rooms['piece_cachee'].inventory['tiroir fermé'] = Item(
            'tiroir fermé',
            "tiroir fermé;",
            1.5,
            detail="Le tiroir est verrouillé. Il faudra une clé appropriée pour l'ouvrir."
        )
        # Positions des sprites pour la pièce cachée
        rooms['piece_cachee'].sprite_positions = {
            'clé secrète': (150, 280),
            'tiroir fermé': (250, 280),
        }

        # Cave à vin
        rooms['cave_a_vin'].inventory['bouteille brisée'] = Item('bouteille brisée', 'des éclats de bouteille et du vin renversé', 0.2)
        rooms['cave_a_vin'].inventory['traces effacées'] = Item('traces effacées', "des marques nettoyées, comme si on avait tenté d'effacer des indices", 0.0)
        rooms['cave_a_vin'].inventory['tonneau déplacé'] = Item('tonneau déplacé', 'un tonneau déplacé laissant un espace vide', 20.0)

        # Atelier
        # Indices importants
        rooms['atelier'].inventory['gants tachés de sang'] = Item(
            'gants tachés de sang', "une paire de gants tachés de sang, indice potentiel", 0.1,
        )
        rooms['atelier'].inventory['outils lourds'] = Item('outils lourds', "une caisse d'outils lourds", 15.0)
        rooms['atelier'].inventory['note manuscrite'] = Item(
            'note manuscrite', "une note griffonnée à la hâte, tombée sous l'établi", 0.02,
            detail="La note indique : 'Club lecture - 22h - Cuisine. Hélène, Clara, Emile confirmés.'\nL'écriture est élégante et penchée... En comparant avec le registre des invités, on reconnaît l'écriture de Maurice Delcourt. Que faisait cette note dans l'atelier ? Maurice est-il passé ici ?"
        )
        rooms['atelier'].inventory['couteau ensanglanté'] = Item(
            'couteau ensanglanté', "un couteau de cuisine couvert de sang séché, caché derrière un établi", 0.4,
            detail="L'arme du crime ! La lame est couverte de sang séché. Étrangement, aucune empreinte digitale n'est visible sur le manche... impossible d'infentifier qui l'a utilisé?"
        )

        # Ajouter les personnages non joueurs dans les pièces
        rooms['jardin_hiver'].characters['Emile'] = Character(
            'Emile',
            "le jardinier silencieux, il connaît des passages secrets...",
            rooms['jardin_hiver'],
            ["Je préfère rester discret... les passages cachés, peu les connaissent. Excusez mes bottes sales, c'est normal pour un jardinier... Vous savez, Hélène et Armand ne s'entendaient plus trop ces derniers temps... Peut-être qu'elle en avait assez et qu'elle voulait la fortune pour elle seule."],
            image='npc_emile.png'
        )
        rooms['cuisine'].characters['Clara Beaumont'] = Character(
            'Clara Beaumont',
            "l'invitée cultivée, étrangement calme malgré le drame...",
            rooms['cuisine'],
            ["Les livres disent parfois plus que les gens. J'étais dans la cuisine cette nuit-là. Le jardinier, Emile... Il connaissait tous les secrets d'Armand. Il travaille ici depuis des années et il voit tout, entend tout."],
            image='npc_clara.png'
        )
        rooms['atelier'].characters['Victor Lenoir'] = Character(
            'Victor Lenoir',
            "l'ingénieur très intelligent, blessé avec des égratignures sur les mains et une coupure au front...",
            rooms['atelier'],
            ["Les mécanismes peuvent être trompeurs. Je conçois des dispositifs, pas des crimes. Entre nous... *il baisse la voix* ...méfiez-vous de Maurice. Ces blessure ? Je me suis blessé à l'atelier."],
            image='npc_victor.png'
        )
        rooms['salon_victorien'].characters['Hélène de Valenbourg'] = Character(
            'Hélène de Valenbourg',
            "l'épouse froide, héritière de la fortune du défunt...(possède une arme à feu)",
            rooms['salon_victorien'],
            ["Je suis encore sous le choc. Armand avait beaucoup d'ennemis... Je n'ai rien à cacher. Maintenant que j'y pense... Maurice et Armand parlaient tout le temps d'un grimoire ces derniers temps. Ils se sont même disputés violemment à ce sujet, la veille du drame."],
            image='npc_helene.png'
        )
        rooms['bibliotheque'].characters['Maurice Delcourt'] = Character(
            'Maurice Delcourt',
            "l'archiviste obsédé par un manuscrit ancien...",
            rooms['bibliotheque'],
            ["Les vieux manuscrits ont des secrets que certains paieraient cher pour découvrir. Si quelqu'un était assez ingénieux pour commettre un meurtre sans faire le moindre bruit, ce serait Victor. Cet homme connaît tous les mécanismes du manoir, je m'en méfierai si j'étais vous"],
            image='npc_maurice.png'
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
            'O': None,
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
            "Le manoir d'Hiver accueille plusieurs invités pour une soirée privée.\n"
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


def main():
    """Module entry point: create and run the game."""
    import sys
    args = sys.argv[1:]
    # If user asked for CLI explicitly, use console mode
    if '--cli' in args:
        Game().play()
        return

    # If Tkinter is available, try to launch GUI, otherwise fallback to CLI
    if tk is not None:
        try:
            from interface import GameGUI
            app = GameGUI()
            app.mainloop()
            return
        except tk.TclError as e:
            print(f"GUI indisponible ({e}). Passage en mode console.")

    # Fallback to console mode
    Game().play()


if __name__ == "__main__":
    main()

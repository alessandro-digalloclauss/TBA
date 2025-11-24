# Description: Game class

"""Simple text-adventure game module.

Contains the Game class which wires rooms, commands and the player
and runs the main loop.
"""

# Import modules

from room import Room
from player import Player
from command import Command
from actions import Actions

class Game:
    """Main game container: rooms, commands, and player state."""

    # Constructor
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        # Initialize directions and aliases early so they exist
        # even if _create_world() is used directly in tests.
        self.directions = set(["N", "E", "S", "O", "U", "D"])  # nord, est, sud, ouest, up, down
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
    
    # Setup the game
    def setup(self):
        """Create rooms, commands and place the player in the starting room."""

        # Setup commands

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
        # Directions used in the game (canonical single-letter codes)
        # and aliases mapping various user inputs to the canonical code.
        self.directions = set(["N", "E", "S", "O", "U", "D"])  # nord, est, sud, ouest, up, down
        # Map common words/variants (case-insensitive) to canonical direction letters.
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
        # Create world (rooms, inventories, exits)
        start_room = self._create_world()

        # Setup player and starting room
        self.player = Player(input("\nEntrez votre nom: "))
        # Start player in the hall by default
        self.player.current_room = start_room

    def _create_world(self):
        """Create rooms, populate inventories and wire exits.

        Returns the starting room (hall).
        """
        # Create all rooms and keep them in a dict for easy referencing
        rooms = {}
        rooms['jardin_hiver'] = Room(
            'Jardin_hiver',
            "le jardin d'hiver, des plantes exotiques,",
            "le jardin d'hiver, des plantes exotiques poussent en "
            "désordre; les feuilles, encore humides, brillent sous une "
            "vitre partiellement brisée, et l'air est lourd d'une humidité "
            "ancienne."
        )
        rooms['hall'] = Room(
            'Hall',
            'un vaste hall éclairé par un grand lustre.',
            "un vaste hall, un grand lustre pend au plafond et "
            "projette des ombres mouvantes; le marbre poli renvoie des "
            "reflets glacés et l'espace respire un calme solennel."
        )
        rooms['salon_victorien'] = Room(
            'Salon_Victorien',
            'le salon victorien, il y a une grande cheminée éteinte,',
            'le salon victorien, la grande cheminée est froide; '
            'les fauteuils en cuir sont effrangés, et une horloge ancienne '
            'égrène un tic-tac irrégulier qui résonne dans la pièce.'
        )
        rooms['cuisine'] = Room(
            'Cuisine',
            'la cuisine, on trouve un chaudron posé sur la cuisinière,',
            'la cuisine, un grand chaudron fume faiblement sur la '
            'cuisinière; les couteaux sont alignés sur le plan de travail, '
            "mais l'un d'eux manque, comme si quelqu'un était parti "
            'précipitamment.'
        )
        rooms['bureau'] = Room(
            'Bureau',
            "le bureau les boiseries sont sombres, un cadavre gis sur le sol.",
            "le bureau, les boiseries sombres absorbent la lumière; "
            "un corps gît au pied d'une étagère renversée, le coffre-fort "
            "est ouvert et des papiers éparpillés révèlent des indices "
            "anciens et troublants."
        )
        rooms['couloir'] = Room(
            'Couloir',
            'un long couloir sombre aux lumières vacillantes.',
            'un long couloir, les appliques vacillent et projettent '
            'des halos tremblants; le parquet grince et chaque pas semble '
            "réveiller des échos du passé."
        )
        rooms['chambre'] = Room(
            'Chambre',
            'la chambre, le lit est défait, la fenêtre entrouverte,',
            "la chambre, le lit est défait et les draps froissés; la "
            "fenêtre est entrouverte et un parfum indéfini flotte, comme "
            "un souvenir qu'on ne parvient pas à nommer."
        )
        rooms['bibliotheque'] = Room(
            'Bibliotheque',
            'la bibliothèque, il y a une odeur de vieux livres,',
            "la bibliothèque, des étagères alourdies de volumes "
            "montent jusqu'au plafond; l'odeur du papier ancien et l'ombre "
            "d'une échelle roulante forment un refuge poussiéreux."
        )
        rooms['piece_cachee'] = Room(
            'Pièce_cachée',
            'une pièce secrète dissimulée derrière un mur.',
            "une pièce secrète, une seule lanterne vacille et projette "
            "des ombres dans lesquelles danseraient d'anciens secrets; un "
            "coffre verrouillé repose dans un coin, promettant des "
            "réponses et des dangers."
        )
        rooms['cave_a_vin'] = Room(
            'Cave_a_vin',
            "la cave à vin est fraîche et humide. Des rangées de bouteilles",
            "la cave à vin, l'air est frais et humide; des bouteilles "
            "anciennes dorment dans des casiers de pierre, et une odeur de "
            "terre et de bois mouillé rappelle des années oubliées."
        )
        rooms['atelier'] = Room(
            'Atelier',
            "l'atelier, il y a des outils, des pièces mécaniques et des",
            "l'atelier, des outils sont éparpillés et des pièces "
            "mécaniques attendent d'être assemblées; des plans froissés "
            "jonchent l'établi et une lampe vacillante jette une lueur "
            "tremblante."
        )

        # Collect rooms in the game's room list
        self.rooms = list(rooms.values())

        # Add a few example items into some rooms (name -> description)
        rooms['jardin_hiver'].inventory['plante étrange'] = (
            'une plante aux feuilles veinées'
        )
        rooms['hall'].inventory['cle'] = 'une petite clé rouillée'
        rooms['cuisine'].inventory['couteau'] = 'un couteau émoussé'
        rooms['bibliotheque'].inventory['grimoire'] = (
            'un vieux grimoire relié de cuir'
        )
        rooms['cave_a_vin'].inventory['bouteille'] = (
            "une bouteille d'un millésime inconnu"
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
            'E': None,
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
            'O': rooms['atelier'],
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
        rooms['bibliotheque'].exits = {
            'N': None,
            'E': rooms['piece_cachee'],
            'S': None,
            'O': rooms['couloir'],
            'U': None,
            'D': None,
        }
        rooms['piece_cachee'].exits = {
            'N': None,
            'E': None,
            'S': None,
            'O': rooms['bibliotheque'],
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

    # Print the welcome message
    def print_welcome(self):
        """Show a short welcome and the current room description."""
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("Entrez 'help' si vous avez besoin d'aide.")
        print(self.player.current_room.get_long_description())


def main():
    """Module entry point: create and run the game."""
    # Create a game object and play the game
    Game().play()


if __name__ == "__main__":
    main()

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
            " <direction> : se déplacer dans une direction cardinale (N, E, S, O, U, D)",
            Actions.go,
            1,
        )
        self.commands["go"] = go
        
        # Setup rooms

        jardin_hiver = Room(
            "Jardin_hiver",
            "Dans le jardin d'hiver, des plantes exotiques, "
            "une vitre brisée sur un côté.",
            "dans le jardin d'hiver, des plantes exotiques poussent en désordre; "
            "les feuilles, encore humides, brillent sous une vitre partiellement brisée, "
            "et l'air est lourd d'une humidité ancienne."
        )
        self.rooms.append(jardin_hiver)
        hall = Room(
            "Hall",
            "dans un vaste hall éclairé par un grand lustre. "
            "Le marbre du sol renvoie une lueur froide.",
            "dans un vaste hall, un grand lustre pend au plafond et projette des ombres mouvantes; "
            "le marbre poli renvoie des reflets glacés et l'espace respire un calme solennel."
        )
        self.rooms.append(hall)
        salon_victorien = Room(
            "Salon_Victorien",
            "dans le salon victorien, il y a une grande cheminée éteinte, "
            "des fauteuils en cuir, une horloge ancienne qui fait un bruit inquiétant.",
            "dans le salon victorien, la grande cheminée est froide; les fauteuils en cuir sont effrangés, "
            "et une horloge ancienne égrène un tic-tac irrégulier qui résonne dans la pièce."
        )
        self.rooms.append(salon_victorien)
        cuisine = Room(
            "Cuisine",
            "dans la cuisine, on trouve un chaudron posé sur la cuisinière, "
            "des couteaux bien alignés (sauf un).",
            "dans la cuisine, un grand chaudron fume faiblement sur la cuisinière; "
            "les couteaux sont alignés sur le plan de travail, mais l'un d'eux manque, "
            "comme si quelqu'un était parti précipitamment."
        )
        self.rooms.append(cuisine)
        bureau = Room(
            "Bureau",
            "dans le bureau les boiseries sont sombres, un cadavre gis sur le sol."
            "une grosse étagère est renversée sur lui, on trouve un coffre-fort ouvert, "
            "des papiers dispersés.",
            "dans le bureau, les boiseries sombres absorbent la lumière; un corps gît au pied d'une étagère renversée, "
            "le coffre-fort est ouvert et des papiers éparpillés révèlent des indices anciens et troublants."
        )
        self.rooms.append(bureau)

        couloir = Room(
            "Couloir",
            "dans un long couloir sombre aux lumières vacillantes. "
            "Le parquet grince à chaque pas.",
            "dans un long couloir, les appliques vacillent et projettent des halos tremblants; "
            "le parquet grince et chaque pas semble réveiller des échos du passé."
        )
        self.rooms.append(couloir)
        chambre = Room(
            "Chambre",
            "dans la chambre, le lit est défait, la fenêtre entrouverte, "
            "un parfum étrange dans l'air.",
            "dans la chambre, le lit est défait et les draps froissés; la fenêtre est entrouverte et un parfum indéfini flotte, "
            "comme un souvenir qu'on ne parvient pas à nommer."
        )
        self.rooms.append(chambre)
        bibliotheque = Room(
            "Bibliotheque",
            "dans la bibliothèque, il y a une odeur de vieux livres, "
            "une lumière tamisée, une échelle roulante.",
            "dans la bibliothèque, des étagères alourdies de volumes montent jusqu'au plafond; "
            "l'odeur du papier ancien et l'ombre d'une échelle roulante forment un refuge poussiéreux."
        )
        self.rooms.append(bibliotheque)
        piece_cachee = Room(
            "Pièce_cachée",
            "dans une pièce secrète dissimulée derrière un mur. "
            "Une lanterne vacille, un coffre verrouillé repose dans un coin.",
            "dans une pièce secrète, une seule lanterne vacille et projette des ombres dans lesquelles danseraient d'anciens secrets; "
            "un coffre verrouillé repose dans un coin, promettant des réponses et des dangers."
        )
        self.rooms.append(piece_cachee)

        cave_a_vin = Room(
            "Cave_a_vin",
            "dans la cave à vin est fraîche et humide. Des rangées de bouteilles "
            "anciennes reposent dans des casiers en pierre. Une odeur de terre "
            "et de vieux bois remplit l'air.",
            "dans la cave à vin, l'air est frais et humide; des bouteilles anciennes dorment dans des casiers de pierre, "
            "et une odeur de terre et de bois mouillé rappelle des années oubliées."
        )
        self.rooms.append(cave_a_vin)
        atelier = Room(
            "Atelier",
            "dans l'atelier, il y a des outils, des pièces mécaniques et des "
            "plans étalés sur un établi. Une lampe vacillante éclaire "
            "difficilement la pièce.",
            "dans l'atelier, des outils sont éparpillés et des pièces mécaniques attendent d'être assemblées; "
            "des plans froissés jonchent l'établi et une lampe vacillante jette une lueur tremblante."
        )
        self.rooms.append(atelier)

        # Create exits for rooms

        jardin_hiver.exits = {
            "N": None,
            "E": hall,
            "S": None,
            "O": None,
            "U": None,
            "D": None,
        }
        hall.exits = {
            "N": None,
            "E": salon_victorien,
            "S": cuisine,
            "O": jardin_hiver,
            "U": couloir,
            "D": None,
        }
        salon_victorien.exits = {
            "N": None,
            "E": None,
            "S": bureau,
            "O": hall,
            "U": None,
            "D": None,
        }
        cuisine.exits = {
            "N": hall,
            "E": None,
            "S": None,
            "O": salon_victorien,
            "U": None,
            "D": cave_a_vin,
        }
        bureau.exits = {
            "N": salon_victorien,
            "E": None,
            "S": None,
            "O": cuisine,
            "U": None,
            "D": None,
        }

        cave_a_vin.exits = {
            "N": None,
            "E": atelier,
            "S": None,
            "O": None,
            "U": cuisine,
            "D": None,
        }
        atelier.exits = {
            "N": None,
            "E": None,
            "S": None,
            "O": atelier,
            "U": None,
            "D": None,
        }

        couloir.exits = {
            "N": chambre,
            "E": bibliotheque,
            "S": None,
            "O": None,
            "U": None,
            "D": cuisine,
        }
        chambre.exits = {
            "N": None,
            "E": None,
            "S": couloir,
            "O": None,
            "U": None,
            "D": None,
        }
        bibliotheque.exits = {
            "N": None,
            "E": piece_cachee,
            "S": None,
            "O": couloir,
            "U": None,
            "D": None,
        }
        piece_cachee.exits = {
            "N": None,
            "E": None,
            "S": None,
            "O": bibliotheque,
            "U": None,
            "D": None,
        }


        # Setup player and starting room

        self.player = Player(input("\nEntrez votre nom: "))
        # Start player in the hall by default
        self.player.current_room = hall

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

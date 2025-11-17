# Description: Game class

# Import modules

from room import Room
from player import Player
from command import Command
from actions import Actions

class Game:

    # Constructor
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
    
    # Setup the game
    def setup(self):

        # Setup commands

        help = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["help"] = help
        quit = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["quit"] = quit
        go = Command("go", " <direction> : se déplacer dans une direction cardinale (N, E, S, O, U, D)", Actions.go, 1)
        self.commands["go"] = go
        
        # Setup rooms

        jardin_hiver = Room("Jardin_hiver", "Dans le jardin d'hiver, des plantes exotiques, une vitre brisée sur un côté.")
        self.rooms.append(jardin_hiver)
        hall = Room("Hall", "Un vaste hall éclairé par un grand lustre. Le marbre du sol renvoie une lueur froide.")
        self.rooms.append(hall)
        salon_victorien = Room("Salon_Victorien", "Dans le salon victorien, il y a une grande cheminée éteinte, des fauteuils en cuir, une horloge ancienne qui fait un bruit inquiétant.")
        self.rooms.append(salon_victorien)
        cuisine = Room("Cuisine", "Dans la cuisine, on trouve un chaudron posé sur la cuisinière, des couteaux bien alignés (sauf un).")
        self.rooms.append(cuisine)
        bureau = Room("Bureau", "Dans le bureau les boiseries sont sombres, on trouve un coffre-fort, des papiers dispersés.")
        self.rooms.append(bureau)

        couloir = Room("Couloir", "Un long couloir sombre aux lumières vacillantes. Le parquet grince à chaque pas.")
        self.rooms.append(couloir)
        chambre = Room("Chambre", "Le lit de la chambre est défait, la fenêtre entrouverte, un parfum étrange dans l'air.")
        self.rooms.append(chambre)
        bibliothèque = Room("Bibliothèque", "Il y a une odeur de vieux livres, une lumière tamisée, une échelle roulante.")
        self.rooms.append(bibliothèque)
        pièce_cachée = Room("Pièce_cachée", "Une pièce secrète dissimulée derrière un mur. Une lanterne vacille, un coffre verrouillé repose dans un coin.")
        self.rooms.append(pièce_cachée)

        cave_a_vin = Room("Cave_a_vin", "La cave à vin est fraîche et humide. Des rangées de bouteilles anciennes reposent dans des casiers en pierre. Une odeur de terre et de vieux bois remplit l'air.")
        self.rooms.append(cave_a_vin)
        atelier = Room("Atelier", "L'atelier est encombré d'outils, de pièces mécaniques et de plans étalés sur un établi. Une lampe vacillante éclaire difficilement la pièce.")
        self.rooms.append(atelier)

        # Create exits for rooms

        jardin_hiver.exits = {"N" : None, "E" : hall, "S" : None, "O" : None, "U" : None, "D" : None}
        hall.exits = {"N" : None, "E" : salon_victorien, "S" : cuisine, "O" : jardin_hiver, "U" : couloir, "D" : None}
        salon_victorien.exits = {"N" : None, "E" : None, "S" : bureau, "O" : hall, "U" : None, "D" : None}
        cuisine.exits = {"N" : Hall, "E" : None, "S" : None, "O" : salon_victorien, "U" : None, "D" : cave_a_vin}
        bureau.exits = {"N" : salon_victorien, "E" : None, "S" : None, "O" : cuisine, "U" : None, "D" : None}

        cave_a_vin.exits = {"N" : None, "E" : atelier, "S" : None, "O" : None, "U" : cuisine, "D" : None}
        atelier.exits = {"N" : None, "E" : None, "S" : None, "O" : atelier, "U" : None, "D" : None}

        couloir.exits = {"N" : chambre, "E" : bibliothèque, "S" : None, "O" : None, "U" : None, "D" : cuisine}
        chambre.exits = {"N" : None, "E" : None, "S" : couloir, "O" : None, "U" : None, "D" : None}
        bibliothèque.exits = {"N" : None, "E" : pièce_cachée, "S" : None, "O" : couloir, "U" : None, "D" : None}
        pièce_cachée.exits = {"N" : None, "E" : None, "S" : None, "O" : bibliothèque, "U" : None, "D" : None}


        # Setup player and starting room

        self.player = Player(input("\nEntrez votre nom: "))
        # Start player in the cuisine by default (was 'swamp' which is undefined)
        self.player.current_room = cuisine

    # Play the game
    def play(self):
        self.setup()
        self.print_welcome()
        # Loop until the game is finished
        while not self.finished:
            # Get the command from the player
            self.process_command(input("> "))
        return None

    # Process the command entered by the player
    def process_command(self, command_string) -> None:

        # Split the command string into a list of words
        list_of_words = command_string.split(" ")

        command_word = list_of_words[0]

        # If the command is not recognized, print an error message
        if command_word not in self.commands.keys():
            print(f"\nCommande '{command_word}' non reconnue. Entrez 'help' pour voir la liste des commandes disponibles.\n")
        # If the command is recognized, execute it
        else:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)

    # Print the welcome message
    def print_welcome(self):
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("Entrez 'help' si vous avez besoin d'aide.")
        #
        print(self.player.current_room.get_long_description())
    

def main():
    # Create a game object and play the game
    Game().play()
    

if __name__ == "__main__":
    main()

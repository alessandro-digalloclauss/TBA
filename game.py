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
        go = Command("go", " <direction> : se déplacer dans une direction cardinale (N, E, S, O)", Actions.go, 1)
        self.commands["go"] = go
        
        # Setup rooms

        cuisine = Room("Cuisine", "dans la cuisine, on trouve un chaudron posé sur la cuisinière, des couteaux bien alignés (sauf un).")
        self.rooms.append(cuisine)
        salon_victorien = Room("Salon_Victorien", "dans le salon_victorien, il y a une grande cheminée éteinte, des fauteuils en cuir, une horloge ancienne qui fait un bruit inquiétant.")
        self.rooms.append(salon_victorien)
        bibliothèque = Room("Bibliothèque", "Il y a une odeur de vieux livres, une lumière tamisée, une échelle roulante.")
        self.rooms.append(bibliothèque)
        chambre_amis = Room("Chambre_amis", "Le lit de la chambre_amis est défait, la fenêtre entrouverte, un parfum étrange dans l'air.")
        self.rooms.append(chambre_amis)
        jardin_hiver = Room("Jardin_hiver", "Dans le jardin_hiver, des plantes exotiques, une vitre brisée sur un côté.")
        self.rooms.append(jardin_hiver)
        bureau = Room("Bureau", "Dans le bureau les boiseries sont sombres, on trouve un coffre-fort, des papiers dispersés.")
        self.rooms.append(bureau)

        # Create exits for rooms

        cuisine.exits = {"N" : bibliothèque, "E" : salon_victorien, "S" : bureau, "O" : None}
        salon_victorien.exits = {"N" : chambre_amis, "E" : None, "S" : jardin_hiver, "O" : cuisine}
        bibliothèque.exits = {"N" : None, "E" : chambre_amis, "S" : cuisine, "O" : None}
        chambre_amis.exits = {"N" : None, "E" : None, "S" : salon_victorien, "O" : bibliothèque}
        jardin_hiver.exits = {"N" : salon_victorien, "E" : None, "S" : None, "O" : bureau}
        bureau.exits = {"N" : cuisine, "E" : jardin_hiver, "S" : None, "O" : None}

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

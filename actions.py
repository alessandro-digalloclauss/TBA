"""Game actions.

This module exposes the small set of actions used by the game loop.
Each action is a static method accepting (game, list_of_words,
number_of_parameters) and returns True on success.
"""

MSG0 = "\nLa commande '{command_word}' ne prend pas de paramètre.\n"
MSG1 = "\nLa commande '{command_word}' prend 1 seul paramètre.\n"


class Actions:
    """Container for actions used by the game loop."""

    @staticmethod
    def go(game, list_of_words, number_of_parameters):
        """Move the player in a cardinal direction.

        Expected form: go <direction>
        """
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        player = game.player
        direction = list_of_words[1]
        player.move(direction)
        return True

    @staticmethod
    def quit(game, list_of_words, number_of_parameters):
        """Quit the game after printing a farewell message."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        msg = f"\nMerci {player.name} d'avoir joué. Au revoir.\n"
        print(msg)
        game.finished = True
        return True

    @staticmethod
    def help(game, list_of_words, number_of_parameters):
        """Print available commands and their help strings."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False
        print("\nVoici les commandes disponibles:")
        # Print commands in a stable, sorted order by command word so
        # newly added commands like 'back' and 'history' always appear.
        for key in sorted(game.commands.keys()):
            command = game.commands[key]
            print("\t- " + str(command))
        print()
        return True

    @staticmethod
    def back(game, list_of_words, number_of_parameters):
        """Move the player back to the previous room using the player's historique."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        # Player.retour handles printing and returns True/False
        return player.retour()

    @staticmethod
    def history(game, list_of_words, number_of_parameters):
        """Print the player's history (visited rooms)."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        print(player.get_history())
        return True

    @staticmethod
    def look(game, list_of_words, number_of_parameters):
        """Show the items present in the current room (look command)."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        current = getattr(player, 'current_room', None)
        if current is None:
            print("\nVous n'êtes dans aucune pièce.\n")
            return False

        # Room.look prints the inventory and returns True/False
        return current.look()

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

    @staticmethod
    def take(game, list_of_words, number_of_parameters):
        """Take an item present in the current room and add it to the player's inventory.

        Expected form: take <item name>
        """
        # Allow multi-word item names by accepting >= required tokens
        if len(list_of_words) < number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        player = game.player
        current = getattr(player, 'current_room', None)
        if current is None:
            print("\nVous n'êtes dans aucune pièce.\n")
            return False

        # Join remaining words to support multi-word item names
        item_name = " ".join(list_of_words[1:]).strip()
        if not item_name:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Check if the item exists in the room
        if item_name not in current.inventory:
            print(f"\nIl n'y a pas d'item nommé '{item_name}' ici.\n")
            return False

        # Remove from room and add to player's inventory
        obj = current.inventory.pop(item_name)
        player.inventory[item_name] = obj
        print(f"\nVous avez pris '{item_name}' et l'avez mis dans votre inventaire.\n")
        return True

    @staticmethod
    def check(game, list_of_words, number_of_parameters):
        """Display the player's inventory (check command)."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        # Player.get_inventory returns a readable string
        print(player.get_inventory())
        return True

    @staticmethod
    def drop(game, list_of_words, number_of_parameters):
        """Drop an item from the player's inventory into the current room.

        Expected form: drop <item name>
        """
        # Allow multi-word item names by accepting >= required tokens
        if len(list_of_words) < number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        player = game.player
        current = getattr(player, 'current_room', None)
        if current is None:
            print("\nVous n'êtes dans aucune pièce.\n")
            return False

        # Join remaining words to support multi-word item names
        item_name = " ".join(list_of_words[1:]).strip()
        if not item_name:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Check if the player has the item
        if item_name not in player.inventory:
            print(f"\nVous n'avez pas d'item nommé '{item_name}' dans votre inventaire.\n")
            return False

        # Remove from player inventory and add to room inventory
        obj = player.inventory.pop(item_name)
        current.inventory[item_name] = obj
        print(f"\nVous avez reposé '{item_name}' dans la pièce.\n")
        return True

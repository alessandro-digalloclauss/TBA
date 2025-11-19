"""Player representation.

This module provides a small Player class that tracks the player's
name and current room and handles movement between rooms.
"""


class Player:
    """Represents the player and their current location."""

    def __init__(self, name):
        """Create a player with the given display name."""
        self.name = name
        self.current_room = None

    def move(self, direction):
        """Attempt to move the player in `direction`.

        Returns True and prints the new room description on success,
        or returns False and prints an error message when movement is
        not possible.
        """
        # Use dict.get to avoid KeyError if direction is missing.
        next_room = self.current_room.exits.get(direction)

        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            return False

        self.current_room = next_room
        print(self.current_room.get_long_description())
        return True


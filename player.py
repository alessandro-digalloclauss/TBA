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
        # historique: stack (list) of previously visited Room objects
        # Use append() to add a room and pop() to go back.
        self.historique = []
        # inventaire: dictionnaire d'objets ramassés (name -> Item instance or count)
        # Initialisé vide.
        self.inventory = {}
        # Capacité de portage (kg). Valeur par défaut raisonnable.
        self.max_weight = 10.0

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

        # push current room to historique before moving
        if self.current_room is not None:
            self.historique.append(self.current_room)

        self.current_room = next_room
        print(self.current_room.get_long_description())
        return True

    def retour(self):
        """Return to the previous room using the historique stack.

        Returns True if the return succeeded, False if there is no history.
        """
        if not self.historique:
            print("\nImpossible de revenir en arrière : historique vide.\n")
            return False

        previous = self.historique.pop()
        self.current_room = previous
        print(self.current_room.get_long_description())
        return True

    def get_history(self):
        """Return a readable string representing the visited rooms history.

        The history lists rooms in the order they were visited (oldest first).
        Each entry is the room's name (underscores replaced by spaces),
        listed oldest first.
        """
        if not self.historique:
            return "Vous n'avez encore visité aucune pièce."

        lines = ["Vous avez déjà visité les pièces suivantes:"]
        for room in self.historique:
            # Use the room's name and make it more readable by replacing
            # underscores with spaces (e.g. 'Salon_Victorien' -> 'Salon Victorien').
            name = getattr(room, 'name', 'inconnue')
            name = name.replace('_', ' ')
            lines.append(f" - {name}")

        return "\n".join(lines)

    def get_inventory(self) -> str:
        """Return a readable string representing the player's inventory.

        If the inventory is empty, returns a short message in French.
        Otherwise returns a header line followed by one entry per item.
        The inventory is a dict mapping item names to item objects (or other
        values). If the stored value looks like an item (has a description
        attribute) we use its string representation; otherwise we fall back
        to the stored value's string form.
        """
        if not self.inventory:
            return "Votre inventaire est vide."

        lines = ["Vous disposez des items suivants :"]
        total = 0.0
        for name, obj in self.inventory.items():
            # If obj is an Item-like object, prefer its __str__ output.
            if hasattr(obj, "description") and hasattr(obj, "weight"):
                lines.append(f" - {obj}")
                try:
                    total += float(obj.weight)
                except Exception:
                    pass
            else:
                lines.append(f" - {name} : {obj}")

        try:
            max_w = float(self.max_weight)
        except Exception:
            max_w = self.max_weight

        total_display = int(total) if float(total).is_integer() else round(total, 2)
        max_display = int(max_w) if float(max_w).is_integer() else round(max_w, 2)
        lines.append(f"Poids total: {total_display} kg / {max_display} kg max")

        return "\n".join(lines)

    def current_carry_weight(self) -> float:
        """Return the total weight currently carried (sum of item.weight where numeric)."""
        total = 0.0
        for obj in self.inventory.values():
            if hasattr(obj, 'weight'):
                try:
                    total += float(obj.weight)
                except Exception:
                    continue
        return total


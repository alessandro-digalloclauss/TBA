"""Room model and description helpers.

This module defines the Room class used by the game. Rooms support a
rich first-visit description and a shorter description for subsequent
visits. Ambient lines are chosen to increase immersion.
"""

import random


class Room:
    """Representation of a room in the game world."""

    def __init__(self, name, description, first_visit_description=None, short_description=None):
        """
        name: identifier string (may include underscores)
        description: default/short description (backwards compatible)
        first_visit_description: optional richer text shown on first entry
        short_description: optional short text shown on subsequent visits
        """
        self.name = name
        self.description = description
        # Backwards compatible: if no first_visit_description provided, use the given description
        self.first_visit_description = first_visit_description or description
        # Short description for later visits (defaults to a compact form)
        self.short_description = short_description or description
        self.exits = {}
        # visited flag to allow different first-visit description
        self.visited = False
        # inventory: dictionnaire d'objets présents dans la pièce (name -> Item instance)
        # Initialisé vide.
        self.inventory = {}

    def get_exit(self, direction):
        """Return the room in the given direction or None if absent."""
        return self.exits.get(direction)

    def get_exit_string(self):
        # Return a readable string listing directions and destination names.
        parts = []
        for d, room in self.exits.items():
            if room is not None:
                dest_name = room.name.replace("_", " ")
                parts.append(f"{d} ({dest_name})")
            else:
                parts.append(f"{d} (—)")
        return "Sorties: " + ", ".join(parts)

    def _clean_description_for_entry(self, raw):
        """Normalize a raw description to a natural entry sentence."""
        desc = raw.strip()
        if desc.lower().startswith("dans "):
            core = desc[5:]
            return f"Vous entrez dans {core}"
        return f"Vous entrez {desc}"

    def _contextual_ambience(self, raw):
        # Choose an ambience phrase, and add contextual lines for known keywords.
        base_ambiances = [
            "Un léger courant d'air frissonne contre votre nuque.",
            "Une odeur particulière flotte dans l'air.",
            "Le silence est seulement brisé par un bruit lointain.",
            "La lumière révèle des détails oubliés.",
            "Quelque chose attire votre regard, sans que vous sachiez quoi.",
            "De faibles échos rebondissent contre les murs.",
            "La poussière danse dans un rayon de lumière.",
            "Un frisson vous parcourt en remarquant un détail incongru.",
            "Des odeurs évoquent le temps et l'abandon.",
            "L'atmosphère est lourde, comme si la maison retenait son souffle."
        ]
        keywords_ambiances = {
            "cadavre": "Un goût métallique vous reste en bouche.",
            "chaudron": "De la vapeur s'élève du chaudron, le liquide bouillonne.",
            "horloge": "Le tic-tac de l'horloge résonne d'une cadence obsédante.",
            "vitre": "Le vent siffle à travers la vitre cassée.",
            "cheminée": "La suie et l'odeur de feu éteint collent aux meubles.",
            "livres": "L'odeur du papier ancien et du cuir vous entoure.",
            "coffre": "Le coffre fermé promet des secrets anciens."
        }

        ambience = random.choice(base_ambiances)
        raw_lower = raw.lower()
        for kw, line in keywords_ambiances.items():
            if kw in raw_lower:
                # prefer a contextual line when a keyword is present
                # occasionally append it to the chosen ambience
                if random.random() < 0.7:
                    return line
                return f"{ambience} {line}"
        return ambience

    def get_long_description(self):
        """Return a rich description. Uses first_visit_description on first call, then short_description."""
        header = self.name.replace("_", " ")

        # choose which base description to use
        base = self.first_visit_description if not self.visited else self.short_description

        entry = self._clean_description_for_entry(base)
        ambience = self._contextual_ambience(base)
        exits = self.get_exit_string()

        # mark visited so next time we show the short description
        self.visited = True

        return f"\n-- {header} --\n\n{entry}. {ambience}\n\n{exits}\n"

    def get_inventory(self) -> str:
        """Return a readable string representing the items present in this room.

        If the room has no items, returns a short message in French.
        Otherwise returns a header line followed by one entry per item. If
        the stored value looks like an Item (has a description and weight)
        we use its string representation; otherwise we fall back to the
        stored value's string form.
        """
        if not self.inventory:
            return "Il n'y a rien ici."

        lines = ["La pièce contient :"]
        for name, obj in self.inventory.items():
            if hasattr(obj, "description") and hasattr(obj, "weight"):
                lines.append(f" - {obj}")
            else:
                lines.append(f" - {name} : {obj}")

        return "\n".join(lines)

    def look(self):
        """Display the items present in this room.

        This method prints a user-friendly list of items (delegates to
        `get_inventory`) so Actions.look can call it directly.
        Returns True after printing for consistency with action handlers.
        """
        print(self.get_inventory())
        return True

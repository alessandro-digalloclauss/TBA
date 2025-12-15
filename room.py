"""Modèle de pièce et aides à la description.

Ce module définit la classe `Room` utilisée par le jeu. Les pièces
peuvent avoir une description enrichie pour la première visite et une
description plus courte pour les visites suivantes. Des lignes
d'ambiance sont choisies pour renforcer l'immersion.
"""

import random


class Room:
    """Représentation d'une pièce dans le monde du jeu."""

    def __init__(self, name, description, first_visit_description=None, short_description=None, image=None):
        """
        name : identifiant de la pièce (peut contenir des underscores)
        description : description par défaut/courte (compatibilité)
        first_visit_description : texte enrichi montré à la première entrée
        short_description : texte court pour les visites suivantes
        """
        self.name = name
        self.description = description
        # Compatibilité : si pas de first_visit_description fournie, utiliser description
        self.first_visit_description = first_visit_description or description
        # Description courte pour les visites suivantes (par défaut la description)
        self.short_description = short_description or description
        self.exits = {}
        # Optional image filename (in ./assets) for UI display (Tkinter)
        self.image = image
        # Indicateur de visite pour distinguer la première description
        self.visited = False
        # inventory : dictionnaire d'objets présents dans la pièce (name -> instance d'Item)
        # Initialisé vide.
        self.inventory = {}
        # characters : dictionnaire des personnages non joueurs présents (name -> Character)
        # Initialisé vide ; rempli depuis `Game.setup()`.
        self.characters = {}

    def get_exit(self, direction):
        """Retourne la pièce dans la direction donnée ou None si absente."""
        return self.exits.get(direction)

    def get_exit_string(self):
        # Retourne une chaîne lisible listant les directions et les noms
        # des destinations.
        parts = []
        for d, room in self.exits.items():
            if room is not None:
                dest_name = room.name.replace("_", " ")
                parts.append(f"{d} ({dest_name})")
            else:
                parts.append(f"{d} (—)")
        return "Sorties: " + ", ".join(parts)

    def _clean_description_for_entry(self, raw):
        """Normalise une description brute pour produire une phrase d'entrée naturelle."""
        desc = raw.strip()
        # Toujours présenter l'entrée avec 'dans' pour une tournure naturelle.
        # Si le texte commence déjà par 'dans ', le retirer pour éviter la
        # duplication.
        if desc.lower().startswith("dans "):
            core = desc[5:]
        else:
            core = desc
        return f"Vous entrez dans {core}"

    def _contextual_ambience(self, raw):
        # Choisit une phrase d'ambiance et ajoute des lignes contextuelles
        # pour des mots-clés reconnus.
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
                # Préférer une ligne contextuelle lorsqu'un mot-clé est présent
                # et parfois l'appendre à l'ambiance choisie.
                if random.random() < 0.7:
                    return line
                return f"{ambience} {line}"
        return ambience

    def get_long_description(self):
        """Retourne une description riche. Utilise first_visit_description lors
        de la première visite, puis short_description.
        """
        header = self.name.replace("_", " ")

        # Choisir la description de base à utiliser
        base = self.first_visit_description if not self.visited else self.short_description

        entry = self._clean_description_for_entry(base)
        ambience = self._contextual_ambience(base)
        exits = self.get_exit_string()

        # Marquer comme visité afin d'afficher la description courte la fois suivante
        self.visited = True

        return f"\n-- {header} --\n\n{entry}. {ambience}\n\n{exits}\n"

    def get_inventory(self) -> str:
        """Retourne une chaîne lisible représentant les items présents dans la pièce.

        Si la pièce ne contient aucun item, renvoie un court message en
        français. Sinon renvoie une ligne d'en-tête suivie d'une entrée par
        item. Si la valeur stockée ressemble à un Item (attributs
        `description` et `weight`), on utilise sa représentation chaîne,
        sinon on tombe en repli sur str(obj).
        """
        # Si ni items ni personnages : message simple
        if not self.inventory and not self.characters:
            return "Il n'y a rien ici."

        lines = ["On voit:"]

        # Items d'abord
        for name, obj in self.inventory.items():
            if hasattr(obj, "description") and hasattr(obj, "weight"):
                lines.append(f" - {obj}")
            else:
                lines.append(f" - {name} : {obj}")

        # Puis les personnages non joueurs
        for name, char in self.characters.items():
            # On suppose que Character définit __str__ convenable
            lines.append(f" - {char}")

        return "\n".join(lines)

    def look(self):
        """Afficher les objets présents dans cette pièce.

        Cette méthode imprime une liste lisible des items (déléguée à
        `get_inventory`) pour que `Actions.look` puisse l'appeler.
        Retourne True après affichage pour cohérence avec les handlers.
        """
        print(self.get_inventory())
        return True

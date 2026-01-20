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
        # sprite_positions : dictionnaire des positions (x, y) pour chaque entité (objet ou PNJ)
        # Exemple: {"cle": (400, 500), "Émile": (250, 300)}
        self.sprite_positions = {}

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
        # Ambiances spécifiques à chaque pièce basées sur leur contenu
        room_ambiances = {
            "jardin": "Des plantes exotiques sont en désordre sous une vitre brisée. Le vent s'engouffre par l'ouverture.",
            "hall": "Le vaste hall est dominé par un grand lustre immobile. L'horloge murale s'est arrêtée à 22:30.",
            "salon": "Des fauteuils usés entourent une cheminée froide. Un verre de vin à moitié bu avec une marque de rouge à lèvres repose sur la table.",
            "cuisine": "Un chaudron fumant trône sur le fourneau. Les couteaux sont alignés, mais l'un d'eux manque...",
            "bureau": "C'EST L'HORREUR ! Un corps gît au sol dans le bureau, entouré de sang et de papiers éparpillés. Les vieux fauteuils ne sont pas à leur place, ils ont visiblement été bousculés.",
            "couloir": "Le long couloir est sombre et le parquet grince sous vos pas. Des traces de pas boueuses mènent vers la bibliothèque.",
            "chambre": "Le lit est défait et la fenêtre entrouverte laisse entrer un courant d'air glacé.",
            "bibliothèque": "De hauts rayonnages remplis de livres anciens couvrent les murs. Tous sont soigneusement alignés, sauf un vieux livre mal rangé qui dépasse de l'étagère.",
            "pièce_cachée": "Une lanterne éclaire faiblement la pièce secrète. Un vieux tiroir du bureau retient l'attention.",
            "cave": "La cave est fraîche et humide. Des bouteilles anciennes sont alignées, certaines brisées au sol.",
            "atelier": "Des outils et des plans froissés sont éparpillés sur l'établi. Des taches suspectes marquent le sol.",
        }
        
        # Chercher une ambiance spécifique basée sur le nom de la pièce
        room_name_lower = self.name.lower()
        for key, ambience in room_ambiances.items():
            if key in room_name_lower:
                return ambience
        
    def get_long_description(self):
        """Retourne une description riche. Utilise first_visit_description lors
        de la première visite, puis short_description.
        """
        header = self.name.replace("_", " ")

        # Créer l'entrée simple : "Vous entrez dans [Nom]."
        entry = f"Vous entrez dans {header}."
        
        ambience = self._contextual_ambience(None)
        exits = self.get_exit_string()

        # Marquer comme visité afin d'afficher la description courte la fois suivante
        self.visited = True

        return f"\n-- {header} --\n\n{entry}\n\n{ambience}\n\n{exits}\n"

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

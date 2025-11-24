"""Représentation du joueur.

Ce module fournit une classe `Player` légère qui mémorise le nom du
joueur, la pièce courante et gère les déplacements entre pièces.
"""


class Player:
    """Représente le joueur et sa position actuelle."""

    def __init__(self, name):
        """Créer un joueur avec le nom d'affichage fourni."""
        self.name = name
        self.current_room = None
        # historique : pile (list) des Room visitées précédemment
        # Utiliser append() pour empiler une salle et pop() pour revenir.
        self.historique = []
        # inventaire : dictionnaire d'objets ramassés (name -> Item instance ou valeur)
        # Initialisé vide.
        self.inventory = {}

    def move(self, direction):
        """Tente de déplacer le joueur dans `direction`.

        Renvoie True et affiche la description de la nouvelle pièce en cas
        de succès, ou False et affiche un message d'erreur si le mouvement
        n'est pas possible.
        """
        # Utiliser dict.get pour éviter KeyError si la direction est absente.
        next_room = self.current_room.exits.get(direction)

        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            return False

        # Empiler la pièce courante dans l'historique avant de bouger
        if self.current_room is not None:
            self.historique.append(self.current_room)

        self.current_room = next_room
        print(self.current_room.get_long_description())
        return True

    def retour(self):
        """Revenir à la pièce précédente en utilisant la pile d'historique.

        Renvoie True si le retour a réussi, False si l'historique est vide.
        """
        if not self.historique:
            print("\nImpossible de revenir en arrière : historique vide.\n")
            return False

        previous = self.historique.pop()
        self.current_room = previous
        print(self.current_room.get_long_description())
        return True

    def get_history(self):
        """Retourne une chaîne lisible représentant l'historique des pièces.

        L'historique liste les pièces dans l'ordre de visite (la plus ancienne
        en premier). Chaque entrée utilise le nom de la pièce (les underscores
        sont remplacés par des espaces).
        """
        if not self.historique:
            return "Vous n'avez encore visité aucune pièce."

        lines = ["Vous avez déjà visité les pièces suivantes:"]
        for room in self.historique:
            # Utiliser le nom de la pièce en le rendant lisible (remplacer
            # les underscores par des espaces, ex. 'Salon_Victorien' -> 'Salon Victorien').
            name = getattr(room, 'name', 'inconnue')
            name = name.replace('_', ' ')
            lines.append(f" - {name}")

        return "\n".join(lines)

    def get_inventory(self) -> str:
        """Retourne une chaîne lisible représentant l'inventaire du joueur.

        Si l'inventaire est vide, renvoie un message court en français. Sinon
        renvoie une ligne d'en-tête suivie d'une entrée par item. L'inventaire
        est un dict mappant le nom de l'item à l'objet (ou autre valeur). Si
        la valeur ressemble à un Item (attributs `description` et `weight`),
        on utilise sa représentation chaîne, sinon on utilise str(value).
        """
        if not self.inventory:
            return "Votre inventaire est vide."

        lines = ["Vous disposez des items suivants :"]
        for name, obj in self.inventory.items():
            # Si obj ressemble à un Item, préférer son __str__.
            if hasattr(obj, "description") and hasattr(obj, "weight"):
                lines.append(f" - {obj}")
            else:
                lines.append(f" - {name} : {obj}")

        return "\n".join(lines)


import random

class Character:
    """Représente un personnage non joueur.

    Attributs:
    - name: nom du personnage (str)
    - description: description textuelle (str)
    - current_room: référence au lieu où le personnage se trouve (optionnel)
    - msgs: liste de messages affichés quand le joueur interroge le personnage
    """

    def __init__(self, name, description, current_room=None, msgs=None):
        self.name = name
        self.description = description
        self.current_room = current_room
        self.msgs = msgs or []

    def __str__(self):
        return f"{self.name} : {self.description}"

    def move(self):
        """Tente de déplacer le personnage.


        Comportement:
        - 50% de chances de rester sur place.
        - Sinon, choisit au hasard une pièce adjacente non nulle et s'y déplace.
        - Met à jour les dictionnaires  des pièces.

        Retourne True si le personnage s'est déplacé, False sinon.
        """

        # Si aucune pièce courante ou pas de sorties, on ne peut pas se déplacer
        if self.current_room is None:
            return False

        # Récupérer les pièces adjacentes valides
        adjacent = [r for r in self.current_room.exits.values() if r is not None]
        if not adjacent:
            return False

        # Chance 1 sur 2 de se déplacer
        if not random.choice([True, False]):
            # debug: personnage décide de rester
            try:
                from game import DEBUG
            except Exception:
                DEBUG = False
            if DEBUG:
                room_name = getattr(self.current_room, 'name', 'inconnue')
                print(f"DEBUG: {self.name} décide de rester dans {room_name}")
            return False

        # Choisir une destination au hasard
        dest = random.choice(adjacent)

        # Mettre à jour l'appartenance : retirer de l'ancienne salle si présent
        try:
            chars = getattr(self.current_room, 'characters', {})
            if self.name in chars:
                del self.current_room.characters[self.name]
        except Exception:
            # Ignorer les erreurs non critiques
            pass

        # Ajouter dans la nouvelle salle
        dest.characters[self.name] = self
        old_name = getattr(self.current_room, 'name', None)
        self.current_room = dest

        # debug: afficher déplacement
        try:
            from game import DEBUG
        except Exception:
            DEBUG = False
        if DEBUG:
            new_name = getattr(dest, 'name', 'inconnue')
            print(f"DEBUG: {self.name} s'est déplacé de {old_name} vers {new_name}")

        return True

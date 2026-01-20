import random

class Character:
    """Représente un personnage non joueur.

    Attributs:
    - name: nom du personnage (str)
    - description: description textuelle (str)
    - current_room: référence au lieu où le personnage se trouve (optionnel)
    - msgs: liste de messages affichés quand le joueur interroge le personnage
    """

    def __init__(self, name, description, current_room=None, msgs=None, image=None):
        self.name = name
        self.description = description
        self.current_room = current_room
        self.msgs = msgs or []
        # Image du sprite du personnage (nom de fichier dans assets/)
        self.image = image
        # Nombre de tours pendant lesquels le PNJ doit rester sur place
        # (décrémente à chaque appel à move()).
        self.stay_turns = 0

    def __str__(self):
        return f"{self.name} : {self.description}"

    def get_msg(self):
        """Retourne le message suivant du personnage en faisant une rotation.

        Si la liste `msgs` est vide, renvoie `None`. Sinon, on supprime et
        retourne le premier élément, puis on l'ajoute à la fin pour permettre
        un affichage cyclique.
        """
        if not self.msgs:
            return None
        try:
            msg = self.msgs.pop(0)
            # Réinsérer le message à la fin pour la rotation
            self.msgs.append(msg)
            return msg
        except Exception:
            return None

    def move(self):
        """Tente de déplacer le personnage.


        Comportement:
        - 50% de chances de rester sur place.
        - Sinon, choisit au hasard une pièce adjacente non nulle et s'y déplace.
        - Ne peut pas entrer dans une salle où il y a déjà un autre PNJ avec le joueur.
        - Met à jour les dictionnaires des pièces.

        Retourne True si le personnage s'est déplacé, False sinon.
        """

        # Si aucune pièce courante ou pas de sorties, on ne peut pas se déplacer
        if self.current_room is None:
            return False

        # Respecter le marqueur de 'stay' : si >0, décrémenter et rester
        if getattr(self, 'stay_turns', 0) > 0:
            try:
                self.stay_turns -= 1
            except Exception:
                self.stay_turns = 0
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

        # Filtrer les destinations : exclure les salles où il y a déjà un PNJ
        # (pour éviter que plusieurs PNJ soient dans la même salle)
        valid_destinations = []
        for dest in adjacent:
            # Vérifier s'il y a déjà un autre PNJ dans cette salle
            other_npcs = [c for c in dest.characters.values() if c is not self]
            if len(other_npcs) == 0:
                valid_destinations.append(dest)

        # Si aucune destination valide, rester sur place
        if not valid_destinations:
            return False

        # Choisir une destination au hasard parmi les valides
        dest = random.choice(valid_destinations)

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

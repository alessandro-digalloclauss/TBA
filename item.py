"""Classe `Item` pour le petit jeu RPG.

Fournit la classe `Item` utilisée pour représenter les objets ramassables.
"""


class Item:
    """Représente un objet que le joueur peut trouver.

    Attributs:
    - name: nom de l'objet
    - description: description textuelle
    - weight: poids (en kg)
    """

    def __init__(self, name: str, description: str, weight: float, detail: str = None):
        self.name = name
        self.description = description
        self.weight = weight
        # detail: description plus précise visible uniquement avec un outil d'inspection (loupe)
        self.detail = detail

    def __str__(self) -> str:
        """Retourne une représentation textuelle lisible de l'objet.

        Le poids est affiché sans décimale si c'est un entier (ex. "2 kg").
        """
        # Affiche le poids sans décimale si c'est un entier
        try:
            w = float(self.weight)
            if w.is_integer():
                w_display = str(int(w))
            else:
                w_display = str(w)
        except (ValueError, TypeError):
            # Si la conversion échoue, afficher la valeur telle quelle
            w_display = str(self.weight)

        return f"{self.name} : {self.description} ({w_display} kg)"

    def describe(self) -> str:
        """Retourne une courte description non-formatée de l'objet."""
        return f"{self.name} - {self.description}"


if __name__ == "__main__":
    # Test rapide (exécuté seulement en script)
    sword = Item("sword", "une épée au fil tranchant comme un rasoir", 2)
    print(sword)

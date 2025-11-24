"""Assistant de commande utilisé par le jeu.

Définit une petite classe `Command` qui regroupe le mot-clé de la
commande, une chaîne d'aide, la fonction d'action et le nombre
attendu de paramètres.
"""


class Command:
    """Représente une commande du joueur.

    Attributs
    ---------
    command_word : str
        Mot-clé utilisé pour invoquer la commande.
    help_string : str
        Bref texte d'aide affiché dans la liste des commandes.
    action : callable
        Fonction appelée pour exécuter la commande.
    number_of_parameters : int
        Nombre de paramètres attendus par la commande.
    """

    def __init__(self, command_word, help_string, action, number_of_parameters):
        self.command_word = command_word
        self.help_string = help_string
        self.action = action
        self.number_of_parameters = number_of_parameters

    def __str__(self):
        return f"{self.command_word}{self.help_string}"


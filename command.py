"""Command helper used by the game.

Defines a small Command class that packages a command word, a help
string, an action callable and the expected number of parameters.
"""


class Command:
    """Represents a player command.

    Attributes
    ----------
    command_word : str
        The keyword used to invoke the command.
    help_string : str
        A short help text shown in the help list.
    action : callable
        The function called to execute the command.
    number_of_parameters : int
        How many parameters the command expects.
    """

    def __init__(self, command_word, help_string, action, number_of_parameters):
        self.command_word = command_word
        self.help_string = help_string
        self.action = action
        self.number_of_parameters = number_of_parameters

    def __str__(self):
        return f"{self.command_word}{self.help_string}"


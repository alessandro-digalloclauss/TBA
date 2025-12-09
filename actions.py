"""Actions du jeu.

Ce module expose l'ensemble restreint d'actions utilisées par la boucle
de jeu. Chaque action est une méthode statique acceptant
`(game, list_of_words, number_of_parameters)` et renvoie `True` en cas
de succès.
"""

MSG0 = "\nLa commande '{command_word}' ne prend pas de paramètre.\n"
MSG1 = "\nLa commande '{command_word}' prend 1 seul paramètre.\n"


class Actions:
    """Container for actions used by the game loop."""

    @staticmethod
    def go(game, list_of_words, number_of_parameters):
        """Déplace le joueur dans une direction cardinale.

        Forme attendue : `go <direction>`
        """
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        player = game.player
        raw = list_of_words[1].strip()
        if not raw:
            print("\nDirection vide. Utilisez une direction (N, E, S, O, U, D).\n")
            return False

        # Normalise l'entrée et associe les alias aux codes canoniques
        # d'une seule lettre (N, E, S, O, U, D).
        key = raw.upper()
        canonical = None
        # Si le jeu fournit une table d'alias, l'utiliser
        if hasattr(game, 'direction_aliases'):
            canonical = game.direction_aliases.get(key)

        # Sinon, accepter la première lettre si elle correspond à une
        # direction connue.
        if canonical is None:
            if len(key) >= 1:
                candidate = key[0]
                if hasattr(game, 'directions') and candidate in game.directions:
                    canonical = candidate

        if canonical is None:
            print(f"\nDirection inconnue: '{raw}'. Utilisez N, E, S, O, U ou D.\n")
            # Plutôt que d'afficher la description longue (ce qui serait
            # déroutant ici), afficher un rappel court de la position
            # courante : 'Vous êtes dans <nom de la pièce>'.
            current = getattr(player, 'current_room', None)
            if current is not None:
                room_name = getattr(current, 'name', 'inconnue').replace('_', ' ')
                print(f"Vous êtes toujours dans {room_name}.\n")
            return False

        # Finally attempt the movement with the canonical direction
        player.move(canonical)
        return True

    @staticmethod
    def quit(game, list_of_words, number_of_parameters):
        """Quitter le jeu après affichage d'un message d'au revoir."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        msg = f"\nMerci {player.name} d'avoir joué. Au revoir.\n"
        print(msg)
        game.finished = True
        return True

    @staticmethod
    def help(game, list_of_words, number_of_parameters):
        """Afficher les commandes disponibles et leurs messages d'aide."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False
        print("\nVoici les commandes disponibles:")
        # Affiche les commandes dans un ordre trié pour que les commandes
        # ajoutées ('back', 'history', ...) apparaissent de façon
        # prévisible.
        for key in sorted(game.commands.keys()):
            command = game.commands[key]
            print("\t- " + str(command))
        print()
        return True

    @staticmethod
    def back(game, list_of_words, number_of_parameters):
        """Ramener le joueur dans la pièce précédente en utilisant l'historique."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        # `player.retour()` gère l'affichage et retourne True/False
        return player.retour()

    @staticmethod
    def history(game, list_of_words, number_of_parameters):
        """Afficher l'historique du joueur (pièces visitées)."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        print(player.get_history())
        return True

    @staticmethod
    def look(game, list_of_words, number_of_parameters):
        """Afficher les objets présents dans la pièce courante (commande look)."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        current = getattr(player, 'current_room', None)
        if current is None:
            print("\nVous n'êtes dans aucune pièce.\n")
            return False

        # `Room.look()` affiche l'inventaire et retourne True/False
        return current.look()

    @staticmethod
    def talk(game, list_of_words, number_of_parameters):
        """Parler à un personnage non joueur présent dans la pièce.

        Forme attendue : `talk <nom>`
        """
        if len(list_of_words) < number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        player = game.player
        current = getattr(player, 'current_room', None)
        if current is None:
            print("\nVous n'êtes dans aucune pièce.\n")
            return False

        # Supporte les noms sur plusieurs mots
        target_name = " ".join(list_of_words[1:]).strip()
        if not target_name:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Recherche robuste des personnages présents (plusieurs stratégies):
        found = None
        tn = target_name.lower()

        # 1) recherche directe sur la clé telle quelle
        if target_name in current.characters:
            found = current.characters[target_name]

        # 2) recherche par nom exact insensible à la casse
        if found is None:
            for char in current.characters.values():
                if getattr(char, 'name', '').lower() == tn:
                    found = char
                    break

        # 3) recherche par clé insensible à la casse
        if found is None:
            for k, v in current.characters.items():
                if k.lower() == tn:
                    found = v
                    break

        # 4) recherche par préfixe / inclusion (pour accepter 'gand' -> 'Gandalf')
        if found is None:
            for v in current.characters.values():
                n = getattr(v, 'name', '').lower()
                if n.startswith(tn) or tn in n:
                    found = v
                    break

        if not found:
            # Fournir une liste des PNJ présents pour guider l'utilisateur
            if current.characters:
                present = [getattr(c, 'name', k) for k, c in current.characters.items()]
                present_list = ", ".join(present)
                print(f"\nIl n'y a aucun personnage nommé '{target_name}' ici. Personnages présents: {present_list}\n")
            else:
                print(f"\nIl n'y a aucun personnage nommé '{target_name}' ici.\n")
            return False

        # Appeler la méthode get_msg() du personnage et afficher le résultat
        if hasattr(found, 'get_msg'):
            msg = found.get_msg()
            if msg is None:
                print(f"\n{found.name} ne répond pas pour l'instant.\n")
                return False
            print(f"\n{msg}\n")
            # Marquer le PNJ pour qu'il reste au moins un tour après la
            # conversation afin que le joueur puisse le re-interroger.
            try:
                found.stay_turns = max(getattr(found, 'stay_turns', 0), 1)
            except Exception:
                pass
            # Vérifier les objectifs de quête pour la conversation
            game.player.quest_manager.check_action_objectives("parler", found.name)
            return True
        else:
            print(f"\n{found.name} ne sait pas parler.\n")
            return False

    @staticmethod
    def take(game, list_of_words, number_of_parameters):
        """Prendre un objet présent dans la pièce et l'ajouter à l'inventaire.

        Forme attendue : `take <nom de l'objet>`
        """
        # Autoriser les noms d'item sur plusieurs mots en acceptant >= tokens requis
        if len(list_of_words) < number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        player = game.player
        current = getattr(player, 'current_room', None)
        if current is None:
            print("\nVous n'êtes dans aucune pièce.\n")
            return False

        # Joindre les mots restants pour supporter les noms sur plusieurs mots
        item_name = " ".join(list_of_words[1:]).strip()
        if not item_name:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Vérifier que l'item existe dans la pièce
        if item_name not in current.inventory:
            print(f"\nIl n'y a pas d'item nommé '{item_name}' ici.\n")
            return False

        # Inspecter l'objet sans l'enlever tout de suite pour vérifier la capacité
        obj = current.inventory.get(item_name)

        # Déterminer le poids de l'objet (0 si absent/non numérique)
        item_weight = 0.0
        if hasattr(obj, 'weight'):
            try:
                item_weight = float(obj.weight)
            except Exception:
                item_weight = 0.0

        # Calculer le poids actuel porté par le joueur
        current_weight = 0.0
        if hasattr(player, 'current_carry_weight'):
            try:
                current_weight = float(player.current_carry_weight())
            except Exception:
                current_weight = 0.0
        else:
            # Recalculer si la méthode n'existe pas
            for o in player.inventory.values():
                if hasattr(o, 'weight'):
                    try:
                        current_weight += float(o.weight)
                    except Exception:
                        pass

        # Vérifier la capacité maximale si définie
        max_w = getattr(player, 'max_weight', None)
        if max_w is not None:
            try:
                max_w_val = float(max_w)
            except Exception:
                max_w_val = None
        else:
            max_w_val = None

        if max_w_val is not None and (current_weight + item_weight) > max_w_val:
            # Ne pas prendre l'objet et afficher un message d'erreur
            cw_disp = int(current_weight) if float(current_weight).is_integer() else round(current_weight, 2)
            iw_disp = int(item_weight) if float(item_weight).is_integer() else round(item_weight, 2)
            mw_disp = int(max_w_val) if float(max_w_val).is_integer() else round(max_w_val, 2)
            print(
                f"\nVous ne pouvez pas prendre '{item_name}' : {iw_disp} kg, "
                f"capacité dépassée ({cw_disp} + {iw_disp} > {mw_disp} kg).\n"
            )
            return False

        # Si tout est OK, enlever de la pièce et ajouter à l'inventaire du joueur
        obj = current.inventory.pop(item_name)
        player.inventory[item_name] = obj
        # Afficher le poids si disponible
        if hasattr(obj, 'weight'):
            try:
                w = float(obj.weight)
                w_display = f" ({w} kg)"
            except Exception:
                w_display = ""
        else:
            w_display = ""

        print(f"\nVous avez pris '{item_name}'{w_display} et l'avez mis dans votre inventaire.\n")
        return True

    @staticmethod
    def check(game, list_of_words, number_of_parameters):
        """Afficher l'inventaire du joueur (commande check)."""
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        # `player.get_inventory()` renvoie une chaîne lisible
        print(player.get_inventory())
        return True

    @staticmethod
    def drop(game, list_of_words, number_of_parameters):
        """Déposer un objet de l'inventaire du joueur dans la pièce courante.

        Forme attendue : `drop <nom de l'objet>`
        """
        # Autoriser les noms d'item sur plusieurs mots en acceptant >= tokens requis
        if len(list_of_words) < number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        player = game.player
        current = getattr(player, 'current_room', None)
        if current is None:
            print("\nVous n'êtes dans aucune pièce.\n")
            return False

        # Joindre les mots restants pour supporter les noms sur plusieurs mots
        item_name = " ".join(list_of_words[1:]).strip()
        if not item_name:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Vérifier que le joueur possède l'item
        if item_name not in player.inventory:
            print(f"\nVous n'avez pas d'item nommé '{item_name}' dans votre inventaire.\n")
            return False

        # Retirer de l'inventaire du joueur et ajouter à l'inventaire de la pièce
        obj = player.inventory.pop(item_name)
        current.inventory[item_name] = obj
        # Afficher le poids si disponible
        if hasattr(obj, 'weight'):
            try:
                w = float(obj.weight)
                w_display = f" ({w} kg)"
            except Exception:
                w_display = ""
        else:
            w_display = ""

        print(f"\nVous avez reposé '{item_name}'{w_display} dans la pièce.\n")
        return True

    @staticmethod
    def quests(game, list_of_words, number_of_parameters):
        """Afficher la liste de toutes les quêtes.

        Forme attendue: `quests`
        """
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        game.player.quest_manager.show_quests()
        return True

    @staticmethod
    def quest(game, list_of_words, number_of_parameters):
        """Afficher les détails d'une quête spécifique.

        Forme attendue: `quest <titre>`
        """
        if len(list_of_words) < number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Récupérer le titre de la quête (peut contenir plusieurs mots)
        quest_title = " ".join(list_of_words[1:])

        # Préparer les compteurs actuels pour afficher la progression
        current_counts = {"Se déplacer": game.player.move_count}

        game.player.quest_manager.show_quest_details(quest_title, current_counts)
        return True

    @staticmethod
    def activate(game, list_of_words, number_of_parameters):
        """Activer une quête par son titre.

        Forme attendue: `activate <titre>`
        """
        if len(list_of_words) < number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Récupérer le titre de la quête (peut contenir plusieurs mots)
        quest_title = " ".join(list_of_words[1:])

        if game.player.quest_manager.activate_quest(quest_title):
            return True

        print(
            f"\nImpossible d'activer la quête '{quest_title}'. "
            "Vérifiez le nom ou si elle n'est pas déjà active.\n"
        )
        return False

    @staticmethod
    def rewards(game, list_of_words, number_of_parameters):
        """Afficher les récompenses obtenues par le joueur.

        Forme attendue: `rewards`
        """
        if len(list_of_words) != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        game.player.show_rewards()
        return True

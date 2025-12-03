class AFD:
    def __init__(self, alphabet, etats, etat_initial, etats_finaux, transitions):
        """
        Initialise l'AFD

        Args:
            alphabet: ensemble des symboles (ex: {'a', 'b'})
            etats: ensemble des états (ex: {'q0', 'q1', 'q2'})
            etat_initial: état de départ
            etats_finaux: ensemble des états finaux
            transitions: dictionnaire des transitions
        """
        self.alphabet = alphabet
        self.etats = etats
        self.etat_initial = etat_initial
        self.etats_finaux = etats_finaux
        self.transitions = transitions
        self.etat_actuel = etat_initial

    def reinitialiser(self):
        """Réinitialise l'automate à l'état initial"""
        self.etat_actuel = self.etat_initial

    def traiter_symbole(self, symbole):
        """
        Traite un symbole et met à jour l'état actuel

        Args:
            symbole: le symbole à traiter

        Returns:
            bool: True si la transition est valide, False sinon
        """
        if symbole not in self.alphabet:
            return False

        if self.etat_actuel in self.transitions and symbole in self.transitions[self.etat_actuel]:
            self.etat_actuel = self.transitions[self.etat_actuel][symbole]
            return True
        return False

    def accepter_chaine(self, chaine):
        """
        Vérifie si une chaîne est acceptée par l'AFD

        Args:
            chaine: la chaîne à tester

        Returns:
            bool: True si la chaîne est acceptée, False sinon
        """
        self.reinitialiser()

        for symbole in chaine:
            if not self.traiter_symbole(symbole):
                return False

        return self.etat_actuel in self.etats_finaux

    def obtenir_chemin(self, chaine):
        """
        Retourne le chemin parcouru pour une chaîne donnée
        """
        self.reinitialiser()
        chemin = [self.etat_actuel]

        for symbole in chaine:
            if self.traiter_symbole(symbole):
                chemin.append(self.etat_actuel)
            else:
                break

        return chemin

    def afficher_info(self):
        """Affiche les informations de l'AFD"""
        print("=== Informations de l'AFD ===")
        print(f"Alphabet: {self.alphabet}")
        print(f"États: {self.etats}")
        print(f"État initial: {self.etat_initial}")
        print(f"États finaux: {self.etats_finaux}")
        print("Table de transition:")
        for etat, trans in self.transitions.items():
            print(f"  {etat}: {trans}")
        print()


def creer_afd_exemple():
    """Crée l'AFD d'exemple du projet"""
    alphabet = {'a', 'b'}
    etats = {'q0', 'q1', 'q2'}
    etat_initial = 'q0'
    etats_finaux = {'q2'}

    transitions = {
        'q0': {'a': 'q1', 'b': 'q0'},
        'q1': {'a': 'q1', 'b': 'q2'},
        'q2': {'a': 'q1', 'b': 'q0'}
    }

    return AFD(alphabet, etats, etat_initial, etats_finaux, transitions)
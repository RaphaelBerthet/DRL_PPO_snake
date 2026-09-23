import pyxel
import copy
from .parametres_snake import Tracer_orientation_serpent
from .pomme import Pomme
from .conversion_numero_coordonnees import conversion_numerocase_coordonnees
from .trouve_direction import trouve_direction

class Serpent:
    def __init__(self, x=5, y=5):
        self.nx = 5
        self.ny = 5
        self.direction = 2  # 1 : gauche; 2 : droite; 3 : haut; 4 : bas
        self.cases_occupe = [(x, y)]  # le 1er correspond à la tête le 2e...

    def actu_direction(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.direction = 1
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.direction = 2
        elif pyxel.btn(pyxel.KEY_UP):
            self.direction = 3
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.direction = 4

    def avancer(self, pomme: Pomme) -> tuple[Pomme, bool, bool]:
        tete = self.cases_occupe[0]
        droite = True
        gauche = True
        haut = True
        bas = True
        for case in self.cases_occupe[1:-1]:
            if case[0] + 1 == tete[0] and case[1] == tete[1]:
                gauche = False
            if case[0] - 1 == tete[0] and case[1] == tete[1]:
                droite = False
            if case[1] - 1 == tete[1] and case[0] == tete[0]:
                bas = False
            if case[1] + 1 == tete[1] and case[0] == tete[0]:
                haut = False
        cases = copy.deepcopy(self.cases_occupe)
        tete = cases[0]
        if self.direction == 1 and tete[0] > 1 and gauche:
            tete = (tete[0] - 1, tete[1])
        elif self.direction == 2 and tete[0] < 10 and droite:
            tete = (tete[0] + 1, tete[1])
        elif self.direction == 3 and tete[1] > 1 and haut:
            tete = (tete[0], tete[1] - 1)
        elif self.direction == 4 and tete[1] < 10 and bas:
            tete = (tete[0], tete[1] + 1)

        pomme_mangee = False
        partie_en_cours = True
        if tete == self.cases_occupe[0]:
            partie_en_cours = False
        elif tete == (pomme.x, pomme.y):
            self.cases_occupe = [tete] + self.cases_occupe
            pomme = Pomme(self.cases_occupe)
            pomme_mangee = True
        else:
            self.cases_occupe = [tete] + self.cases_occupe[:-1]
        return pomme, partie_en_cours, pomme_mangee

    def tracer(self):
        case = self.cases_occupe[0]
        case2 = self.cases_occupe[-1]
        pyxel.rect(conversion_numerocase_coordonnees(case[0]), conversion_numerocase_coordonnees(case[1]), 11, 11, 2)
        pyxel.rect(conversion_numerocase_coordonnees(case2[0]), conversion_numerocase_coordonnees(case2[1]), 11, 11, 1)
        for i in range(len(self.cases_occupe[1:-1])):
            indice_reel = i + 1
            x = conversion_numerocase_coordonnees(self.cases_occupe[indice_reel][0])
            y = conversion_numerocase_coordonnees(self.cases_occupe[indice_reel][1])
            pyxel.rect(x, y, 11, 11, 4)
            direction_case_avant = trouve_direction(self.cases_occupe[indice_reel], self.cases_occupe[indice_reel - 1])
            direction_case_apres = trouve_direction(self.cases_occupe[indice_reel], self.cases_occupe[indice_reel + 1])
            for direction in [direction_case_avant, direction_case_apres]:
                if direction == "erreur":
                    print("erreur tracer direction serpent")
                else:
                    values = Tracer_orientation_serpent[direction]
                    dx, dy, L, l = values[0], values[1], values[2], values[3]
                    pyxel.rect(x + dx, y + dy, L, l, 3)

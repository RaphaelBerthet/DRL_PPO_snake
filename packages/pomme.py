import pyxel
import random
from .conversion_numero_coordonnees import conversion_numerocase_coordonnees
class Pomme:
    def __init__(self, cases_occupe: list[tuple[int, int]]):
        cases_libres = [(i, j) for i in range(1, 11) for j in range(1, 11)]
        for case in cases_occupe:
            cases_libres.remove(case)
        x, y = random.choice(cases_libres)
        self.x = x
        self.y = y

    def tracer(self):
        pyxel.circ(conversion_numerocase_coordonnees(self.x) + 5, conversion_numerocase_coordonnees(self.y) + 5, 3, 8)

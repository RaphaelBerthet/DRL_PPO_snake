import pyxel
import time
from packages.serpent import Serpent
from packages.pomme import Pomme
from packages.parametres_snake import LONGUEUR, LARGEUR, PERIODE_ACTU
from packages.reseau_neurones_principal import Reseau_neurones_principal
from packages.parametres_reseau_principal import TAILLE_STATE
import numpy as np
from packages.build_state import build_state
import random

pyxel.init(LONGUEUR, LARGEUR, title='snake')

def draw():
    pyxel.cls(0)
    ## grille
    pyxel.rect(0, 0, 121, 1, 11)
    pyxel.rect(0, 0, 1, 121, 11)
    pyxel.rect(120, 0, 1, 121, 11)
    pyxel.rect(0, 120, 121, 1, 11)
    for i in range(1, 10):
        pyxel.rect(i * 12, 1, 1, 119, 11)
        pyxel.rect(1, i * 12, 119, 1, 11)

    serpent.tracer()
    pomme.tracer()

def update():
    global last_t, pomme

    state = build_state(TAILLE_STATE, serpent, pomme)
    serpent.direction = int(np.argmax(reseau_neurones.calcul_couche_sortie(state))) + 1
    if time.perf_counter() - PERIODE_ACTU > last_t:
        pomme, partie_en_cours, _ = serpent.avancer(pomme)
        last_t = time.perf_counter()
        if not partie_en_cours:
            time.sleep(1)
            pyxel.quit()

serpent = Serpent(random.randint(-2, 2) + 5, random.randint(-2, 2) + 5)
pomme = Pomme(serpent.cases_occupe)
last_t = time.perf_counter()
reseau_neurones = Reseau_neurones_principal("reseau_neurones_principal.npz")

pyxel.run(update, draw)
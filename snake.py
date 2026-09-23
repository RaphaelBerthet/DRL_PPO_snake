import pyxel
import time
from packages.serpent import Serpent
from packages.pomme import Pomme
from packages.parametres_snake import LONGUEUR, LARGEUR, PERIODE_ACTU

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

    serpent.actu_direction()
    if time.perf_counter() - PERIODE_ACTU > last_t:
        pomme, partie_en_cours, _ = serpent.avancer(pomme)
        last_t = time.perf_counter()
        if not partie_en_cours:
            time.sleep(1)
            pyxel.quit()

serpent = Serpent()
pomme = Pomme(serpent.cases_occupe)
last_t = time.perf_counter()


pyxel.run(update, draw)
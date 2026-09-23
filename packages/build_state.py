import numpy as np
from numpy.typing import NDArray
from .serpent import Serpent
from .pomme import Pomme
from collections import deque
import copy

'''voisins: list[tuple[int, int]] = []
for dx in [n - 10 for n in range(1, 20)]:
    for dy in [n - 10 for n in range(1, 20)]:
        ## on parcourt toutes les cases accessibles depuis la tete : 9 sur tous les cotés
        if 1 <= abs(dx) + abs(dy):  # bien accessible au moins 1 coup
            voisins.append((dx, dy))

def build_state(taille_state: int, serpent: Serpent, pomme: Pomme) -> NDArray[np.float32]:
    state = np.zeros(taille_state, dtype=np.float32)
    xtete, ytete = serpent.cases_occupe[0]

    # Une seule passe sur le serpent, O(L) total (au lieu de O(360*L))
    temps_liberation = {
        pos: len(serpent.cases_occupe) - i
        for i, pos in enumerate(serpent.cases_occupe)
    }

    indice = 0
    for d in voisins:
        dx, dy = d
        n = abs(dx) + abs(dy)
        pos = (xtete + dx, ytete + dy)

        if not (1 <= pos[0] <= 10 and 1 <= pos[1] <= 10):
            state[indice] = -1
        elif pos in temps_liberation and temps_liberation[pos] > n:
            state[indice] = -0.2 -((temps_liberation[pos] - n) / 100) * 0.8
        elif pos == (pomme.x, pomme.y):
            state[indice] = 1
        else:
            state[indice] = 0
        indice += 1
    return state
'''

'''_dx = np.array([d[0] for d in voisins], dtype=np.int32)
_dy = np.array([d[1] for d in voisins], dtype=np.int32)
_n  = np.abs(_dx) + np.abs(_dy)

def build_state(taille_state, serpent, pomme):
    xtete, ytete = serpent.cases_occupe[0]
    px = xtete + _dx
    py = ytete + _dy

    hors_plateau = ~((1 <= px) & (px <= 10) & (1 <= py) & (py <= 10))

    grille_temps = np.zeros((12, 12), dtype=np.float32)  # marge pour indices hors bornes
    for i, (cx, cy) in enumerate(serpent.cases_occupe):
        if 0 <= cx <= 11 and 0 <= cy <= 11:
            grille_temps[cx, cy] = len(serpent.cases_occupe) - i

    px_clip = np.clip(px, 0, 11)
    py_clip = np.clip(py, 0, 11)
    temps_lib = grille_temps[px_clip, py_clip]

    danger = (temps_lib > _n)
    est_pomme = (px == pomme.x) & (py == pomme.y)

    state = np.zeros(taille_state, dtype=np.float32)
    state[danger & ~hors_plateau] = -0.2 - ((temps_lib[danger & ~hors_plateau] - _n[danger & ~hors_plateau]) / 100) * 0.8
    state[est_pomme & ~danger & ~hors_plateau] = 1.0
    state[hors_plateau] = -1.0
    return state'''

voisins: list[tuple[int, int]] = []  # len(voisins) = 60
for dx in [n - 5 for n in range(11)]:
    for dy in [n - 5 for n in range(11)]:
        ## on parcourt toutes les cases accessibles depuis la tete : 9 sur tous les cotés
        if 1 <= abs(dx) + abs(dy) <= 5:  # bien accessible au moins 1 coup
            voisins.append((dx, dy))

def build_state(taille_state, serpent: Serpent, pomme: Pomme):
    state = np.zeros(taille_state, dtype=np.float32)
    xtete, ytete = serpent.cases_occupe[0][0], serpent.cases_occupe[0][1]
    state[0] = (xtete - pomme.x) / 10
    state[1] = (ytete - pomme.y) / 10
    temps_liberation = {
        pos: len(serpent.cases_occupe) - i
        for i, pos in enumerate(serpent.cases_occupe)
    }
    indice = 2
    for d in voisins:
        dx, dy = d
        n = abs(dx) + abs(dy)
        pos = (xtete + dx, ytete + dy)
        if not (1 <= pos[0] <= 10 and 1 <= pos[1] <= 10):
            state[indice] = - 1
        elif pos in temps_liberation and temps_liberation[pos] > n:
            state[indice] = -0.2 - ((temps_liberation[pos] - n) / 100) * 0.8
        elif pos == (pomme.x, pomme.y):
            state[indice] = 1
        else:
            state[indice] = 0
        indice += 1
    return state
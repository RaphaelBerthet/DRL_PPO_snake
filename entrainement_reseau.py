from packages.build_state import build_state
from packages.reseau_neurones_principal import Reseau_neurones_principal
from packages.reseau_neurones_V_estimate import Reseau_neurones_V_estimate
from packages.parametres_reseau_principal import TAILLE_STATE, NB_PARTIES, PERIODE_EXPORTATION, PERIODE_ENTRAINEMENT, gamma, GAE_LAMBDA
from packages.parametres_V_estimate import PERIODE_GEL_V_OLD
from packages.parametres_snake import directions
from packages.serpent import Serpent
from packages.pomme import Pomme
import numpy as np
from numpy.typing import NDArray
import copy
import math
import random

"""
state (62): 
distance a la pomme-tete selon x et y
dangers immediats sur 5 cases autour

actions (4):
gauche : 0
droite : 1
haut : 2
bas : 3 
"""

TAILLE_SAMPLE = 2 * TAILLE_STATE + 4


def calcul_gae(rewards, values, values_next, terminals, gamma, lam):
    T = len(rewards)
    advantages = np.zeros(T, dtype=np.float32)
    gae = np.float32(0.0)
    for t in reversed(range(T)):
        delta = rewards[t] + gamma * (1.0 - terminals[t]) * values_next[t] - values[t]
        gae = delta + gamma * lam * (1.0 - terminals[t]) * gae
        advantages[t] = gae
    return advantages

def jouer_une_partie(reseau_neurones_principal: Reseau_neurones_principal) -> NDArray[np.float32]:
    global serpent, pomme
    serpent = Serpent(random.randint(-2, 2) + 5, random.randint(-2, 2) + 5)
    pomme = Pomme(serpent.cases_occupe)
    samples_liste = []
    partie_en_cours = True
    state2 = build_state(TAILLE_STATE, serpent, pomme)
    i = 0
    while partie_en_cours and i < 1000:
        i += 1
        state1 = state2
        action, proba = choisir_action(reseau_neurones_principal, state1)
        reward, partie_en_cours = executer_action(action)
        state2 = build_state(TAILLE_STATE, serpent, pomme)
        extra = np.array([action, reward, proba, not partie_en_cours], dtype=np.float32)
        sample = np.concatenate([state1, state2, extra]).astype(np.float32, copy=False)
        samples_liste.append(sample)
    return np.array(samples_liste, dtype=np.float32)

def choisir_action(reseau_neurones_principal: Reseau_neurones_principal, state: NDArray[np.float32]) -> tuple[int, float]:
    A3 = reseau_neurones_principal.calcul_couche_sortie(state)
    action = np.random.choice(len(A3), p=A3)
    return action, A3[action]  # action : 0, 1, 2...

def executer_action(action: int) -> tuple[float, bool]:
    global pomme, serpent
    dx, dy = directions[action]
    x, y = serpent.cases_occupe[0]
    nouvelle_case = (x + dx, y + dy)
    if nouvelle_case not in serpent.cases_occupe:
        serpent.direction = action + 1

    tete = serpent.cases_occupe[0]
    distance_avant = math.sqrt((pomme.x - tete[0]) ** 2 + (pomme.y - tete[1]) ** 2)
    pomme, partie_en_cours, pomme_mangee = serpent.avancer(pomme)
    tete = serpent.cases_occupe[0]
    if pomme_mangee:
        reward = 1
    elif not partie_en_cours:
        reward = -1
    else:
        '''distance_apres = math.sqrt((pomme.x - tete[0]) ** 2 + (pomme.y - tete[1]) ** 2)
        reward = min(0.01 * (distance_avant - distance_apres), 0.04 * (distance_avant - distance_apres))'''
        reward = 0
    return reward, partie_en_cours

def entrainer(nb_parties: int = NB_PARTIES):
    reseau_neurones_principal = Reseau_neurones_principal("reseau_neurones_principal.npz")
    reseau_neurones_V_estimate = Reseau_neurones_V_estimate("reseau_neurones_V_estimate.npz")
    samples_P_liste = []
    samples_V_liste = []
    nb_samples_P = 0
    reseau_neurones_V_estimate_old = copy.deepcopy(reseau_neurones_V_estimate)
    nb_entrainements = 0
    nb_entrainements_V = 0
    pommes_mangees_fenetre = 0
    longueurs_parties_fenetre = []

    for partie in range(nb_parties):
        new_samples = jouer_une_partie(reseau_neurones_principal)
        pommes_mangees_fenetre += int(np.sum(new_samples[:, TAILLE_STATE * 2 + 1] == 1))
        longueurs_parties_fenetre.append(len(new_samples))
        states  = new_samples[:, :TAILLE_STATE]
        states2 = new_samples[:, TAILLE_STATE:TAILLE_STATE * 2]
        rewards  = new_samples[:, TAILLE_STATE * 2 + 1]
        terminal = new_samples[:, TAILLE_STATE * 2 + 3]

        V_old      = reseau_neurones_V_estimate_old.calcul_V_estimate(states)
        V_next_old = reseau_neurones_V_estimate_old.calcul_V_estimate(states2)

        # GAE calculé sur la trajectoire complète de la partie, dans l'ordre
        advantages_gae = calcul_gae(rewards, V_old, V_next_old, terminal, gamma, GAE_LAMBDA)
        targets = advantages_gae + V_old  # retour cible = A_GAE + V(s)

        # on ajoute l'avantage comme colonne supplémentaire pour le réseau principal
        new_samples_P = np.concatenate([new_samples, advantages_gae[:, None]], axis=1, dtype=np.float32)
        samples_P_liste.append(new_samples_P)
        nb_samples_P += len(new_samples_P)

        new_samples_V = np.concatenate(
            [states, V_old[:, None], targets[:, None]],
            axis=1, dtype=np.float32
        )
        samples_V_liste.append(new_samples_V)

        if nb_samples_P >= PERIODE_ENTRAINEMENT:
            nb_entrainements += 1
            samples_P = np.concatenate(samples_P_liste, axis=0)

            reseau_neurones_principal.entrainement_reseau(samples_P)  # plus besoin de passer reseau_neurones_V_estimate            

            samples_P_liste = []
            samples_V_liste = []
            nb_samples_P = 0

            nb_entrainements_V += 1
            if nb_entrainements_V >= PERIODE_GEL_V_OLD:
                reseau_neurones_V_estimate_old = copy.deepcopy(reseau_neurones_V_estimate)
                nb_entrainements_V = 0

        if nb_entrainements >= PERIODE_EXPORTATION:
            nb_entrainements = 0
            taux = pommes_mangees_fenetre / max(1, len(longueurs_parties_fenetre))
            print(f"progression : {partie * 100 / nb_parties} %")
            print(f"pommes/partie : {taux:.3f} | longueur moyenne : {np.mean(longueurs_parties_fenetre):.1f}")
            pommes_mangees_fenetre = 0
            longueurs_parties_fenetre = []
            reseau_neurones_principal.export_reseau()
            reseau_neurones_V_estimate.export_reseau()

    reseau_neurones_principal.export_reseau()
    reseau_neurones_V_estimate.export_reseau()


if __name__ == "__main__":
    entrainer()

def trouve_direction(origine: tuple[int, int], point: tuple[int, int]) -> str:
    """Renvoie la direction de point par rapport à origine."""
    if (origine[0] + 1, origine[1]) == point:
        return "droite"
    elif (origine[0] - 1, origine[1]) == point:
        return "gauche"
    elif (origine[0], origine[1] + 1) == point:
        return "bas"
    elif (origine[0], origine[1] - 1) == point:
        return "haut"

    return "erreur"
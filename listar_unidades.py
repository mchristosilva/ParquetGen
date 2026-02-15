import string
import os


def listar_unidades():
    unidades = []
    for letra in string.ascii_uppercase:
        drive = f"{letra}:/"
        if os.path.exists(drive):
            unidades.append(drive)
    return unidades

from cores.biped import BipedCore, SpriteMap
from config import BOAR_NAME


class Boar(BipedCore):
    name = BOAR_NAME
    sprites = SpriteMap(
        face_right="boar_right",
        face_down="boar_down",
        face_up="boar_up",
        walk_right=("boar_walkright0", "boar_right", "boar_walkright1", "boar_right"),
        walk_down=("boar_walkdown0", "boar_down", "boar_walkdown1", "boar_down"),
        walk_up=("boar_walkup0", "boar_up", "boar_walkup1", "boar_up")
    )

    def __init__(mouse, *args, faction="enemy", **kwargs):
        super().__init__(
            name=Boar.name,
            faction=faction,
            *args, **kwargs)

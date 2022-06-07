import lib.vector as vector
from dungeon.actors.genie import Genie
from helpers.npc import handle_menus


def on_place(room, stage):
    eyeball = stage.find_elem(cls="Eyeball")
    stage.remove_elem(eyeball)

    GENIE_NAME = "Joshin"
    genie_cell = vector.scale(eyeball.cell, 2)
    genie = Genie(
        name=GENIE_NAME,
        message=handle_menus(GENIE_NAME)
    )
    stage.spawn_elem_at(genie_cell, genie)

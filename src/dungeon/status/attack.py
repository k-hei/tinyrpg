from dungeon.status import StatsEffect
from cores import Stats

from lib.sprite import Sprite
from lib.filters import replace_color
from colors.palette import BLACK, RED
from assets import sprites


class AtkEffect(StatsEffect):
    pass


class AtkUpEffect(AtkEffect):

    image = replace_color(sprites["status_atkup"], BLACK, RED)

    def __init__(effect, potency=1.25):
        super().__init__(stat_mask=Stats(
            st=potency,
            ma=potency,
        ))

    def view(effect):
        return [Sprite(image=AtkUpEffect.image)]


class AtkDownEffect(AtkEffect):

    def __init__(effect, potency=0.75):
        super().__init__(stat_mask=Stats(
            st=potency,
            ma=potency,
        ))

    def view(effect):
        pass

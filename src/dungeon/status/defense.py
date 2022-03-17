from dungeon.status import StatsEffect
from cores import Stats

from lib.sprite import Sprite
from lib.filters import replace_color
from colors.palette import BLACK, RED
from assets import sprites


class DefEffect(StatsEffect):
    pass


class DefUpEffect(DefEffect):

    image = replace_color(sprites["status_defup"], BLACK, RED)

    def __init__(effect, potency=1.25):
        super().__init__(stat_mask=Stats(en=potency))

    def view(effect):
        return [Sprite(image=DefUpEffect.image)]


class DefDownEffect(DefEffect):

    def __init__(effect, potency=0.75):
        super().__init__(stat_mask=Stats(en=potency))

    def view(effect):
        return []

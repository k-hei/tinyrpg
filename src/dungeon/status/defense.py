from dungeon.status import StatsEffect
from cores import Stats


class DefEffect(StatsEffect):
    pass


class DefUpEffect(DefEffect):

    def __init__(effect, potency=1.5):
        super().__init__(stat_mask=Stats(en=potency))


class DefDownEffect(DefEffect):

    def __init__(effect, potency=0.75):
        super().__init__(stat_mask=Stats(en=potency))

from dungeon.status import StatsEffect
from cores import Stats


class AtkEffect(StatsEffect):
    pass


class AtkUpEffect(AtkEffect):

    def __init__(effect, potency=1.25):
        super().__init__(stat_mask=Stats(
            st=potency,
            ma=potency,
        ))


class AtkDownEffect(AtkEffect):

    def __init__(effect, potency=0.75):
        super().__init__(stat_mask=Stats(
            st=potency,
            ma=potency,
        ))

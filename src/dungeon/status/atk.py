from dungeon.status import StatsEffect
from cores import Stats


class AtkEffect(StatsEffect):
    pass


class AtkUpEffect(AtkEffect):

    def __init__(effect):
        super().__init__(stat_mask=Stats(
            st=2,
            ma=2,
        ))


class AtkDownEffect(AtkEffect):

    def __init__(effect):
        super().__init__(stat_mask=Stats(
            st=0.5,
            ma=0.5,
        ))

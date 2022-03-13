from dungeon.status import StatsEffect
from cores import Stats


class AtkEffect(StatsEffect):
    pass


class AtkUpEffect(AtkEffect):

    def __init__(effect):
        EFFECT_POTENCY = 1.5 # TODO: variable potency
        super().__init__(stat_mask=Stats(
            st=EFFECT_POTENCY,
            ma=EFFECT_POTENCY,
        ))


class AtkDownEffect(AtkEffect):

    def __init__(effect):
        EFFECT_POTENCY = 0.75 # TODO: variable potency
        super().__init__(stat_mask=Stats(
            st=EFFECT_POTENCY,
            ma=EFFECT_POTENCY,
        ))

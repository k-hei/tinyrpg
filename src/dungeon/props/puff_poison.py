from dungeon.status.poison import PoisonImmunityEffect
from dungeon.props.puff_cloud import CloudPuff


class PoisonPuff(CloudPuff):
    max_turns = 7

    def effect(puff, game, trigger=None, on_end=None):
        if not super().effect(game, trigger, on_end):
            return False

        if trigger.has_status_effect(PoisonImmunityEffect):
            on_end and on_end()
            return False

        game.inflict_poison(trigger, on_end=on_end)
        return True

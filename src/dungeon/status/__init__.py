
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from cores import Stats


class StatusEffect(ABC):

    def __init__(effect, turns):
        effect._turns = turns

    @property
    def turns(effect):
        return effect._turns

    @property
    def family(effect):
        return type(effect).__bases__[0]

    def step(effect):
        effect._turns = max(0, effect._turns - 1)

    @abstractmethod
    def view(effect):
        return []


class StatsEffect(StatusEffect):

    def __init__(effect, stat_mask, turns=16, *args, **kwargs):
        super().__init__(turns=turns, *args, **kwargs)
        effect._stat_mask = stat_mask

    @property
    def stat_mask(effect):
        return effect._stat_mask


@dataclass
class Status:
    _effects: list[StatusEffect] = field(default_factory=list)

    def get_stat_mask(status):
        stat_masks = [effect.stat_mask for effect in status._effects
            if isinstance(effect, StatsEffect)]

        if not stat_masks:
            return Stats()

        stat_mask = Stats()
        for mask in stat_masks:
            stat_mask.hp *= mask.hp
            stat_mask.st *= mask.st
            stat_mask.ma *= mask.ma
            stat_mask.en *= mask.en
            stat_mask.ag *= mask.ag
            stat_mask.dx *= mask.dx
            stat_mask.lu *= mask.lu

        return stat_mask

    def apply(status, effect):
        effect_family = effect.family
        effect_sibling = next((effect for effect in status._effects
            if isinstance(effect, effect_family)), None)

        if (effect_sibling
        and type(effect) is type(effect_sibling)
        and effect_sibling.turns > effect.turns):
            return # existing effect takes precedence

        status.clear(effect_sibling)
        status._effects.append(effect)

    def clear(status, effect=None):
        if not effect:
            status._effects.clear()
            return

        if type(effect) is type:
            effect_type = effect
            effect = next((effect for effect in status._effects
                if type(effect) is effect_type), None)

        if effect:
            status._effects.remove(effect)

    def step(status):
        for effect in status._effects:
            effect.step()

        status._effects = [effect for effect in status._effects if effect._turns]

    def view(status):
        sprites = []
        for effect in status._effects:
            sprites += effect.view()
        return sprites

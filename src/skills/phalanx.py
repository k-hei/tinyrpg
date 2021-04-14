from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim

ATTACK_DURATION = 12

class Phalanx(Skill):
  def __init__(skill):
    super().__init__(
      name="Phalanx",
      kind="shield",
      element=None,
      desc="Completely nulls one attack",
      cost=12,
      radius=0
    )

  def effect(skill, game, on_end=None):
    game.log.print("But nothing happened...")

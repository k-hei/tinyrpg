from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim

ATTACK_DURATION = 12

class Obscura(Skill):
  def __init__(skill):
    super().__init__(
      name="Obscura",
      kind="spell",
      desc="Blinds target with darkness",
      cost=8,
      radius=1
    )

  def effect(skill, game, on_end=None):
    if game.sp >= skill.cost:
      game.sp -= skill.cost
    game.log.print("But nothing happened...")

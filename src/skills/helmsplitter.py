from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim

ATTACK_DURATION = 12

class HelmSplitter(Skill):
  def __init__(skill):
    super().__init__(
      name="Helm Splitter",
      kind="axe",
      element=None,
      desc="Stuns target with mighty swing",
      cost=6,
      radius=1
    )

  def effect(skill, game, on_end=None):
    if game.sp >= skill.cost:
      game.sp -= skill.cost
    game.log.print("But nothing happened...")

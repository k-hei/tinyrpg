from dungeon.props import Prop
from anims import Anim

class ArrowTrap(Prop):
  period = 45

  def __init__(trap, facing):
    trap.facing = facing
    trap.anim = Anim(duration=60)

  def update(trap):
    trap.anim.update()

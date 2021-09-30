import lib.vector as vector
from anims.attack import AttackAnim
from anims.pause import PauseAnim

def sequence_mage_bump(room, game):
  mage = room.mage
  return [
    lambda step: game.anims.extend([
      [AttackAnim(
        target=mage,
        src=mage.cell,
        dest=vector.add(mage.cell, mage.facing)
      )],
      [PauseAnim(duration=10, on_end=step)],
      [AttackAnim(
        target=mage,
        src=mage.cell,
        dest=vector.add(mage.cell, mage.facing)
      )],
      [PauseAnim(duration=35, on_end=step)],
    ])
  ]
